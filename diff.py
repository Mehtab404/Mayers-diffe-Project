"""Provisional command-line frontend for the Myers diff assignment.

Usage:
    python diff.py FILE_A FILE_B             # combined line + character diff (default)
    python diff.py --lines-only FILE_A FILE_B # Part A line diff only
    python diff.py --chars FILE_A FILE_B      # explicit combined output
    python diff.py --chars --ansi FILE_A FILE_B

The official assignment output format can be adopted by changing the renderer
functions here; the Myers algorithm itself lives in myers.py.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

from myers import Edit, myers_diff


OLD_MARK_OPEN = "{-"
OLD_MARK_CLOSE = "-}"
NEW_MARK_OPEN = "{+"
NEW_MARK_CLOSE = "+}"
ANSI_RED = "\033[31m"
ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"


def read_lines(path: str) -> List[str]:
    """Read UTF-8 text as logical lines, normalising CRLF/CR to LF."""

    with open(path, "r", encoding="utf-8", newline=None) as handle:
        return handle.read().splitlines()


def character_highlight(old: str, new: str, ansi: bool = False) -> Tuple[str, str]:
    """Highlight only changed character runs in a pair of changed lines."""

    script = myers_diff(list(old), list(new))
    old_parts: List[str] = []
    new_parts: List[str] = []
    changed_old: List[str] = []
    changed_new: List[str] = []

    def flush_changed() -> None:
        if not changed_old and not changed_new:
            return
        old_text = "".join(changed_old)
        new_text = "".join(changed_new)
        if ansi:
            if old_text:
                old_parts.extend((ANSI_RED, old_text, ANSI_RESET))
            if new_text:
                new_parts.extend((ANSI_GREEN, new_text, ANSI_RESET))
        else:
            if old_text:
                old_parts.extend((OLD_MARK_OPEN, old_text, OLD_MARK_CLOSE))
            if new_text:
                new_parts.extend((NEW_MARK_OPEN, new_text, NEW_MARK_CLOSE))
        changed_old.clear()
        changed_new.clear()

    for edit in script:
        if edit.kind == "equal":
            flush_changed()
            old_parts.append(edit.value)
            new_parts.append(edit.value)
        elif edit.kind == "delete":
            changed_old.append(edit.value)
        else:
            changed_new.append(edit.value)
    flush_changed()
    return "".join(old_parts), "".join(new_parts)


def render_line_diff(script: Sequence[Edit[str]], chars: bool = True, ansi: bool = False) -> str:
    """Render a line script using `` ``, ``-``, and ``+`` prefixes."""

    output: List[str] = []
    index = 0
    while index < len(script):
        edit = script[index]
        if edit.kind == "equal":
            output.append(" " + edit.value + "\n")
            index += 1
            continue

        # A contiguous delete/insert block is a changed-line block. Pairing
        # entries lets Part B highlight characters without changing Part A's
        # line-level edit decisions.
        deleted: List[str] = []
        inserted: List[str] = []
        while index < len(script) and script[index].kind != "equal":
            if script[index].kind == "delete":
                deleted.append(script[index].value)
            else:
                inserted.append(script[index].value)
            index += 1

        pairs = min(len(deleted), len(inserted)) if chars else 0
        for pair_index in range(pairs):
            old_line, new_line = character_highlight(
                deleted[pair_index], inserted[pair_index], ansi=ansi
            )
            output.append("-" + old_line + "\n")
            output.append("+" + new_line + "\n")
        for line in deleted[pairs:]:
            output.append("-" + line + "\n")
        for line in inserted[pairs:]:
            output.append("+" + line + "\n")

    return "".join(output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Minimal Myers line diff")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--chars", dest="chars", action="store_true", help="highlight changed characters (default)")
    group.add_argument("--lines-only", dest="chars", action="store_false", help="show only the line-level diff")
    parser.set_defaults(chars=True)
    parser.add_argument("--ansi", action="store_true", help="use terminal colors for Part B highlights")
    parser.add_argument("file_a", help="original file")
    parser.add_argument("file_b", help="updated file")
    return parser


def main(argv: Sequence[str] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        lines_a = read_lines(args.file_a)
        lines_b = read_lines(args.file_b)
    except (OSError, UnicodeError) as error:
        print("diff.py: {}".format(error), file=sys.stderr)
        return 2

    script = myers_diff(lines_a, lines_b)
    sys.stdout.write(render_line_diff(script, chars=args.chars, ansi=args.ansi))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
