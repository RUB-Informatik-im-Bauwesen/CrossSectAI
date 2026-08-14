from typing import Sequence
from pathlib import Path
import numpy as np
from itertools import groupby
from pycocotools import mask

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


def write_allplan_parameter_file(output_dir: str, params: Sequence[float], template_type: int):
    """
    Writes a TCL parameter file for Allplan based on the given template type and parameter values.

    Args:
        output_dir (str): Directory where the parameter file will be saved.
        params (Sequence[float]): List of parameter values. Offset parameters 1 and 2 are skipped.
        template_type (int): Identifier for the type of cross-section template to be used in the TCL file.

    Returns:
        None
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


    