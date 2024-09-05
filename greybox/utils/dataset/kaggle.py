from pathlib import Path
from kaggle.api.kaggle_api_extended import KaggleApi
import os

from .._file_utils import extract_archive


def download_dataset(
    repo_id: str,
    path: str | Path,
    unzip: bool = False,
    force: bool = False,
    quiet: bool = False,
    username: str | None = None,
    token: str | None = None,
) -> str:
    """Download a full dataset from kaggle.

    Args:
        repo_id (str): kaggle dataset path ("username/dataset_id").
        path (str | Path): path to download to.
        unzip (bool): whether to unzip the files.
        force (bool, optional): force download (overwrite existing). Defaults to False.
        username (str | None, optional): kaggle username. Defaults to None.
        token (str | None, optional): kaggle api key. Defaults to None.

    Returns:
        str: path of the downloaded dataset
    """
    if username:
        os.environ["KAGGLE_USERNAME"] = username
    if token:
        os.environ["KAGGLE_KEY"] = token

    api = KaggleApi()
    api.authenticate()

    path = Path(path).expanduser().resolve()
    dataset_name = repo_id.split("/")[-1]
    zip_exists = (path / dataset_name).with_suffix(".zip").exists()
    if not zip_exists or force:
        # zip doesnt exist, or we are force re-downloading it
        path.mkdir(exist_ok=True, parents=True)
        api.dataset_download_files(
            repo_id, path=path.as_posix(), force=force, unzip=unzip, quiet=quiet
        )
    return path
