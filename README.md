# CLI Tool Representation

A simple Python script that introspects any CLI’s usage, flags, and subcommands, and outputs a structured JSON object.

## Requirements

- Python 3.6+

## Quick Start

```bash
# Top-level view of Docker
python3 extract.py -t docker -d 1

# Inspect Git push
python3 extract.py -t git -s push -d 1
```

### Arguments

- `-t, --tool TOOL`       Base command to inspect (e.g., `docker`, `git`)
- `-s, --subcmd SUBCMD…`  Optional subcommands under TOOL (e.g., `push`, `buildx`)
- `-d, --depth N`         Levels of subcommands to recurse (default: 2)

### Output

Prints a JSON object with keys:

- `name`: the command or subcommand name
- `usage`: the `Usage:` line from help text
- `options`: list of `{"flags": [...], "help": "..."}`
- `subcommands`: nested command objects (same structure)

**Example Output**

```json
{
  "name": "buildx",
  "usage": "Usage: docker buildx [OPTIONS] COMMAND [ARGS]...",
  "options": [
    { "flags": ["--builder string"], "help": "Override the builder instance" },
    { "flags": ["-D", "--debug"], "help": "Enable debug logging" }
  ],
  "subcommands": [ ... ]
}
```
