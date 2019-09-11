import sys

from .cmdline import parse_cmdline
from .exceptions import BriefcaseError


def main():
    try:
        command = parse_cmdline(sys.argv[1:])
        command.parse_config('pyproject.toml')
        command()
        result = 0
    except BriefcaseError as e:
        print(e, file=sys.stdout if e.error_code == 0 else sys.stderr)
        result = e.error_code

    sys.exit(result)


if __name__ == '__main__':
    main()
