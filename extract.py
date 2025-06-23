import subprocess
import sys
import argparse
import re
import json
import os  # disable pagers

# Clean backspace formatting
def clean_text(text: str) -> str:
    out = []
    i = 0
    while i < len(text):
        if i + 1 < len(text) and text[i+1] == '\x08':
            i += 2
        else:
            out.append(text[i])
            i += 1
    return ''.join(out)

# Invoke help: docker uses --help, others -h
def get_help(cmd_list):
    env = dict(os.environ, PAGER='cat', MANPAGER='cat')
    flag = '--help' if cmd_list[0] == 'docker' else '-h'
    try:
        raw = subprocess.check_output(
            cmd_list + [flag], stderr=subprocess.STDOUT, text=True, env=env
        )
    except subprocess.CalledProcessError as e:
        raw = e.output or ''
    except FileNotFoundError:
        print(f"Error: command not found: {' '.join(cmd_list)}", file=sys.stderr)
        sys.exit(1)
    return clean_text(raw)

# Parse options: capture inline and wrapped descriptions
WRAP_THRESHOLD = 20

def parse_options(help_text: str):
    """
    Scan every indented flag line, split flags/help on two+ spaces,
    and wrap descriptions when missing, unbalanced, or too long.
    """
    opts = []
    seen = set()
    lines = help_text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r'^\s+(-{1,2}\S.*)$', line)
        if not m:
            continue
        entry = m.group(1).rstrip(',')
        # split flags and inline help
        parts = re.split(r'\s{2,}', entry, maxsplit=1)
        flags_part = parts[0]
        desc = parts[1].strip() if len(parts) > 1 else ''
        # wrap when necessary
        need_wrap = (
            not desc or
            desc.count('(') > desc.count(')') or
            len(desc) > WRAP_THRESHOLD
        )
        if need_wrap and i + 1 < len(lines):
            wrap_lines = []
            j = i + 1
            while j < len(lines) and lines[j].startswith(' '):
                nxt = lines[j].strip()
                # stop at next flag or empty
                if not nxt or nxt.startswith('-'):
                    break
                wrap_lines.append(nxt)
                j += 1
            if wrap_lines:
                desc = (desc + ' ' + ' '.join(wrap_lines)).strip()
        # parse flags
        flags = [f.strip() for f in flags_part.split(',')]
        key = tuple(flags)
        if key and key not in seen:
            seen.add(key)
            opts.append({'flags': flags, 'help': desc})
    return opts

# Parse Docker-like subcommands (Common, Management, etc.)
def parse_subcommands(help_text: str):
    subs = []
    seen = set()
    lines = help_text.splitlines()
    i = 0
    while i < len(lines):
        if re.search(r'(?i)commands?:', lines[i]):
            i += 1
            while i < len(lines) and lines[i].startswith(' '):
                stripped = lines[i].lstrip()
                if not stripped or stripped.startswith('-') or stripped[0].isdigit():
                    i += 1
                    continue
                parts = re.split(r'\s{2,}', stripped, maxsplit=1)
                name = parts[0]
                help_desc = parts[1].strip() if len(parts) > 1 else ''
                if name not in seen:
                    seen.add(name)
                    subs.append({'name': name, 'help': help_desc})
                i += 1
            continue
        i += 1
    return subs

# Parse Git top-level subcommands via category sections
def parse_git_subcommands(help_text: str):
    subs = []
    seen = set()
    lines = help_text.splitlines()
    capture = False
    for line in lines:
        if line and not line.startswith(' ') and not re.match(r'(?i)^usage:', line):
            capture = True
            continue
        if capture and line.startswith('   '):
            stripped = line.strip()
            if stripped and not stripped.startswith('-'):
                parts = re.split(r'\s{2,}', stripped, maxsplit=1)
                name = parts[0]
                help_desc = parts[1].strip() if len(parts) > 1 else ''
                if name not in seen:
                    seen.add(name)
                    subs.append({'name': name, 'help': help_desc})
        if capture and not line:
            capture = False
    return subs

# Build tree: first level, use '...' placeholder for deeper children
def build_tree(cmd_list):
    help_text = get_help(cmd_list)
    lines = help_text.splitlines()
    # first usage line
    usage = ''
    for l in lines:
        if re.match(r'(?i)^usage:', l):
            usage = re.sub(r'(?i)^usage:\s*', '', l.strip())
            break
    options = parse_options(help_text)
    # choose subcommands parser
    if len(cmd_list) == 1 and cmd_list[0] == 'git':
        direct = parse_git_subcommands(help_text)
    else:
        direct = parse_subcommands(help_text)
    node = {
        'name': cmd_list[-1],
        'usage': usage,
        'options': options,
        'subcommands': []
    }
    for sub in direct:
        sub_help = get_help(cmd_list + [sub['name']])
        sub_usage = ''
        for l2 in sub_help.splitlines():
            if re.match(r'(?i)^usage:', l2):
                sub_usage = re.sub(r'(?i)^usage:\s*', '', l2.strip())
                break
        sub_opts = parse_options(sub_help)
        # detect deeper
        if len(cmd_list) == 1 and cmd_list[0] == 'git':
            deeper = bool(parse_git_subcommands(sub_help))
        else:
            deeper = bool(parse_subcommands(sub_help))
        node['subcommands'].append({
            'name': sub['name'],
            'usage': sub_usage,
            'options': sub_opts,
            'subcommands': ['...'] if deeper else []
        })
    return node

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Introspect CLI usage & options")
    parser.add_argument('-t', '--tool', required=True, help="Base command (docker, git, etc.)")
    parser.add_argument('-s', '--subcmd', nargs='+', default=[], help="Subcommand path")
    args = parser.parse_args()
    print(json.dumps(build_tree([args.tool] + args.subcmd), indent=2))
