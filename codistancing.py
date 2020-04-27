#!/usr/bin/env python
import sys
import tokenize
from argparse import ArgumentParser
from argparse import ArgumentDefaultsHelpFormatter
import random
from io import BytesIO


class Reformatter:
    def __init__(self, mean: int = 4, std: int = 0) -> None:
        self.indent_type = ""
        self.mean = mean
        self.std = std

    def reformat_string(self, contents: str, line_distance: bool = False) -> str:
        """Reormats string and adds social distancing spaces.

        :param contents: String to reformat.
        :param line_distance: If True - adds lines of space between every two
                              consecutive lines.
        :return: Formatted string.

        >>> reformat_string('if x == y:\n    print("hello!")')
        if     x    ==    y    :
            print    (    "hello!"    )
        """
        return self._reformat(BytesIO(contents.encode()), line_distance)

    def _reformat(self, contents, line_distance):
        all_tokens = list(tokenize.tokenize(contents.readline))
        output = ""
        for i, token in enumerate(all_tokens):
            next_token = all_tokens[i + 1]
            spaces = True
            if next_token.type == tokenize.ENDMARKER:
                break
            if not self._should_add_token(token, next_token, line_distance):
                continue

            output += token.string

            # we will take care of padding next iteration
            if self._is_newline(next_token):
                continue
            if self._is_newline(token):
                if line_distance:
                    output += token.string * 2
                spaces = False
            if (indent := self._get_indent(token, next_token)) :
                output += indent
                continue
            elif self._is_indent(token):
                if not self.indent_type:
                    self.indent_type = token.string[0]
                continue
            elif spaces:
                output += self._randup(" ")
        return output

    def _randup(self, unit: str) -> str:
        """Returns random (normally-distributed) number of copies of `unit`."""
        n = max(int(random.gauss(self.mean, self.std)), 1)
        return unit * n

    def _should_add_token(self, token, next_token, line_distance):
        if token.type == tokenize.ENCODING:
            return False
        if line_distance and self._is_newline(token) and self._is_newline(next_token):
            return False
        return True

    def _is_newline(self, token: tokenize.TokenInfo) -> bool:
        return token.exact_type in (tokenize.NEWLINE, tokenize.NL)

    def _is_indent(self, token: tokenize.TokenInfo) -> bool:
        return token.exact_type in (tokenize.INDENT, tokenize.DEDENT)

    def _get_indent(
        self, token: tokenize.TokenInfo, next_token: tokenize.TokenInfo
    ) -> str:
        if self._is_indent(next_token):
            return ""
        if token.exact_type == tokenize.DEDENT:
            return self.indent_type * token.end[1]
        elif self._is_newline(token):
            return self.indent_type * next_token.start[1]
        return ""

    def reformat_file(self, dst: str, line_distance: bool, dry_run: bool) -> bool:
        """Reformats file by adding social-distancing spaces.
        Changes are done in-place.

        :param dst: Location of file to reformat.
        :param line_distance: If True - adds lines of space between every two
                              consecutive lines.
        :param dry_run: If True - does not write changes back.

        :return: True if there is diff between source and reformatted file, False
                 otherwise.

        """
        with open(dst, "rb") as f:
            output = self._reformat(f, line_distance)

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
    parser = ArgumentParser(
        description="The annoying (yet disease-free) code formatter.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-l", "--line", action="store_true", help="Include distancing between lines"
    )
    parser.add_argument(
        "-m", "--mean", type=int, default=4, help="Mean number of spaces to add."
    )
    parser.add_argument(
        "-s",
        "--std",
        type=int,
        default=0,
        help="Standard deviation of number of spaces to add.",
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument(
        "files", metavar="FILE", nargs="*", default=[], help="Files to reformat (in place)"
    )
    source.add_argument("-c", "--code", help="Format the code passed in as a string.")
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        help="Don't write the files back, just return "
        "the status.  Return code 0 means nothing would "
        "change. Return code 1 means some files would be "
        "reformatted.",
    )

    args = parser.parse_args()

    reformatter = Reformatter(mean=args.mean, std=args.std)
    if args.code:
        output = reformatter.reformat_string(args.code, line_distance=args.line)
        print_stderr(output)
    else:
        status = [
            reformatter.reformat_file(f, line_distance=args.line, dry_run=args.dry_run)
            for f in args.files
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
        if reformatted:
            exit(1)
    exit(0)


def print_stderr(string):
    print(string, file=sys.stderr)


if __name__ == "__main__":
    main()
