from pathlib import Path
import pandas as pd
import requests


def download_image(image_url: str, path: str | Path):
    response = requests.get(image_url)
    if response.status_code == 200:
        content_type = response.headers.get("Content-Type")
        if content_type == "image/png":
            ext = ".png"
        elif content_type == "image/jpeg":
            ext = ".jpeg"
        else:
            raise ValueError(f"Unknown content type: {content_type}")
        file = Path(path).with_suffix(ext)  # if its an image? check?
        with open(file.as_posix(), "wb") as file:
            file.write(response.content)
        return file
    else:
        raise response.raise_for_status()


game_metadata_path = (
    Path("~/.dataset/google-play-apps-and-games/game_metadata/").expanduser().resolve()
)
game_media_path = game_metadata_path.parent / "media"

for meta_file in game_metadata_path.glob("*.csv"):
    df = pd.read_csv(meta_file.as_posix())
    for i, row in df.iterrows():
        folder = game_media_path / row["appid"].replace(".", "-")
        folder.mkdir(parents=True)
        download_image(row["icon"])
    break
