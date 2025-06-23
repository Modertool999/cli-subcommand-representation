# CLI Tool Representation

A Python script that prints out CLI’s usage, flags, and subcommands

## Usage
```bash
# Docker top-level overview
python3 extract.py -t COMMAND_NAME -s SUBCOMMAND_NAME
```

Note: the -s SUBCOMMAND_NAME part is optional 


## Examples
```bash
# Docker top-level overview
python3 extract.py -t docker

# Git push details (with placeholders for deeper levels)
python3 extract.py -t git -s push

```
Note: subcommands of subcommands are displayed as '...' if they exist to avoid extenisve recursion