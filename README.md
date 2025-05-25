# CLI Tool Representation

A simple Python script that lists a command-line tool’s options and subcommands in JSON.

## Requirements

* Python 3.6+

## Quick Start


   ```bash
   # Top-level view of docker
   python3 extract.py -t docker -d 1

   # Inspect git push
   python3 extract.py -t git -s push -d 1
   ```

### Flags

* `-t TOOL`, `--tool TOOL`   Command to inspect (e.g. docker, git, etc.)
* `-s SUBCMD…`, `--subcmd SUBCMD…`   Subcommands under TOOL (e.g. push, build, etc.)
* `-d N`, `--depth N`   Levels to explore (default: 2)
