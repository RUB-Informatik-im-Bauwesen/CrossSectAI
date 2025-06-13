from PIL import ImageColor
from pathlib import Path
import matplotlib.pyplot as plt
import cv2
import io
import numpy as np


def hex_to_bgr(color_hex):
    """Convert a RGB hex color string to a BGR tuple.

    Args:
        color_hex: RGB hex string (e.g., '#FF0000').

    Returns:
        Tuple representing the BGR color.
    """
    color_rgb = ImageColor.getrgb(color_hex)

    return color_rgb[::-1]

def clone_image(img):
    """Return a copy of the input image.

    Args:
        img: Input image.

    Returns:
        A copy of the input image.
    """
    return img.copy()

def save_image(img, output_dir, filename):
    """Save the image to the specified directory with the given filename.

    Args:
        img: Input image.
        output_dir: Path to the output directory.
        filename: Name of the output image file (e.g., "result.png").

    Returns:
        None.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)  # Ensure directory exists

    file_path = Path.joinpath(output_path, filename)
    cv2.imwrite(str(file_path), img)


def draw_line(img, line, color_hex, thickness=30):
    """
    Draws a line on a cloned copy of the input image using a specified color and thickness.
    Args:
        image: Input image.
        line: The line to draw, specified by two endpoints (x0, y0) and (x1, y1).
        color_hex: RGB hex string.
        thickness: Border thickness in pixels.

    Returns:
        img: A new image with the specified line drawn.
    """

    output_image = clone_image(img)
    
    color_bgr = hex_to_bgr(color_hex)

    x0, y0 = line[0]
    x1, y1 = line[1]
    cv2.line(output_image, (int(x0), int(y0)), (int(x1), int(y1)), color_bgr, thickness)

    return output_image


def draw_point(img, center, color_hex, radius=30, thickness=-1):
    """Draw a point on a copy of the image.

        Args:
            img: Input image.
            center: Coordinates of the point (x, y).
            color_hex: BGR color as list, or RGB hex string. If empty, a random color is used.
            radius: Radius of the point in pixels.
            thickness: Border thickness in pixels. -1 fills the circle.

        Returns:
            Image with the point drawn.
    """

    output_image = clone_image(img)
    color_bgr = hex_to_bgr(color_hex)

    x_center, y_center = center
    cv2.circle(output_image, (int(x_center), int(y_center)), radius, color_bgr, thickness)

    return output_image

def draw_bbox(img, bbox, color_hex, thickness=5, alpha=0.0):
    """Draw a bounding box with optional fill and transparency on the image.

    Args:
        image: Input image.
        bbox: Bounding box in (x, y, width, height) format.
        color_hex: RGB hex string.
        thickness: Border thickness in pixels.
        alpha: Transparency of the fill (0.0 = fully transparent, 1.0 = opaque).

    Returns:
        Image with the bounding box drawn.
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


def draw_contours(img, contours, color_hex, thickness=30):
    """Draw contours on a copy of the image.

    Args:
        img: Input image.
        contours: List of contours to draw.
        color_hex: RGB hex string.
        thickness: Thickness of the contour lines.

    Returns:
        Image with contours drawn.
    """
    output_image = clone_image(img)

    if not contours:
        return output_image
    
    color_bgr = hex_to_bgr(color_hex)
    cv2.drawContours(output_image, contours, -1, color_bgr, thickness) # -1 to draw all contours
    
    return output_image


def draw_polygon(img, polygon, color_hex, thickness=5, alpha=0.0, show_points=False, radius=3, pts_color_hex="#000000"):

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

def draw_text(img, text, position, color_hex, opts=None):
    """Draw text on a copy of the image.

    Args:
        img: Input image.
        text: Text string to render.
        position: Bottom-left corner of the text (x, y).
        color_hex: RGB hex string.
        opts: Optional dictionary with style settings:
            - "font_scale": Float scaling factor for text size.
            - "font_thickness": Line thickness (int).
            - "font": OpenCV font constant (e.g., cv2.FONT_HERSHEY_SIMPLEX).

    Returns:
        Image with the text drawn.
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

def draw_point_star(img, center, color_hex, marker_size=375, dpi=80, linewidth=1.25):    
    """Visualize a point as a star marker and save the result as an image.

    Args:
        img: Input image.
        point: (x, y) coordinate of the point to visualize.
        color_hex: RGB hex string for the star color.
        marker_size: Size of the star marker.
        dpi: Resolution of the saved figure.
        linewidth: Edge line thickness of the star marker.

    Returns:
        Image with the star marker.
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


def draw_mask(img, mask, color_hex, alpha=1):
    """Draw a binary mask on a copy of the image using a specified color.

    Args:
        img: Input image.
        mask: Binary mask (2D array) to be drawn.
        color_hex: RGB hex string for the mask color.
        alpha: Opacity of the mask overlay (0 = opaque, 1 = transparent).
    Returns:
        Image with the mask overlay rendered and returned as a NumPy array.
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