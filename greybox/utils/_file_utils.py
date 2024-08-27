import os
import patoolib
from pathlib import Path
from tqdm import tqdm
import time

patoolib.log.logger.setLevel("ERROR")


__all__ = (
    "FileExtractor",
    "find_all_files_with_keyword",
    "find_all_files",
    "extract_archive",
)


def find_all_files_with_keyword(directory: str | Path, keywords_whitelist: list[str]):
    # Traverse the directory tree
    for root, _, files in os.walk(Path(directory).as_posix()):
        for file in files:
            # Check if any of the keywords are in the filename
            if any(keyword.lower() in file.lower() for keyword in keywords_whitelist):
                yield Path(root, file)


def find_all_files(directory: str | Path):
    for root, _, files in os.walk(Path(directory).as_posix()):
        for file in files:
            yield Path(root, file)


def extract_archive(path: str | Path, out: str | Path):
    path, out = Path(path).expanduser().resolve(), Path(out).expanduser().resolve()
    return patoolib.extract_archive(path.as_posix(), outdir=out.as_posix())


class FileExtractor:

    ARCHIVE_EXTENSIONS = [".zip", ".rar", ".gz", ".tar"]
    IMAGE_EXTENSIONS = [
        ".png",
        ".jpg",
        ".jpeg",
        ".svg",
        ".webp",
        ".tiff",
        ".tif",
        ".bmp",
        ".psd",
    ]
    VIDEO_EXTENSIONS = [".mp4", ".mov", ".gif"]

    FONT_EXTENSIONS = [".otf"]

    def __init__(
        self,
        extract_archives: bool = True,
    ):
        super().__init__()
        self._extensions = (
            FileExtractor.IMAGE_EXTENSIONS
            + FileExtractor.VIDEO_EXTENSIONS
            + FileExtractor.FONT_EXTENSIONS  # for icon fonts
        )
        self._extract_archives = extract_archives
        if self._extract_archives:
            assert not any(
                ext in self._extensions for ext in FileExtractor.ARCHIVE_EXTENSIONS
            )

    def find_all(self, path: str | Path, depth: int = 1):
        if depth == 0:
            yield from []
        file_iter = find_all_files(path)
        for file in file_iter:
            if Path(file).is_symlink():
                continue  # TODO ignore simlinks...?
            if file.suffix in self._extensions:
                yield file
            elif file.suffix in FileExtractor.ARCHIVE_EXTENSIONS:
                out = extract_archive(
                    file, f"./tmp/{file.name.split('.')[0]}-{time.time()}"
                )
                yield from self.find_all(out, depth=depth - 1)
            else:
                pass  # tqdm.write(f"Unknown file extention: {file.name}, skipping...")
