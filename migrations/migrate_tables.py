from sqlalchemy import inspect
from database import db

def migrate_tables(app):
    with app.app_context():
        inspector = inspect(db.engine)
        created = []

        for table in db.metadata.sorted_tables:
            if not inspector.has_table(table.name):
                table.create(db.engine)
                created.append(table.name)

        if created:
            print("✅ Created tables:", ", ".join(created))
        return created
