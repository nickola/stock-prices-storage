import argparse
from utilities import import_symbol


def base_import_arguments(parser):
    parser.add_argument('file', help="CSV file path")
    parser.add_argument('--offset', type=int, help="Initial file offset")
    parser.add_argument('--remove', action='store_true', help="Remove existent data")
    parser.add_argument('--skip-errors', action='store_true', help="Skip errors")


def parser():
    # Parser
    parser = argparse.ArgumentParser(description="Storage management")
    action_parsers = parser.add_subparsers(help="Management actions")

    # Reset
    reset_parser = action_parsers.add_parser('reset', help="Recreate database schema")
    reset_parser.set_defaults(action='reset')

    # Import
    import_parser = action_parsers.add_parser('import', help="Import data from CSV file")
    import_parser.set_defaults(action='import')
    import_parsers = import_parser.add_subparsers(help="Import modes")

    # Import: days
    import_days_parser = import_parsers.add_parser('days', help="Days mode import")
    import_days_parser.set_defaults(mode='days')
    base_import_arguments(import_days_parser)

    # Import: minutes
    import_minutes_parser = import_parsers.add_parser('minutes', help="Minutes mode import")
    import_minutes_parser.set_defaults(mode='minutes')

    import_minutes_parser.add_argument('symbol', help="Symbol")
    base_import_arguments(import_minutes_parser)

    # Import: adjustments
    import_adjustments_parser = import_parsers.add_parser('adjustments', help="Adjustments mode import")
    import_adjustments_parser.set_defaults(mode='adjustments')

    import_adjustments_parser.add_argument('symbol', help="Symbol")
    base_import_arguments(import_adjustments_parser)

    # Merge
    merge_parser = action_parsers.add_parser('merge', help="Merge imported data")
    merge_parser.set_defaults(action='merge')

    # Adjust
    adjust_parser = action_parsers.add_parser('adjust', help="Adjust prices")
    adjust_parser.set_defaults(action='adjust')
    adjust_parser.add_argument('--skip-errors', action='store_true', help="Skip errors")

    # Get
    get_parser = action_parsers.add_parser('get', help="Get adjusted prices")
    get_parser.set_defaults(action='get')
    get_parsers = get_parser.add_subparsers(help="Get modes")

    # Get: day
    get_day_parser = get_parsers.add_parser('day', help="Day mode get")
    get_day_parser.set_defaults(mode='day')
    get_day_parser.add_argument('symbol', help="Symbol")
    get_day_parser.add_argument('date', help="Date (YYYY-MM-DD)")

    # Get: minute
    get_minute_parser = get_parsers.add_parser('minute', help="Minute mode get")
    get_minute_parser.set_defaults(mode='minute')
    get_minute_parser.add_argument('symbol', help="Symbol")
    get_minute_parser.add_argument('date', help="Date (YYYY-MM-DD hh:mm:ss)")

    return parser


def main():
    arguments = vars(parser().parse_args())
    action = arguments.pop('action', None)

    if action:
        Action = import_symbol('actions.{}'.format(action), 'Action')
        Action().start(**arguments)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
