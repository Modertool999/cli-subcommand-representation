import subprocess
import sys
import json
import argparse

# Default recursion depth to prevent very long runs
MAX_DEPTH = 2

def get_help(cmd_list):
    """
    Run the tool's help command and return its output.
    cmd_list must be the command contained in a list, ex. [git]
    """
    try:
        return subprocess.check_output(
            cmd_list + ['--help'],
            stderr=subprocess.STDOUT,
            text=True
        )
    except subprocess.CalledProcessError as e:
        # some tools return non-zero when printing help
        return e.output or ''
    except FileNotFoundError:
        print(f"Error: command not found: {' '.join(cmd_list)}", file=sys.stderr)
        sys.exit(1)