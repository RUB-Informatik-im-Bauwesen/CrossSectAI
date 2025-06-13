import cv2
from shapely.geometry import Polygon
import numpy as np
from typing import List, Optional
 
 
class PolygonSimplifier: 
    """
    Extract and simplify the longest contour polygon from a binary mask.
    Simplification reduces vertex count for faster downstream processing.
    """
    
    def __init__(
        self,
        factor_arclength: float,
        approx_method: int = cv2.CHAIN_APPROX_NONE
    ):
        """
        :param factor_arclength: fraction of perimeter used as tolerance
        :param approx_method: contour retrieval method for findContours
        """
        self.factor_arclength = factor_arclength
        self.approx_method = approx_method


    def simplify(self, mask: np.ndarray) :
        """
        Find the longest outer contour in the mask and return its simplified polygon.

        :param mask: binary mask array (any non zero is treated as foreground)
        :return: simplified polygon or None if no valid contour exists
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
        mask_uint8 = (mask.astype(np.uint8)) * 255
        contours, _ = cv2.findContours(
            mask_uint8,
            cv2.RETR_EXTERNAL,
            self.approx_method
        )

        return contours

    def _find_longest_polygon(self, contours: List[np.ndarray]):
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
        coords = np.array(polygon.exterior.coords, dtype=np.int32).reshape(-1, 1, 2)
        peri = cv2.arcLength(coords, closed=True)

        epsilon = self.factor_arclength * peri
        approx = cv2.approxPolyDP(coords, epsilon, closed=True)

        simplified_pts = approx.reshape(-1, 2)

        return Polygon(simplified_pts)
