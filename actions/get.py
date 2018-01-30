from settings import CLICKHOUSE_PRICES_ALL_VIEW
from .base import BaseAction


class Action(BaseAction):
    def deserialize(self, data):
        return {
            'symbol': data['symbol'],
            'date': str(data['date']),
            'open': self.demultiplied(data['open']),
            'high': self.demultiplied(data['high']),
            'low': self.demultiplied(data['low']),
            'close': self.demultiplied(data['close']),
            'adjusted_open': self.demultiplied(data['adjusted_open']),
            'adjusted_high': self.demultiplied(data['adjusted_high']),
            'adjusted_low': self.demultiplied(data['adjusted_low']),
            'adjusted_close': self.demultiplied(data['adjusted_close'])
        }

    def start(self, symbol, date):
        fields = ('symbol', 'date', 'open', 'high', 'low', 'close',
                  'adjusted_open', 'adjusted_high', 'adjusted_low', 'adjusted_close')

        rows = self.clickhouse.execute('''
            SELECT {fields} FROM {view} WHERE symbol = '{symbol}' AND date = '{date}'
        '''.format(fields=', '.join(fields), view=CLICKHOUSE_PRICES_ALL_VIEW, symbol=symbol, date=date))

        if rows:
            for row in rows:
                self.log("FOUND:")

                for key, value in self.deserialize({field: row[index] for index, field in enumerate(fields)}).items():
                    self.log("  - {key}: {value}".format(key=key, value=value))

        else:
            self.log("NOT FOUND")
