# Tasks

## Prep
- [ ] Re-read T2 notes on Myers' O(ND) algorithm (edit graph, k-diagonals, V array, snakes)
- [x] Confirm language choice (Python)

## Part A: line diff
- [x] Read files A and B into lists of lines (handle CRLF, trailing newline, UTF-8)
- [x] Implement Myers forward search (find D)
- [x] Add backtracking to recover the edit script (keep / delete / insert)
- [x] Print the diff (provisional format: ` ` keep, `-` delete, `+` insert)
- [x] Create small test files and sample pairs: identical, empty, insertion, deletion, replacement, and reorder cases
- [x] Unit tests: edit count is minimal and applying the script rebuilds B

## Part B: character highlights
- [x] Pair deleted/inserted lines that belong to the same change
- [x] Run Myers on characters of each pair
- [x] Mark the changed character ranges in the output with `{-…-}` and `{+…+}` (for example, `-80{-0-}0` and `+80{+8+}0`)
- [x] Add optional ANSI color output with `--ansi`

## When the tool arrives (weekend)
- [ ] Read the official input/output spec and adapt the output code
- [ ] Run the official public tests locally
- [ ] Check performance on large files (consider linear-space variant if needed)
- [ ] Submit for grading
