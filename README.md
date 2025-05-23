# CLI Introspector

A simple Python script that lists a command-line tool’s options and subcommands in JSON.

## Requirements

* Python 3.6+

## Quick Start

1. Save `introspect.py` and make it executable:

   ```bash
   chmod +x introspect.py
   ```
2. Run it:

   ```bash
   # Top-level view of docker
   ./introspect.py -t docker -d 1

   # Inspect git push
   ./introspect.py -t git -s push -d 1
   ```

### Flags

* `-t TOOL`, `--tool TOOL`   Command to inspect (e.g. docker, git)
* `-s SUBCMD…`, `--subcmd SUBCMD…`   Subcommands under TOOL (e.g. push, "remote add")
* `-d N`, `--depth N`   Levels to explore (default: 2)
