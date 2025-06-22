import math
from typing import Sequence
from shapely import Polygon

class BaseTemplate():
      """
      Base class for geometric template processing and line classification.
      Initializes default thresholds and tolerances used for edge filtering and orientation detection.
      """
      def __init__(self):            
            self.horizontal_angle_threshold = 15
            self.vertical_angle_threshold = 35

            self.min_edge_length  = 10
            self.parameter_range_limit  = 500
            
            self.min_bound = 10 
            
      def create_bounds(self, params: Sequence[float]):         
            """
            Creates search bounds for each parameter by applying a symmetric range around the initial value.

            Args:
                  params (Sequence[float]): List of initial parameter values.

            Returns:
                  list: A list of [lower_bound, upper_bound] pairs for each parameter.
            """
            bounds = []
            for param in params:
                  lower = max(self.min_bound, param - self.parameter_range_limit)
                  upper = param + self.parameter_range_limit
                  bounds.append([lower, upper])
            return bounds

      def find_edge_lines(self, polygon: Polygon):
            """
            Finds and sorts nearly horizontal and vertical edges of the polygon.
            
            Args:
                  polygon (shapely.geometry.Polygon): Input polygon to analyze.

            Returns:
                  None: Stores the sorted lines in instance variables:
                        - sorted_top_to_bottom_horizontal_lines
                        - sorted_left_to_right_vertical_lines
            """
            horizontal_lines = self.find_lines_with_angle(
                  polygon,
                  target_angle=0, 
                  angle_tolerance=self.horizontal_angle_threshold
            )
            self.sorted_top_to_bottom_horizontal_lines = sorted(
                  horizontal_lines,
                  key=lambda line: min(line[0][1], line[1][1])
            )

            vertical_lines = self.find_lines_with_angle(
                  polygon,
                  target_angle=90, 
                  angle_tolerance=self.vertical_angle_threshold
            )
            self.sorted_left_to_right_vertical_lines = sorted(
                  vertical_lines,
                  key=lambda line: min(line[0][0], line[1][0])
            )
            
            
      def find_lines_with_angle(self, polygon: Polygon, target_angle: float, angle_tolerance: float):
            """
            Identifies edges in the polygon whose orientation matches a target angle within a given tolerance.

            Args:
                  polygon (shapely.geometry.Polygon): Input polygon to analyze.
                  target_angle (float): Desired angle in degrees relative to the horizontal axis.
                  angle_tolerance (float): Allowed deviation from the target angle in degrees.

            Returns:
                  list: A list of lines matching the target orientation, each represented as [[x0, y0], [x1, y1]].
            """
            
            coords = list(polygon.exterior.coords)
            lines = []

            for (x0, y0), (x1, y1) in zip(coords, coords[1:]):
                  if self.lineLength((x0, y0), (x1, y1)) < self.min_line_length:
                        continue
                  
                  # Skip short lines
                  if self.min_line_length > self._lineLength((x0, y0), (x1, y1)):
                        continue

                  angle = abs(math.degrees(math.atan2(y1 - y0, x1 - x0))) % 360
                  
                  if abs(angle - target_angle) <= angle_tolerance:
                        lines.append([[x0, y0], [x1, y1]])
        
            return lines
           
      

      def line_length(self, line):
            """
            Calculates the length of a line segment.

            Args:
                  line (tuple): A pair of endpoints, each as (x, y) coordinates.

            Returns:
                  float: The Euclidean distance between the two endpoints.
            """
            (x0, y0), (x1, y1) = line

            return math.hypot(x1 - x0, y1 - y0)
