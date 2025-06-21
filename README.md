# CLI Tool Representation

A Python script that introspects any CLI’s usage, flags, and subcommands and outputs a JSON tree.

## Quick Start
```bash
# Docker top-level overview
python3 extract.py -t docker

# Git push details (with placeholders for deeper levels)
python3 extract.py -t git -s push

```
Note: subcommands of sucommands are displayed as '...' if they exist to avoid extenisve recursion