from settings import CLICKHOUSE_IMPORT_TABLE, CLICKHOUSE_PRICES_TABLE, CLICKHOUSE_DIVIDENDS_SPLITS_TABLE
from .base import BaseAction


class Action(BaseAction):
    def start(self):
        self.log("Merging prices...")

        prices_fields = ', '.join(self.get_table_fields(CLICKHOUSE_PRICES_TABLE))

        self.clickhouse.execute('''
            INSERT INTO {prices_table} ({prices_fields})
            SELECT DISTINCT {prices_fields} FROM {import_table}
            WHERE (symbol, date) NOT IN (SELECT (symbol, date) FROM {prices_table})
        '''.format(import_table=CLICKHOUSE_IMPORT_TABLE,
                   prices_table=CLICKHOUSE_PRICES_TABLE,
                   prices_fields=prices_fields))

        self.log("Merging dividends and splits...")

        dividends_splits_fields = ', '.join(self.get_table_fields(CLICKHOUSE_DIVIDENDS_SPLITS_TABLE))

        self.clickhouse.execute('''
            INSERT INTO {dividends_splits_table} ({dividends_splits_fields})
            SELECT DISTINCT {dividends_splits_fields} FROM {import_table}
            WHERE (dividend != {empty_dividend} OR split_ratio != {empty_split_ratio})
                  AND (symbol, date) NOT IN (SELECT (symbol, date) FROM {dividends_splits_table});
        '''.format(import_table=CLICKHOUSE_IMPORT_TABLE,
                   dividends_splits_table=CLICKHOUSE_DIVIDENDS_SPLITS_TABLE,
                   dividends_splits_fields=dividends_splits_fields,
                   empty_dividend=self.empty_dividend,
                   empty_split_ratio=self.empty_split_ratio))
