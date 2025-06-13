from typing import Sequence
from pathlib import Path
import numpy as np
from itertools import groupby
from pycocotools import mask

def binary_mask_to_rle_uncompressed(binary_mask: np.ndarray):
    """
    Converts a 2D binary mask to run-length encoding (RLE).
    Parameters:
        binary_mask (np.ndarray): A 2D array of 0s and 1s.

    Returns:
        dict: A dictionary with RLE 'counts' and original 'size'.
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
        dict: A dictionary with RLE 'counts' as a UTF-8 string and the original 'size'.
    """
    
    binary_mask = np.asfortranarray(binary_mask.astype(np.uint8))
    
    rle = mask.encode(binary_mask)  
    rle["counts"] = rle["counts"].decode("utf-8")

    return rle


def write_allplan_parameter_file(output_dir: str, params: Sequence[float], template_type: int):
    """
    Writes a TCL parameter file for Allplan using the provided template type and parameters.
    Parameters at index 0 and 1 are skipped intentionally.
    """

    lines = [
        "# Define template and parameters",
        "# Template types: 0 = Slab Girder, 1 = T-Girder, 2 = Tapered T-Girder",
        f"set template_type {template_type}",
        "# Parameter values"
    ]
    
    for i in range(2, len(params)):
        value = float(params[i])
        lines.append(f"set P{i} {value}")

    output_path = Path.joinpath(Path(output_dir), "variables.tcl")

    with open(str(output_path), "w") as file:
        file.write("\n".join(lines) + "\n")

def create_coco_result_file():
    """
    Creates an empty COCO-style result dictionary.

    Returns:
        dict: A dictionary with empty fields for images, annotations, and metadata 
              in COCO format.
    """

    results = {
        "images": [],
        "annotation": [],
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
        }]
    }

    return results


