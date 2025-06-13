import math
from shapely import Polygon
from typing import Sequence
from  scipy.optimize import dual_annealing

class ParameterExtractor:
    """
    Extracts geometric parameters by optimizing a loss function 
    that considers three fundamental aspects of bounding box alignment:
    overlap area, distance between box centers, and aspect ratio consistency.

    Args:
        weight_overlap (float): Weight for the IoU-based overlap area term.
        weight_distance (float): Weight for the DIoU-based center distance term.
        weight_aspect_ratio (float): Weight for the CIoU-based aspect ratio term.
    """
    
    def __init__(
        self,
        weight_overlap: float,
        weight_distance: float,
        weight_aspect_ratio: float
    ):
        self.w_overlap = weight_overlap
        self.w_distance = weight_distance
        self.w_aspect_ratio = weight_aspect_ratio


    def ciou_loss(self, params: Sequence[float], template):
        """
        Compute the combined geometric CIoU loss between the reference polygon and a candidate polygon.

        The loss function integrates three geometric components:
        1. IoU-based overlap loss (area similarity)
        2. Centroid distance loss (center alignment)
        3. Aspect ratio loss (shape similarity)

        Args:
            params (Sequence[float]): Parameter vector used to generate the candidate polygon.
            template: Template object with a `make_polygon_from_params` method.

        Returns:
            float: Combined geometric loss value.
        """
        
        candidate_polygon = template.make_polygon_from_params(params)
        reference_polygon = self.reference_polygon

        overlap_loss = self.iou_loss(reference_polygon, candidate_polygon)
        centroid_loss = self.centroid_alignment_loss(reference_polygon, candidate_polygon)
        aspect_loss = self.aspect_ratio_loss(reference_polygon, candidate_polygon)

        total_loss = self.w_overlap*overlap_loss + self.w_distance*centroid_loss + self.w_aspect_ratio*aspect_loss
        
        return total_loss
        
    
    
    def iou_loss(self, reference_polygon: Polygon, candidate_polygon: Polygon):            
        """
        Compute the IoU-based loss between the reference and candidate polygons.
        
        Args:
            reference_polygon (Polygon): The ground truth or target polygon.
            candidate_polygon (Polygon): The polygon generated from the current parameter estimate.

        Returns:
            float: IoU loss value in the range [0, 1], where 0 indicates perfect overlap.
        """
        
        intersection = reference_polygon.intersection(candidate_polygon).area
        union = reference_polygon.union(candidate_polygon).area
        
        return 1 - intersection/(union+1e-10)
    
        
    def centroid_alignment_loss(self, reference_polygon: Polygon, candidate_polygon: Polygon):
        """
        Compute the centroid alignment loss between the reference and candidate polygons.

        Args:
            reference_polygon (Polygon): The ground truth or target polygon.
            candidate_polygon (Polygon): The polygon generated from the current parameter estimate.

        Returns:
            float: Normalized centroid alignment loss (non-negative), where 0 indicates perfect centroid alignment.
        """
        
        x_ref, y_ref = reference_polygon.centroid.coords[0]
        x_cand, y_cand = candidate_polygon.centroid.coords[0]

        # Compute squared centroid distance
        squared_distance = (x_ref - x_cand) ** 2 + (y_ref - y_cand) ** 2
                
        # Get bounding box corners
        minx_ref, miny_ref, maxx_ref, maxy_ref = reference_polygon.bounds
        minx_cand, miny_cand, maxx_cand, maxy_cand = candidate_polygon.bounds
        
        # Compute squared diagonal length of enclosing box
        min_x = min(minx_ref, minx_cand)
        max_x = max(maxx_ref, maxx_cand)
        min_y = min(miny_ref, miny_cand)
        max_y = max(maxy_ref, maxy_cand)
        
        enclosing_diag_squared = (max_x - min_x) ** 2 + (max_y - min_y) ** 2 + 1e-10

        return squared_distance / enclosing_diag_squared
        
    
    def aspect_ratio_loss(self, reference_polygon: Polygon, candidate_polygon: Polygon):
        """
        Compute the aspect ratio loss between the reference and candidate polygons.

        Args:
            reference_polygon (Polygon): The ground truth or target polygon.
            candidate_polygon (Polygon): The polygon generated from the current parameter estimate.

        Returns:
            float: Squared difference in aspect ratios (non-negative), where 0 indicates identical shape proportions.
        """
        
        iou = 1-self.iou_loss(reference_polygon, candidate_polygon)
        if iou < 0.5:
            return 0.0

        # Get bounds
        minx_ref, miny_ref, maxx_ref, maxy_ref = reference_polygon.bounds
        minx_cand, miny_cand, maxx_cand, maxy_cand = candidate_polygon.bounds

        # Compute width and height for both polygons
        width_ref = maxx_ref - minx_ref
        height_ref = maxy_ref - miny_ref

        width_cand = maxx_cand - minx_cand
        height_cand = maxy_cand - miny_cand
        

        # Aspect ratio difference term
        angle_diff = math.atan2(width_ref, height_ref) - math.atan2(width_cand, height_cand)
        v = (4 / math.pi**2) * (angle_diff ** 2)          
        
        alpha = v / (1 - iou + v + 1e-10)
        return alpha * v
        
        


    def optimize(self, template, reference_polygon, record_iterations=False, **kwargs):
        """
        Optimize template parameters to best fit a given reference polygon.
        The method performs global optimization using dual annealing. 

        Args:
            template: Parametric cross-section template with a method 
                `make_polygon_from_params(params: Sequence[float])`.
            reference_polygon (Polygon): Target polygon to fit the template to.
            track_history (bool): If True, returns all evaluated parameter vectors 
                along with their associated loss values.

        Returns:
            Sequence[float]: Optimal parameter vector.
            If `track_history` is True, also returns a list of all iterations as
            lists (parameter_vector, loss_value).
        """
        
        self.reference_polygon = reference_polygon

        initial_parameters = template.estimate_initial_parameters_simple(reference_polygon)
        initial_bounds = template.create_bounds(initial_parameters)
        
        
        if record_iterations:
            def make_callback(storage):
                def callback(x, f, context):
                    storage.append([x.tolist(), f])  
                return callback
        
            iterations = []
            callback = make_callback(iterations)
        
        else:
            callback = lambda *_: None
        
        results = dual_annealing(
            func=self.ciou_loss, 
            bounds=initial_bounds, 
            args=(template,), 
            callback=callback,
            **kwargs)
    

        if record_iterations:
            return results.x, iterations

        return results.x
