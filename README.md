# 📁 DownSort: Smart Download Folder Sorter & Local File Organizer

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Build & Test](https://github.com/harshkr04/DownSort/actions/workflows/ci.yml/badge.svg)](https://github.com/harshkr04/DownSort/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Privacy: 100% Local](https://img.shields.io/badge/Privacy-100%25%20Local%20(Offline)-success.svg)]()

**DownSort** is a fast, lightweight, and intelligent **download folder sorter** and local file organizer for Windows, Mac, and Linux. It automatically cleans up cluttered Downloads directories by categorizing loose files into structured subfolders based on file types, metadata, and deep content inspection.

Unlike basic extension-only file sorters, DownSort performs **deep local inspection** (e.g. reading PDF text for admit cards, PYQs, and class notes; detecting WhatsApp images and high-resolution wallpapers; identifying movie files and Android APKs).

---

## 🎯 Why Use This Download Folder Sorter?

Most generic file sorters just look at `.pdf` or `.jpg` and dump everything into one folder. DownSort solves real-world folder clutter:
- **Smart PDF Separation**: Distinguishes between Admit Cards, Question Papers (PYQs), Study Notes, Certificates, and Official IDs.
- **Single / Unique PDF Routing**: If a PDF doesn't match standard academic/official types, it is safely filed into `PDFs/Other`.
- **Media Detection**: Separates WhatsApp forwards from wallpapers, screenshots, and passport photos/signatures.
- **100% Local & Private**: No cloud uploads, no tracking. Runs completely offline on `localhost`.
- **Safe Mode with 1-Click Rollback**: Never loses or overwrites a file. If you don't like the result, undo the entire batch with one click.

---

## ✨ Categorization Criteria

| Category | Supported Types & Detection Criteria | Target Folder |
| :--- | :--- | :--- |
| **🎫 Admit Cards** | Hall tickets, TCS NQT, GATE, NTA, ISRO, AFCAT, roll numbers, exam venues | `PDFs/Admit Cards` |
| **🎓 PYQ Papers** | Previous year question papers, semester exams, GATE/JEE papers | `PDFs/PYQ Papers` |
| **📖 Study Notes** | Lecture notes, course modules, assignments, lab manuals | `PDFs/Notes & Study Material` |
| **📜 Certificates** | Coursera, Udemy, IBM, NPTEL credentials, internship certificates | `PDFs/Certificates` |
| **🛡️ Govt IDs & Forms** | Aadhaar cards, PAN cards, marksheets, affidavits, declarations | `PDFs/Official & ID Docs` |
| **📁 Other PDFs** | Single or unique PDFs not matching the above categories | `PDFs/Other` |
| **💬 WhatsApp Media** | Images matching WhatsApp media formats (`IMG-YYYYMMDD-WA*`) | `Images/WhatsApp` |
| **👤 Photos & Signatures** | Scanned signatures (aspect ratio) and passport/profile photos | `Images/Photos & Signatures` |
| **🌄 Wallpapers** | High-resolution images (1080p, 2K, 4K, 16:9 widescreen or 9:16 phone) | `Images/Wallpapers` |
| **📸 Screenshots** | Screenshots and screen clips | `Images/Screenshots` |
| **🍿 Movies & Series** | Videos > 500 MB or files with release tags (`1080p`, `WEB-DL`, `HEVC`) | `Videos/Movies` |
| **📱 APKs & Apps** | Android packages (`.apk`, `.xapk`, `.apks`, `.aab`) | `APKs` |
| **📑 Office Documents** | Word (`.docx`), Excel (`.xlsx`), PowerPoint (`.pptx`), Text (`.txt`) | `Documents/` |
| **🗜️ Archives & Tools** | Compressed zip files (`.zip`, `.rar`, `.7z`) and installers (`.exe`) | `Archives/`, `Installers/` |

---

## 🚀 Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/harshkr04/DownSort.git
cd DownSort
pip install -r requirements.txt
```

### 2. Run Web Dashboard
```bash
python run.py
```
This starts the local web server and opens the dashboard in your default browser at `http://127.0.0.1:5050`.

### 3. Windows 1-Click Launch
Double-click `Launch_DownSort.bat` inside the project folder.

---

## 💻 Command-Line Interface (CLI)

You can also use DownSort directly from your terminal:

```bash
# Preview how files will be categorized (dry-run)
python cli.py --scan

# Organize files using Move mode
python cli.py --organize --mode move

# Organize files using Copy mode (safe testing)
python cli.py --organize --mode copy

# View sorting history
python cli.py --history

# Rollback / Undo the latest organization run
python cli.py --undo latest
```

---

## 🔒 Safety & Conflict Handling
- **No Overwriting**: If a file with the same name already exists in the destination folder, DownSort renames it to `filename (1).ext`.
- **1-Click Rollback**: Every session is recorded in a local transaction log. One click restores every file to its original location.

---

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/harshkr04/DownSort/issues).

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
