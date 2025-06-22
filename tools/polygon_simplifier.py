import cv2
from shapely.geometry import Polygon
import numpy as np
from typing import List
 
 
class PolygonSimplifier: 
    """
        Initializes a polygon simplifier using contour approximation.

        Args:
            factor_arclength (float): Fraction of the polygon perimeter to use as the approximation tolerance.
            approx_method (int): OpenCV contour approximation method (default: cv2.CHAIN_APPROX_NONE).

        Attributes:
            factor_arclength (float): Tolerance factor for polygon simplification.
            approx_method (int): Method used by OpenCV's findContours function.
        """
    
    def __init__(
        self,
        factor_arclength: float,
        approx_method: int = cv2.CHAIN_APPROX_NONE
    ):
        self.factor_arclength = factor_arclength
        self.approx_method = approx_method


    def simplify(self, mask: np.ndarray) :
        """
        Simplifies the longest contour found in the input mask and returns it as a polygon.

        Args:
            mask (np.ndarray): Binary mask where the target shape is represented by foreground pixels.

        Returns:
            shapely.geometry.Polygon or None: A simplified and validated polygon representation of the detected contour, 
            or None if no valid contour is found.
        """
        contours = self._find_contours(mask)
        polygon = self._find_longest_polygon(contours)
        if polygon is None:
            return None
        
        simplified_polygon = self._simplify_polygon(polygon)

        if not simplified_polygon.is_valid:
            simplified_polygon = simplified_polygon.buffer(0)

        return simplified_polygon
    

    def _find_contours(self, mask: np.ndarray):
        """
        Finds contours in the provided binary mask image.

        Args:
            mask (np.ndarray): Binary mask where object pixels have value 1, and background pixels have value 0.

        Returns:
            list: Detected contours, each represented as an array of contour points.
        """
        mask_uint8 = (mask.astype(np.uint8)) * 255
        contours, _ = cv2.findContours(
            mask_uint8,
            cv2.RETR_EXTERNAL,
            self.approx_method
        )

        return contours

    def _find_longest_polygon(self, contours: List[np.ndarray]):
        """
        Converts contours to polygons and returns the one with the longest perimeter.

        Args:
            contours (List[np.ndarray]): List of contour arrays, each representing a sequence of points.

        Returns:
            shapely.geometry.Polygon or None: The polygon with the greatest boundary length, or None if no valid polygon is found.
        """
        polygons = []
        for c in contours:
            if len(c) > 2:
                # reshape to (n,2) and convert to list of [x,y]
                pts = c.reshape(-1, 2).tolist()
                polygons.append(Polygon(pts))

        if not polygons:
            return None
        
        # perimeter is length of polygon boundary
        return max(polygons, key=lambda p: p.length)


    def _simplify_polygon(self, polygon: Polygon):
        """
        Simplifies a polygon using the Ramer–Douglas–Peucker algorithm.

        Args:
            polygon (shapely.geometry.Polygon): Input polygon to be simplified.

        Returns:
            shapely.geometry.Polygon: Simplified polygon based on the arc length tolerance.
        """
        coords = np.array(polygon.exterior.coords, dtype=np.int32).reshape(-1, 1, 2)
        peri = cv2.arcLength(coords, closed=True)

        epsilon = self.factor_arclength * peri
        approx = cv2.approxPolyDP(coords, epsilon, closed=True)

        simplified_pts = approx.reshape(-1, 2)

        return Polygon(simplified_pts)
