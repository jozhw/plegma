import json
import argparse

from .db_manager import DBManager

import typing as tp


def create_cli():
    """Create CLI"""

    parser = argparse.ArgumentParser(description="Personal Database CLI Tool")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new entry")
    add_parser.add_argument(
        "table",
        choices=[
            "tags",
            "person",
            "entity",
            "signature",
            "address",
            "email",
            "phone_number",
        ],
    )
    add_parser.add_argument(
        "--json", help="JSON string or file path containing entry data"
    )
    add_parser.add_argument(
        "--interactive", action="store_true", help="Interactive mode"
    )

    # Update command
    update_parser = subparsers.add_parser("update", help="Update an existing entry")
    update_parser.add_argument(
        "table",
        choices=[
            "tags",
            "person",
            "entity",
            "signature",
            "address",
            "email",
            "phone_number",
        ],
    )
    update_parser.add_argument("id", help="Entry ID to update")
    update_parser.add_argument(
        "--json", help="JSON string or file path containing update data"
    )

    # Search command
    search_parser = subparsers.add_parser("search", help="Search entries")
    search_parser.add_argument(
        "table",
        choices=[
            "tags",
            "person",
            "entity",
            "signature",
            "address",
            "email",
            "phone_number",
        ],
    )
    search_parser.add_argument("pattern", help="Regex pattern to search for")
    search_parser.add_argument("--field", help="Specific field to search in")

    # Get command
    get_parser = subparsers.add_parser("get", help="Get entry by ID")
    get_parser.add_argument(
        "table",
        choices=[
            "tags",
            "person",
            "entity",
            "signature",
            "address",
            "email",
            "phone_number",
        ],
    )
    get_parser.add_argument("id", help="Entry ID")

    # List command
    list_parser = subparsers.add_parser("list", help="List entries")
    list_parser.add_argument(
        "table",
        choices=[
            "tags",
            "person",
            "entity",
            "signature",
            "address",
            "email",
            "phone_number",
        ],
    )
    list_parser.add_argument("--limit", type=int, help="Limit number of results")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete an entry")
    delete_parser.add_argument(
        "table",
        choices=[
            "tags",
            "person",
            "entity",
            "signature",
            "address",
            "email",
            "phone_number",
        ],
    )
    delete_parser.add_argument("id", help="Entry ID to delete")

    # Backup command
    subparsers.add_parser("backup", help="Create database backup")

    # Import command
    import_parser = subparsers.add_parser("import", help="Import from JSON")
    import_parser.add_argument(
        "table",
        choices=[
            "tags",
            "person",
            "entity",
            "signature",
            "address",
            "email",
            "phone_number",
        ],
    )
    import_parser.add_argument("file", help="JSON file to import")

    # Export command
    export_parser = subparsers.add_parser("export", help="Export to JSON")
    export_parser.add_argument(
        "table",
        choices=[
            "tags",
            "person",
            "entity",
            "signature",
            "address",
            "email",
            "phone_number",
        ],
    )
    export_parser.add_argument("file", help="Output JSON file")

    return parser


def interactive_add(db: DBManager, table_name: str) -> tp.Dict[str, tp.Any]:
    """Interactive mode for adding entries."""
    data = {}

    # Define required fields for each table
    required_fields = {
        "tags": ["tag_name"],
        "person": ["first_name", "last_name"],
        "entity": ["entity_name"],
        "signature": ["signature"],
        "address": ["longitude", "latitude"],
        "email": ["email_address", "owner"],
        "phone_number": ["phone_number", "owner"],
    }

    optional_fields = {
        "tags": ["description"],
        "person": ["middle_name", "preferred_name", "description"],
        "entity": ["preferred_name", "description"],
        "signature": ["is_person", "is_entity", "description"],
        "address": ["apartment", "current_occupants", "past_occupants", "description"],
        "email": ["email_type", "is_active", "description"],
        "phone_number": [
            "country_code",
            "phone_number_type",
            "owner_history",
            "is_active",
            "description",
        ],
    }

    # Get required fields
    for field in required_fields.get(table_name, []):
        value = input(f"Enter {field.replace('_', ' ')}: ")
        if field in ["is_person", "is_entity", "is_active"]:
            data[field] = value.lower() in ["true", "1", "yes", "y"]
        elif field in ["country_code"]:
            data[field] = int(value) if value else 1
        else:
            data[field] = value

    # Get optional fields
    print("\nOptional fields (press Enter to skip):")
    for field in optional_fields.get(table_name, []):
        value = input(f"Enter {field.replace('_', ' ')}: ")
        if value:
            if field in ["is_person", "is_entity", "is_active"]:
                data[field] = value.lower() in ["true", "1", "yes", "y"]
            elif field in ["country_code"]:
                data[field] = int(value)
            else:
                data[field] = value

    return data


def format_output(data: tp.List[tp.Dict[str, tp.Any]]) -> str:
    """Format output for display."""
    if not data:
        return "No entries found."

    output = []
    for entry in data:
        output.append("=" * 50)
        for key, value in entry.items():
            if key == "update_history" and value:
                try:
                    history = json.loads(value)
                    output.append(f"{key}: {len(history)} updates")
                except:
                    output.append(f"{key}: {value}")
            else:
                output.append(f"{key}: {value}")
        output.append("")

    return "\n".join(output)
