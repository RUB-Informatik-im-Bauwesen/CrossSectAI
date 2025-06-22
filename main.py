import yaml
import argparse
import csv

from tools.cross_section_detector import CrossSectionDetector
from tools.mask_generator import MaskGenerator
from tools.polygon_simplifier import PolygonSimplifier
from tools.parameter_extractor import ParameterExtractor

from pathlib import Path
import cv2
from tqdm import tqdm
import numpy as np

from utils import drawing_utils, general_utils

if __name__ == "__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument("-i", "--input", type=Path, required=True, 
                        help="Path to a PNG image or a folder containing PNG images.")
    parser.add_argument("-o", "--output", type=Path, required=True,
                        help="Path to the output directory.")
    parser.add_argument("-c", "--config", type=Path, default=Path("default.yaml"),
                        help="Optional path to a configuration file (default: default.yaml).")
    parser.add_argument("--draw-results", action="store_true",
                        help="Draw and save intermediate results (default: False).")
    parser.add_argument("--save-coco", action="store_true",
                        help="Save detections and segmentations in COCO format (default: False).")
    parser.add_argument("--template-type", type=int, choices=[0, 1, 2], default=2,
                        help="Template type: 0 = Slab Girder, 1 = T-Girder, 2 = Tapered T-Girder (default: 2).")
    


    args = parser.parse_args()

    input_path = args.input
    output_dir = args.output
    config_file = args.config

    template_type = args.template_type

    DRAW_RESULTS = args.draw_results
    SAVE_COCO = args.save_coco
    

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


    if DRAW_RESULTS:
        result_image_folder = Path.joinpath(output_dir, "Results")
        result_image_folder.mkdir(parents=True, exist_ok=True)
        


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


    # Load templates

    match template_type:
        case 0:
            from templates.slab_template import SlabTemplate
            template = SlabTemplate()
        case 1:
            from templates.t_girder_template import TGirderTemplate
            template = TGirderTemplate()
        case 2:
            from templates.tapered_t_girder_template import TaperedTGirderTemplate
            template = TaperedTGirderTemplate()
  

    
    if SAVE_COCO:
        coco_results = general_utils.create_coco_result_file()
        img_counter = 0
        annotation_counter = 0
        
        
    csv_header = [
        "Bbox_x0",
        "Bbox_y0",
        "Bbox_x1",
        "Bbox_y1",
        "template_type",
        "P1",
        "P2",
        "P3",
        "P4",
        "P5",
        "P6",
        "P7",
        "P8"
    ]
    
    
    allplan_script_written = False
        
    
    for img_path in tqdm(image_paths):
        img = cv2.imread(str(img_path))
        img_height, img_width, _ = img.shape

        if DRAW_RESULTS:
            result_image_bbox = drawing_utils.clone_image(img)
            result_image_mask = drawing_utils.clone_image(img)
            result_image_polygon = drawing_utils.clone_image(img)
            result_image_final_polygon = drawing_utils.clone_image(img)


        csv_result_file = []
        csv_result_file.append(csv_header)
        
        
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
            x0, y0, x1, y1 = box.xyxy.cpu().tolist()[0]
            bbox = [x0, y0, x1-x0, y1-y0]

        
                        
            masks, scores, logits = mask_generator.predict(
                box=np.array([x0, y0, x1, y1]),
                multimask_output=config["MaskGenerator"]["multimask"]
            )

            bi_mask = masks[0]

                        

            if SAVE_COCO:
                rle = general_utils.binary_mask_to_rle_compressed(bi_mask)
                
                area = (x1 - x0)*(y1 - y0)
                
                coco_results["annotation"].append({
                    "id": annotation_counter, 
                    "image_id": img_counter, 
                    "category_id": 0, 
                    "segmentation": rle, 
                    "area": area, 
                    "bbox": bbox, 
                    "iscrowd": 1,
                })
                
                annotation_counter += 1


            reference_polygon = polygon_simplifier.simplify(bi_mask)          
    
            initial_parameters = template.estimate_initial_parameters_simple(reference_polygon)

            final_parameters = parameter_extractor.optimize(
                template, 
                reference_polygon, 
                maxiter=config["ParameterOptimizer"]["maxiter"], 
                initial_temp=config["ParameterOptimizer"]["initial_temp"])
            
            match template_type:
                case 0:
                    P1 = final_parameters[0]
                    P2 = final_parameters[1]
                    P3 = final_parameters[2]
                    P4 = final_parameters[3]
                    P5 = 0
                    P6 = final_parameters[4]
                    P7 = final_parameters[5]
                    P8 = 0
                case 1:
                    P1 = final_parameters[0]
                    P2 = final_parameters[1]
                    P3 = final_parameters[2]
                    P4 = final_parameters[3]
                    P5 = final_parameters[4]
                    P6 = final_parameters[5]
                    P7 = final_parameters[6]
                    P8 = 0
                case 2:
                    P1 = final_parameters[0]
                    P2 = final_parameters[1]
                    P3 = final_parameters[2]
                    P4 = final_parameters[3]
                    P5 = final_parameters[4]
                    P6 = final_parameters[5]
                    P7 = final_parameters[6]
                    P8 = final_parameters[7]
                    
            

            csv_result_file.append(
                [
                    round(x0, 4), round(y0,4), round(x1,4), round(y1,4),
                    template_type,
                    round(P1, 4), round(P2, 4), round(P3, 4), round(P4, 4),
                    round(P5, 4), round(P6, 4), round(P7, 4), round(P8, 4)
                ]
            )
            
            
            # Currently, only the first cross-section is exported to the Allplan Bridge script
            if allplan_script_written == False:
                general_utils.write_allplan_parameter_file(output_dir, [P1, P2, P3, P4, P5, P6, P7, P8], template_type)
                allplan_script_written = True
            
            
           
       
            if DRAW_RESULTS:
                result_image_bbox = drawing_utils.draw_bbox(
                    result_image_bbox, 
                    bbox,
                    color_hex=config["General"]["bbox_color"],
                    alpha=0.5
                )
                
                result_image_mask = drawing_utils.draw_mask(
                    result_image_mask, 
                    bi_mask,
                    color_hex=config["General"]["mask_color"],
                    alpha=0.5
                )

                result_image_polygon = drawing_utils.draw_polygon(
                    result_image_polygon, 
                    reference_polygon,
                    color_hex=config["General"]["polygon_color"],
                    alpha=0.5
                )
                
                final_polygon = template.__class__.make_polygon_from_params(final_parameters)
                result_image_final_polygon = drawing_utils.draw_polygon(
                    result_image_final_polygon, 
                    final_polygon,
                    color_hex=config["General"]["final_polygon_color"],
                    alpha=0.5
                )
          
        if SAVE_COCO:
            coco_results["images"].append({
                "id": img_counter, 
                "width": img_width, 
                "height": img_height, 
                "file_name": img_path.name, 
                "license": 0, 
                "flickr_url": "", 
                "coco_url": "", 
                "date_captured": "",
            })

            img_counter += 1

        if DRAW_RESULTS:
            
            img_filepath_bbox = Path.joinpath(result_image_folder, f"{img_path.stem}_bbox.png")
            cv2.imwrite(str(img_filepath_bbox), result_image_bbox)
            
            img_filepath_mask = Path.joinpath(result_image_folder, f"{img_path.stem}_mask.png")
            cv2.imwrite(str(img_filepath_mask), result_image_mask)
            
            img_filepath_polygon = Path.joinpath(result_image_folder, f"{img_path.stem}_polygon.png")
            cv2.imwrite(str(img_filepath_polygon), result_image_polygon)
            
            img_filepath_final_polygon = Path.joinpath(result_image_folder, f"{img_path.stem}_final_polygon.png")          
            cv2.imwrite(str(img_filepath_final_polygon), result_image_final_polygon)
            
            
        csv_filepath = Path.joinpath(output_dir, f"{img_path.stem}.csv")
        with open(str(csv_filepath), 'w') as fw:
            writer = csv.writer(fw, delimiter=';')
            writer.writerows(csv_result_file)
            
    if SAVE_COCO:
        import json
        
        coco_filepath = Path.joinpath(output_dir, "coco.json")
        with open(str(coco_filepath), "w") as fw:
            json.dump(coco_results, fw)
        

        
    