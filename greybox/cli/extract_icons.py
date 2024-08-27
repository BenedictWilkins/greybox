import cv2
import numpy as np
from PIL import Image
import os
from PIL import Image
from collections import Counter


def extract_icons_from_color_background(
    image: Image.Image | np.ndarray,
    background_color: tuple[int, int, int],
    close_enough_threshold: int = 10,
):
    # Convert image to numpy array
    image = np.array(image)

    # Validate image shape
    if image.shape[-1] != 3 and image.shape[-1] != 4:
        raise ValueError(f"Image must be RGB or RGBA, got shape: {image.shape}")

    # Separate the RGB channels
    r, g, b = image[..., 0], image[..., 1], image[..., 2]

    # Create a mask where the background color is detected
    mask = cv2.inRange(cv2.merge([r, g, b]), background_color, background_color)
    mask = cv2.bitwise_not(
        mask
    )  # Invert mask to get icons as white on black background

    # Find contours (icons) using the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Combine close contours
    bounding_rects = []
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        bounding_rects.append((x, y, w, h))

    combined_rects = combine_close_bounding_rects(
        bounding_rects, close_enough_threshold
    )

    # Extract icons
    for i, (x, y, w, h) in enumerate(combined_rects):
        # Extract the icon using the bounding box
        icon = image[y : y + h, x : x + w]

        # Convert the extracted icon back to an Image (with alpha channel if available)
        icon_image = Image.fromarray(icon)
        yield icon_image


def combine_close_bounding_rects(bounding_rects, threshold):
    combined = []

    def are_close(rect1, rect2, threshold):
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        return abs(x1 - x2) <= threshold and abs(y1 - y2) <= threshold

    while bounding_rects:
        rect = bounding_rects.pop(0)
        combined_rects = [rect]

        for other_rect in bounding_rects[:]:
            if any(are_close(rect, other_rect, threshold) for rect in combined_rects):
                combined_rects.append(other_rect)
                bounding_rects.remove(other_rect)

        # Create a bounding box that covers all combined rectangles
        x_coords = [r[0] for r in combined_rects]
        y_coords = [r[1] for r in combined_rects]
        widths = [r[0] + r[2] for r in combined_rects]
        heights = [r[1] + r[3] for r in combined_rects]

        x_min = min(x_coords)
        y_min = min(y_coords)
        x_max = max(widths)
        y_max = max(heights)

        combined.append((x_min, y_min, x_max - x_min, y_max - y_min))

    return combined


def most_common_color(image: Image.Image | np.ndarray):
    if isinstance(image, np.ndarray):
        image = Image.fromarray(image)
    colors = list(image.getdata())
    color_counts = Counter(colors)
    return color_counts.most_common(1)[0][0]


# Example usage
input_image_path = "input_image.png"
background_color = (255, 255, 255)  # White background
close_enough_threshold = 10  # Adjust this value as needed

# Example usage
input_image_path = "/home/ben/Documents/repos/graybox/input-prompt/4df982325757d7789451de6dc7ba3bb5a2331ebc.png"
image = Image.open(input_image_path).convert("RGBA")
background_color = most_common_color(image)
print(f"Using background color: {background_color}")

# output_directory = "/home/ben/Documents/repos/graybox/dataset/input-prompts/unknown"

# # Extract icons
# for i, icon_image in enumerate(
#     extract_icons_from_color_background(image, background_color, close_enough_threshold)
# ):
#     output_path = os.path.join(output_directory, f"UNKNOWN_{i+1}.png")

#     icon_image.save(output_path)
