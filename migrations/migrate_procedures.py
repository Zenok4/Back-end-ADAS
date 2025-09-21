import os
from database import db
from sqlalchemy import text

SQL_DIR = "migrations/sql/procedures"

def migrate_procedures(app):
    applied = []
    with app.app_context():
        if not os.path.exists(SQL_DIR):
            return applied

        for file in os.listdir(SQL_DIR):
            if file.endswith(".sql"):
                with open(os.path.join(SQL_DIR, file), "r", encoding="utf-8") as f:
                    sql = f.read()
                    db.session.execute(text(sql))
                    applied.append(file)
                    print(f"⚡ Applied procedure from {file}")

        db.session.commit()
    return applied
