import cv2
from PIL import Image
import numpy as np
import os


def extract_icons(image: Image.Image | np.ndarray, alpha_threshold: float = 0.0):

    # Convert image to numpy array
    image = np.array(image)

    # Validate image shape
    if image.shape[-1] != 4:
        raise ValueError(f"Image must have an alpha channel, got shape: {image.shape}")

    # Separate the alpha channel
    a = image[..., -1]

    # Create a binary mask using the alpha channel
    _, mask = cv2.threshold(a, alpha_threshold, 255, cv2.THRESH_BINARY)

    # Find contours (icons) using the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Loop through each contour and save the extracted icon
    for i, contour in enumerate(contours):
        # Get the bounding box for each contour
        x, y, w, h = cv2.boundingRect(contour)

        # Extract the icon using the bounding box
        icon = image[y : y + h, x : x + w]

        # Convert the extracted icon back to an Image (with alpha channel)
        icon_image = Image.fromarray(icon)
        yield icon_image


def is_tilesheet(image: Image.Image | np.ndarray):
    image = np.array(image)


if __name__ == "__main__":

    # Example usage
    input_image_path = "/home/ben/Documents/repos/graybox/input-prompt/4df982325757d7789451de6dc7ba3bb5a2331ebc.png"
    image = Image.open(input_image_path).convert("RGBA")
    output_directory = "/home/ben/Documents/repos/graybox/dataset/input-prompts/unknown"
    for i, icon_image in enumerate(extract_icons(image)):
        # Save the icon as a separate file
        output_path = os.path.join(output_directory, f"UNKNOWN_{i+1}.png")

        icon_image.save(output_path)
