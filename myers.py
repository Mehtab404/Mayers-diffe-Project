"""Generic Myers O(ND) shortest-edit-script implementation.

The script uses three operation names:

* ``equal``  - an item is present in both sequences
* ``delete`` - an item is removed from the first sequence
* ``insert`` - an item is added from the second sequence

The implementation is intentionally independent of files and strings so the
same algorithm can be used for lines and for characters.
"""

from dataclasses import dataclass
from typing import Generic, Iterable, List, Sequence, TypeVar


T = TypeVar("T")


@dataclass(frozen=True)
class Edit(Generic[T]):
    """One operation in a shortest edit script."""

    kind: str
    value: T

    def __post_init__(self) -> None:
        if self.kind not in {"equal", "delete", "insert"}:
            raise ValueError("kind must be equal, delete, or insert")


def _shortest_trace(a: Sequence[T], b: Sequence[T]):
    """Return Myers' V frontiers and the minimum number of edits.

    ``trace[d - 1]`` is the frontier from which the d-th edit is recovered.
    Storing one frontier per edit distance makes the backtracking pass simple;
    the forward search itself remains the standard O(ND) Myers search.
    """

    n, m = len(a), len(b)
    trace = []
    v = {0: 0}

    for d in range(n + m + 1):
        next_v = {}
        for k in range(-d, d + 1, 2):
            # Move down (insert from b) or right (delete from a), then follow
            # the diagonal as far as possible (the "snake").
            if k == -d or (k != d and v.get(k - 1, -1) <= v.get(k + 1, -1)):
                x = v.get(k + 1, 0)
            else:
                x = v.get(k - 1, 0) + 1
            y = x - k

            while x < n and y < m and a[x] == b[y]:
                x += 1
                y += 1

            next_v[k] = x
            if x >= n and y >= m:
                trace.append(next_v)
                return trace, d

        trace.append(next_v)
        v = next_v

    # The loop always reaches (n, m), but retaining an explicit failure makes
    # accidental changes to the algorithm easier to diagnose.
    raise RuntimeError("Myers search did not reach the end of the sequences")


def myers_diff(a: Sequence[T], b: Sequence[T]) -> List[Edit[T]]:
    """Return a minimal edit script transforming sequence ``a`` into ``b``.

    The number of ``delete`` plus ``insert`` operations is the Myers edit
    distance D. Equal items are included so callers can render or apply the
    alignment without recomputing it.
    """

    if not a and not b:
        return []

    trace, distance = _shortest_trace(a, b)
    if distance == 0:
        return [Edit("equal", item) for item in a]

    edits: List[Edit[T]] = []
    x, y = len(a), len(b)

    # Walk from the bottom-right of the edit graph to the origin. The
    # frontier at d-1 tells us which edge entered the d-th frontier.
    for d in range(distance, 0, -1):
        previous = trace[d - 1]
        k = x - y

        if k == -d or (k != d and previous.get(k - 1, -1) <= previous.get(k + 1, -1)):
            previous_k = k + 1       # insertion: move up
        else:
            previous_k = k - 1       # deletion: move left

        previous_x = previous[previous_k]
        previous_y = previous_x - previous_k

        # First consume the diagonal snake leading to this edit.
        while x > previous_x and y > previous_y:
            edits.append(Edit("equal", a[x - 1]))
            x -= 1
            y -= 1

        if x == previous_x:
            edits.append(Edit("insert", b[y - 1]))
            y -= 1
        else:
            edits.append(Edit("delete", a[x - 1]))
            x -= 1

    while x > 0 and y > 0:
        # Only a zero-edit snake can remain here.
        edits.append(Edit("equal", a[x - 1]))
        x -= 1
        y -= 1

    if x != 0 or y != 0:
        raise RuntimeError("Invalid Myers backtrack")

    edits.reverse()
    return edits


def edit_distance(script: Iterable[Edit[T]]) -> int:
    """Count inserted and deleted items in an edit script."""

    return sum(edit.kind != "equal" for edit in script)


def apply_script(a: Sequence[T], script: Iterable[Edit[T]]) -> List[T]:
    """Apply ``script`` to ``a`` and return the resulting sequence.

    Validation of consumed values catches malformed scripts and is useful in
    tests because it proves the alignment really transforms A into B.
    """

    result: List[T] = []
    a_index = 0

    for edit in script:
        if edit.kind == "equal":
            if a_index >= len(a) or a[a_index] != edit.value:
                raise ValueError("equal operation does not match input sequence")
            result.append(edit.value)
            a_index += 1
        elif edit.kind == "delete":
            if a_index >= len(a) or a[a_index] != edit.value:
                raise ValueError("delete operation does not match input sequence")
            a_index += 1
        else:
            result.append(edit.value)

    if a_index != len(a):
        raise ValueError("edit script did not consume the input sequence")
    return result
