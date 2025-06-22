from ultralytics import YOLO


class CrossSectionDetector(YOLO):
    """
    A wrapper class around the YOLO model specifically designed for detecting bridge cross-sections.

    Initializes a YOLO detection model using provided weights. While it does not add new behavior at the 
    moment, it provides a clear interface for integrating cross-section detection 
    into the processing pipeline.

    Args:
        weight_path (str): File path to the pre-trained YOLO model weights.
    """
    def __init__(self, weight_path: str):
        super().__init__(model=weight_path)


    