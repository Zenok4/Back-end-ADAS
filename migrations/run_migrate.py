import argparse
import inspect
from flask import Flask
from models import init_dtb
from . import (
    migrate_tables,
    migrate_columns,
    migrate_constraints,
    migrate_uniques,
    migrate_indexes,
    migrate_procedures,
    migrate_triggers
)

MIGRATIONS = [
    migrate_tables.migrate_tables,
    migrate_columns.migrate_columns,
    migrate_constraints.migrate_constraints,
    migrate_uniques.migrate_uniques,
    migrate_indexes.migrate_indexes,
    migrate_procedures.migrate_procedures,
    migrate_triggers.migrate_triggers,
]

def run_migrations(app, drop=False):
    changed = False

    for migrate in MIGRATIONS:
        sig = inspect.signature(migrate)
        if "drop" in sig.parameters:
            result = migrate(app, drop=drop)
        else:
            result = migrate(app)

        # Kiểm tra xem có thay đổi nào không
        if result and any(value for value in result.values() if isinstance(value, list)):
            changed = True

    if not changed:
        print("ℹ️ Database schema is up to date")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run database migrations")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop columns that exist in DB but not in models"
    )
    args = parser.parse_args()

    app = Flask(__name__)
    init_dtb(app)
    run_migrations(app, drop=args.drop)