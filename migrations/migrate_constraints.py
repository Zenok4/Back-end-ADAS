from sqlalchemy import inspect, text
from database import db

def migrate_constraints(app, drop=False):
    """
    - Tạo các foreign key mới nếu chưa tồn tại
    - Nếu drop=True, drop column thừa kèm FK cũ
    """
    def drop_fk_before_column(table_name, column_name):
        """Nếu column có FK, drop FK trước khi drop column"""
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            if column_name in fk["constrained_columns"]:
                fk_name = fk["name"]
                print(f"🔗 Dropping FK {fk_name} on {table_name}.{column_name}")
                db.session.execute(text(f"ALTER TABLE {table_name} DROP FOREIGN KEY {fk_name}"))
                return True
        return False

    with app.app_context():
        inspector = inspect(db.engine)
        added = []
        dropped = []
        warnings = []

        for table in db.metadata.sorted_tables:
            # Cột hiện có FK trong DB
            existing_fks = {fk["constrained_columns"][0] for fk in inspector.get_foreign_keys(table.name)}

            # Thêm FK mới nếu chưa tồn tại
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

            # Drop các column thừa (nếu drop=True)
            existing_cols = {col["name"] for col in inspector.get_columns(table.name)}
            model_cols = {col.name for col in table.columns}

            for col_name in existing_cols - model_cols:
                if drop:
                    # Drop FK trước
                    drop_fk_before_column(table.name, col_name)

                    # Drop column
                    sql = f"ALTER TABLE {table.name} DROP COLUMN {col_name}"
                    db.session.execute(text(sql))
                    dropped.append((table.name, col_name))
                else:
                    warnings.append((table.name, col_name))

        db.session.commit()

        # Log kết quả
        for t, c, rt, rc in added:
            print(f"🔗 Added FK on '{t}.{c}' → '{rt}.{rc}'")
        for t, c in dropped:
            print(f"🗑️ Dropped column '{c}' from '{t}'")
        for t, c in warnings:
            print(f"⚠️ Column '{c}' in '{t}' exists in DB but not in models (consider dropping)")

        return {
            "added": added,
            "dropped": dropped,
            "warnings": warnings
        }
