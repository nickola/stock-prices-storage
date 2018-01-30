import os
import csv
from datetime import datetime
from utilities import parse_date, chunked
from settings import CLICKHOUSE_IMPORT_TABLE
from .base import BaseAction


class Action(BaseAction):
    minimum_date = parse_date('1970-01-01')  # See: https://clickhouse.yandex/docs/en/data_types/date.html
    chunk_size = 100000

    def serialize(self, data):
        return {
            'symbol': data['ticker'],
            'date': parse_date(data['date']),
            'open': self.multiplied(data['open']),
            'high': self.multiplied(data['high']),
            'low': self.multiplied(data['low']),
            'close': self.multiplied(data['close']),
            'dividend': self.multiplied(data['ex-dividend']),
            'split_ratio': self.multiplied(data['split_ratio'])
        }

    def start(self, file, offset=None, skip_errors=False):
        if not (file and os.path.isfile(file)):
            raise self.Error("No file found: {file}".format(file=file))

        self.remove_table(CLICKHOUSE_IMPORT_TABLE)
        self.create_table(CLICKHOUSE_IMPORT_TABLE)

        fields = ', '.join(self.get_table_fields(CLICKHOUSE_IMPORT_TABLE))
        sql = 'INSERT INTO {table} ({fields}) VALUES'.format(table=CLICKHOUSE_IMPORT_TABLE, fields=fields)

        total = 0

        with open(file) as csv_file:
            reader = csv.DictReader(csv_file)

            for rows in chunked(csv.DictReader(csv_file), size=self.chunk_size):
                items = []

                for row in rows:
                    try:
                        item = self.serialize(row)

                    except Exception as error:
                        self.log("Serialization error: {error}".format(error=error), data=row, error=True)

                        if not skip_errors:
                            return

                    if item['date'] >= self.minimum_date:
                        total += 1

                        if not offset or total >= offset:
                            items.append(item)

                    else:
                        self.log("Skipped (minimum date is {minimum_date})".format(minimum_date=self.minimum_date),
                                 data=row, warning=True)

                if items:
                    self.clickhouse.execute(sql, items)
                    self.log("Imported: {total} rows".format(total=total))
