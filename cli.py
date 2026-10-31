import argparse
import os
import sys
from organizer import scan_folder, execute_organization, undo_organization_session, load_history

def main():
    parser = argparse.ArgumentParser(description="DownSort CLI - Smart Local File Organizer")
    parser.add_argument("--folder", "-f", default=os.path.normpath(os.path.expanduser(r"~\Downloads")), help="Target folder to scan/organize")
    parser.add_argument("--scan", action="store_true", help="Scan and display classification preview")
    parser.add_argument("--organize", action="store_true", help="Execute organization")
    parser.add_argument("--mode", choices=["move", "copy"], default="move", help="Operation mode (move or copy)")
    parser.add_argument("--history", action="store_true", help="View past organization runs")
    parser.add_argument("--undo", help="Undo a specific session ID (or 'latest')")

    args = parser.parse_args()

    if args.history:
        history = load_history()
        if not history:
            print("[INFO] No sorting history found.")
            return
        print("\n=== Sorting History ===")
        for s in history:
            status = f"({s.get('status', 'active')})"
            print(f"- {s['session_id']} | {s['timestamp']} | {len(s.get('moves', []))} files {s.get('mode', 'moved')} {status}")
        return

    if args.undo:
        session_id = args.undo
        if session_id == "latest":
            hist = load_history()
            active = [s for s in hist if s.get("status") != "undone"]
            if not active:
                print("[ERROR] No active session to undo.")
                return
            session_id = active[0]["session_id"]

        print(f"[ACTION] Rolling back session {session_id}...")
        res = undo_organization_session(session_id)
        if res.get("success"):
            print(f"[SUCCESS] Restored {res['restored']} file(s) back to original locations.")
        else:
            print(f"[ERROR] Rollback failed: {res.get('error')}")
        return

    if args.organize:
        print(f"[ACTION] Scanning {args.folder}...")
        scan_data = scan_folder(args.folder)
        files = scan_data.get("files", [])
        if not files:
            print("[INFO] No loose files found to organize.")
            return

        actions = [{"filepath": f["filepath"], "target_folder": f["target_folder"]} for f in files]
        print(f"[ACTION] {args.mode.upper()}ing {len(actions)} files into categorized folders...")
        res = execute_organization(args.folder, actions, mode=args.mode)
        print(f"[SUCCESS] Organized {res['successful']} file(s). (Failed: {res['failed']})")
        print(f"Session ID: {res['session_id']} (Use --undo {res['session_id']} to rollback)")
        return

    # Default action: Scan preview
    print(f"\n[SCAN] Analyzing files in: {args.folder}\n")
    data = scan_folder(args.folder)

    print(f"Total Files: {data['total_files']} | Total Size: {data['total_size_formatted']} | PDFs: {data['pdf_count']}\n")
    print(f"{'Category':<32} | {'Count':<6} | {'Total Size':<10}")
    print("-" * 55)
    for c in data["categories_breakdown"]:
        print(f"{c['category']:<32} | {c['count']:<6} | {c['size_formatted']:<10}")

    print("\nRun with '--organize' to sort these files, or launch the web dashboard using 'python run.py'.")

if __name__ == "__main__":
    main()
