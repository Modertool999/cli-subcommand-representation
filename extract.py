import subprocess
import sys
import json
import argparse

# TODO: might need to change output from JSON depending on argparse output

# Default recursion depth to prevent excessively deep recursion
MAX_DEPTH = 2

def clean_text(text: str) -> str:
    """
    Remove any <char><backspace> sequences from the text
    This strips out Git’s backspace-based bold/underline formatting
    """
    out = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i+1] == '\x08':
            # skip both the character and the backspace
            i += 2
        else:
            out.append(text[i])
            i += 1
    return ''.join(out)

def get_help(cmd_list):
    """
    Run cmd_list + ['--help'], capture stdout+stderr, strip formatting,
    and return clean help text

    cmd_list is the tool with an optional subcommand as a string 
    contained within a list, ex. ['git'] or ['docker', 'build']
    """
    try:
        raw = subprocess.check_output(
            cmd_list + ['--help'],
            stderr=subprocess.STDOUT,
            text=True
        )
    except subprocess.CalledProcessError as e:
        raw = e.output or ''
    except FileNotFoundError:
        print(f"Error: command not found: {' '.join(cmd_list)}", file=sys.stderr)
        sys.exit(1)

    return clean_text(raw)

def parse_options(help_text):
    """
    Return a sorted list of unique tokens starting with '-' or '--'
    found anywhere in the help text
    """
    opts = set()
    for line in help_text.splitlines():
        for tok in line.strip().split():
            if tok.startswith('-') and not tok[1:].isdigit():
                opts.add(tok.rstrip(','))
    return sorted(opts)

def parse_subcommands(help_text):
    """
    Return a sorted list of subcommand names by scanning indented lines,
    ignoring any token that starts with '-' or a digit
    """
    found = set()
    for line in help_text.splitlines():
        if not line.startswith(' '):
            continue
        token = line.lstrip().split()[0]
        if token.startswith('-') or token[0].isdigit():
            continue
        found.add(token)
    return sorted(found)

def build_tree(cmd_list, depth=0, max_depth=MAX_DEPTH):
    """
    Recursively build a dict representing the CLI structure:
    {
      "name":       <command name>,
      "options":    [...],
      "subcommands": { <sub>: {same structure}, ... }
    }
    """
    name = cmd_list[-1]
    help_text = get_help(cmd_list)
    options = parse_options(help_text)
    subs    = parse_subcommands(help_text)

    node = {
        'name':       name,
        'options':    options,
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

def main():
    parser = argparse.ArgumentParser(
        description="Introspect a CLI tool's flags & subcommands"
    )
    parser.add_argument(
        '--tool','-t',
        required=True,
        help="Base command to inspect (e.g. docker, git, pip)"
    )
    parser.add_argument(
        '--subcmd','-s',
        nargs='+',
        default=[],
        help="Optional subcommand path under the base tool (e.g. 'push' or 'remote add')"
    )
    parser.add_argument(
        '--depth','-d',
        type=int,
        default=MAX_DEPTH,
        help=f"How many levels of subcommands to explore (default {MAX_DEPTH})"
    )
    args = parser.parse_args()

    cmd_list = [args.tool] + args.subcmd
    tree = build_tree(cmd_list, depth=0, max_depth=args.depth)
    print(json.dumps(tree, indent=2))

if __name__ == '__main__':
    main()
