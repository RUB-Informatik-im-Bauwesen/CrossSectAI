import math
from typing import Sequence


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

      def find_edge_lines(self):
            """
            Finds and sorts nearly horizontal and vertical edges of the polygon.

            Returns:
                  None: Stores the sorted lines in instance variables:
                        - sorted_top_to_bottom_horizontal_lines
                        - sorted_left_to_right_vertical_lines
            """
            horizontal_lines = self.find_lines_with_angle(
                  target_angle=0, 
                  angle_tolerance=self.horizontal_angle_threshold
            )
            self.sorted_top_to_bottom_horizontal_lines = sorted(
                  horizontal_lines,
                  key=lambda line: min(line[0][1], line[1][1])
            )

            vertical_lines = self.find_lines_with_angle(
                  target_angle=90, 
                  angle_tolerance=self.vertical_angle_threshold
            )
            self.sorted_left_to_right_vertical_lines = sorted(
                  vertical_lines,
                  key=lambda line: min(line[0][0], line[1][0])
            )
            
      # TODO:
      # Was mit dem polygon_gt
      def find_lines_with_angle(self, target_angle, angle_tolerance):
            """
            Identifies lines in the polygon that match a target angle.

            Args:
                  target_angle (float): Desired angle in degrees relative to the horizontal axis.

            Returns:
                  list: A list of lines, each represented by two endpoints [[x0, y0], [x1, y1]].
            """
            
            coords = list(self.polygon_gt.exterior.coords)
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
