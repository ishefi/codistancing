#!/usr/bin/env python
import tokenize
from argparse import ArgumentParser
from io import BytesIO


def reformat_string(contents: str, line_distance: bool=False) -> str:
    """Formats string and adds social distancing spaces.

    :param contents: String to
    :param line_distance: If True - adds 4 lines of space between every two
                          consecutive lines.
    :return: Formatted string.

    >>> format_string('if x == y:\n    print("hello!")')
    if     x    ==    y    :
        print    (    "hello!"    )
    """
    return _reformat(BytesIO(contents.encode()), line_distance)


def _reformat(contents, line_distance):
    all_tokens = list(tokenize.tokenize(contents.readline))
    output = ''
    curr_indent = 0
    for i, token in enumerate(all_tokens):
        next_token = all_tokens[i + 1]
        if next_token.type == tokenize.ENDMARKER:
            break
        if token.type == tokenize.ENCODING:
            continue
        output += token.string
        # no spaces before new line
        if _is_newline(next_token):
            continue
        elif token.type == tokenize.INDENT:
            continue
            # curr_indent = token.end[1]
        elif _is_newline(token):
            if next_token.type == tokenize.ENDMARKER:
                break
            if token.string != '\n':
                continue
            if line_distance:
                output += token.string * 4
            if next_token.type not in (tokenize.INDENT, tokenize.DEDENT):
                output += ' ' * next_token.start[1]
        # make sure indentation matches original
        elif token.type == tokenize.DEDENT:
            if not next_token.type in (tokenize.INDENT, tokenize.DEDENT):
                # output += ' ' * token.end[1]
                curr_indent = token.start[1]
                output += ' ' * curr_indent
        # code distance!
        else:
            output += '    '
    return output

# def _intetation(token, next_token):
#     # # we will deal with this in the next token
#     # if next_token.type in (tokenize.INDENT, tokenize.DEDENT):
#     #     return ''


def _is_newline(token: tokenize.TokenInfo) -> bool:
    return token.exact_type in (tokenize.NEWLINE, tokenize.NL)


def reformat_file(dst: str, line_distance: bool, dry_run: bool) -> None:
    with open(dst, 'rb') as f:
        output = _reformat(f, line_distance)

    if not dry_run:
        with open(dst, 'w') as f:
            f.write(output)


def main():
    parser = ArgumentParser(description="The annoying (yet disease free) code "
                                        "formatter.")
    parser.add_argument("-l", "--line", action="store_true",
                        help="Include distancing between lines")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("FILES", nargs="*", default=[],
                        help="Files to reformat (in place)")
    source.add_argument("-c", "--code",
                        help="Format the code passed in as a string.")
    parser.add_argument("-d", "--dry-run", action="store_true",
                        help="Do nothing. Really nothing.")
    args = parser.parse_args()

    if args.code:
        output = reformat_string(args.string, line_distance=args.line)
        print("Output:")
        print("==============================")
        print(output)
        print("==============================")
    else:
        for f in args.FILES:
            print(f"Formatting {f}...")
            reformat_file(f, line_distance=args.line, dry_run=args.dry_run)
        print("Done!")


if __name__ == "__main__":
    main()
