# Base
NUMBER_MULTIPLIER = 10000

# Clickhouse settings
CLICKHOUSE_HOST = 'localhost'
CLICKHOUSE_PORT = 9000
CLICKHOUSE_DATABASE = 'default'
CLICKHOUSE_USER = 'default'
CLICKHOUSE_PASSWORD = ''

# Clickhouse schema
CLICKHOUSE_IMPORT_TABLE = 'import'
CLICKHOUSE_PRICES_TABLE = 'prices'
CLICKHOUSE_DIVIDENDS_SPLITS_TABLE = 'dividends_splits'
CLICKHOUSE_PRICES_ADJUSTED_TABLE = 'prices_adjusted'
CLICKHOUSE_PRICES_ALL_VIEW = 'prices_all'

CLICKHOUSE_TABLES = {
    'import': {
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
    'prices': {
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
    'dividends_splits': {
        'engine': 'ReplacingMergeTree(date, (symbol, date), 8192)',
        'fields': [
            {'name': 'symbol', 'type': 'String'},
            {'name': 'date', 'type': 'Date'},
            {'name': 'dividend', 'type': 'UInt64'},
            {'name': 'split_ratio', 'type': 'UInt64'}
        ]
    },
    'prices_adjusted': {
        'engine': 'ReplacingMergeTree(date, (symbol, date), 8192)',
        'fields': [
            {'name': 'symbol', 'type': 'String'},
            {'name': 'date', 'type': 'Date'},
            {'name': 'adjusted_open', 'type': 'UInt64'},
            {'name': 'adjusted_high', 'type': 'UInt64'},
            {'name': 'adjusted_low', 'type': 'UInt64'},
            {'name': 'adjusted_close', 'type': 'UInt64'}
        ]
    }
}

CLICKHOUSE_VIEWS = {
    'prices_all': 'SELECT symbol, date, open, high, low, close, '
                  'adjusted_open, adjusted_high, adjusted_low, adjusted_close '
                  'FROM prices ANY LEFT JOIN prices_adjusted USING symbol, date'
}
