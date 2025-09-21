from sqlalchemy import inspect, text
from database import db

def migrate_uniques(app):
    with app.app_context():
        inspector = inspect(db.engine)
        added = []
        for table in db.metadata.sorted_tables:
            existing_uniques = {u['name'] for u in inspector.get_unique_constraints(table.name)}
            for constraint in table.constraints:
                if constraint.__class__.__name__ == "UniqueConstraint":
                    name = constraint.name or f"uq_{table.name}_{'_'.join(c.name for c in constraint.columns)}"
                    if name not in existing_uniques:
                        cols = ", ".join(c.name for c in constraint.columns)
                        sql = f"ALTER TABLE {table.name} ADD CONSTRAINT {name} UNIQUE ({cols})"
                        db.session.execute(text(sql))
                        added.append((table.name, name))
        db.session.commit()
        if added:
            print("⚡ Added unique constraints:", added)
        return added
