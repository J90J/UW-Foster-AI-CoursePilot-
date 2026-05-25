"""
Download course PDFs from shared Google Drive folders into local Syllabus/ and Schedules/.

Usage:
    python3 sync_drive.py

Requires DRIVE_SYLLABUS_FOLDER_ID and DRIVE_SCHEDULES_FOLDER_ID in .env (or shell env).
The Drive folders must be shared as "Anyone with the link can view".
"""
import shutil
import sys
from pathlib import Path

import gdown

from config import BASE_DIR, SCHEDULES_DIR, SYLLABUS_DIR, DRIVE_SYLLABUS_FOLDER_ID, DRIVE_SCHEDULES_FOLDER_ID


def sync_folder(folder_id: str, local_dir: Path, label: str) -> int:
    if not folder_id:
        print(f"  Skipping {label}: no folder ID set in .env")
        return 0

    # gdown writes into a subdirectory named after the Drive folder — we use a temp dir
    tmp = BASE_DIR / f"_tmp_{label.lower()}"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()

    url = f"https://drive.google.com/drive/folders/{folder_id}"
    print(f"  Downloading {label} from Drive...")
    try:
        gdown.download_folder(url=url, output=str(tmp), quiet=False, use_cookies=False)
    except Exception as exc:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"  ERROR downloading {label}: {exc}")
        print("  Make sure the folder is shared as 'Anyone with the link can view'.")
        return 0

    # Move all PDFs from wherever gdown put them into the target local dir
    local_dir.mkdir(exist_ok=True)
    downloaded = 0
    for pdf in tmp.rglob("*.pdf"):
        dest = local_dir / pdf.name
        shutil.copy2(pdf, dest)
        downloaded += 1

    shutil.rmtree(tmp, ignore_errors=True)
    return downloaded


def main() -> None:
    print("Foster MBA Bot — syncing PDFs from Google Drive\n")

    syllabus_count = sync_folder(DRIVE_SYLLABUS_FOLDER_ID, SYLLABUS_DIR, "Syllabus")
    schedule_count = sync_folder(DRIVE_SCHEDULES_FOLDER_ID, SCHEDULES_DIR, "Schedules")

    total = syllabus_count + schedule_count
    if total == 0:
        print("\nNo files downloaded. Check your folder IDs and sharing settings.")
        sys.exit(1)

    print(f"\nDone. Downloaded {syllabus_count} syllabus PDFs and {schedule_count} schedule PDFs.")
    print("Next step: python3 ingest.py --reset")


if __name__ == "__main__":
    main()
