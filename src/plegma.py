#!/usr/bin/env python3

import os
import sys
import json
from pathlib import Path


from .cli import create_cli, interactive_add, format_output
from .db_manager import DBManager, DBConfig

CWD = os.getcwd()

DB_PATH = str(Path(CWD, "db", "database.sqlite"))
BACKUP_PATH = str(Path(CWD, "db", "backups" "database.sqlite"))
SCHEMA_PATH = str(Path(CWD, "config", "schema.sql"))
PREFIX_PATH = str(Path(CWD, "config", "prefixes.json"))


def main():

    config = DBConfig(DB_PATH, BACKUP_PATH, SCHEMA_PATH, PREFIX_PATH)

    parser = create_cli()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    db = DBManager(config)

    try:
        if args.command == "add":
            if args.interactive:
                data = interactive_add(db, args.table)
            elif args.json:
                if os.path.isfile(args.json):
                    with open(args.json, "r") as f:
                        data = json.load(f)
                else:
                    data = json.loads(args.json)
            else:
                print("Error: Either --json or --interactive must be specified")
                return

            entry_id = db.add_entry(args.table, data)
            print(f"Added entry with ID: {entry_id}")

        elif args.command == "update":
            if args.json:
                if os.path.isfile(args.json):
                    with open(args.json, "r") as f:
                        data = json.load(f)
                else:
                    data = json.loads(args.json)
            else:
                print("Error: --json must be specified")
                return

            success = db.update_entry(args.table, args.id, data)
            print(f"{'Updated' if success else 'Failed to update'} entry {args.id}")

        elif args.command == "search":
            results = db.search_entries(args.table, args.pattern, args.field)
            print(format_output(results))

        elif args.command == "get":
            result = db.get_entry_by_id(args.table, args.id)
            if result:
                print(format_output([result]))
            else:
                print(f"Entry {args.id} not found")

        elif args.command == "list":
            results = db.list_entries(args.table, args.limit)
            print(format_output(results))

        elif args.command == "delete":
            success = db.delete_entry(args.table, args.id)
            print(f"{'Deleted' if success else 'Failed to delete'} entry {args.id}")

        elif args.command == "backup":
            backup_path = db.backup_database()
            print(f"Backup created: {backup_path}")

        elif args.command == "import":
            count = db.import_from_json(args.table, args.file)
            print(f"Imported {count} entries")

        elif args.command == "export":
            count = db.export_to_json(args.table, args.file)
            print(f"Exported {count} entries to {args.file}")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

    finally:
        db.close()


if __name__ == "__main__":
    main()
