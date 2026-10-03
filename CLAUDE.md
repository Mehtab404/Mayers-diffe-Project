# CLAUDE.md

## Project
Command-line diff tool built on Myers' O(ND) algorithm.

- Part A: line diff only with `--lines-only`.
- Part B: the default combined diff, plus character-level highlights for changed lines (e.g. `8000` -> `8080` becomes `-80{-0-}0` and `+80{+8+}0`).

## Language
Python 3 (allowed: Python, Java, C++). Standard library only.

## Rules
- Diff must be minimal: fewest possible deletions + insertions.
- Must handle real files: .txt, .py, .c, .cpp, .java, .ts (from real open-source commits).
- Input/output format is NOT final yet; official spec and test tool arrive this weekend. Keep output code isolated so it's easy to change.
- Watch for: empty files, missing trailing newline, CRLF vs LF, tabs/trailing whitespace, non-ASCII/UTF-8.

## Layout
```
myers.py        # Myers O(ND) core: generic over any sequence (lines or chars)
diff.py         # CLI entry point, Part A + Part B output
tests/          # small hand-made test file pairs (a.txt / b.txt)
```

## Usage (provisional)
```
python diff.py fileA fileB                 # combined line + character diff (default)
python diff.py --lines-only fileA fileB   # Part A line diff only
python diff.py --chars fileA fileB        # explicit combined output
```

## Testing
- Verify minimality: number of edits == Myers' D.
- Verify correctness: applying the edit script to A reproduces B exactly.
- Run: `python -m unittest discover tests`
