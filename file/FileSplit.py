# Author: Dipen Patel
# Date: 5/3/2023
# Split files by a repeating delimiter (e.g. HL7 MSH). Config-driven, logging, archive.
# Use FileSplit_config.json or set FILESPLIT_CONFIG env to point to your config.

import json
import os
import shutil
import logging
from logging.handlers import RotatingFileHandler
from typing import List, Tuple, Optional

DEFAULT_CONFIG = {
    "root_folder": "C:/DP-Temp/Split Test",
    "subfolders": {
        "inbound": "Inbound",
        "processed": "Processed",
        "archived": "Archived",
        "logs": "Logs",
    },
    "file_extensions": [".txt", ".hl7"],
    "repeating_string": "MSH|^~\\&|",
    "max_parts_per_file": 1000,
    "log_file_size_limit_mb": 2,
    "log_backup_count": 1,
}


def load_config(path: Optional[str] = None) -> dict:
    if path and os.path.isfile(path):
        with open(path, "r") as f:
            loaded = json.load(f)
        out = DEFAULT_CONFIG.copy()
        deep_update(out, loaded)
        return out
    return DEFAULT_CONFIG.copy()


def deep_update(base: dict, override: dict) -> None:
    for k, v in override.items():
        if k in base and isinstance(base[k], dict) and isinstance(v, dict):
            deep_update(base[k], v)
        else:
            base[k] = v


CONFIG_FILE = os.environ.get(
    "FILESPLIT_CONFIG",
    os.path.join(os.path.dirname(__file__) or ".", "FileSplit_config.json"),
)
CONFIG = load_config(CONFIG_FILE)

ROOT_FOLDER = os.path.normpath(CONFIG["root_folder"])
SUBFOLDERS = CONFIG["subfolders"]


def _path(name: str) -> str:
    return os.path.join(ROOT_FOLDER, SUBFOLDERS[name])


input_folder = _path("inbound")
output_folder = _path("processed")
move_folder = _path("archived")
log_folder = _path("logs")

file_extensions = tuple(CONFIG["file_extensions"])
repeating_string = CONFIG["repeating_string"]
max_parts_per_file = CONFIG["max_parts_per_file"]
log_file_size_limit = CONFIG["log_file_size_limit_mb"] * 1024 * 1024
log_backup_count = CONFIG.get("log_backup_count", 1)

log_file_path = os.path.join(log_folder, "SplitHistory.log")
logger = logging.getLogger("SplitHistory")
logger.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=log_file_size_limit, backupCount=log_backup_count
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def _ensure_folders(folders: List[str]) -> None:
    for folder in folders:
        os.makedirs(folder, exist_ok=True)


def split_file_content(
    file_contents: str,
    repeating_string: str,
    max_parts_per_file: int,
) -> List[List[str]]:
    parts = file_contents.split(repeating_string)
    batches = []
    current = []
    for part in parts:
        current.append(part)
        if len(current) == max_parts_per_file:
            batches.append(current)
            current = []
    if current:
        batches.append(current)
    return batches


def write_batch(
    file_path: str,
    file_parts: List[str],
    repeating_string: str,
) -> None:
    with open(file_path, "w") as f:
        f.write(repeating_string.join(file_parts))


def split_single_file(
    input_file_path: str,
    output_folder: str,
    repeating_string: str,
    max_parts_per_file: int = 1000,
    move_folder: Optional[str] = None,
    archive_source: bool = True,
) -> List[str]:
    _ensure_folders([output_folder])
    if move_folder and archive_source:
        _ensure_folders([move_folder])

    filename = os.path.basename(input_file_path)
    output_file_prefix = os.path.splitext(filename)[0]
    output_file_paths = []

    logger.info(f"Splitting file: {filename}")

    with open(input_file_path, "r", encoding="utf-8", errors="replace") as input_file:
        file_contents = input_file.read()

    batches = split_file_content(file_contents, repeating_string, max_parts_per_file)

    for file_parts in batches:
        output_file_path = os.path.join(
            output_folder,
            f"{output_file_prefix}_{len(output_file_paths) + 1}.txt",
        )
        write_batch(output_file_path, file_parts, repeating_string)
        logger.info(f"Created file: {output_file_path}")
        output_file_paths.append(output_file_path)

    if archive_source and move_folder:
        move_file_path = os.path.join(move_folder, filename)
        shutil.move(input_file_path, move_file_path)
        logger.info(f"Moved file: {move_file_path}")

    return output_file_paths


def split_files(
    input_folder: str,
    output_folder: str,
    file_extensions: Tuple[str, ...],
    repeating_string: str,
    move_folder: str,
    max_parts_per_file: int = 1000,
) -> List[str]:
    _ensure_folders([output_folder, move_folder])
    all_output_paths = []

    for filename in os.listdir(input_folder):
        if not filename.endswith(file_extensions):
            continue
        input_file_path = os.path.join(input_folder, filename)
        if not os.path.isfile(input_file_path):
            continue
        paths = split_single_file(
            input_file_path,
            output_folder,
            repeating_string,
            max_parts_per_file=max_parts_per_file,
            move_folder=move_folder,
            archive_source=True,
        )
        all_output_paths.extend(paths)

    return all_output_paths


def get_all_folders() -> List[str]:
    return [ROOT_FOLDER, input_folder, output_folder, move_folder, log_folder]


if __name__ == "__main__":
    _ensure_folders(get_all_folders())
    output_file_paths = split_files(
        input_folder,
        output_folder,
        file_extensions,
        repeating_string,
        move_folder,
        max_parts_per_file=max_parts_per_file,
    )
    logger.info(f"Total {len(output_file_paths)} files created.")
    logger.removeHandler(file_handler)
    file_handler.close()
    logger.handlers = []
