import subprocess
import time
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    raise RuntimeError("watchdog is not installed. Run: pip install watchdog")

PROCESS = None
BASE_DIR = Path(__file__).parent.resolve()
APP_FILE = (BASE_DIR / "app.py").resolve()

def restart():
    global PROCESS
    if PROCESS and PROCESS.poll() is None:
        PROCESS.terminate()
        PROCESS.wait()
    PROCESS = subprocess.Popen(["python", str(APP_FILE)])
    print("🔄 App restarted")

class Handler(FileSystemEventHandler):
    """Restart app when app.py changes"""
    def on_modified(self, event):
        # Watch only the app.py file
        changed_file = Path(event.src_path).resolve()
        if changed_file == APP_FILE:
            restart()

if __name__ == "__main__":
    restart()
    observer = Observer()
    observer.schedule(Handler(), str(BASE_DIR), recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        if PROCESS:
            PROCESS.terminate()
    observer.join()
