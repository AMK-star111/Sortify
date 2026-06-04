# Sortify
File Intelligence | File organizing software

A local-first intelligent file organizer built with Python.

DriftSort automatically scans and organizes files into clean categories, helping transform chaotic folders into structured workspaces.

The project starts with simple rule-based organization and gradually evolves toward intelligent file understanding, semantic classification, and automated workflows.

Why Sortify?
Most people have folders that look something like this:

Downloads/
├── IMG_3829.png
├── resume_final_final_v4.pdf
├── random.zip
├── notes.pdf
├── screenshot (12).png
├── project.zip
└── document.docx

DriftSort aims to automatically organize this chaos into a structured system:

Downloads/
├── Images/
├── Documents/
├── Archives/
├── Music/
└── Code/

Current Features:

Scan the Downloads folder
Detect file extensions
Categorize files automatically
Beautiful terminal output using Rich
Modular architecture for future expansion

ROADMAP:

Version 1:
Scan files
Detect file types
Categorize files
Move files automatically
Create folders if missing
Dry-run mode
Duplicate file handling

Version 2:
Real-time folder monitoring
Custom configuration file
Logging and file history
CLI commands

Version 3:
PDF content analysis
OCR support
Intelligent document classification
Smart file naming

Version 4:
Semantic organization
Local AI support
Natural language commands
Advanced search and retrieval

Tech Stack:
Python
pathlib
Rich

Planned:
Watchdog
SQLite
PyMuPDF
Pytesseract
Sentence Transformers

Installation:
Clone the repository:
git clone https://github.com/yourusername/DriftSort.git
cd Sortify  

Install dependencies:
pip install -r requirements.txt
Run:
python main.py

Contributing:
Contributions, ideas, bug reports, and feature suggestions are welcome.
If you find an issue or have an idea for improving DriftSort, feel free to open an issue or submit a pull request.

License:
MIT License

Author:
Built by Ameya as an open-source project to learn software engineering, automation, and intelligent systems through real-world development.
