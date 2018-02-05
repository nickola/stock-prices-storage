import os
import csv
from decimal import Decimal
from utilities import chunked, parse_datetime
from settings import CLICKHOUSE_MINUTES_IMPORT_TABLE, CLICKHOUSE_DAYS_IMPORT_TABLE, CLICKHOUSE_ADJUSTMENTS_IMPORT_TABLE
from .base import BaseAction


class Action(BaseAction):
    minimum_date = parse_datetime('1970-01-01 00:00:00')  # See: https://clickhouse.yandex/docs/en/data_types/date.html
    chunk_size = 100000

    def serialize_day(self, data):
        return {
            'symbol': data['ticker'],
            'date': parse_datetime(data['date'], format='%Y-%m-%d').date(),
            'open': self.multiplied(data['open']),
            'high': self.multiplied(data['high']),
            'low': self.multiplied(data['low']),
            'close': self.multiplied(data['close']),
            'dividend': self.multiplied(data['ex-dividend']),
            'split_ratio': self.multiplied(data['split_ratio'])
        }

    def serialize_minute(self, symbol, data):
        return {
            'symbol': symbol,
            'date': parse_datetime(data['date']),
            'open': self.multiplied(data['open']),
            'high': self.multiplied(data['high']),
            'low': self.multiplied(data['low']),
            'close': self.multiplied(data['close'])
        }

    def serialize_adjustment(self, symbol, data):
        return {
            'symbol': symbol,
            'date': parse_datetime(data['Date(ex)'], format='%Y.%m.%d').date(),
            'dividend': self.multiplied(data['RegularDividend$']),
            'split_ratio': self.multiplied(1 / Decimal(data['Split']))
        }

    def start(self, mode, file, symbol=None, **kwargs):
        if not (file and os.path.isfile(file)):
            self.log("No file found: {file}".format(file=file), error=True)
            return

        if mode == 'minutes':
            symbol = symbol.upper()

            self.import_data(csv_file=file,
                             csv_fields=('date', 'high', 'low', 'open', 'close', 'volume', 'last_volume'),
                             serializer=lambda data: self.serialize_minute(symbol, data),
                             table=CLICKHOUSE_MINUTES_IMPORT_TABLE,
                             minimum_date=self.minimum_date,
                             **kwargs)

        elif mode == 'days':
            self.import_data(csv_file=file,
                             serializer=self.serialize_day,
                             table=CLICKHOUSE_DAYS_IMPORT_TABLE,
                             minimum_date=self.minimum_date.date(),
                             **kwargs)

        elif mode == 'adjustments':
            symbol = symbol.upper()

            self.import_data(csv_file=file,
                             serializer=lambda data: self.serialize_adjustment(symbol, data),
                             table=CLICKHOUSE_ADJUSTMENTS_IMPORT_TABLE,
                             minimum_date=self.minimum_date.date(),
                             **kwargs)

    def import_data(self, csv_file, serializer, table, csv_fields=None, minimum_date=None,
                    remove=False, skip_errors=False, offset=None):
        if remove:
            self.remove_table(table)
            self.create_table(table)

        total = 0
        sql = 'INSERT INTO {table} ({fields}) VALUES'.format(table=table,
                                                             fields=', '.join(self.get_table_fields(table)))

        with open(csv_file) as file_handler:
            for rows in chunked(csv.DictReader(file_handler, fieldnames=csv_fields), size=self.chunk_size):
                items = []

                for row in rows:
                    try:
                        item = serializer(row)

                    except Exception as error:
                        self.log("Serialization error: {error}".format(error=error), data=row, error=True)

                        if not skip_errors:
                            return

                    if minimum_date is None or item['date'] >= minimum_date:
                        total += 1

                        if not offset or total >= offset:
                            items.append(item)

                    else:
                        self.log("Skipped (minimum date is {minimum_date})".format(minimum_date=minimum_date),
                                 data=row, warning=True)

                if items:
                    self.clickhouse.execute(sql, items)
                    self.log("Imported: {total} rows".format(total=total))
