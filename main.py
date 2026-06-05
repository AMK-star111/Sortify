import os
import shutil
import json
import logging
import argparse
import time
import re
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import fitz  # PyMuPDF

console = Console()

# 1. Setup Logging
logging.basicConfig(
    filename="sortify.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_config(config_path="config.json"):
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        console.print("[bold red]Error:[/bold red] config.json not found!")
        exit(1)

def sanitize_filename(name, max_length=40):
    """Removes invalid characters and truncates the filename safely."""
    # Remove invalid filename characters
    name = re.sub(r'[\\/*?:"<>|]', "", name)
    # Replace multiple spaces with a single underscore
    name = re.sub(r'\s+', '_', name).strip('_')
    # Truncate if too long
    if len(name) > max_length:
        name = name[:max_length]
    return name if name else "Untitled"

def smart_rename_pdf(file_path, config):
    """Reads the first page of a PDF and renames it based on the content."""
    if not config.get("smart_rename", False):
        return file_path

    path = Path(file_path)
    if path.suffix.lower() != ".pdf":
        return file_path

    try:
        doc = fitz.open(path)
        if doc.page_count == 0:
            doc.close()
            return file_path
            
        # Read the first 500 characters of the first page
        page = doc[0]
        text = page.get_text()[:500].strip()
        doc.close()

        if not text:
            return file_path

        # Take the first line or first few words as the new name
        new_name_base = text.split('\n')[0].strip()
        clean_name = sanitize_filename(new_name_base, config.get("max_filename_length", 40))
        
        new_path = path.parent / f"{clean_name}.pdf"
        
        # Avoid overwriting existing files
        new_path = get_unique_destination(new_path)
        
        os.rename(path, new_path)
        console.print(f"  [dim]✏️ Renamed to:[/dim] [cyan]{new_path.name}[/cyan]")
        logging.info(f"Renamed: {path.name} → {new_path.name}")
        return new_path

    except Exception as e:
        console.print(f"  [dim yellow]⚠️ Could not read PDF for renaming:[/dim yellow] {e}")
        return file_path

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
    """The core logic to categorize, optionally rename, and move a single file."""
    path = Path(file_path)
    
    if path.name.startswith(".") or path.suffix.lower() in config.get("ignore_temp_files", []):
        return

    # --- VERSION 3: SMART RENAMING ---
    if path.suffix.lower() == ".pdf":
        path = Path(smart_rename_pdf(path, config))

    # Determine category
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

# Watchdog Event Handler
class SortifyHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config

    def on_created(self, event):
        if not event.is_directory:
            time.sleep(1.5) # Slightly longer delay to ensure PDF is fully written
            organize_single_file(event.src_path, self.config)

    def on_moved(self, event):
        if not event.is_directory:
            time.sleep(1.5)
            organize_single_file(event.dest_path, self.config)

def start_monitoring(folder_path, config):
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
    path = Path(folder_path).resolve()
    console.print(f"\n[bold cyan]🔍 Organizing existing files in:[/bold cyan] {path}\n")
    
    for file in path.iterdir():
        if file.is_file():
            organize_single_file(file, config)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sortify v3.0: Smart File Organizer")
    parser.add_argument("--watch", action="store_true", help="Run in real-time monitoring mode")
    parser.add_argument("--config", default="config.json", help="Path to config file")
    args = parser.parse_args()

    config = load_config(args.config)
    target_folder = config.get("target_folder", "./test_downloads")

    if not Path(target_folder).exists():
        Path(target_folder).mkdir(parents=True, exist_ok=True)

    if args.watch:
        start_monitoring(target_folder, config)
    else:
        organize_existing(target_folder, config)