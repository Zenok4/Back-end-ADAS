from sqlalchemy import inspect, text
from database import db

def migrate_tables(app, drop=False):
    """
    - Tạo table mới nếu chưa có
    - Drop table trong DB nhưng không còn trong models nếu drop=True
    """
    with app.app_context():
        inspector = inspect(db.engine)
        created = []
        dropped = []
        warnings = []

        existing_tables = inspector.get_table_names()
        model_tables = [table.name for table in db.metadata.sorted_tables]

        # 1️⃣ Tạo table mới
        for table in db.metadata.sorted_tables:
            if table.name not in existing_tables:
                table.create(db.engine)
                created.append(table.name)

        # 2️⃣ Table thừa
        extra_tables = [t for t in existing_tables if t not in model_tables]

        if drop and extra_tables:
            # Tắt FK tạm thời
            db.session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            for table_name in extra_tables:
                db.session.execute(text(f"DROP TABLE {table_name}"))
                dropped.append(table_name)
            db.session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        else:
            warnings.extend(extra_tables)

        db.session.commit()

        if created:
            print("✅ Created tables:", ", ".join(created))
        if dropped:
            print("🗑️ Dropped tables:", ", ".join(dropped))
        if warnings:
            print("⚠️ Tables in DB but not in models:", ", ".join(warnings))

        return {
            "created": created,
            "dropped": dropped,
            "warnings": warnings
        }
