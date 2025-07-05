# Plegma: Keeping track of signatures, tags, and contacts

Writen for my own personal file system organization. I mainly focus on keeping a record of my tags and signatures (as defined by denote emacs). Since people and entities will be part of the signatures, I have also created tables in the database to contain their contact information.

I wanted this to be lightweight, simple, and flexible. If other cli tools can do things better then that feature will not be included here.

## Quick Start

Assume the working directoy is the root directory.

### Install and setup

Clone this repo, then

```shell

    chmod +x src/plegma.py src/backup_scheduler.py

```

### Add first signature

```shell

    python plegma.py add signatures --interactive

```

### Search by pattern

```shell

    python plegma.py search signatures "marketing"
    python plegma.py get signatures si12345678

```

### Set up auto backups

```shell

    # Add to crontab for daily backups
    0 2 * * * ./src/backup_scheduler.py --backup

```

## Usage Examples

### Adding entries interactively

```shell

    python3 plegma.py add tags --interactive
    python3 plegma.py add persons --interactive

```

### Adding entries from json

```shell

    python plegma.py add tags --json example_tags.json
    python plegma.py add persons --json example_persons.json

```

### Search signatures by regex pattern

```shell

    # Find all signatures containing "john"
    python plegma.py search signatures "john"

    # Find signatures in a specific field
    python plegma.py search signatures "marketing" --field description

```

### Get specific entry by id

```shell

    python plegma.py get signatures si12345678

```

### List all entries

```shell

    python plegma.py list signatures
    python plegma.py list signatures --limit 10

```

### Signature look up

```shell

    # Find what signature ID "si12345678" refers to
    python plegma.py get signatures si12345678

    # Search for signatures containing specific terms
    python plegma.py search signatures "marketing|client" --field description

```

### Add new signatures

```shell

    # Add a new signature for a persons
    python plegma.py add signatures --json '{"signature": "jane-doe-pm", "is_person": true, "description": "Jane Doe - Project Manager"}'

```

### Update existing entries

```shell

    # Update a signature description
    python plegma.py update signatures si12345678 --json '{"description": "Updated description"}'

```


## Backups and Plegmatance

### Create manual backup

```shell

    python plegma.py backup

```

### Automated backup with scheduler

```shell

    python backup_scheduler.py --backup
    python backup_scheduler.py --status

```

### Set up automated backups with cron

```shell

    # Edit crontab
    crontab -e

    # Add line to backup daily at 2 AM
    0 2 * * * /path/to/backup_scheduler.py --backup

    # Or backup every 6 hours
    0 */6 * * * /path/to/backup_scheduler.py --backup

```

## Import and Export

### Exporting data

```shell

    python plegma.py export signatures my_signatures.json
    python plegma.py export persons my_contacts.json

```

### Import data

```shell

    python plegma.py import signature my_signatures.json

```
