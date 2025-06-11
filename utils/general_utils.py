from typing import Sequence
from pathlib import Path
import numpy as np
import cv2
from itertools import groupby

def binary_mask_to_rle(binary_mask: np.ndarray):
    """
    Converts a 2D binary mask to run-length encoding (RLE).
    Parameters:
        binary_mask (np.ndarray): A 2D array of 0s and 1s.

    Returns:
        dict: A dictionary with RLE 'counts' and original 'size'.
    """
   
    if len(binary_mask.shape) == 2:
        bimask = np.ravel(binary_mask).astype(int)

    rle = {'counts': [], 'size': list(binary_mask.shape)}
    counts = rle['counts']
    
    for i, (value, group) in enumerate(groupby(bimask)):
        if i == 0 and value == 1:
            counts.append(0)  # Leading run of 1s must be preceded by a zero-length run of 0s
        counts.append(len(list(group)))
        
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
