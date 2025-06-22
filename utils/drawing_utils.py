from PIL import ImageColor
import matplotlib.pyplot as plt
import cv2
import io
import numpy as np


def hex_to_bgr(color_hex: str):
    """Convert a RGB hex color string to a BGR tuple.

    Args:
        color_hex (str): Color as a hexadecimal RGB string (e.g., "#FF0000").

    Returns:
        Tuple: BGR color.
    """
    color_rgb = ImageColor.getrgb(color_hex)

    return color_rgb[::-1]

def clone_image(img: np.array):
    """Return a copy of the input image.

    Args:
        img (np.ndarray): Input image array.

    Returns:
       np.ndarray: A copy of the input image.
    """
    return img.copy()

def draw_line(img: np.ndarray, line: list, color_hex: str, thickness: int = 30):
    """
    Draws a line on a copy of the input image using a specified color and thickness.

    Args:
        img (np.ndarray): Input image array.
        line (list): Coordinates of the line defined as [x0, y0, x1, y1].
        color_hex (str): Color as a hexadecimal RGB string (e.g., "#FF0000").
        thickness (int, optional): Line thickness in pixels (default: 30).

    Returns:
        np.ndarray: A copy of the input image with the specified line drawn on it.
    """
    
    output_image = clone_image(img)
    
    color_bgr = hex_to_bgr(color_hex)

    x0, y0 = line[0]
    x1, y1 = line[1]
    cv2.line(output_image, (int(x0), int(y0)), (int(x1), int(y1)), color_bgr, thickness)

    return output_image


def draw_point(img: np.ndarray, center: tuple, color_hex: str, radius: int = 30, thickness: int = -1):
    """
    Draws a point on a copy of the input image.

    Args:
        img (np.ndarray): Input image array.
        center (tuple): Coordinates of the point as (x, y).
        color_hex (str): Color as a hexadecimal RGB string (e.g., "#FF0000").
        radius (int, optional): Radius of the point in pixels (default: 30).
        thickness (int, optional): Thickness of the circle border in pixels. Use -1 to fill the circle (default: -1).

    Returns:
        np.ndarray: A copy of the input image with the point drawn.
    """

    output_image = clone_image(img)
    color_bgr = hex_to_bgr(color_hex)

    x_center, y_center = center
    cv2.circle(output_image, (int(x_center), int(y_center)), radius, color_bgr, thickness)

    return output_image

def draw_bbox(img: np.ndarray, bbox: tuple, color_hex: str, thickness: int = 5, alpha: float = 0.0):
    """
    Draws a bounding box on the input image, with optional fill and transparency.

    Args:
        img (np.ndarray): Input image array.
        bbox (tuple): Bounding box defined as (x, y, width, height).
        color_hex (str): Color as an RGB hex string (e.g., "#0000FF").
        thickness (int, optional): Border thickness in pixels (default: 5).
        alpha (float, optional): Transparency of the fill area (0.0 = fully transparent, 1.0 = opaque). Default is 0.0.

    Returns:
        np.ndarray: A copy of the input image with the bounding box drawn.
    """
    output_image = clone_image(img)
    overlay = clone_image(img)
    
    color_bgr = hex_to_bgr(color_hex)
    
    
    x, y, w, h = bbox

        
    # Filled rectangle with transparency (optional)
    if alpha > 0.0:
        cv2.rectangle(overlay, (int(x), int(y)), (int(x + w), int(y + h)), color_bgr, -1)
        cv2.addWeighted(overlay, alpha, output_image, 1 - alpha, 0, output_image)
    
    cv2.rectangle(output_image, (int(x), int(y)), (int(x + w), int(y + h)), color_bgr, thickness)
   
    return output_image


def draw_contours(img: np.ndarray, contours: list, color_hex: str, thickness: int = 30):
    """
    Draws contours on a copy of the input image.

    Args:
        img (np.ndarray): Input image array.
        contours (list): List of contours, where each contour is a NumPy array of points.
        color_hex (str): Color as an RGB hex string (e.g., "#FFA500").
        thickness (int, optional): Line thickness for drawing the contours (default: 30).

    Returns:
        np.ndarray: A copy of the input image with contours drawn.
    """
    output_image = clone_image(img)

    if not contours:
        return output_image
    
    color_bgr = hex_to_bgr(color_hex)
    cv2.drawContours(output_image, contours, -1, color_bgr, thickness) # -1 to draw all contours
    
    return output_image


def draw_polygon(
    img: np.ndarray,
    polygon,
    color_hex: str,
    thickness: int = 5,
    alpha: float = 0.0,
    show_points: bool = False,
    radius: int = 3,
    pts_color_hex: str = "#000000"
):
    """
    Draws a polygon on a copy of the input image, with optional fill transparency and point markers.

    Args:
        img (np.ndarray): Input image array.
        polygon (shapely.geometry.Polygon): Polygon to be drawn.
        color_hex (str): Color as an RGB hex string (e.g., "#00FF00").
        thickness (int, optional): Thickness of the polygon outline in pixels (default: 5).
        alpha (float, optional): Transparency of the filled area (0.0 = fully transparent, 1.0 = opaque). Default is 0.0.
        show_points (bool, optional): If True, draws a circle at each polygon vertex (default: False).
        radius (int, optional): Radius of the point markers (default: 3).
        pts_color_hex (str, optional): Color of the point markers as an RGB hex string (default: "#000000").

    Returns:
        np.ndarray: A copy of the input image with the polygon drawn.
    """

    output_image = clone_image(img)
    overlay = clone_image(img)
    
    color_bgr = hex_to_bgr(color_hex)
    
    coords = np.array(polygon.exterior.coords, dtype=np.int32)
    pts = coords.reshape((-1, 1, 2))
    
    # Filled rectangle with transparency (optional)
    if alpha > 0.0:
        cv2.fillPoly(overlay, [pts], color_bgr)
        cv2.addWeighted(overlay, alpha, output_image, 1 - alpha, 0, output_image)
    
    cv2.polylines(output_image, [pts], True, color_bgr, thickness)

    if show_points:
        pts_color_bgr = hex_to_bgr(pts_color_hex)

        for p in pts:
            x, y = p[0]
            cv2.circle(output_image, (int(x), int(y)), radius, pts_color_bgr, -1)

    return output_image    

def draw_text(img: np.ndarray, text: str, position: tuple, color_hex: str, opts: dict = None):
    """
    Draws text on a copy of the input image.

    Args:
        img (np.ndarray): Input image array.
        text (str): Text string to render.
        position (tuple): Bottom-left corner of the text as (x, y).
        color_hex (str): Color as an RGB hex string (e.g., "#FFFFFF").
        opts (dict, optional): Optional style settings. Supported keys include:
            - "font_scale" (float): Scaling factor for text size.
            - "font_thickness" (int): Line thickness of the text.
            - "font" (int): OpenCV font constant (e.g., cv2.FONT_HERSHEY_SIMPLEX).

    Returns:
        np.ndarray: A copy of the input image with the text drawn.
    """

    output_image = clone_image(img)

    if opts is None:
        opts = {}

    font_scale = opts.get("font_scale", 1)
    thickness = opts.get("font_thickness", 2)
    font = opts.get("font", cv2.FONT_HERSHEY_SIMPLEX)
    color_bgr = hex_to_bgr(color_hex)

    text_size, baseline = cv2.getTextSize(text, font, font_scale, thickness)
    text_width, text_height = text_size

    # Adjust Y to account for descenders
    adjusted_pos = (
        position[0],
        position[1] - baseline
    )

    cv2.putText(output_image, text, adjusted_pos, font, font_scale, color_bgr, thickness, cv2.LINE_AA)

    return output_image

def draw_point_star(
    img: np.ndarray, 
    center: tuple, 
    color_hex: str, 
    marker_size: int = 375, 
    dpi: int = 80, 
    linewidth: float = 1.25):
    """
    Visualizes a point as a star marker and returns the resulting image.

    Args:
        img (np.ndarray): Input image array.
        center (tuple): Coordinates of the point as (x, y).
        color_hex (str): Color specified as an RGB hex string (e.g., "#FFD700").
        marker_size (int, optional): Size of the star marker (default: 375).
        dpi (int, optional): Resolution of the rendered figure in dots per inch (default: 80).
        linewidth (float, optional): Thickness of the star's edge line (default: 1.25).

    Returns:
        np.ndarray: A copy of the input image with the star marker drawn.
    """
    color_rgb = hex_to_bgr(color_hex)[::-1]
    color_rgb = [c/255 for c in color_rgb]
    
    output_image = clone_image(img)
    output_image_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)

    height, width, _ = output_image_rgb.shape
    figsize = width / float(dpi), height / float(dpi)
        
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    ax.imshow(output_image_rgb)
    
    px, py = center
    ax.scatter(px, py, color=color_rgb, marker='*', s=marker_size, 
                edgecolor=color_rgb, linewidth=linewidth)
    ax.axis('off')    
    plt.tight_layout(pad=0)
        
    # Save plot to buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=dpi, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()

    img_bgr = cv2.imdecode(img_arr, cv2.IMREAD_UNCHANGED)

    return img_bgr


def draw_mask(img: np.ndarray, mask: np.ndarray, color_hex: str, alpha: float = 1.0):
    """
    Draws a binary mask as a colored overlay on a copy of the input image.

    Args:
        img (np.ndarray): Input image array.
        mask (np.ndarray): Binary mask as a 2D array, where nonzero values indicate the masked region.
        color_hex (str): Color specified as an RGB hex string (e.g., "#00FF00").
        alpha (float, optional): Transparency of the mask overlay (0 = fully opaque, 1 = fully transparent). Default is 1.0.

    Returns:
        np.ndarray: A copy of the input image with the colored mask overlay applied.
    """

    color_bgr = np.array(hex_to_bgr(color_hex), dtype=np.uint8)
    output_image = clone_image(img)

    # Ensure mask shape matches image
    if mask.shape != img.shape[:2]:
        raise ValueError("Mask shape does not match image dimensions.")

    mask_bool = mask.astype(bool)

    # Blend only on masked pixels
    for c in range(3):
        output_image[:, :, c][mask_bool] = (
            alpha * output_image[:, :, c][mask_bool] +
            (1 - alpha) * color_bgr[c]
        ).astype(np.uint8)

    return output_image