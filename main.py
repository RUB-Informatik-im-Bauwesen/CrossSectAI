import yaml
import argparse

from tools.cross_section_detector import CrossSectionDetector
from tools.mask_generator import MaskGenerator
from tools.polygon_simplifier import PolygonSimplifier
from tools.parameter_extractor import ParameterExtractor

from pathlib import Path
import cv2
from tqdm import tqdm
import numpy as np

from utils import general_utils

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", type=Path, required=True,
                        help="Path to a PNG image or a folder containing PNG images.")
    parser.add_argument("-o", "--output", type=Path, required=True,
                        help="Path to the output directory.")
    parser.add_argument("-c", "--config", type=Path, default=Path("default.yaml"),
                        help="Optional path to a configuration file (default: default.yaml).")

    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output
    config_file = args.config

    if input_path.is_file():
        if input_path.suffix.lower() == ".png":
            image_paths = [input_path]
        else:
            raise ValueError(f"The provided file is not a PNG image: {input_path}")
    elif input_path.is_dir():
        image_paths = [f for f in input_path.iterdir() if input_path.suffix.lower() == ".png"]
    else:
        raise FileNotFoundError(f"The provided path does not exist: {input_path}")

    if not output_dir.exists():
        output_dir.mkdir(parents=True, exist_ok=True)

    with open(str(config_file), 'r') as config_file:
        config = yaml.safe_load(config_file)

    # Init components
    cross_section_detector = CrossSectionDetector(
        weight_path=config["CrossSectionDetector"]["model"]
    )

    mask_generator = MaskGenerator(
        sam_chkpt=config["MaskGenerator"]["sam_chkpt"],
        model_type=config["MaskGenerator"]["model_type"],
        device=config["MaskGenerator"]["device"]
    )

    polygon_simplifier = PolygonSimplifier(
        factor_arclength = config["PolygonSimplifier"]["factor_arclength"],
        approx_method = cv2.CHAIN_APPROX_NONE
    )

    parameter_extractor = ParameterExtractor(
        weight_overlap = config["ParameterOptimizer"]["weight_overlap"],
        weight_distance = config["ParameterOptimizer"]["weight_distance"],
        weight_aspect_ratio = config["ParameterOptimizer"]["weight_aspect_ratio"]
    )

    for img_path in tqdm(image_paths):
        img = cv2.imread(str(img_path))

        geojson_features = []

        detection_results = cross_section_detector.predict(
            source=img,
            conf=config["CrossSectionDetector"]["conf"],
            iou=config["CrossSectionDetector"]["iou"],
            imgsz=config["CrossSectionDetector"]["imgsz"],
            device=config["CrossSectionDetector"]["device"]
        )

        if len(detection_results[0].boxes) == 0:
            continue

        mask_generator.set_image(img)

        for box in detection_results[0].boxes:
            template_class_id = int(box.cls.cpu().tolist()[0])

            x0, y0, x1, y1 = box.xyxy.cpu().tolist()[0]

            masks, scores, logits = mask_generator.predict(
                box=np.array([x0, y0, x1, y1]),
                multimask_output=config["MaskGenerator"]["multimask"]
            )

            bi_mask = masks[0]

            # Load templates
            match template_class_id:
                case 0:
                    from templates.slab_template import SlabTemplate
                    template = SlabTemplate()
                case 1:
                    from templates.t_girder_template import TGirderTemplate
                    template = TGirderTemplate()
                case 2:
                    from templates.tapered_t_girder_template import TaperedTGirderTemplate
                    template = TaperedTGirderTemplate()

            reference_polygon = polygon_simplifier.simplify(bi_mask)

            initial_parameters = template.estimate_initial_parameters_simple(reference_polygon)

            final_parameters = parameter_extractor.optimize(
                template,
                reference_polygon,
                maxiter=config["ParameterOptimizer"]["maxiter"],
                initial_temp=config["ParameterOptimizer"]["initial_temp"])

            final_polygon = template.__class__.make_polygon_from_params(final_parameters)

            geojson_features.append(
                general_utils.polygon_to_geojson_feature(
                    final_polygon,
                    template_class_id,
                    config["General"]["final_polygon_color"],
                    feature_index=len(geojson_features),
                )
            )

        general_utils.write_geojson_file(output_dir, img_path.stem, geojson_features)
