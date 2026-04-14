"""
File & Folder Organizer Bot
----------------------------
Monitors a folder and automatically sorts files into subfolders by type.
Logs every action with a timestamp.
Usage: python file_organizer.py --watch "C:/Users/YourName/Downloads"
"""

import argparse
import logging
import os
import shutil
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ── FILE TYPE → FOLDER MAPPING ────────────────────────────────────────────────

FOLDER_MAP = {
    # Documents
    ".pdf":  "docs/pdfs",
    ".docx": "docs/word",
    ".doc":  "docs/word",
    ".txt":  "docs/text",
    ".xlsx": "docs/excel",
    ".xls":  "docs/excel",
    ".pptx": "docs/presentations",
    ".ppt":  "docs/presentations",
    ".csv":  "docs/data",

    # Images
    ".jpg":  "images",
    ".jpeg": "images",
    ".png":  "images",
    ".gif":  "images",
    ".bmp":  "images",
    ".svg":  "images",
    ".webp": "images",

    # Videos
    ".mp4":  "videos",
    ".mov":  "videos",
    ".avi":  "videos",
    ".mkv":  "videos",
    ".wmv":  "videos",

    # Audio
    ".mp3":  "audio",
    ".wav":  "audio",
    ".flac": "audio",
    ".aac":  "audio",

    # Code
    ".py":   "code/python",
    ".js":   "code/javascript",
    ".html": "code/web",
    ".css":  "code/web",
    ".java": "code/java",
    ".cpp":  "code/cpp",
    ".c":    "code/cpp",

    # Archives
    ".zip":  "archives",
    ".rar":  "archives",
    ".tar":  "archives",
    ".gz":   "archives",
    ".7z":   "archives",

    # Executables / Installers
    ".exe":  "installers",
    ".msi":  "installers",
    ".dmg":  "installers",
}

# ── LOGGING SETUP ─────────────────────────────────────────────────────────────

def setup_logging(watch_folder):
    log_path = os.path.join(watch_folder, "organizer_log.txt")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s  [%(levelname)s]  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),
        ]
    )
    logging.info(f"Organizer started. Watching: {watch_folder}")
    logging.info(f"Log file: {log_path}")


# ── FILE MOVER ────────────────────────────────────────────────────────────────

def move_file(filepath, watch_folder):
    path = Path(filepath)

    # Skip log files, hidden files, and folders
    if not path.is_file():
        return
    if path.name.startswith("."):
        return
    if path.name == "organizer_log.txt":
        return

    ext = path.suffix.lower()
    subfolder = FOLDER_MAP.get(ext, "other")
    target_dir = Path(watch_folder) / subfolder
    target_dir.mkdir(parents=True, exist_ok=True)

    target_path = target_dir / path.name

    # Avoid overwriting — add a number suffix if file exists
    counter = 1
    while target_path.exists():
        stem = path.stem
        target_path = target_dir / f"{stem}_{counter}{ext}"
        counter += 1

    shutil.move(str(path), str(target_path))
    logging.info(f"MOVED  {path.name}  →  {subfolder}/")


# ── WATCHDOG EVENT HANDLER ────────────────────────────────────────────────────

class OrganizerHandler(FileSystemEventHandler):
    def __init__(self, watch_folder):
        self.watch_folder = watch_folder

    def on_created(self, event):
        if not event.is_directory:
            # Small delay to ensure file is fully written before moving
            time.sleep(1)
            move_file(event.src_path, self.watch_folder)

    def on_moved(self, event):
        if not event.is_directory:
            time.sleep(1)
            move_file(event.dest_path, self.watch_folder)


# ── ORGANIZE EXISTING FILES ───────────────────────────────────────────────────

def organize_existing(watch_folder):
    logging.info("Organizing existing files in folder...")
    count = 0
    for filename in os.listdir(watch_folder):
        filepath = os.path.join(watch_folder, filename)
        if os.path.isfile(filepath) and filename != "organizer_log.txt":
            move_file(filepath, watch_folder)
            count += 1
    logging.info(f"Organized {count} existing file(s).")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="File & Folder Organizer Bot")
    parser.add_argument("--watch", required=True, help="Folder path to monitor")
    parser.add_argument("--existing", action="store_true",
                        help="Also organize files already in the folder")
    args = parser.parse_args()

    watch_folder = os.path.abspath(args.watch)

    if not os.path.isdir(watch_folder):
        print(f"[ERROR] Folder not found: {watch_folder}")
        return

    setup_logging(watch_folder)

    if args.existing:
        organize_existing(watch_folder)

    # Start watching
    event_handler = OrganizerHandler(watch_folder)
    observer = Observer()
    observer.schedule(event_handler, watch_folder, recursive=False)
    observer.start()

    logging.info("Watching for new files... Press Ctrl+C to stop.")
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
        logging.info("Organizer stopped.")
    observer.join()


if __name__ == "__main__":
    main()
