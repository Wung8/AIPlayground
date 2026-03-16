import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from server import app, db

app.app_context().push()

with db.engine.connect() as conn:
    conn.execute(text("ALTER TABLE bot ADD COLUMN metric FLOAT"))
    conn.execute(text("UPDATE bot SET metric = CAST(elo AS FLOAT)"))
    conn.execute(text("ALTER TABLE bot DROP COLUMN elo"))
    pass