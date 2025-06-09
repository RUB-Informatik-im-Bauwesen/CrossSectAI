
from segment_anything import SamPredictor

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

    Parameters
    ----------
    sam_chkpt : str
        Path to the SAM model checkpoint file.
    model_type : str
        Type of SAM model variant to use. Typically one of: "vit_h", "vit_l", "vit_b".
    device : str
        Torch device identifier, e.g. "cuda:0" or "cpu".
    multimask : bool
        If True, the generator will return multiple mask proposals per input.
    """

    def __init__(self, 
                 sam_chkpt, 
                 model_type, 
                 device, 
                ):
        
        from segment_anything import sam_model_registry
        
        sam = sam_model_registry[model_type](checkpoint=sam_chkpt)
        sam.to(device=device)
        
        super().__init__(sam)


    