# Organize files in a folder by extension (Audio, Video, Images, Documents, etc.).
# Set ROOT_FOLDER or pass as first argument. Only top-level files are moved (no recursion).

import os
import shutil
import sys

ROOT_FOLDER = os.environ.get("ORGANIZE_ROOT", r"C:\DP-Temp")

AUDIO = (
    ".3ga", ".aac", ".ac3", ".aif", ".aiff", ".alac", ".amr", ".ape", ".au", ".dss",
    ".flac", ".flv", ".m4a", ".m4b", ".m4p", ".mp3", ".mpga", ".ogg", ".oga", ".mogg",
    ".opus", ".qcp", ".tta", ".voc", ".wav", ".wma", ".wv",
)
VIDEO = (".webm", ".mts", ".m2ts", ".ts", ".mov", ".mp4", ".m4p", ".m4v", ".mxf")
IMG = (".jpg", ".jpeg", ".jfif", ".pjpeg", ".pjp", ".png", ".gif", ".webp", ".svg", ".apng", ".avif")
DOC = (".pdf", ".docx", ".txt", ".xlsx", ".doc", ".csv")
SQL = (".sql",)
PY = (".py",)


def get_category(ext: str) -> str:
    ext = ext.lower()
    if ext in AUDIO:
        return "Audio"
    if ext in VIDEO:
        return "Video"
    if ext in IMG:
        return "Images"
    if ext in DOC:
        return "Documents"
    if ext in SQL:
        return "Database_Scripts"
    if ext in PY:
        return "Python_Scripts"
    return "Other"


def organize_files(root_folder: str) -> None:
    root_folder = os.path.normpath(root_folder)
    for filename in os.listdir(root_folder):
        path = os.path.join(root_folder, filename)
        if os.path.isdir(path):
            continue
        ext = os.path.splitext(path)[1]
        category = get_category(ext)
        category_folder = os.path.join(root_folder, category)
        os.makedirs(category_folder, exist_ok=True)
        dest = os.path.join(category_folder, filename)
        counter = 1
        while os.path.exists(dest):
            name, e = os.path.splitext(filename)
            dest = os.path.join(category_folder, f"{name}_{counter}{e}")
            counter += 1
        shutil.move(path, dest)
        print(f"Moved {filename} -> {dest}")


if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else ROOT_FOLDER
    print(f"Organizing: {root}")
    organize_files(root)
    print("Done.")
