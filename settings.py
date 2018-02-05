# Base
NUMBER_MULTIPLIER = 10000

# Clickhouse settings
CLICKHOUSE_HOST = 'localhost'
CLICKHOUSE_PORT = 9000
CLICKHOUSE_DATABASE = 'default'
CLICKHOUSE_USER = 'default'
CLICKHOUSE_PASSWORD = ''

# Clickhouse schema
CLICKHOUSE_ADJUSTMENTS_TABLE = 'adjustments'
CLICKHOUSE_ADJUSTMENTS_IMPORT_TABLE = 'adjustments_import'

CLICKHOUSE_MINUTES_TABLE = 'minutes'
CLICKHOUSE_MINUTES_IMPORT_TABLE = 'minutes_import'
CLICKHOUSE_MINUTES_VIEW = 'minutes_view'

CLICKHOUSE_DAYS_TABLE = 'days'
CLICKHOUSE_DAYS_IMPORT_TABLE = 'days_import'
CLICKHOUSE_DAYS_ADJUSTED_TABLE = 'days_adjusted'
CLICKHOUSE_DAYS_VIEW = 'days_view'

CLICKHOUSE_TABLES = {
    # Import
    'minutes_import': {
        'engine': 'Log',
        'fields': [
            {'name': 'symbol', 'type': 'String'},
            {'name': 'date', 'type': 'DateTime'},
            {'name': 'open', 'type': 'UInt64'},
            {'name': 'high', 'type': 'UInt64'},
            {'name': 'low', 'type': 'UInt64'},
            {'name': 'close', 'type': 'UInt64'}
        ]
    },
    'days_import': {
        'engine': 'Log',
        'fields': [
            {'name': 'symbol', 'type': 'String'},
            {'name': 'date', 'type': 'Date'},
            {'name': 'open', 'type': 'UInt64'},
            {'name': 'high', 'type': 'UInt64'},
            {'name': 'low', 'type': 'UInt64'},
            {'name': 'close', 'type': 'UInt64'},
            {'name': 'dividend', 'type': 'UInt64'},
            {'name': 'split_ratio', 'type': 'UInt64'}
        ]
    },
    'adjustments_import': {
        'engine': 'Log',
        'fields': [
            {'name': 'symbol', 'type': 'String'},
            {'name': 'date', 'type': 'Date'},
            {'name': 'dividend', 'type': 'UInt64'},
            {'name': 'split_ratio', 'type': 'UInt64'}
        ]
    },
    # Minutes, days, adjustments
    'minutes': {
        'engine': 'ReplacingMergeTree(day, (symbol, date), 8192)',
        'fields': [
            {'name': 'symbol', 'type': 'String'},
            {'name': 'day', 'type': 'Date'},
            {'name': 'date', 'type': 'DateTime'},
            {'name': 'open', 'type': 'UInt64'},
            {'name': 'high', 'type': 'UInt64'},
            {'name': 'low', 'type': 'UInt64'},
            {'name': 'close', 'type': 'UInt64'}
        ]
    },
    'days': {
        'engine': 'ReplacingMergeTree(date, (symbol, date), 8192)',
        'fields': [
            {'name': 'symbol', 'type': 'String'},
            {'name': 'date', 'type': 'Date'},
            {'name': 'open', 'type': 'UInt64'},
            {'name': 'high', 'type': 'UInt64'},
            {'name': 'low', 'type': 'UInt64'},
            {'name': 'close', 'type': 'UInt64'}
        ]
    },
    'adjustments': {
        'engine': 'ReplacingMergeTree(date, (symbol, date), 8192)',
        'fields': [
            {'name': 'symbol', 'type': 'String'},
            {'name': 'date', 'type': 'Date'},
            {'name': 'dividend', 'type': 'UInt64'},
            {'name': 'split_ratio', 'type': 'UInt64'}
        ]
    },
    # Adjusted
    'days_adjusted': {
        'engine': 'ReplacingMergeTree(date, (symbol, date), 8192)',
        'fields': [
            {'name': 'symbol', 'type': 'String'},
            {'name': 'date', 'type': 'Date'},
            {'name': 'adjustment_coefficient', 'type': 'UInt64'},
            {'name': 'adjusted_open', 'type': 'UInt64'},
            {'name': 'adjusted_high', 'type': 'UInt64'},
            {'name': 'adjusted_low', 'type': 'UInt64'},
            {'name': 'adjusted_close', 'type': 'UInt64'}
        ]
    }
}

CLICKHOUSE_VIEWS = {
    'days_view': 'SELECT symbol, date, open, high, low, close, '
                 'adjusted_open, adjusted_high, adjusted_low, adjusted_close '
                 'FROM days '
                 'ANY LEFT JOIN days_adjusted USING symbol, date',
    'minutes_view': ('SELECT symbol, date, open, high, low, close, '
                     'toInt64(open * adjustment_coefficient / {multiplier}) as adjusted_open, '
                     'toInt64(high * adjustment_coefficient / {multiplier}) as adjusted_high, '
                     'toInt64(low * adjustment_coefficient / {multiplier}) as adjusted_low, '
                     'toInt64(close * adjustment_coefficient / {multiplier}) as adjusted_close '
                     'FROM minutes '
                     'ANY LEFT JOIN (select symbol, date as day, adjustment_coefficient from days_adjusted) '
                     'USING symbol, day').format(multiplier=NUMBER_MULTIPLIER)
}
