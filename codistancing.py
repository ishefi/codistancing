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


indent_type = None
def _reformat(contents, line_distance):
    global indent_type
    indent_type = ''
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
            if not indent_type:
                indent_type = token.string[0]
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
        return indent_type * token.end[1]
    elif _is_newline(token):
        return indent_type * next_token.start[1]
    return ""



def reformat_file(dst: str, line_distance: bool, dry_run: bool) -> bool:
    """Reformats file by adding social-distancing spaces.
    Changes are done in-place.

    :param dst: Location of file to reformat.
    :param line_distance: If True - adds 4 lines of space between every two
                          consecutive lines.
    :param dry_run: If True - does not write changes back.

    :return: True if there is diff between source and reformatted file, False
             otherwise.

    """
    with open(dst, "rb") as f:
        output = _reformat(f, line_distance)

    with open(dst, "r") as f:
        source = f.read()

    change = output != source


    if change:
        if dry_run:
            print_stderr(f"would reformat {dst}")
        else:
            with open(dst, "w") as f:
                f.write(output)
            print_stderr(f"reformatted {dst}")
        return True
    else:
        return False


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
        output = reformat_string(args.code, line_distance=args.line)
        print_stderr(output)
    else:
        status = [
            reformat_file(f, line_distance=args.line, dry_run=args.dry_run)
            for f in args.FILE
        ]
        log = []
        reformatted = status.count(True)
        time_marker = "would be " if args.dry_run else ""
        if reformatted:
            log.append(f"{reformatted} files {time_marker}reformatted")
        untouched = status.count(False)
        if untouched:
            log.append(f"{untouched} files {time_marker}left unchanged")

        print_stderr(f"{', '.join(log)}.")


def print_stderr(string):
    print(string, file=sys.stderr)


if __name__ == "__main__":
    main()
