import os
import shutil
import json
import logging
import argparse
import time
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Initialize Rich Console
console = Console()

# 1. Setup Logging
logging.basicConfig(
    filename="sortify.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_config(config_path="config.json"):
    """Loads organization rules from config.json"""
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] config.json not found!")
        exit(1)

def get_unique_destination(dest_path):
    """Handles duplicates by appending a number if the file already exists."""
    if not dest_path.exists():
        return dest_path
    
    stem = dest_path.stem
    suffix = dest_path.suffix
    parent = dest_path.parent
    counter = 1
    
    while True:
        new_name = f"{stem}_{counter}{suffix}"
        new_dest = parent / new_name
        if not new_dest.exists():
            return new_dest
        counter += 1

def organize_single_file(file_path, config):
    """The core logic to categorize and move a single file."""
    path = Path(file_path)
    
    # Ignore hidden files or temporary download files
    if path.name.startswith(".") or path.suffix.lower() in config.get("ignore_temp_files", []):
        return

    category = "Others"
    for cat, extensions in config["categories"].items():
        if path.suffix.lower() in extensions:
            category = cat
            break

    dest_dir = path.parent / category
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    dest_path = get_unique_destination(dest_dir / path.name)
    
    try:
        shutil.move(str(path), str(dest_path))
        msg = f"Moved: {path.name} → {category}/"
        console.print(f"[green]✓[/green] {msg}")
        logging.info(msg)
    except Exception as e:
        msg = f"Failed to move {path.name}: {e}"
        console.print(f"[bold red]✗[/bold red] {msg}")
        logging.error(msg)

# 2. Watchdog Event Handler
class SortifyHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config

    def on_created(self, event):
        # Sometimes files are created as directories first, we only care about files
        if not event.is_directory:
            # Small delay to ensure the file is fully written to disk
            time.sleep(1) 
            organize_single_file(event.src_path, self.config)

    def on_moved(self, event):
        # Handles cases where a file is renamed or moved into the folder
        if not event.is_directory:
            time.sleep(1)
            organize_single_file(event.dest_path, self.config)

def start_monitoring(folder_path, config):
    """Starts the real-time folder watcher."""
    path = Path(folder_path).resolve()
    console.print(f"\n[bold cyan]👁️ Watching folder:[/bold cyan] {path}")
    console.print("[dim]Press Ctrl+C to stop the watcher...[/dim]\n")
    
    event_handler = SortifyHandler(config)
    observer = Observer()
    observer.schedule(event_handler, str(path), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        console.print("\n[bold yellow]⏹️ Stopping watcher...[/bold yellow]")
        observer.stop()
    observer.join()

def organize_existing(folder_path, config):
    """Organizes files already in the folder (like our old v1 script)."""
    path = Path(folder_path).resolve()
    console.print(f"\n[bold cyan]🔍 Organizing existing files in:[/bold cyan] {path}\n")
    
    for file in path.iterdir():
        if file.is_file():
            organize_single_file(file, config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sortify v2.0: Real-time File Organizer")
    parser.add_argument("--watch", action="store_true", help="Run in real-time monitoring mode")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.config)
    target_folder = config.get("target_folder", "./test_downloads")

    # Setup dummy folder if it doesn't exist for testing
    if not Path(target_folder).exists():
        Path(target_folder).mkdir(parents=True, exist_ok=True)
        Path(target_folder, "new_image.png").touch()
        Path(target_folder, "new_script.py").touch()

    if args.watch:
        start_monitoring(target_folder, config)
    else:
        organize_existing(target_folder, config)