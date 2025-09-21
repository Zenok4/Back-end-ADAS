from sqlalchemy import inspect, text
from database import db

def migrate_indexes(app):
    added = []
    with app.app_context():
        inspector = inspect(db.engine)

        for table in db.metadata.sorted_tables:
            existing_indexes = {i["name"] for i in inspector.get_indexes(table.name)}
            for idx in table.indexes:
                if idx.name not in existing_indexes:
                    cols = ", ".join(c.name for c in idx.columns)
                    unique = "UNIQUE " if idx.unique else ""
                    sql = f"CREATE {unique}INDEX {idx.name} ON {table.name} ({cols})"
                    db.session.execute(text(sql))
                    added.append((table.name, idx.name))

        db.session.commit()

    if added:
        for t, n in added:
            print(f"📌 Added index '{n}' on '{t}'")
    return added
