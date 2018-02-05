from settings import (CLICKHOUSE_MINUTES_IMPORT_TABLE, CLICKHOUSE_MINUTES_TABLE,
                      CLICKHOUSE_DAYS_IMPORT_TABLE, CLICKHOUSE_DAYS_TABLE,
                      CLICKHOUSE_ADJUSTMENTS_IMPORT_TABLE, CLICKHOUSE_ADJUSTMENTS_TABLE)
from .base import BaseAction


class Action(BaseAction):
    def start(self):
        self.log("Merging minutes prices...")

        fields = self.get_table_fields(CLICKHOUSE_MINUTES_TABLE)
        insert_fields = ', '.join(fields)
        select_fields = ', '.join(map(lambda field: 'toDate(date) AS day' if field == 'day' else field, fields))

        self.clickhouse.execute('''
            INSERT INTO {insert_table} ({insert_fields})
            SELECT DISTINCT {select_fields} FROM {select_table}
            WHERE (symbol, date) NOT IN (SELECT (symbol, date) FROM {insert_table})
        '''.format(insert_table=CLICKHOUSE_MINUTES_TABLE, insert_fields=insert_fields,
                   select_table=CLICKHOUSE_MINUTES_IMPORT_TABLE, select_fields=select_fields))

        self.log("Merging days prices...")

        self.clickhouse.execute('''
            INSERT INTO {insert_table} ({fields})
            SELECT {fields} FROM (SELECT DISTINCT symbol,
                                                  day as date,
                                                  argMin(open, date) as open,
                                                  max(high) as high,
                                                  min(low) as low,
                                                  argMax(close, date) as close
                                  FROM {select_table}
                                  GROUP BY day, symbol)
            WHERE (symbol, date) NOT IN (SELECT (symbol, date) FROM {insert_table})
        '''.format(insert_table=CLICKHOUSE_DAYS_TABLE,
                   select_table=CLICKHOUSE_MINUTES_TABLE,
                   fields=', '.join(self.get_table_fields(CLICKHOUSE_DAYS_TABLE))))

        self.clickhouse.execute('''
            INSERT INTO {insert_table} ({fields})
            SELECT DISTINCT {fields} FROM {select_table}
            WHERE (symbol, date) NOT IN (SELECT (symbol, date) FROM {insert_table})
        '''.format(insert_table=CLICKHOUSE_DAYS_TABLE,
                   select_table=CLICKHOUSE_DAYS_IMPORT_TABLE,
                   fields=', '.join(self.get_table_fields(CLICKHOUSE_DAYS_TABLE))))

        self.log("Merging adjustments...")

        fields = ', '.join(self.get_table_fields(CLICKHOUSE_ADJUSTMENTS_TABLE))

        self.clickhouse.execute('''
            INSERT INTO {insert_table} ({fields})
            SELECT DISTINCT {fields} FROM {select_table}
            WHERE (dividend != {empty_dividend} OR split_ratio != {empty_split_ratio})
                  AND (symbol, date) NOT IN (SELECT (symbol, date) FROM {insert_table});
        '''.format(insert_table=CLICKHOUSE_ADJUSTMENTS_TABLE,
                   select_table=CLICKHOUSE_DAYS_IMPORT_TABLE,
                   fields=fields,
                   empty_dividend=self.empty_dividend,
                   empty_split_ratio=self.empty_split_ratio))

        self.clickhouse.execute('''
            INSERT INTO {insert_table} ({fields})
            SELECT DISTINCT {fields} FROM {select_table}
            WHERE (dividend != {empty_dividend} OR split_ratio != {empty_split_ratio})
                  AND (symbol, date) NOT IN (SELECT (symbol, date) FROM {insert_table});
        '''.format(insert_table=CLICKHOUSE_ADJUSTMENTS_TABLE,
                   select_table=CLICKHOUSE_ADJUSTMENTS_IMPORT_TABLE,
                   fields=fields,
                   empty_dividend=self.empty_dividend,
                   empty_split_ratio=self.empty_split_ratio))
