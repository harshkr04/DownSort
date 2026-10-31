import os
import shutil
import json
import time
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor
from classifier import classify_file, CATEGORY_META

HISTORY_FILE = os.path.join(os.path.dirname(__file__), ".sort_history.json")


def format_size(bytes_size: int) -> str:
    """Format bytes into readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} PB"


def get_unique_destination_path(target_dir: str, filename: str) -> str:
    """Ensure we never overwrite an existing file by generating a safe unique name."""
    name, ext = os.path.splitext(filename)
    counter = 1
    dest_path = os.path.join(target_dir, filename)

    while os.path.exists(dest_path):
        new_filename = f"{name} ({counter}){ext}"
        dest_path = os.path.join(target_dir, new_filename)
        counter += 1

    return dest_path


def load_history() -> List[Dict[str, Any]]:
    """Load transaction history."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history: List[Dict[str, Any]]) -> None:
    """Save transaction history."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error saving history: {e}")


def _process_single_file(folder_path: str, entry: str) -> Optional[Dict[str, Any]]:
    """Process a single file for classification."""
    full_path = os.path.join(folder_path, entry)
    if not os.path.isfile(full_path):
        return None

    try:
        stat = os.stat(full_path)
        size_bytes = stat.st_size
        mod_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
    except Exception:
        size_bytes = 0
        mod_time = "Unknown"

    classification = classify_file(full_path)
    cat = classification["category"]

    return {
        "id": str(uuid.uuid4())[:8],
        "filename": entry,
        "filepath": full_path,
        "size_bytes": size_bytes,
        "size_formatted": format_size(size_bytes),
        "modified": mod_time,
        "extension": os.path.splitext(entry)[1].lower(),
        "category": cat,
        "group": classification["group"],
        "reason": classification["reason"],
        "icon": classification["icon"],
        "color": classification["color"],
        "label": classification["label"],
        "target_folder": cat,
        "selected": True
    }


def scan_folder(folder_path: str) -> Dict[str, Any]:
    """
    Scans loose files in the target directory (ignores internal app directories).
    Uses ThreadPoolExecutor for fast parallel scanning of PDFs and images.
    """
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        raise ValueError(f"Directory does not exist: {folder_path}")

    ignored_names = {
        "localfilesorter", "smartdownloadsorter", ".sort_history.json",
        "desktop.ini", "thumbs.db", "$recycle.bin"
    }

    raw_entries = sorted(os.listdir(folder_path))
    valid_entries = [
        e for e in raw_entries
        if not e.startswith('.') and e.lower() not in ignored_names and os.path.isfile(os.path.join(folder_path, e))
    ]

    files_list = []
    category_counts: Dict[str, int] = {}
    category_sizes: Dict[str, int] = {}
    total_size = 0

    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(_process_single_file, folder_path, entry) for entry in valid_entries]
        for f in futures:
            res = f.result()
            if res:
                files_list.append(res)
                cat = res["category"]
                sz = res["size_bytes"]
                total_size += sz
                category_counts[cat] = category_counts.get(cat, 0) + 1
                category_sizes[cat] = category_sizes.get(cat, 0) + sz

    # Sort files by filename
    files_list.sort(key=lambda x: x["filename"].lower())

    # Build category breakdown
    categories_breakdown = []
    for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
        meta = CATEGORY_META.get(cat, {"icon": "file", "color": "gray", "label": cat})
        categories_breakdown.append({
            "category": cat,
            "label": meta["label"],
            "icon": meta["icon"],
            "color": meta["color"],
            "count": count,
            "size_formatted": format_size(category_sizes[cat]),
            "size_bytes": category_sizes[cat]
        })

    pdf_breakdown = [c for c in categories_breakdown if c["category"].startswith("PDFs/")]

    return {
        "folder_path": folder_path,
        "total_files": len(files_list),
        "total_size_bytes": total_size,
        "total_size_formatted": format_size(total_size),
        "categories_breakdown": categories_breakdown,
        "pdf_count": sum(c["count"] for c in pdf_breakdown),
        "files": files_list
    }


def execute_organization(
    base_folder: str,
    file_actions: List[Dict[str, Any]],
    mode: str = "move"
) -> Dict[str, Any]:
    """
    Executes the file organization.
    - file_actions: List of dicts with {'filepath': ..., 'target_folder': ...}
    - mode: 'move' or 'copy'
    """
    if not os.path.exists(base_folder):
        raise ValueError("Target folder does not exist")

    session_id = f"run_{int(time.time())}_{str(uuid.uuid4())[:6]}"
    session_record = {
        "session_id": session_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "base_folder": base_folder,
        "mode": mode,
        "status": "completed",
        "moves": []
    }

    successful = 0
    failed = 0
    errors = []

    for item in file_actions:
        src = item.get("filepath")
        rel_target = item.get("target_folder")

        if not src or not os.path.exists(src):
            continue

        filename = os.path.basename(src)
        target_dir = os.path.join(base_folder, *rel_target.split("/"))

        try:
            os.makedirs(target_dir, exist_ok=True)
            dest = get_unique_destination_path(target_dir, filename)

            if mode == "move":
                shutil.move(src, dest)
            else:
                shutil.copy2(src, dest)

            session_record["moves"].append({
                "source": src,
                "destination": dest,
                "filename": filename,
                "category": rel_target
            })
            successful += 1
        except Exception as e:
            failed += 1
            errors.append({"file": filename, "error": str(e)})

    # Save to history if at least one move succeeded and mode is 'move'
    if successful > 0 and mode == "move":
        history = load_history()
        history.insert(0, session_record)
        save_history(history)

    return {
        "session_id": session_id,
        "mode": mode,
        "successful": successful,
        "failed": failed,
        "errors": errors
    }


def undo_organization_session(session_id: str) -> Dict[str, Any]:
    """Rolls back a previously completed organization session."""
    history = load_history()
    target_session = None

    for s in history:
        if s["session_id"] == session_id:
            target_session = s
            break

    if not target_session:
        return {"success": False, "error": f"Session {session_id} not found"}

    if target_session.get("status") == "undone":
        return {"success": False, "error": "This session has already been rolled back"}

    restored = 0
    failed = 0
    errors = []

    for item in reversed(target_session.get("moves", [])):
        dest = item["destination"]
        src = item["source"]

        if not os.path.exists(dest):
            continue

        try:
            target_dir = os.path.dirname(src)
            filename = os.path.basename(src)
            final_src = get_unique_destination_path(target_dir, filename) if os.path.exists(src) else src

            shutil.move(dest, final_src)
            restored += 1
        except Exception as e:
            failed += 1
            errors.append({"file": dest, "error": str(e)})

    # Mark session as undone
    target_session["status"] = "undone"
    target_session["undone_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_history(history)

    # Clean up empty category directories created by the tool
    base_folder = target_session.get("base_folder")
    if base_folder and os.path.exists(base_folder):
        for root, dirs, files in os.walk(base_folder, topdown=False):
            if root != base_folder and not dirs and not files:
                try:
                    os.rmdir(root)
                except Exception:
                    pass

    return {
        "success": True,
        "session_id": session_id,
        "restored": restored,
        "failed": failed,
        "errors": errors
    }
