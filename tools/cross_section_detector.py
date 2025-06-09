from ultralytics import YOLO


class CrossSectionDetector(YOLO):
    """
    A lightweight wrapper around the YOLO model for detecting cross-sectional shapes.

    This class currently inherits directly from the YOLO base class and initializes 
    the model from a provided weight file. While it does not add new behavior at the 
    moment, it provides a clear interface for integrating cross-section detection 
    into the processing pipeline.

    Parameters
    ----------
    weight_path : str
        Path to the YOLO model weights.
    """

    def __init__(self, weight_path):
        super().__init__(model=weight_path)


    