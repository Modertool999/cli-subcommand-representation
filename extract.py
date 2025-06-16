import subprocess
import sys
import argparse
import re



# Default recursion depth to prevent excessively deep recursion
MAX_DEPTH = 2

def clean_text(text: str) -> str:
    """
    Remove any <char><backspace> sequences from the text.
    This strips out Git’s backspace-based formatting.
    """
    out = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i+1] == '\x08':
            i += 2
        else:
            out.append(text[i])
            i += 1
    return ''.join(out)

def get_help(cmd_list):
    """
    Run cmd_list + ['--help'], capture stdout+stderr, strip formatting,
    and return clean help text.
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

def parse_options(help_text: str):
    """
    Return a list of dicts {'flags': [...], 'help': str}
    """
    opts = []
    for line in help_text.splitlines():
        stripped = line.lstrip()
        # filter out non-option lines and lone '-'
        if not stripped.startswith('-') or stripped == '-':
            continue
        # split on two or more spaces to separate flags and description
        parts = re.split(r'\s{2,}', stripped, maxsplit=1)
        flags_part = parts[0].rstrip(',')
        desc = parts[1].strip() if len(parts) > 1 else ''
        flags = [f.strip().rstrip(',') for f in flags_part.split(',') if len(f.strip()) > 1]
        if flags:
            opts.append({'flags': flags, 'help': desc})
    return opts

def parse_subcommands(help_text: str):
    """
    Return a list of dicts {'name': str, 'help': str}
    """
    subs = []
    lines = help_text.splitlines()
    in_section = False
    for line in lines:
        # detect Commands: or Available Commands:
        if re.search(r'(?i)commands?:', line):
            in_section = True
            continue
        if not in_section:
            continue
        # stop at next non-indented line
        if not line.startswith(' '):
            break
        stripped = line.lstrip()
        # skip flags or numbered lists
        if stripped.startswith('-') or stripped[0].isdigit():
            continue
        parts = re.split(r'\s{2,}', stripped, maxsplit=1)
        name = parts[0]
        help_desc = parts[1].strip() if len(parts) > 1 else ''
        subs.append({'name': name, 'help': help_desc})
    return subs

def build_tree(cmd_list, depth=0, max_depth=MAX_DEPTH):
    """
    Recursively build a dict representing the CLI structure,
    formatted similarly to argparse.
    """
    help_text = get_help(cmd_list)
    description = help_text.splitlines()[0].strip() if help_text else ''
    options = parse_options(help_text)
    subcommands = parse_subcommands(help_text)

    node = {
        'name': cmd_list[-1],
        'description': description,
        'options': options,
        'subcommands': []
    }

    if depth < max_depth:
        for sub in subcommands:
            subtree = build_tree(cmd_list + [sub['name']], depth + 1, max_depth)
            node['subcommands'].append(subtree)

    return node

def main():
    parser = argparse.ArgumentParser(
        description="Introspect a CLI tool's flags & subcommands"
    )
    parser.add_argument(
        '--tool', '-t',
        required=True,
        help="Base command to inspect (e.g. docker, git, pip)"
    )
    parser.add_argument(
        '--subcmd', '-s',
        nargs='+',
        default=[],
        help="Optional subcommand path under the base tool"
    )
    parser.add_argument(
        '--depth', '-d',
        type=int,
        default=MAX_DEPTH,
        help=f"How many levels of subcommands to explore (default {MAX_DEPTH})"
    )
    args = parser.parse_args()

    cmd_list = [args.tool] + args.subcmd
    tree = build_tree(cmd_list, depth=0, max_depth=args.depth)
    # print Python dict representation rather than JSON
    print(tree)

if __name__ == '__main__':
    main()
