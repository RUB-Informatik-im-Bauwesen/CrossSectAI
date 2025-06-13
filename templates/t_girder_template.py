from shapely import Polygon
from typing import Sequence
from templates.base_template import BaseTemplate
            
           
class TGirderTemplate(BaseTemplate):
    """
    Template class for t-type bridge cross-sections.
    Inherits default settings and utilities from BaseTemplate.
    """ 
    def __init__(self):
        super().__init__()
        

    def estimate_initial_parameters_simple(self, reference_polygon: Polygon):
        """
        Estimates initial template parameters from the bounding box of a reference polygon.

        Args:
            reference_polygon (Polygon): Shapely polygon used as geometric reference.

        Returns:
            list: A list of initial parameter values 
                  [offset_x, offset_y, flange_height, flange_taper_height, web_height, flange_width, web_width].
        """
        # Unpack bounding box
        origin_x, origin_y, max_x, max_y = reference_polygon.bounds
        width = max_x - origin_x
        height = max_y - origin_y

        # Split height into flange and web components
        flange_height = height / 4
        flange_taper_height = height / 4
        web_height = height / 2

        # Split width into flange and web components
        flange_width = width / 8
        web_width = width / 2

        initial_parameters = [
            origin_x,
            origin_y,
            flange_height,
            flange_taper_height,
            web_height,
            flange_width,
            web_width
        ]


        # Build and save the initial candidate polygon
        self.candidate_polygon = TGirderTemplate.make_polygon_from_params(initial_parameters)

        return initial_parameters
      
      
 
    @staticmethod
    def make_polygon_from_params(params: Sequence[float]):
        """
        Creates a t-type cross-section polygon from a set of geometric parameters.

        Args:
            params (Sequence[float]): List of parameter values in the order:
                [offset_x, offset_y, flange_height, flange_taper_height, web_height, flange_width, web_width].

        Returns:
            Polygon: A Shapely polygon representing the cross-section.
        """
        offset_x, offset_y, flange_height, flange_taper_height, web_height, flange_width, web_width = params           
            
        # relative offsets for the 8 corners
        offsets = [
            (0, 0),
            (2 * flange_width + web_width, 0),
            (2 * flange_width + web_width, flange_height),
            (flange_width + web_width, flange_height + flange_taper_height),
            (flange_width + web_width, flange_height + flange_taper_height + web_height),
            (flange_width, flange_height + flange_taper_height + web_height),
            (flange_width, flange_height + flange_taper_height),
            (0, flange_height),
            (0, 0)
        ]

        coords = [(offset_x + dx, offset_y + dy) for dx, dy in offsets]
        polygon = Polygon(coords)

        if not polygon.is_valid:
            polygon = polygon.buffer(0)

        return polygon
      
        

