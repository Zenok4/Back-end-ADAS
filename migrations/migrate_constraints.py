from sqlalchemy import inspect, text
from database import db

def migrate_constraints(app):
    with app.app_context():
        inspector = inspect(db.engine)
        added = []

        for table in db.metadata.sorted_tables:
            existing_fks = {fk["constrained_columns"][0] for fk in inspector.get_foreign_keys(table.name)}

            for fk in table.foreign_keys:
                col_name = fk.parent.name
                if col_name not in existing_fks:
                    fk_name = f"fk_{table.name}_{col_name}"
                    target_table = fk.column.table.name
                    target_col = fk.column.name
                    sql = f"""
                        ALTER TABLE {table.name}
                        ADD CONSTRAINT {fk_name}
                        FOREIGN KEY ({col_name}) REFERENCES {target_table}({target_col})
                    """
                    db.session.execute(text(sql))
                    added.append((table.name, col_name, target_table, target_col))

        db.session.commit()

        if added:
            for t, c, rt, rc in added:
                print(f"🔗 Added FK on '{t}.{c}' → '{rt}.{rc}'")
        return added
