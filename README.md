# CLI Tool Representation

A simple Python script that introspects any CLI’s usage, flags, and subcommands, and outputs a structured JSON object.

## Requirements

- Python 3.6+

## Quick Start

```bash
# Top-level view of Docker (shows two levels)


# Inspect Git push (and placeholder for deeper commands)
python3 extract.py -t git -s push
```

### Arguments

- `-t, --tool TOOL`       Base command to inspect (e.g., `docker`, `git`)
- `-s, --subcmd SUBCMD…`  Optional subcommands under TOOL (e.g., `push`, `buildx`)

### Behavior

1. **First-level** subcommands are fully expanded.
2. **Second-level** subcommands show a `"..."` placeholder if deeper children exist, otherwise an empty list.

### Output

Prints a JSON object with:

- `name`: command or subcommand name
- `description`: first line of help text
- `options`: array of `{ "flags": [...], "help": "..." }`
- `subcommands`: array of nested command objects (same structure), with `"..."` placeholders for further levels

**Example Output**

```json
{
  "name": "buildx",
  "description": "Build and extend with BuildKit",
  "options": [
    { "flags": ["--builder string"], "help": "Override the builder instance" },
    { "flags": ["-D", "--debug"],    "help": "Enable debug logging" }
  ],
  "subcommands": [
    {
      "name": "create",
      "description": "Create a new builder instance",
      "options": [ /* ... */ ],
      "subcommands": ["..."]
    },
    /* ... */
  ]
}
```
