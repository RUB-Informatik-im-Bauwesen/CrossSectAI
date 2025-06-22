
from segment_anything import SamPredictor
from segment_anything import sam_model_registry

class MaskGenerator(SamPredictor):
    """
    A wrapper for the Segment Anything Model (SAM) that generates segmentation masks
    for detected cross-sections.

    This class currently extends the base `SamAutomaticMaskGenerator` provided by the 
    SAM model API and passes configuration parameters during initialization. While it 
    doesn't implement new functionality at the moment, it provides a dedicated interface 
    within the geometry reconstruction pipeline for future integration or customization.
    
    Pretrained weights can be downloaded from:
    https://github.com/facebookresearch/segment-anything/blob/main/README.md#model-checkpoints

    Args:
        sam_chkpt (str): Path to the SAM model checkpoint file.
        model_type (str): Variant of the SAM model to initialize. Options include "vit_h", "vit_l", and "vit_b".
        device (str): Torch device identifier, for example, "cuda:0" or "cpu".
    """

    def __init__(self, 
                 sam_chkpt: str, 
                 model_type: str, 
                 device: str, 
                ):
        
        sam = sam_model_registry[model_type](checkpoint=sam_chkpt)
        sam.to(device=device)
        
        super().__init__(sam)


    