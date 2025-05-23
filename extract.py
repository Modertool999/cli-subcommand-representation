import subprocess
import sys
import json
import argparse

# Default recursion depth to prevent very long runs
MAX_DEPTH = 2

def get_help(cmd_list):
    """
    Run the tool's help command and return its output.
    cmd_list must be the command contained in a list, ex. ['git'] or ['docker', 'build']
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

def parse_subcommands(help_text):
    """
    Find subcommand names in indented sections of help_text
    Ignores options (starting with '-') and numbered lists
    """
    # commands already seen
    found = set()
    for line in help_text.splitlines():
        # ignore non-indents
        if not line.startswith(' '):
            continue
        text = line.lstrip()
        if not text:
            continue
        token = text.split()[0]
        if token.startswith('-') or token[0].isdigit():
            continue
        found.add(token)
    return sorted(found)

def parse_options(help_text):
    """
    Find all options (flags) in the help text by looking for tokens that start
    with '-' or '--'. Strips trailing commas.
    """
    opts = set()
    for line in help_text.splitlines():
        # split on whitespace, examine each token
        for tok in line.strip().split():
            if tok.startswith('-') and not tok[1:].isdigit():
                opts.add(tok.rstrip(','))
    return sorted(opts)

def build_tree(cmd_list, depth=0, max_depth=MAX_DEPTH):
    """
    Recursively build a dict representing:
      {
        name:       <command name>,
        options:    [...list of flags...],
        subcommands:{ <sub>: {same structure}, ... }
      }
    """
    name = cmd_list[-1]
    help_text = get_help(cmd_list)
    options = parse_options(help_text)
    subs    = parse_subcommands(help_text)

    node = {
        'name': name,
        'options': options,
        'subcommands': {}
    }

    if depth < max_depth:
        for sub in subs:
            node['subcommands'][sub] = build_tree(
                cmd_list + [sub],
                depth + 1,
                max_depth
            )
    return node