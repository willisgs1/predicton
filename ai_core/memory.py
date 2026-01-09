import sqlite3
import json
import time
import os

class LongTermMemory:
    def __init__(self, db_path="memory.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS experiences
                     (id INTEGER PRIMARY KEY, timestamp REAL, source TEXT, content TEXT, confidence REAL)''')
        conn.commit()
        conn.close()

    def add_observation(self, source, content, confidence):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("INSERT INTO experiences (timestamp, source, content, confidence) VALUES (?, ?, ?, ?)",
                  (time.time(), source, str(content), confidence))
        conn.commit()
        conn.close()

    def save_memory(self):
        # SQLite commits immediately, but this is kept for API compatibility
        pass

    def get_stats(self):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("SELECT COUNT(*) FROM experiences")
            count = c.fetchone()[0]
            conn.close()
            return f"Memory Bank: {count} entries"
        except:
            return "Memory Bank: Offline"
