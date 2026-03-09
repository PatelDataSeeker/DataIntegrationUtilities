# Python Scripts – Generic utilities

Reusable Python utilities: delimiter-based file splitting (config + logging), organize files by type, Excel date cleanup. Standard library where possible; see `requirements.txt` for the rest.

## Scripts (generic only)

| Script | Purpose |
|--------|--------|
| **file/FileSplit.py** | Split large text/HL7 files by a repeating delimiter. Config via `FileSplit_config.json` (copy `FileSplit_config.json.example`) or env `FILESPLIT_CONFIG`. Creates Inbound → Processed, archives source, rotating log. |
| **utils/organize_files_by_type.py** | Move top-level files into folders by extension (Audio, Video, Images, Documents, Database_Scripts, Python_Scripts, Other). Set `ROOT_FOLDER` in script or pass path as first argument; or env `ORGANIZE_ROOT`. |
| **utils/excel_clean_dates.py** | Load Excel, parse date columns, drop rows missing key columns. Set `FILE_PATH` (and optional `DATE_COLUMNS` / `DROPNA_COLUMNS`) or pass file path as first argument. |

## FileSplit quick start

1. Copy `scripts/python/file/FileSplit_config.json.example` to `FileSplit_config.json` in the same folder (or set `FILESPLIT_CONFIG` to your config path).
2. Set `root_folder` and paths in the config.
3. Put files in the inbound folder and run: `python scripts/python/file/FileSplit.py`

## Requirements

```bash
pip install -r requirements.txt
```

Only needed for Excel script: `pandas`, `openpyxl`. FileSplit and organize_files_by_type use the standard library.

## Other files in this repo

Older split variants (e.g. FileSplit-v1.py, SplitFiles.py) and project-specific scripts (e.g. HL7Creation-Grady, JvionGrady) remain in the repo for reference and are not part of the generic set above.
