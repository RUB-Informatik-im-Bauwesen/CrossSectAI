from typing import Sequence
from pathlib import Path
import json
import time
from datetime import datetime, timezone
import numpy as np
from itertools import groupby
from pycocotools import mask
from shapely import affinity
from shapely.geometry import Polygon, mapping

TEMPLATE_TYPE_NAMES = {
    0: "Slab Girder",
    1: "T-Girder",
    2: "Tapered T-Girder",
}

def binary_mask_to_rle_uncompressed(binary_mask: np.ndarray):
    """
    Converts a 2D binary mask to uncompressed run-length encoding (RLE).

    Args:
        binary_mask (np.ndarray): A 2D NumPy array consisting of 0s and 1s.

    Returns:
        dict: A dictionary with the following keys:
            - 'counts': A list of run-length encoded pixel counts.
            - 'size': The original size of the mask as [height, width].
    """
   
    if len(binary_mask.shape) == 2:
        binary_mask = np.ravel(binary_mask).astype(int)

    rle = {'counts': [], 'size': list(binary_mask.shape)}
    counts = rle['counts']
    
    for i, (value, group) in enumerate(groupby(binary_mask)):
        if i == 0 and value == 1:
            counts.append(0)  # Leading run of 1s must be preceded by a zero-length run of 0s
        counts.append(len(list(group)))
        
    return rle  







def binary_mask_to_rle_compressed(binary_mask: np.ndarray):
    """
    Converts a 2D binary mask to COCO-style run-length encoding (RLE).

    Args:
        binary_mask (np.ndarray): A 2D array containing 0s and 1s.

    Returns:
        dict: A dictionary with the following keys:
            - 'counts': RLE as a UTF-8 string 
            - 'size': The original size of the mask as [height, width].
    """
    
    binary_mask = np.asfortranarray(binary_mask.astype(np.uint8))
    
    rle = mask.encode(binary_mask)  
    rle["counts"] = rle["counts"].decode("utf-8")

    return rle


def polygon_to_geojson_feature(polygon: Polygon, template_type: int, color: str, feature_index: int):
    """
    Converts a fitted cross-section polygon into a GeoJSON Polygon Feature.

    Coordinates are kept in raw image-pixel units (no scale factor applied) and are
    translated so that the polygon's own bounding-box center maps to (0, 0), rather than
    being left relative to the image's top-left corner.

    Args:
        polygon (Polygon): Shapely polygon in image-pixel coordinates.
        template_type (int): Identifier for the type of cross-section template.
        color (str): Hex color code to store on the feature's properties.
        feature_index (int): Index of this feature among the features generated for the
            current image, used to keep generated ids unique.

    Returns:
        dict: A GeoJSON Feature with a Polygon geometry.
    """

    min_x, min_y, max_x, max_y = polygon.bounds
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    centered_polygon = affinity.translate(polygon, xoff=-center_x, yoff=-center_y)

    geometry = mapping(centered_polygon)
    geometry["coordinates"] = [
        [[int(round(x)), int(round(y))] for x, y in ring]
        for ring in geometry["coordinates"]
    ]

    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    return {
        "type": "Feature",
        "geometry": geometry,
        "properties": {
            "id": f"polygon-{int(time.time() * 1000)}-{feature_index}",
            "name": TEMPLATE_TYPE_NAMES.get(template_type),
            "color": color,
            "created_at": created_at,
        },
    }


def write_geojson_file(output_dir: str, image_stem: str, features: Sequence[dict]):
    """
    Writes a GeoJSON FeatureCollection file containing the given Polygon features.

    Args:
        output_dir (str): Directory where the GeoJSON file will be saved.
        image_stem (str): Stem of the source image filename, used to name the output file.
        features (Sequence[dict]): GeoJSON Feature dicts, e.g. from `polygon_to_geojson_feature`.

    Returns:
        None
    """

    feature_collection = {
        "type": "FeatureCollection",
        "features": list(features),
    }

    output_path = Path.joinpath(Path(output_dir), f"{image_stem}.geojson")

    with open(str(output_path), "w") as file:
        json.dump(feature_collection, file, indent=2)




def create_coco_result_file():
    """
    Creates an empty result dictionary following the COCO format.

    Returns:
        dict: A dictionary with the following top-level fields:
            - 'info': Dictionary with general dataset metadata.
            - 'license': List containing a single license entry.
            - 'categories': List containing category definition.
            - 'images': Empty list to store image metadata.
            - 'annotation': Empty list to store annotation entries.
    """

    results = {
        "info": {
            "year": "", 
            "version": "", 
            "description": "", 
            "contributor": "", 
            "url": "", 
            "date_created": "",
        },
        "license": [{
            "id": 0, 
            "name": "", 
            "url": "",
        }],
        "categories": [{
            "id": 0, 
            "name": "bridge cross-section", 
            "supercategory": "infrastructure"
        }],
        "images": [],
        "annotation": [],
    }

    return results


    