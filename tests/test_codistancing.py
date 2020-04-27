from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase
from codistancing import Reformatter
import re
import statistics


class CodistancingTestCase(TestCase):
    def test_simple(self):
        self.assert_string_reformat(source="x = 42", expected="x    =    42")

    def test_brackets_distancing(self):
        self.assert_string_reformat(source="(x)", expected="(    x    )")

    def test_brackets_distancing_only_top_up(self):
        self.assert_string_reformat(source="(  x  )", expected="(    x    )")

    def test_brackets_distancing_remove_when_too_many(self):
        self.assert_string_reformat(
            source="(           x                        )", expected="(    x    )"
        )

    def test_do_not_add_EOL_SOL(self):
        self.assert_string_reformat(source="(\n" ")", expected="(\n" ")")

    def test_remove_EOL(self):
        self.assert_string_reformat(source="(  \n" ")", expected="(\n" ")")

    def test_do_not_remove_SOL(self):
        self.assert_string_reformat(
            source="    class    Foo", expected="    class    Foo"
        )

    def test_semicolon_before(self):
        self.assert_string_reformat(
            source="if    x:", expected="if    x    :",
        )

    def test_brackets__in_other_directions(self):
        self.assert_string_reformat(source="foo()", expected="foo    (    )")

    def test_additional_symbols(self):
        for symbol in ("/", "-", "+", "=", "*", "&", "|", "+="):
            self.assert_string_reformat(
                source=f"x{symbol}y", expected=f"x    {symbol}    y"
            )

    def test_string(self):
        self.assert_string_reformat(
            source="x = 'hello world!'", expected="x    =    'hello world!'"
        )

    def test_string2(self):
        self.assert_string_reformat(
            source='x = "hello world!"', expected='x    =    "hello world!"'
        )

    def test_bytes(self):
        self.assert_string_reformat(
            source='b"hello world!"', expected='b"hello world!"'
        )

    def test_dot(self):
        self.assert_string_reformat(source="str.format", expected="str    .    format")

    def test_line_distance(self):
        self.assert_string_reformat(
            source="x = 1\n" "y = 2",
            expected="x    =    1\n" "\n" "\n" "y    =    2",
            line_distance=True,
        )

    def test_empty_string(self):
        self.assert_string_reformat(
            source="", expected="",
        )

    def test_multiline_inner_block(self):
        self.assert_reformatting_from_data_file("multiline_inner_block.py")

    def test_multiline_outer_block(self):
        self.assert_reformatting_from_data_file("multiline_outer_block.py")

    def test_block_with_multiple_detents(self):
        self.assert_reformatting_from_data_file("block_with_multiple_detents.py")

    def test_newline_and_indents__with_line_distance(self):
        self.assert_reformatting_from_data_file(
            "newline_and_indents__with_line_distance.py", line_distance=True
        )

    def test_comments(self):
        self.assert_reformatting_from_data_file("comments.py", line_distance=True)

    def test_line_distance_after_docstring(self):
        self.assert_reformatting_from_data_file(
            "line_distance_after_docstring.py", line_distance=True
        )

    def test_no_more_than_two_line_distance(self):
        self.assert_reformatting_from_data_file(
            "no_more_than_two_line_distance.py", line_distance=True
        )

    def test_tabs(self):
        self.assert_reformatting_from_data_file("tabs.py")

    def test_reformat_file(self):
        source, expected = self._read_test_data_file("fibonacci.py")
        with TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            path = (workspace / "file.py").resolve()
            with open(path, "w") as fh:
                fh.write(source)
            Reformatter().reformat_file(path, line_distance=True, dry_run=False)
            with open(path, "r") as fh:
                output = fh.read()
        self.assertEqual(output, expected)

    def test_reformat_file__dry_run(self):
        source, expected = self._read_test_data_file("fibonacci.py")
        with TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            path = (workspace / "file.py").resolve()
            with open(path, "w") as fh:
                fh.write(source)
            Reformatter().reformat_file(path, line_distance=True, dry_run=True)
            with open(path, "r") as fh:
                output = fh.read()
        self.assertEqual(output, source)

    def test_data_science(self):
        reformatter = Reformatter(mean=4, std=1)
        actual = reformatter.reformat_string(
            "for i in range(5): "
            "for j in range(9): "
            "for k in range(3): "
            "print(i*j+k)"
        )
        blanks = re.split(r"\S+", actual)
        lens = [len(b) for b in blanks if b]
        self.assertEqual(statistics.median(lens), 4)
        self.assertNotEqual(set(lens), {4})

    def _read_test_data_file(self, test_file):
        with open(f"data/{test_file}", "r") as f:
            source, expected = f.read().split("# output\n")
        return source, expected

    def assert_string_reformat(self, source, expected, line_distance=False):
        actual = Reformatter().reformat_string(source, line_distance)
        self.assertEqual(expected.replace(" ", "▀"), actual.replace(" ", "▀"))

    def assert_reformatting_from_data_file(self, test_file, line_distance=False):
        source, expected = self._read_test_data_file(test_file)
        self.assert_string_reformat(
            source=source, expected=expected, line_distance=line_distance
        )
