import numpy as np
from pathlib import Path
from PIL import Image


def convert_to_png(input_path: str | Path, output_path: str | Path | None = None):
    input_path = Path(input_path).expanduser().resolve()
    if input_path.suffix == ".png":
        return input_path  # the file is already a png

    if output_path is None:
        output_path = input_path.with_suffix(".png")
    else:
        output_path = Path(output_path).expanduser().resolve()

    try:
        with Image.open(input_path) as img:
            img.save(output_path, "PNG")
            return output_path

    except Exception as e:
        return None


def color_visual(
    color: tuple[int, int, int] | tuple[int, int, int],
    size: int | tuple[int, int] = 10,
    checkerboard_size: int = 2,
):
    """Create an image that shows the given color, including the alpha channel

    Args:
        color (tuple): color (0-255) RGB or RGBA
        size (int | tuple[int, int], optional): size of the output image. Defaults to (w,h) = (10,10).
        checkerboard_size (int, optional): size of the checkerboard to use when visualising RGBA colors. Defaults to 2.

    Returns:
        image in RGB HWC format: image representing the color of shape (h, w, 3)
    """
    r, g, b, *a = color
    rgb = (r, g, b)
    if isinstance(size, int):
        size = (size, size)
    if a:
        # has alpha
        image = np.ones((*size, 3), dtype=np.uint8) * 255
        grey = np.full((3,), 192)
        for y in range(0, size[0], checkerboard_size):
            for x in range(0, size[1], checkerboard_size):
                if (x // checkerboard_size) % 2 == (y // checkerboard_size) % 2:
                    image[y : y + checkerboard_size, x : x + checkerboard_size] = grey

        a = a[0]
        a = a / 255
        for c in range(3):
            image[..., c] = image[..., c] * (1 - a) + rgb[c] * a
        return image
    else:
        # HWC format
        return np.tile(np.array(rgb).reshape(1, 1, 3), (size[1], size[0], 1))


if __name__ == "__main__":

    import matplotlib.pyplot as plt

    plt.imshow(color_visual([255, 255, 0, 10]))
    plt.show()
