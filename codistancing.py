#!/usr/bin/env python
import sys
import tokenize
from argparse import ArgumentParser
from io import BytesIO


def reformat_string(contents: str, line_distance: bool=False) -> str:
    """Reormats string and adds social distancing spaces.

    :param contents: String to reformat.
    :param line_distance: If True - adds 4 lines of space between every two
                          consecutive lines.
    :return: Formatted string.

    >>> reformat_string('if x == y:\n    print("hello!")')
    if     x    ==    y    :
        print    (    "hello!"    )
    """
    return _reformat(BytesIO(contents.encode()), line_distance)


def _reformat(contents, line_distance):
    all_tokens = list(tokenize.tokenize(contents.readline))
    output = ''
    for i, token in enumerate(all_tokens):
        next_token = all_tokens[i + 1]
        spaces = True
        if next_token.type == tokenize.ENDMARKER:
            break
        if not _should_add_token(token, next_token, line_distance):
            continue

        output += token.string

        # we will take care of padding next iteration
        if _is_newline(next_token):
            continue
        if _is_newline(token):
            if line_distance:
                output += token.string * 2
            spaces = False
        if (indent := _get_indent(token, next_token)):
            output += indent
            continue
        elif _is_indent(token):
            continue
        elif spaces:
            output += '    '
    return output

def _should_add_token(token, next_token, line_distance):
    if token.type == tokenize.ENCODING:
        return False
    if line_distance and _is_newline(token) and _is_newline(next_token):
        return False
    return True

def _is_newline(token: tokenize.TokenInfo) -> bool:
    return token.exact_type in (tokenize.NEWLINE, tokenize.NL)

def _is_indent(token):
    return token.exact_type in (tokenize.INDENT, tokenize.DEDENT)

def _get_indent(token, next_token):
    if _is_indent(next_token):
        return ""
    if token.exact_type == tokenize.DEDENT:
        return " " * token.end[1]
    elif _is_newline(token):
        return " " * next_token.start[1]
    return ""



def reformat_file(dst: str, line_distance: bool, dry_run: bool) -> None:
    """Reformats file by adding social-distancing spaces.
    Changes are done in-place.

    :param dst: Location of file to reformat.
    :param line_distance: If True - adds 4 lines of space between every two
                          consecutive lines.
    :param dry_run: If True - does not write changes back.
    """
    with open(dst, "rb") as f:
        output = _reformat(f, line_distance)

    if not dry_run:
        with open(dst, "w") as f:
            f.write(output)


def main():
    parser = ArgumentParser(description="The annoying (yet disease free) code "
                                        "formatter.")
    parser.add_argument("-l", "--line", action="store_true",
                        help="Include distancing between lines")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("FILE", nargs="*", default=[],
                        help="Files to reformat (in place)")
    source.add_argument("-c", "--code",
                        help="Format the code passed in as a string.")
    parser.add_argument("-d", "--dry-run", action="store_true",
                        help="Do nothing. Really nothing.")
    args = parser.parse_args()

    if args.code:
        output = reformat_string(args.string, line_distance=args.line)
        print(output, file=sys.stderr)
    else:
        for f in args.FILE:
            print(f"Formatting {f}...", file=sys.stderr)
            reformat_file(f, line_distance=args.line, dry_run=args.dry_run)
        print("Done!", file=sys.stderr)


if __name__ == "__main__":
    main()
