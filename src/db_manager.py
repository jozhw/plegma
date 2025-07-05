import json
import sqlite3
import uuid
import re
import shutil

from pathlib import Path
from datetime import datetime


from dataclasses import dataclass
import typing as tp


@dataclass
class DBConfig:
    "Configuration class for DBManager"

    db_path: str
    backup_path: str
    schema_path: str
    prefix_path: str


class DBManager:

    def __init__(self, config: DBConfig):

        self.db_path = Path(config.db_path)
        self.backup_dir = Path(config.backup_path)
        self.backup_dir.mkdir(exist_ok=True)
        self.schema_path = config.schema_path
        self.prefix_path = config.prefix_path

        self.prefixes = None
        self.tables = None
        self.conn = None

        self._get_schema()
        self._init_db()

    def _get_schema(self):

        # load prefixes
        with open(self.prefix_path, "r") as f:

            self.prefixes: tp.Optional[tp.Dict] = json.load(f)

        assert self.prefixes is not None, "Failed to obtain prefixes"

        tables = self.prefixes.keys()

        self.tables = list(tables)

    def _init_db(self):
        """
        Initialize database connection and create tables from schema if not exist
        """

        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row  # enable dictionary like access

        # create tables
        self._create_tables()

    def _create_tables(self):

        assert self.conn is not None, "Connection cannot be established"

        cursor = self.conn.cursor()

        with open(self.schema_path, "r") as schema:
            sql_script = schema.read()

        cursor.executescript(sql_script)

        self.conn.commit()

    def _generate_id(self, table_name: str) -> str:

        prefix = self.prefixes.get(table_name, "xx")  # pyright: ignore
        unique_part = str(uuid.uuid4())[:8]

        return f"{prefix}{unique_part}"

    def _update_history(self, current_history: tp.Optional[str]) -> str:
        "Add current timestamp to history"

        now = datetime.now().isoformat()

        if current_history:

            history_list = json.loads(current_history)

        else:

            history_list = []

        history_list.append(now)

        return json.dumps(history_list)

    def add_entry(self, table_name: str, data: tp.Dict[str, tp.Any]) -> str:
        """
        Add new entry to specified table
        """

        # keeps linter happy
        assert (
            self.tables is not None
        ), "self.tables cannot be None, initialization must have failed"

        if table_name not in self.tables:

            raise ValueError("Invalid table name: {}".format(table_name))

        if "id" not in data:

            data["id"] = self._generate_id(table_name)

        # add update history
        data["update_history"] = self._update_history(None)

        # build sql
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?" for _ in data])
        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        assert self.conn is not None, "Connection failure for add_entry"
        cursor = self.conn.cursor()
        cursor.execute(sql, list(data.values()))

        self.conn.commit()

        return data["id"]

    def update_entry(
        self, table_name: str, entry_id: str, data: tp.Dict[str, tp.Any]
    ) -> bool:
        """Update existing entry"""

        # keeps linter happy
        assert (
            self.tables is not None
        ), "self.tables cannot be None, initialization must have failed"

        if table_name not in self.tables:

            raise ValueError("Invalid table name: {}".format(table_name))

        assert self.conn is not None, "Connection failure for add_entry"
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT update_history FROM {} WHERE id = ?".format(table_name), (entry_id,)
        )
        result = cursor.fetchone()

        if not result:
            return False

        # update history
        data["update_history"] = self._update_history(result["update_history"])
        data["last_updated"] = datetime.now().isoformat()

        # build sql
        set_clause = ", ".join(["{} = ?".format(k) for k in data.keys()])
        sql = "UPDATE {} SET {} WHERE id = ?".format(table_name, set_clause)

        cursor.execute(sql, list(data.values()) + [entry_id])
        self.conn.commit()

        return cursor.rowcount > 0

    def search_entries(
        self, table_name: str, pattern: str, field: tp.Optional[str] = None
    ) -> tp.List[tp.Dict[str, tp.Any]]:
        """Search entries using regrex pattern."""

        # keeps linter happy
        assert (
            self.tables is not None
        ), "self.tables cannot be None, initialization must have failed"

        if table_name not in self.tables:

            raise ValueError("Invalid table name: {}".format(table_name))

        assert self.conn is not None, "Connection failure for search_entries"

        cursor = self.conn.cursor()

        if field:

            cursor.execute(f"SELECT * FROM {table_name}")
            results = cursor.fetchall()
            filtered_results = []

            for row in results:

                if (
                    field in row.keys()
                    and row[field]
                    and re.search(pattern, str(row[field]), re.IGNORECASE)
                ):

                    filtered_results.append(dict(row))

            return filtered_results

        else:

            # search all text fields
            cursor.execute(f"SELECT * FROM {table_name}")
            results = cursor.fetchall()
            filtered_results = []

            for row in results:

                row_dict = dict(row)

                for value in row_dict.values():

                    if (
                        value
                        and isinstance(value, str)
                        and re.search(pattern, value, re.IGNORECASE)
                    ):

                        filtered_results.append(row_dict)

                        break

            return filtered_results

    def get_entry_by_id(
        self, table_name: str, entry_id: str
    ) -> tp.Optional[tp.Dict[str, tp.Any]]:
        """Get a specific entry by id."""

        assert (
            self.conn is not None
        ), "Issue with connection when calling get_entry_by_id"
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (entry_id,))
        result = cursor.fetchone()

        return dict(result) if result else None

    def list_entries(
        self, table_name: str, limit: tp.Optional[int] = None
    ) -> tp.List[tp.Dict[str, tp.Any]]:
        """List all entries in a table"""

        assert self.conn is not None, "Issue with connection when calling list_entries"

        cursor = self.conn.cursor()

        sql = f"SELECT * FROM {table_name} ORDER BY date_added DESC"

        if limit:

            sql += f" LIMIT {limit}"

        cursor.execute(sql)

        results = cursor.fetchall()

        return [dict(row) for row in results]

    def delete_entry(self, table_name: str, entry_id: str) -> bool:
        """Delete an entry by ID."""

        assert self.conn is not None, "Issue with connection to db from delete_entry"
        cursor = self.conn.cursor()

        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (entry_id,))

        self.conn.commit()

        return cursor.rowcount > 0

    def backup_database(self) -> str:
        """Create a backup for database"""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"db_backup_{timestamp}.sqlite"

        shutil.copy2(self.db_path, backup_path)

        return str(backup_path)

    def import_from_json(self, table_name: str, json_file: str) -> int:
        """Import entries from JSON file."""

        with open(json_file, "r") as f:

            data = json.load(f)

        count = 0

        for entry in data:

            try:

                self.add_entry(table_name, entry)

            except Exception as e:

                print(f"Error importing entry: {e}")

        return count

    def export_to_json(self, table_name: str, output_file: str) -> int:
        """Export table entries to json file"""
        entries = self.list_entries(table_name)

        with open(output_file, "w") as f:

            json.dump(entries, f, indent=2, default=str)

        return len(entries)

    def close(self):
        """Close database connection."""

        if self.conn:
            self.conn.close()
