import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from diff import character_highlight, main, read_lines, render_line_diff  # noqa: E402
from myers import Edit, apply_script, edit_distance, myers_diff  # noqa: E402


class MyersCoreTests(unittest.TestCase):
    def assertTransforms(self, original, updated):
        script = myers_diff(original, updated)
        self.assertEqual(apply_script(original, script), list(updated))
        return script

    def test_identical_sequence_has_only_equal_operations(self):
        script = self.assertTransforms(list("abc"), list("abc"))
        self.assertEqual(script, [Edit("equal", c) for c in "abc"])
        self.assertEqual(edit_distance(script), 0)

    def test_empty_sequences_and_one_sided_changes(self):
        self.assertEqual(myers_diff([], []), [])
        inserted = self.assertTransforms([], list("abc"))
        removed = self.assertTransforms(list("abc"), [])
        self.assertEqual(edit_distance(inserted), 3)
        self.assertEqual(edit_distance(removed), 3)

    def test_replacement_uses_one_delete_and_one_insert(self):
        script = self.assertTransforms(list("cat"), list("cut"))
        self.assertEqual(edit_distance(script), 2)
        self.assertEqual([(e.kind, e.value) for e in script], [
            ("equal", "c"), ("delete", "a"), ("insert", "u"), ("equal", "t")
        ])

    def test_repeated_values_remain_minimal(self):
        script = self.assertTransforms(["a", "b", "a"], ["a", "a", "b"])
        self.assertEqual(edit_distance(script), 2)

    def test_small_exhaustive_cases_are_minimal(self):
        # For short binary strings, compare D with an independent recurrence.
        def expected_distance(a, b):
            if not a:
                return len(b)
            if not b:
                return len(a)
            if a[0] == b[0]:
                return expected_distance(a[1:], b[1:])
            return 1 + min(expected_distance(a[1:], b), expected_distance(a, b[1:]))

        values = ["", "a", "b", "aa", "ab", "ba", "bb"]
        for old in values:
            for new in values:
                script = self.assertTransforms(list(old), list(new))
                self.assertEqual(edit_distance(script), expected_distance(old, new))


class RendererTests(unittest.TestCase):
    def test_character_highlight_marks_only_changed_digits(self):
        old, new = character_highlight("8000", "8080")
        self.assertEqual(old, "80{-0-}0")
        self.assertEqual(new, "80{+8+}0")

    def test_character_highlight_handles_insertion_and_deletion(self):
        old, new = character_highlight("colour", "color")
        self.assertEqual(old, "colo{-u-}r")
        self.assertEqual(new, "color")

    def test_part_a_rendering(self):
        script = myers_diff(["same", "old"], ["same", "new"])
        self.assertEqual(render_line_diff(script, chars=False), " same\n-old\n+new\n")

    def test_read_lines_normalises_line_endings(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "mixed.txt"
            path.write_bytes("one\r\ntwo\rthree\n".encode("utf-8"))
            self.assertEqual(read_lines(str(path)), ["one", "two", "three"])

    def test_cli_part_b(self):
        with TemporaryDirectory() as directory:
            old_path = Path(directory) / "old.txt"
            new_path = Path(directory) / "new.txt"
            old_path.write_text("value=8000\n", encoding="utf-8", newline="")
            new_path.write_text("value=8080\n", encoding="utf-8", newline="")
            output = io.StringIO()
            with redirect_stdout(output):
                code = main([str(old_path), str(new_path)])
            self.assertEqual(code, 0)
            self.assertEqual(output.getvalue(), "-value=80{-0-}0\n+value=80{+8+}0\n")


if __name__ == "__main__":
    unittest.main()
