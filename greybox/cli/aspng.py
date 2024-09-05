import os
import argparse
from pathlib import Path
from tqdm import tqdm
from PIL import Image


def convert_to_png(input_path: str | Path, output_path: str | Path | None = None):
    input_path = Path(input_path).expanduser().resolve()

    if output_path is None:
        output_path = input_path.with_suffix(".png")
    else:
        output_path = Path(output_path).expanduser().resolve()

    i = 0
    _temp = output_path
    while _temp.exists():
        i += 1
        _temp = _temp.with_stem(f"{output_path.stem}-{i}")

    output_path = _temp

    try:
        with Image.open(input_path) as img:
            img.save(output_path, "PNG")
            return output_path

    except Exception:
        tqdm.write(f"Failed to convert: {input_path.as_posix()}")


def convert_images_to_png(input_dir: str | Path, output_dir: str | Path):
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Loop through all files in the input directory
    for file_path in tqdm(Path(input_dir).rglob("*.*")):
        if file_path.is_file():  # Ensure it's a file and not a directory
            try:
                print(file_path.name)
                # Convert the image to PNG and save to the output directory
                output_file = Path(output_dir) / f"{file_path.stem}.png"
                convert_to_png(str(file_path), str(output_file))
            except Exception as e:
                print(e)


def main():
    parser = argparse.ArgumentParser(
        description="Convert all image files in a directory to PNG format."
    )

    parser.add_argument(
        "input_dir", type=str, help="Path to the input directory containing images."
    )
    parser.add_argument(
        "output_dir",
        type=str,
        help="Path to the output directory where PNGs will be saved.",
    )

    args = parser.parse_args()

    convert_images_to_png(args.input_dir, args.output_dir)


if __name__ == "__main__":
    main()
