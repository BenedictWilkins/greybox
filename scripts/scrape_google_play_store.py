"""Script that will scrape the google play store for mobile game meta-data.

Requires the `google-play-scraper` package to be installed.

1. Download dataset from kaggle: "tapive/google-play-apps-and-games" this dataset contains the unique play store app ids for many mobile games.

"""

import ray
import time
import pandas as pd
from tqdm import tqdm
from pathlib import Path


from greybox.utils.dataset.kaggle import download_dataset
from google_play_scraper import app, exceptions

kaggle_dataset_path = download_dataset(
    "tapive/google-play-apps-and-games",
    path="~/.dataset/google-play-apps-and-games",
    unzip=True,
    quiet=False,
)

appid_dataset_path = kaggle_dataset_path / "game-app-ids.csv"

# extract all game app ids
if not appid_dataset_path.exists():
    # read the csv file and extract all game app ids, we will scrape these apps!
    df = pd.read_csv(list(kaggle_dataset_path.glob("*.csv"))[0])
    df_games = df[df["genreId"].str.contains("GAME", case=False, na=False)].reset_index(
        drop=True
    )
    # save/cache all of the app ids for later use
    with open(appid_dataset_path.as_posix(), "w") as f:
        for appid in tqdm(df_games["appId"], desc="writing app ids"):
            f.write(appid)
            f.write("\n")


# Main function to handle chunking and task management
def scrape_all(
    appids: list[str], path: str | Path, chunk_size: int = 100, num_tasks: int = 5
):
    total = 0
    path = Path(path).expanduser().resolve()
    path.mkdir(exist_ok=True, parents=True)

    def _chunk():
        for i in range(0, len(appids), chunk_size):
            yield appids[i : i + chunk_size], path / f"game-data-{time.time_ns()}.csv"

    pbar = tqdm(total=len(appids) / chunk_size)
    chunks = _chunk()

    active_tasks = []

    for _ in range(num_tasks):
        try:
            chunk, chunk_path = next(chunks)
            task = scrape.remote(chunk, chunk_path)
            active_tasks.append(task)
        except StopIteration:
            break

    # As tasks complete, submit new ones until all chunks are processed
    while active_tasks:
        # Wait for the first task to complete
        done, active_tasks = ray.wait(active_tasks, num_returns=1)
        for task in done:
            try:
                total += ray.get(task)
                pbar.update(1)
                pbar.set_description(f"Total: {total}")
            except Exception as e:
                print(f"Task failed with exception: {e}")

        try:
            chunk, chunk_path = next(chunks)
            task = scrape.remote(chunk, chunk_path)
            active_tasks.append(task)
        except StopIteration:
            pass  # No more chunks to process


def scrape(appids: list[str], path: str | Path, pbar: tqdm):
    columns = [
        "appId",
        "genre",
        "categories",
        "icon",
        "headerImage",
        "video",
        "videoImage",
        "price",
        "title",
        "summary",
        "description",
    ]
    results = []
    pbar.reset()
    for id_ in appids:
        pbar.update(1)
        try:
            result = app(id_, lang="en", country="us")
            result["categories"] = [x["name"] for x in result["categories"]]
            results.append(result)
        except exceptions.NotFoundError as e:
            pass  # this app was not found, this happens often
        except exceptions.ExtraHTTPError as e:
            pass  # app was not found? internal server error?
    total = len(results)
    df = pd.DataFrame(data=results, columns=columns)
    df = df.rename(columns={c: c.lower() for c in columns})
    df.to_csv(path.as_posix(), index=False)
    return total


appids = set(pd.read_csv(open(appid_dataset_path.as_posix()), header=None)[0].tolist())
game_metadata_path = kaggle_dataset_path / "game_metadata"

# get any existing meta data from previous runs
print("Checking appids from previous session...")
existing_appids = []
for meta_file in game_metadata_path.glob("*.csv"):
    existing_appids.extend(pd.read_csv(open(meta_file.as_posix()))["appid"].tolist())
print(f"Found {len(existing_appids)} existing appids")

appids -= set(existing_appids)
appids = list(appids)
print(f"Scraping {len(appids)} games from play store...")

chunk_size = 100
pbar = tqdm(range(0, len(appids), chunk_size))
pbar_inner = tqdm()
total = 0
for i in pbar:
    pbar.set_description(f"Total: {total}")
    total += scrape(
        appids[i : i + chunk_size],
        game_metadata_path / f"game-data-{time.time_ns()}.csv",
        pbar_inner,
    )
