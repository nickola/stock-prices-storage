import argparse
from utilities import import_symbol


# Parser
parser = argparse.ArgumentParser(description="Storage management")
action_parsers = parser.add_subparsers(help="Management actions")

# Reset
reset_parser = action_parsers.add_parser('reset', help="Recreate database schema")
reset_parser.set_defaults(action='reset')

# Import
import_parser = action_parsers.add_parser('import', help="Import data from CSV file")
import_parser.set_defaults(action='import')
import_parser.add_argument('file', help="CSV file path")
import_parser.add_argument('--skip-errors', action='store_true', help="Skip errors")
import_parser.add_argument('--offset', type=int, help="Initial file offset")

# Merge
merge_parser = action_parsers.add_parser('merge', help="Merge imported data")
merge_parser.set_defaults(action='merge')

# Adjust
adjust_parser = action_parsers.add_parser('adjust', help="Adjust prices")
adjust_parser.set_defaults(action='adjust')

# Get
get_parser = action_parsers.add_parser('get', help="Get adjusted prices")
get_parser.set_defaults(action='get')
get_parser.add_argument('symbol', help="Symbol")
get_parser.add_argument('date', help="Date (YYYY-MM-DD)")


def main():
    arguments = vars(parser.parse_args())
    action = arguments.pop('action', None)

    if action:
        Action = import_symbol('actions.{}'.format(action), 'Action')
        Action().start(**arguments)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
