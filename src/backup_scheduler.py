#!/usr/bin/env python3
"""
Automated Backup Script for Personal Database
Run this script with cron to automatically backup your database.
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add the directory containing the main script to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db_manager import DBManager, DBConfig


class BackupScheduler:
    def __init__(self, config: DBConfig, max_backups: int = 30):
        self.config = config
        self.db_path = Path(config.db_path)
        self.max_backups = max_backups
        self.backup_dir = Path(config.backup_path)
        self.backup_dir.mkdir(exist_ok=True)

    def create_backup(self) -> str:
        """Create a backup of the database."""
        db = DBManager(self.config)
        backup_path = db.backup_database()
        db.close()
        return backup_path

    def cleanup_old_backups(self):
        """Remove old backups, keeping only the most recent ones."""
        backup_files = list(self.backup_dir.glob("personal_db_backup_*.sqlite"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # Remove old backups
        for backup_file in backup_files[self.max_backups :]:
            backup_file.unlink()
            print(f"Removed old backup: {backup_file}")

    def run_backup(self):
        """Run the backup process."""
        try:
            # Check if database exists
            if not self.db_path.exists():
                print(f"Database not found: {self.db_path}")
                return False

            # Create backup
            backup_path = self.create_backup()
            print(f"Backup created: {backup_path}")

            # Cleanup old backups
            self.cleanup_old_backups()

            # Log the backup
            log_entry = (
                f"{datetime.now().isoformat()}: Backup created - {backup_path}\n"
            )
            with open(self.backup_dir / "backup_log.txt", "a") as f:
                f.write(log_entry)

            return True

        except Exception as e:
            error_msg = f"{datetime.now().isoformat()}: Backup failed - {str(e)}\n"
            with open(self.backup_dir / "backup_log.txt", "a") as f:
                f.write(error_msg)
            print(f"Backup failed: {e}")
            return False

    def get_backup_status(self):
        """Get information about recent backups."""
        backup_files = list(self.backup_dir.glob("personal_db_backup_*.sqlite"))
        backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        print(f"Total backups: {len(backup_files)}")
        print(f"Backup directory: {self.backup_dir.absolute()}")

        if backup_files:
            latest_backup = backup_files[0]
            backup_time = datetime.fromtimestamp(latest_backup.stat().st_mtime)
            print(f"Latest backup: {latest_backup.name}")
            print(f"Created: {backup_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Size: {latest_backup.stat().st_size / 1024:.2f} KB")
        else:
            print("No backups found")


def main():
    import argparse

    from plegma import DB_PATH, BACKUP_PATH, SCHEMA_PATH, PREFIX_PATH

    config = DBConfig(DB_PATH, BACKUP_PATH, SCHEMA_PATH, PREFIX_PATH)

    parser = argparse.ArgumentParser(description="Personal Database Backup Scheduler")
    parser.add_argument("--backup", action="store_true", help="Create a backup now")
    parser.add_argument("--status", action="store_true", help="Show backup status")
    parser.add_argument(
        "--max-backups", type=int, default=30, help="Maximum number of backups to keep"
    )
    parser.add_argument(
        "--db-path", default="personal_db.sqlite", help="Database file path"
    )

    args = parser.parse_args()

    scheduler = BackupScheduler(config, args.max_backups)

    if args.backup:
        success = scheduler.run_backup()
        sys.exit(0 if success else 1)
    elif args.status:
        scheduler.get_backup_status()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
