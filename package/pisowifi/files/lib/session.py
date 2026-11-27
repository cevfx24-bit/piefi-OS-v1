import threading, time, logging
from lib import db, firewall

class SessionManager(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._stop = threading.Event()
    def run(self):
        while not self._stop.wait(1):
            try:
                expired = db.tick_clients()
                for mac in expired:
                    firewall.remove_authorized(mac)
            except Exception:
                pass
