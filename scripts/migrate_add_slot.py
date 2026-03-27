import sqlite3
import os
from collections import defaultdict

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "instance", "site.db")

conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT id, name, date_posted, metric, user_id, environment FROM bot ORDER BY id ASC")
bots = cur.fetchall()

# assign slot 0, 1, 2 per user+environment in order of existing id
slot_counters = defaultdict(int)
bot_slots = {}
for bot in bots:
    key = (bot["user_id"], bot["environment"])
    bot_slots[bot["id"]] = slot_counters[key]
    slot_counters[key] += 1

cur.execute("""
    CREATE TABLE bot_new (
        id INTEGER NOT NULL PRIMARY KEY,
        name VARCHAR(30) UNIQUE,
        date_posted DATETIME,
        metric FLOAT,
        user_id INTEGER NOT NULL REFERENCES user (id),
        environment VARCHAR(30) NOT NULL,
        slot INTEGER NOT NULL
    )
""")

for bot in bots:
    cur.execute(
        "INSERT INTO bot_new (id, name, date_posted, metric, user_id, environment, slot) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (bot["id"], bot["name"], bot["date_posted"], bot["metric"], bot["user_id"], bot["environment"], bot_slots[bot["id"]])
    )

cur.execute("DROP TABLE bot")
cur.execute("ALTER TABLE bot_new RENAME TO bot")

conn.commit()
conn.close()
print("Migration complete.")
