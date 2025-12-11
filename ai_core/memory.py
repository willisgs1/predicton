import sqlite3
import os
import time
import json

class LongTermMemory:
    def __init__(self, filepath="memory.db"):
        self.filepath = filepath
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Initializes the SQLite database."""
        self.conn = sqlite3.connect(self.filepath, check_same_thread=False)
        c = self.conn.cursor()

        # Observations Table
        c.execute('''CREATE TABLE IF NOT EXISTS observations
                     (id INTEGER PRIMARY KEY, timestamp REAL, source TEXT, state TEXT, confidence REAL)''')

        # Concepts Table (The Knowledge Graph)
        c.execute('''CREATE TABLE IF NOT EXISTS concepts
                     (keyword TEXT PRIMARY KEY, related_terms TEXT, weight INTEGER)''')

        self.conn.commit()
        print("[Memory] Grand Archive (SQL) initialized.")

    def add_observation(self, source_url, quantum_state, confidence):
        try:
            c = self.conn.cursor()
            c.execute("INSERT INTO observations (timestamp, source, state, confidence) VALUES (?, ?, ?, ?)",
                      (time.time(), source_url, quantum_state, confidence))
            self.conn.commit()
        except Exception as e:
            print(f"[Memory] Insert failed: {e}")

    def associate_concept(self, keyword, related_term):
        """
        Updates the concept graph.
        """
        try:
            c = self.conn.cursor()
            c.execute("SELECT related_terms, weight FROM concepts WHERE keyword=?", (keyword,))
            row = c.fetchone()

            if row:
                related = json.loads(row[0])
                weight = row[1] + 1
                if related_term not in related:
                    related.append(related_term)

                c.execute("UPDATE concepts SET related_terms=?, weight=? WHERE keyword=?",
                          (json.dumps(related), weight, keyword))
            else:
                c.execute("INSERT INTO concepts (keyword, related_terms, weight) VALUES (?, ?, ?)",
                          (keyword, json.dumps([related_term]), 1))

            self.conn.commit()
        except Exception as e:
            print(f"[Memory] Association failed: {e}")

    def save_memory(self):
        # SQLite saves automatically on commit, but we keep the method signature for compatibility
        if self.conn:
            self.conn.commit()

    def get_stats(self):
        c = self.conn.cursor()
        c.execute("SELECT COUNT(*) FROM observations")
        obs_count = c.fetchone()[0]
        c.execute("SELECT COUNT(*) FROM concepts")
        conc_count = c.fetchone()[0]
        return f"Observations: {obs_count}, Concepts: {conc_count}"

if __name__ == "__main__":
    mem = LongTermMemory("test_memory.db")
    mem.add_observation("test.com", "101", 0.9)
    mem.associate_concept("AI", "Evolution")
    print(mem.get_stats())
