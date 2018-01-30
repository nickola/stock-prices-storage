from utilities import chunked
from settings import CLICKHOUSE_PRICES_TABLE, CLICKHOUSE_DIVIDENDS_SPLITS_TABLE, CLICKHOUSE_PRICES_ADJUSTED_TABLE
from .base import BaseAction


class Action(BaseAction):
    chunk_size = 100000

    @staticmethod
    def adjusted(value, precede_value, precede_adjusted, precede_dividend, precede_split):
        return precede_adjusted + precede_adjusted * ((value * (1 / precede_split) - precede_value - precede_dividend)
                                                      / precede_value)

    def serialize(self, data, symbol, date):
        return {
            'symbol': symbol,
            'date': date,
            'adjusted_open': self.multiplied(data['open']),
            'adjusted_high': self.multiplied(data['high']),
            'adjusted_low': self.multiplied(data['low']),
            'adjusted_close': self.multiplied(data['close'])
        }

    def start(self):
        self.remove_table(CLICKHOUSE_PRICES_ADJUSTED_TABLE)
        self.create_table(CLICKHOUSE_PRICES_ADJUSTED_TABLE)

        self.log("Adjusting prices...")

        select_sql = '''
            SELECT symbol, date, open, high, low, close, dividend, split_ratio FROM {prices_table}
            ANY LEFT JOIN {dividends_splits_table} USING symbol, date
            ORDER BY {prices_table}.symbol, {prices_table}.date DESC
        '''.format(prices_table=CLICKHOUSE_PRICES_TABLE, dividends_splits_table=CLICKHOUSE_DIVIDENDS_SPLITS_TABLE)

        insert_fields = ', '.join(self.get_table_fields(CLICKHOUSE_PRICES_ADJUSTED_TABLE))
        insert_sql = 'INSERT INTO {table} ({fields}) VALUES'.format(table=CLICKHOUSE_PRICES_ADJUSTED_TABLE,
                                                                    fields=insert_fields)

        price_fields = ('open', 'high', 'low', 'close')
        precede, precede_date = None, None
        current_symbol = None
        total = 0

        for rows in chunked(self.clickhouse.execute(select_sql), size=self.chunk_size):
            items = []

            for row in rows:
                symbol, date, open, high, low, close, dividend, split_ratio = row
                total += 1

                if symbol != current_symbol:
                    current_symbol = symbol
                    precede, precede_date = None, None

                current = {
                    'open': self.demultiplied(open),
                    'high': self.demultiplied(high),
                    'low': self.demultiplied(low),
                    'close': self.demultiplied(close),
                    'dividend': self.demultiplied(dividend or self.empty_dividend),
                    'split_ratio': self.demultiplied(split_ratio or self.empty_split_ratio)
                }

                if precede:
                    current['adjusted'] = {
                        price: self.adjusted(value=current[price],
                                             precede_value=precede[price],
                                             precede_adjusted=precede['adjusted'][price],
                                             precede_dividend=precede['dividend'],
                                             precede_split=precede['split_ratio'])
                        for price in price_fields
                    }

                    for value in current['adjusted'].values():
                        if value <= 0:
                            self.log("Adjusted value is <= 0, check data for symbol: {symbol}".format(symbol=symbol),
                                     data={precede_date: precede, date: current}, error=True, pretty=True)
                            return

                else:
                    current['adjusted'] = {price: current[price] for price in price_fields}

                items.append(self.serialize(current['adjusted'], symbol=symbol, date=date))

                precede, precede_date = current, date

            if items:
                self.clickhouse.execute(insert_sql, items)
                self.log("Adjusted: {total} rows".format(total=total))
