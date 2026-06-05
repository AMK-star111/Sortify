import os
import shutil
import argparse
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# 1. Define our categorization rules
CATEGORIES = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".xls", ".xlsx", ".ppt", ".pptx", ".md"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Music": {".mp3", ".wav", ".flac", ".aac", ".ogg"},
    "Code": {".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".json"},
    "Videos": {".mp4", ".mkv", ".mov", ".avi", ".flv"},
}

def get_category(file_extension):
    """Determines the category of a file based on its extension."""
    for category, extensions in CATEGORIES.items():
        if file_extension.lower() in extensions:
            return category
    return "Others"

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

def organize_files(folder_path, dry_run=True):
    """Scans, categorizes, and optionally moves files."""
    console = Console()
    path = Path(folder_path).resolve() # Get absolute path
    
    if not path.exists() or not path.is_dir():
        console.print(f"[bold red]Error:[/bold red] The folder '{folder_path}' does not exist!")
        return

    console.print(f"\n[bold cyan]🔍 Scanning folder:[/bold cyan] {path}\n")
    
    actions = [] # Keep track of what we did or will do

    for file in path.iterdir():
        if file.is_file():
            category = get_category(file.suffix)
            dest_dir = path / category
            
            # Create category folder if it doesn't exist
            if not dest_dir.exists() and not dry_run:
                dest_dir.mkdir(parents=True, exist_ok=True)
            
            dest_path = get_unique_destination(dest_dir / file.name)
            
            if dry_run:
                actions.append(f"[yellow]Would move:[/yellow] {file.name} [dim]→[/dim] {category}/")
            else:
                try:
                    shutil.move(str(file), str(dest_path))
                    actions.append(f"[green]Moved:[/green] {file.name} [dim]→[/dim] {category}/")
                except Exception as e:
                    actions.append(f"[bold red]Failed to move {file.name}:[/bold red] {e}")

    # Display Results
    if dry_run:
        console.print(Panel.fit("\n".join(actions), title="[bold]🛡️ DRY RUN RESULTS (No files were moved)[/bold]", border_style="yellow"))
    else:
        console.print(Panel.fit("\n".join(actions), title="[bold]✅ ORGANIZATION COMPLETE[/bold]", border_style="green"))

if __name__ == "__main__":
    # 2. Set up Command Line Arguments
    parser = argparse.ArgumentParser(description="Sortify: Intelligent File Organizer")
    parser.add_argument("folder", nargs="?", default="./test_downloads", help="Folder to organize (default: ./test_downloads)")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without moving files")
    
    args = parser.parse_args()

    # --- Setup a dummy test environment if it doesn't exist ---
    test_folder = Path(args.folder)
    if not test_folder.exists():
        test_folder.mkdir(parents=True, exist_ok=True)
        dummy_files = [
            "IMG_3829.png", "resume_final_final_v4.pdf", "random.zip", 
            "notes.pdf", "screenshot (12).png", "project.zip", 
            "document.docx", "song.mp3", "script.py", "unknown_file.xyz",
            "notes.pdf" # Added a duplicate to test our logic!
        ]
        for f in dummy_files:
            Path(test_folder, f).touch()
    # ----------------------------------------------------------

    # Run the organizer!
    organize_files(test_folder, dry_run=args.dry_run)