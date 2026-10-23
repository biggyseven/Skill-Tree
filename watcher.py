import time
import threading
import requests  # <-- Ajout de cette librairie (déjà installée normalement)
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.db import connect, ensure_ready
from app.loader import load_content, ContentError

CONTENT_DIR = Path(__file__).parent / "content"
DB_PATH = "skilltree.db"
API_URL = "http://127.0.0.1:8000/api/trigger-update"

class ContentWatcher(FileSystemEventHandler):
    def __init__(self):
        self.last_reload = 0
        self.lock = threading.Lock()

    def on_modified(self, event): self.handle_event(event)
    def on_created(self, event): self.handle_event(event)
    def on_deleted(self, event): self.handle_event(event)

    def handle_event(self, event):
        if event.is_directory: return
        if not event.src_path.endswith((".md", ".json")): return

        now = time.time()
        if now - self.last_reload < 2: return
        
        with self.lock:
            self.last_reload = now
            print(f"\n👀 Modification détectée : {Path(event.src_path).name}")
            print("⏳ Mise à jour de la base de données en cours...")
            
            try:
                conn = connect(DB_PATH)
                ensure_ready(conn)
                report = load_content(conn)
                conn.close()
                print(f"✅ Succès ! {report.nodes} nœuds chargés.")
                
                # === LA LIGNE MAGIQUE ===
                try:
                    requests.post(API_URL, timeout=2)
                    print("📡 Navigateurs notifiés en temps réel.")
                except Exception:
                    print("⚠️ Impossible de notifier l'API (le serveur est-il allumé ?).")
                # ========================
                
            except ContentError as e:
                print(f"❌ ERREUR DANS TON CONTENU : {e}\n")
            except Exception as e:
                print(f"❌ ERREUR TECHNIQUE : {e}\n")

def start_watcher():
    event_handler = ContentWatcher()
    observer = Observer()
    observer.schedule(event_handler, str(CONTENT_DIR), recursive=True)
    observer.start()
    print(f"👀 Surveillance du dossier '{CONTENT_DIR}' activée.")
    return observer

if __name__ == "__main__":
    print("Démarrage du mode Auto-Sync (Ctrl+C pour arrêter)...")
    observer = start_watcher()
    try:
        while True: time.sleep(1)
    except KeyboardInterrupt: observer.stop()
    observer.join()