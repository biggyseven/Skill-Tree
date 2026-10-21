import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ContentWatcher(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        if event.src_path.endswith((".md", ".json")):
            print(f"🚀 Nouveau fichier détecté : {event.src_path}")
            print("⏳ Mise à jour de la base de données...")
            subprocess.run(["python", "main.py", "import"])
            print("✅ Base de données mise à jour !")

if __name__ == "__main__":
    path = "content"
    event_handler = ContentWatcher()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    print(f"👀 Surveillance du dossier '{path}' en cours... (Ctrl+C pour arrêter)")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()