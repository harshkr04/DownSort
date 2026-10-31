import os
import re
import logging
from typing import Dict, Any, Optional

# Suppress noisy pypdf logs
logging.getLogger("pypdf").setLevel(logging.ERROR)

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

# File Extension Sets
IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.svg', '.tiff'}
VIDEO_EXTENSIONS = {'.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv', '.webm', '.m4v'}
AUDIO_EXTENSIONS = {'.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg', '.wma'}
DOC_WORD_EXTENSIONS = {'.docx', '.doc', '.odt', '.rtf'}
DOC_EXCEL_EXTENSIONS = {'.xlsx', '.xls', '.csv', '.tsv', '.ods'}
DOC_PPT_EXTENSIONS = {'.pptx', '.ppt', '.odp'}
ARCHIVE_EXTENSIONS = {'.zip', '.rar', '.7z', '.tar', '.gz', '.bz2', '.xz', '.iso'}
INSTALLER_EXTENSIONS = {'.exe', '.msi'}
APK_EXTENSIONS = {'.apk', '.xapk', '.apks', '.aab'}
CODE_EXTENSIONS = {'.py', '.ipynb', '.java', '.cpp', '.c', '.h', '.js', '.ts', '.html', '.css', '.json', '.sql', '.sh', '.bat', '.ps1', '.drawio', '.tex'}
TEXT_EXTENSIONS = {'.txt', '.md', '.log'}

# Category metadata with UI badges and colors
CATEGORY_META = {
    # PDFs
    "PDFs/Admit Cards": {"icon": "ticket", "color": "purple", "label": "Admit Cards & Hall Tickets"},
    "PDFs/PYQ Papers": {"icon": "graduation-cap", "color": "amber", "label": "PYQs & Question Papers"},
    "PDFs/Notes & Study Material": {"icon": "book-open", "color": "blue", "label": "Notes & Study Material"},
    "PDFs/Certificates": {"icon": "award", "color": "emerald", "label": "Certificates"},
    "PDFs/Official & ID Docs": {"icon": "shield-check", "color": "indigo", "label": "Government ID & Official Docs"},
    "PDFs/Applications & Receipts": {"icon": "receipt", "color": "cyan", "label": "Applications & Receipts"},
    "PDFs/Research Papers": {"icon": "file-text", "color": "violet", "label": "Research Papers"},
    "PDFs/Resumes & CVs": {"icon": "user-check", "color": "teal", "label": "Resumes & CVs"},
    "PDFs/Other": {"icon": "file-question", "color": "slate", "label": "Other PDFs"},

    # Images
    "Images/WhatsApp": {"icon": "message-circle", "color": "green", "label": "WhatsApp Images"},
    "Images/Photos & Signatures": {"icon": "user", "color": "rose", "label": "Photos & Signatures"},
    "Images/Wallpapers": {"icon": "image", "color": "fuchsia", "label": "Wallpapers & Backgrounds"},
    "Images/Screenshots": {"icon": "monitor", "color": "sky", "label": "Screenshots"},
    "Images/AI Generated": {"icon": "sparkles", "color": "pink", "label": "AI Generated Images"},
    "Images/Documents & Cards": {"icon": "file-badge", "color": "orange", "label": "Scanned Cards & Certificates"},
    "Images/General": {"icon": "image", "color": "gray", "label": "General Images"},

    # Videos
    "Videos/Movies": {"icon": "film", "color": "red", "label": "Movies & Series"},
    "Videos/Recordings": {"icon": "video", "color": "orange", "label": "Screen Recordings"},
    "Videos/General": {"icon": "play-circle", "color": "rose", "label": "General Videos"},

    # Apps
    "APKs": {"icon": "smartphone", "color": "emerald", "label": "Android APKs"},

    # Documents
    "Documents/Word": {"icon": "file-text", "color": "blue", "label": "Word Documents"},
    "Documents/Spreadsheets": {"icon": "table", "color": "emerald", "label": "Spreadsheets & Tables"},
    "Documents/Presentations": {"icon": "presentation", "color": "amber", "label": "PowerPoint Presentations"},
    "Documents/Text": {"icon": "file-code", "color": "gray", "label": "Text & Markdown"},

    # Software & Utilities
    "Archives": {"icon": "archive", "color": "yellow", "label": "Compressed Archives"},
    "Installers": {"icon": "box", "color": "purple", "label": "Installers & Software"},
    "Code & Projects": {"icon": "code", "color": "blue", "label": "Code & Development"},
    "Audio": {"icon": "music", "color": "pink", "label": "Audio & Music"},
    "Other Files": {"icon": "file", "color": "slate", "label": "Other Loose Files"}
}


def extract_pdf_snippet(pdf_path: str, max_pages: int = 2) -> str:
    """Safely extract text from the first couple pages of a PDF."""
    if not PYPDF_AVAILABLE:
        return ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        extracted = []
        for i, page in enumerate(reader.pages[:max_pages]):
            text = page.extract_text()
            if text:
                extracted.append(text)
        return " ".join(extracted).lower()
    except Exception:
        return ""


def classify_pdf(filename: str, filepath: str) -> Dict[str, Any]:
    """
    Sub-classifies a PDF using Fast Filename Match first,
    falling back to content extraction only when needed.
    """
    fn_lower = filename.lower()

    # --- FAST PATH: Check filename patterns first ---
    # 1. Admit Card
    if any(k in fn_lower for k in ["admit card", "admitcard", "admit_card", "hall ticket", "hallticket", "admit.", "afcat", "e-admit", "gate admit"]):
        return {
            "category": "PDFs/Admit Cards",
            "group": "Admit Cards",
            "reason": "Filename matches Admit Card / Hall Ticket"
        }

    # 2. PYQ Paper / Question Paper
    if any(k in fn_lower for k in ["pyq", "question paper", "question_paper", "sample paper", "model paper", "paper1", "paper2", "paper 1", "paper 2"]) or \
       (re.search(r'\b(gate|jee|neet|cbse|cs|it|ec|me|ce|exam)\b.*\b(paper|20\d\d)\b', fn_lower)):
        return {
            "category": "PDFs/PYQ Papers",
            "group": "PYQ Papers",
            "reason": "Filename matches Previous Year Question / Exam Paper"
        }

    # 3. Notes & Assignments
    if any(k in fn_lower for k in ["assignment", "nlp_assignment", "lecture", "unit-", "unit 1", "unit 2", "unit 3", "unit 4", "unit 5", "notes", "handwritten", "tutorial", "lab manual", "syllabus"]):
        return {
            "category": "PDFs/Notes & Study Material",
            "group": "Notes & Study Material",
            "reason": "Filename matches Academic Notes or Assignment"
        }

    # 4. Certificates
    if any(k in fn_lower for k in ["certificate", "certi", "completion", "coursera", "udemy", "nptel", "ibm da", "internship"]):
        return {
            "category": "PDFs/Certificates",
            "group": "Certificates",
            "reason": "Filename matches Certificate or Credential"
        }

    # 5. Government IDs & Official Documents
    if any(k in fn_lower for k in ["aadhaar", "aadhar", "pan card", "pancard", "voter", "passport", "caste certi", "affidavit", "declaration", "marksheet", "grade card", "transcript", "domicile"]):
        return {
            "category": "PDFs/Official & ID Docs",
            "group": "Official & ID Docs",
            "reason": "Filename matches Official Identity or Legal Document"
        }

    # 6. Applications, Invoices & Receipts
    if any(k in fn_lower for k in ["application", "submitted_application", "acknowledgement", "receipt", "invoice", "bill", "salary slip", "payslip", "fee receipt"]):
        return {
            "category": "PDFs/Applications & Receipts",
            "group": "Applications & Receipts",
            "reason": "Filename indicates Application Form or Receipt"
        }

    # 7. Research Papers & Articles
    if any(k in fn_lower for k in ["research paper", "conference paper", "arxiv", "proceedings"]) or re.search(r'\d{4}\.\d{4,5}(v\d+)?', fn_lower):
        return {
            "category": "PDFs/Research Papers",
            "group": "Research Papers",
            "reason": "Filename matches Research or ArXiv Paper"
        }

    # 8. Resumes & CVs
    if any(k in fn_lower for k in ["resume", "cv", "curriculum_vitae"]):
        return {
            "category": "PDFs/Resumes & CVs",
            "group": "Resumes & CVs",
            "reason": "Filename indicates Resume or CV"
        }

    # --- SLOW PATH: If filename is ambiguous, inspect text content ---
    content = ""
    if os.path.exists(filepath):
        content = extract_pdf_snippet(filepath, max_pages=2)

    if content:
        # Check Admit Card
        if "admit card" in content or "hall ticket" in content or (("roll no" in content or "roll number" in content) and ("exam" in content or "venue" in content) and "reporting time" in content):
            return {
                "category": "PDFs/Admit Cards",
                "group": "Admit Cards",
                "reason": "PDF content contains Admit Card markers"
            }

        # Check Question Paper
        pyq_content_indicators = [
            "carry one mark each", "carry two mark", "maximum marks:", "time allowed:", "duration: 3 hours",
            "general aptitude (ga)", "section - a", "section a:", "sample question paper",
            "end semester examination", "mid semester examination", "question paper code"
        ]
        if sum(1 for k in pyq_content_indicators if k in content) >= 2 or (("gate 20" in content or "question paper" in content) and ("mark" in content or "section" in content)):
            return {
                "category": "PDFs/PYQ Papers",
                "group": "PYQ Papers",
                "reason": "PDF content structure matches Question Paper"
            }

        # Check Academic Notes / Assignment
        notes_content_indicators = [
            "assignment -", "assignment 1", "assignment 2", "course code", "submitted by",
            "lecture notes", "module 1", "module 2", "module 3", "unit i", "unit ii", "unit iii",
            "learning objectives", "department of computer science", "b.tech"
        ]
        if sum(1 for k in notes_content_indicators if k in content) >= 2 or "assignment" in content:
            return {
                "category": "PDFs/Notes & Study Material",
                "group": "Notes & Study Material",
                "reason": "PDF content indicates Lecture Notes or Assignment"
            }

        # Check Certificates
        if "certificate of completion" in content or "has successfully completed" in content or "certifies that" in content or "awarded to" in content:
            return {
                "category": "PDFs/Certificates",
                "group": "Certificates",
                "reason": "PDF content indicates Completion Certificate"
            }

        # Check Govt IDs
        if "unique identification authority of india" in content or "government of india" in content or "income tax department" in content or "aadhaar" in content:
            return {
                "category": "PDFs/Official & ID Docs",
                "group": "Official & ID Docs",
                "reason": "PDF content matches Government ID / Authority Record"
            }

        # Check Applications & Receipts
        if "application form" in content or "acknowledgement slip" in content or "tax invoice" in content or "fee receipt" in content:
            return {
                "category": "PDFs/Applications & Receipts",
                "group": "Applications & Receipts",
                "reason": "PDF content indicates Application, Receipt, or Bill"
            }

        # Check Research Papers
        if ("abstract" in content and ("introduction" in content or "references" in content)) and ("ieee" in content or "doi:" in content or "arxiv" in content or "conference" in content):
            return {
                "category": "PDFs/Research Papers",
                "group": "Research Papers",
                "reason": "PDF content structure indicates Academic Research Paper"
            }

        # Check Resume
        if "curriculum vitae" in content or (("education" in content or "experience" in content) and ("skills" in content and "projects" in content)):
            return {
                "category": "PDFs/Resumes & CVs",
                "group": "Resumes & CVs",
                "reason": "PDF content indicates Resume / CV"
            }

    # 9. Fallback / Single distinct PDF -> PDFs/Other as explicitly requested by user!
    return {
        "category": "PDFs/Other",
        "group": "Other PDFs",
        "reason": "General or distinct PDF (routed to 'Other' as requested)"
    }


def classify_image(filename: str, filepath: str) -> Dict[str, Any]:
    """Sub-classifies images."""
    fn_lower = filename.lower()

    # 1. WhatsApp Images
    if re.search(r'img-\d{8}-wa\d+', fn_lower) or "whatsapp image" in fn_lower or "wa_img" in fn_lower:
        return {
            "category": "Images/WhatsApp",
            "group": "WhatsApp Images",
            "reason": "Filename matches WhatsApp image pattern"
        }

    # 2. Photos & Signatures
    if any(k in fn_lower for k in ["signature", "sign", "gate_.*signature"]):
        return {
            "category": "Images/Photos & Signatures",
            "group": "Photos & Signatures",
            "reason": "Filename indicates Signature"
        }
    if any(k in fn_lower for k in ["photo", "passport", "avatar", "profile_pic", "pic"]):
        return {
            "category": "Images/Photos & Signatures",
            "group": "Photos & Signatures",
            "reason": "Filename indicates Passport Photo or Profile Picture"
        }

    # 3. Screenshots
    if any(k in fn_lower for k in ["screenshot", "screen shot", "screen_capture", "snipping"]):
        return {
            "category": "Images/Screenshots",
            "group": "Screenshots",
            "reason": "Filename indicates Screenshot"
        }

    # 4. AI Generated Images
    if any(k in fn_lower for k in ["chatgpt image", "gemini_generated", "midjourney", "dall-e", "stablediffusion", "copilot_"]):
        return {
            "category": "Images/AI Generated",
            "group": "AI Generated",
            "reason": "Filename indicates AI Generated Image"
        }

    # 5. Documents / Certificates in image format
    if any(k in fn_lower for k in ["certi", "10 th", "12 th", "marksheet", "id card", "aadhaar", "pan card", "decleration", "declaration"]):
        return {
            "category": "Images/Documents & Cards",
            "group": "Documents & Cards",
            "reason": "Filename indicates ID Card, Certificate, or Document scan"
        }

    # 6. Wallpapers (filename check)
    if any(k in fn_lower for k in ["wallpaper", "wall_", "bg_", "background", "desktop_wall", "phone_wall"]):
        return {
            "category": "Images/Wallpapers",
            "group": "Wallpapers",
            "reason": "Filename indicates Wallpaper or Background"
        }

    # Check image size & aspect ratio if PIL is available
    if PIL_AVAILABLE and os.path.exists(filepath):
        try:
            with Image.open(filepath) as img:
                w, h = img.size
                aspect = w / h if h > 0 else 1.0

                # Check signature aspect ratio: wide & short
                if aspect > 2.2 and w <= 1200 and h <= 500:
                    return {
                        "category": "Images/Photos & Signatures",
                        "group": "Photos & Signatures",
                        "reason": f"Dimensions ({w}x{h}, aspect {aspect:.2f}) match Signature"
                    }

                # Check wallpaper resolution: 1920x1080, 2K, 4K or mobile portrait wallpaper
                if (w >= 1920 and h >= 1080 and 1.5 <= aspect <= 2.4) or (w >= 1080 and h >= 1920 and 0.4 <= aspect <= 0.65):
                    return {
                        "category": "Images/Wallpapers",
                        "group": "Wallpapers",
                        "reason": f"High resolution ({w}x{h}) matches Wallpaper"
                    }
        except Exception:
            pass

    return {
        "category": "Images/General",
        "group": "General Images",
        "reason": "Standard image file"
    }


def classify_video(filename: str, filepath: str) -> Dict[str, Any]:
    """Sub-classifies videos into Movies, Screen Recordings, or General Videos."""
    fn_lower = filename.lower()
    file_size_mb = 0
    if os.path.exists(filepath):
        try:
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        except Exception:
            pass

    movie_tags = ["1080p", "720p", "2160p", "4k", "bluray", "web-dl", "webrip", "hevc", "x264", "x265", "bollyflix", "yts", "hdrip", "movie"]
    is_movie_named = any(tag in fn_lower for tag in movie_tags)

    if file_size_mb > 500 or is_movie_named:
        return {
            "category": "Videos/Movies",
            "group": "Movies",
            "reason": f"File size ({file_size_mb:.1f} MB) or release keywords match Movie"
        }

    if re.search(r'recording \d{4}-|\d{4}-\d{2}-\d{2} \d{2}-\d{2}-\d{2}|zoom_|obs_|screen_rec', fn_lower):
        return {
            "category": "Videos/Recordings",
            "group": "Recordings",
            "reason": "Filename indicates Screen or Video Recording"
        }

    return {
        "category": "Videos/General",
        "group": "General Videos",
        "reason": "Standard video file"
    }


def classify_file(filepath: str) -> Dict[str, Any]:
    """Top-level classification dispatcher for any file."""
    filename = os.path.basename(filepath)
    ext = os.path.splitext(filename)[1].lower()

    if ext == '.pdf':
        res = classify_pdf(filename, filepath)
    elif ext in IMAGE_EXTENSIONS:
        res = classify_image(filename, filepath)
    elif ext in VIDEO_EXTENSIONS:
        res = classify_video(filename, filepath)
    elif ext in APK_EXTENSIONS:
        res = {
            "category": "APKs",
            "group": "APKs & Apps",
            "reason": "Android application package (.apk)"
        }
    elif ext in DOC_WORD_EXTENSIONS:
        res = {
            "category": "Documents/Word",
            "group": "Word Documents",
            "reason": f"Word document ({ext})"
        }
    elif ext in DOC_EXCEL_EXTENSIONS:
        res = {
            "category": "Documents/Spreadsheets",
            "group": "Spreadsheets",
            "reason": f"Spreadsheet / Data file ({ext})"
        }
    elif ext in DOC_PPT_EXTENSIONS:
        res = {
            "category": "Documents/Presentations",
            "group": "Presentations",
            "reason": f"Presentation slide ({ext})"
        }
    elif ext in TEXT_EXTENSIONS:
        res = {
            "category": "Documents/Text",
            "group": "Text Files",
            "reason": f"Plain text document ({ext})"
        }
    elif ext in ARCHIVE_EXTENSIONS:
        res = {
            "category": "Archives",
            "group": "Compressed Archives",
            "reason": f"Archive file ({ext})"
        }
    elif ext in INSTALLER_EXTENSIONS:
        res = {
            "category": "Installers",
            "group": "Installers & Software",
            "reason": f"Executable installer ({ext})"
        }
    elif ext in AUDIO_EXTENSIONS:
        res = {
            "category": "Audio",
            "group": "Audio & Music",
            "reason": f"Audio file ({ext})"
        }
    elif ext in CODE_EXTENSIONS:
        res = {
            "category": "Code & Projects",
            "group": "Source Code & Scripts",
            "reason": f"Source code / project file ({ext})"
        }
    else:
        res = {
            "category": "Other Files",
            "group": "Other Files",
            "reason": f"Uncategorized file type ({ext or 'no extension'})"
        }

    meta = CATEGORY_META.get(res["category"], {"icon": "file", "color": "gray", "label": res["category"]})
    res["icon"] = meta["icon"]
    res["color"] = meta["color"]
    res["label"] = meta["label"]
    return res
