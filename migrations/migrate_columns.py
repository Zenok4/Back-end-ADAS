from sqlalchemy import inspect, text
from database import db

def types_equal(existing_type, new_type, table_name, column_name):
    """
    So sánh kiểu dữ liệu giữa cột trong DB và model.
    - BOOLEAN tương đương TINYINT(1)
    - ENUM lấy giá trị từ information_schema để so sánh
    """
    existing_lower = str(existing_type).lower().replace(" ", "")
    new_lower = new_type.lower().replace(" ", "")

    # Boolean / TINYINT(1)
    if existing_lower.startswith("tinyint") and new_lower in ("bool", "boolean"):
        return True

    # DECIMAL và NUMERIC coi như giống nhau
    if (existing_lower.startswith("decimal") and new_lower.startswith("numeric")) \
        or (existing_lower.startswith("numeric") and new_lower.startswith("decimal")):
        # So sánh precision, scale nếu có
        import re
        def parse_ps(s):
            m = re.search(r"\((\d+),(\d+)\)", s)
            if m:
                return int(m[1]), int(m[2])
            return None
        existing_ps = parse_ps(existing_lower)
        new_ps = parse_ps(new_lower)
        return existing_ps == new_ps
    
    # ENUM
    if existing_lower.startswith("enum") and new_lower.startswith("enum"):
        # Lấy danh sách giá trị ENUM từ information_schema
        query = text("""
            SELECT COLUMN_TYPE 
            FROM information_schema.columns 
            WHERE TABLE_NAME = :table_name 
            AND COLUMN_NAME = :column_name
        """)
        result = db.session.execute(query, {"table_name": table_name, "column_name": column_name}).fetchone()
        if result:
            enum_def = result[0].lower()  # Ví dụ: enum('login','verify','reset')
            existing_vals = enum_def[5:-1].replace("'", "").split(",") if enum_def.startswith("enum") else []
        else:
            existing_vals = []

        new_vals = new_lower[5:-1].replace("'", "").split(",") if new_lower.startswith("enum") else []
        
        return set(existing_vals) == set(new_vals)

    return existing_lower == new_lower

def migrate_columns(app, drop=False):
    """
    - Thêm cột mới
    - Sửa cột khác kiểu
    - Cảnh báo cột thừa nếu drop=False
    - Xoá cột thừa nếu drop=True
    """
    with app.app_context():
        inspector = inspect(db.engine)
        added = []
        altered = []
        dropped = []
        warnings = []

        for table in db.metadata.sorted_tables:
            # Cột hiện tại trong DB
            existing_cols = {col["name"]: col for col in inspector.get_columns(table.name)}
            # Cột trong model
            model_cols = {col.name: col for col in table.columns}

            # Thêm / sửa cột
            for col_name, col in model_cols.items():
                if col_name not in existing_cols:
                    # Thêm cột mới
                    col_type = col.type.compile(db.engine.dialect)
                    nullable = "NULL" if col.nullable else "NOT NULL"
                    sql = f"ALTER TABLE {table.name} ADD COLUMN {col.name} {col_type} {nullable}"
                    db.session.execute(text(sql))
                    added.append((table.name, col_name))
                else:
                    # So sánh kiểu dữ liệu
                    existing_type = str(existing_cols[col_name]["type"])
                    new_type = col.type.compile(db.engine.dialect)
                    if not types_equal(existing_type, new_type, table.name, col_name):
                        sql = f"ALTER TABLE {table.name} MODIFY COLUMN {col.name} {new_type}"
                        db.session.execute(text(sql))
                        altered.append((table.name, col_name, existing_type, new_type))

            # Trong hàm migrate_columns, sửa đổi đoạn "Xoá / cảnh báo cột thừa":
            for col_name in existing_cols:
                if col_name not in model_cols:
                    if drop:
                        # Sửa đổi: Gỡ FK trước khi DROP COLUMN
                        # Bạn cần truyền inspector từ migrate_constraints vào hoặc định nghĩa lại hàm này
                        
                        # --- Tái tạo logic gỡ FK ---
                        fk_query = text("""
                            SELECT CONSTRAINT_NAME
                            FROM information_schema.KEY_COLUMN_USAGE
                            WHERE TABLE_SCHEMA = DATABASE()
                            AND TABLE_NAME = :table
                            AND COLUMN_NAME = :column
                            AND REFERENCED_TABLE_NAME IS NOT NULL
                        """)

                        fk_rows = db.session.execute(
                            fk_query,
                            {"table": table.name, "column": col_name}
                        ).fetchall()

                        for row in fk_rows:
                            fk_name = row[0]
                            print(f"🔗 Dropping FK {fk_name} on {table.name}.{col_name}")
                            db.session.execute(
                                text(f"ALTER TABLE `{table.name}` DROP FOREIGN KEY `{fk_name}`")
                            )

                        # --- DROP COLUMN ---
                        sql = f"ALTER TABLE {table.name} DROP COLUMN {col_name}"
                        db.session.execute(text(sql))
                        dropped.append((table.name, col_name))
                    else:
                        warnings.append((table.name, col_name))

                    db.session.commit()

        # Log
        for t, c in added:
            print(f"⚡ Added column '{c}' to '{t}'")
        for t, c, old, new in altered:
            print(f"🔄 Modified column '{c}' in '{t}' from {old} -> {new}")
        for t, c in dropped:
            print(f"🗑️ Dropped column '{c}' from '{t}'")
        for t, c in warnings:
            print(f"⚠️ Column '{c}' in '{t}' exists in DB but not in models (consider dropping)")

        return {
            "added": added,
            "altered": altered,
            "dropped": dropped,
            "warnings": warnings
        }