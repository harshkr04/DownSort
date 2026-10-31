import sys
import os
import socket
import webbrowser
import threading
import time
import uvicorn

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def find_available_port(start_port: int = 5050) -> int:
    port = start_port
    while is_port_in_use(port):
        port += 1
    return port

def open_browser(url: str):
    time.sleep(1.2)
    print(f"\n[🚀] Opening DownSort in your browser: {url}")
    webbrowser.open(url)

def main():
    port = find_available_port(5050)
    url = f"http://127.0.0.1:{port}"
    
    print("=" * 65)
    print("  📁 DownSort - Smart Local Downloads & Deep PDF Organizer")
    print("=" * 65)
    print(f"  * Mode: 100% Local & Privacy-Preserving")
    print(f"  * Web Dashboard: {url}")
    print(f"  * Press Ctrl+C in this window anytime to stop the server")
    print("=" * 65)

    # Launch browser automatically
    threading.Thread(target=open_browser, args=(url,), daemon=True).start()

    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    sys.path.insert(0, script_dir)

    uvicorn.run("app:app", host="127.0.0.1", port=port, log_level="info")

if __name__ == "__main__":
    main()
