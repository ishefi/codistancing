from unittest import TestCase
from codistancing import reformat_string


class CodistancingTestCase(TestCase):
    def test_simple(self):
        self.assert_string_format(
            source="x = 42",
            expected="x    =    42"
        )

    def test_brackets_distancing(self):
        self.assert_string_format(
            source="(x)",
            expected="(    x    )"
        )

    def test_brackets_distancing_only_top_up(self):
        self.assert_string_format(
            source="(  x  )",
            expected="(    x    )"
        )

    def test_brackets_distancing_remove_when_too_many(self):
        self.assert_string_format(
            source="(           x                        )",
            expected="(    x    )"
        )

    def test_do_not_add_EOL_SOL(self):
        self.assert_string_format(
            source="(\n"
                   ")",
            expected="(\n"
                     ")"
        )

    def test_remove_EOL(self):
        self.assert_string_format(
            source="(  \n"
                   ")",
            expected="(\n"
                     ")"
        )

    def test_do_not_remove_SOL(self):
        self.assert_string_format(
            source="    class    Foo",
            expected="    class    Foo"
        )

    def test_semicolon_before(self):
        self.assert_string_format(
            source="if    x:",
            expected="if    x    :",
        )

    def test_brackets__in_other_directions(self):
        self.assert_string_format(
            source="foo()",
            expected="foo    (    )"
        )

    def test_additional_symbols(self):
        for symbol in ('/', '-', '+', '=', '*', '&', '|', '+='):
            self.assert_string_format(
                source=f"x{symbol}y",
                expected=f"x    {symbol}    y"
            )

    def test_string(self):
        self.assert_string_format(
            source="x = 'hello world!'",
            expected="x    =    'hello world!'"
        )

    def test_string2(self):
        self.assert_string_format(
            source='x = "hello world!"',
            expected='x    =    "hello world!"'
        )

    def test_bytes(self):
        self.assert_string_format(
            source='b"hello world!"',
            expected='b"hello world!"'
        )

    def test_dot(self):
        self.assert_string_format(
            source='str.format',
            expected='str    .    format'
        )

    def test_line_distance(self):
        self.assert_string_format(
            source="x = 1\ny = 2",
            expected="x    =    1\n\n\n\n\ny    =    2",
            line_distance=True
        )

    def test_empty_string(self):
        self.assert_string_format(
            source="",
            expected="",
        )

    def test_some_piece_of_code(self):
        self.assert_string_format(source="""
if (a + b) > 2:
    if b < a:
        print("hello world!")
    else:
        print(str.format("b <= a"))
else:
    exit(0)
""",
                                  expected="""
if    (    a    +    b    )    >    2    :
    if    b    <    a    :
        print    (    "hello world!"    )
    else    :
        print    (    str    .    format    (    "b <= a"    )    )
else    :
    exit    (    0    )
"""
        )

    def test_multiline_block(self):
        self.assert_string_format(
            source="""
if True:
    x = 1
    y = 2"""
,
            expected="""
if    True    :
    x    =    1
    y    =    2""",
        )

    def test_big_ending_block(self):
        self.assert_string_format(
            source="""
        if x:
            pass
        x = False
        y = True
        z = "oh no"
""",
            expected="""
        if    x    :
            pass
        x    =    False
        y    =    True
        z    =    "oh no"
"""

        )

    def test_block_multiple_detents(self):
        self.assert_string_format(
            source="""
# empty line
    if True:
        if False:
            pass
    # comment
    if True:
        pass
""",
            expected="""
# empty line
    if    True    :
        if    False    :
            pass
    # comment
    if    True    :
        pass
"""
        )

    def assert_string_format(self, source, expected, line_distance=False):
        actual = reformat_string(source, line_distance)
        self.assertEqual(expected.replace(' ', '▀'), actual.replace(' ', '▀'))

