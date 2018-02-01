from decimal import Decimal
from utilities import chunked
from settings import CLICKHOUSE_PRICES_TABLE, CLICKHOUSE_DIVIDENDS_SPLITS_TABLE, CLICKHOUSE_PRICES_ADJUSTED_TABLE
from .base import BaseAction


class Action(BaseAction):
    chunk_size = 100000

    def serialize(self, data, symbol, date):
        return {
            'symbol': symbol,
            'date': date,
            'adjusted_open': int(data['open']),
            'adjusted_high': int(data['high']),
            'adjusted_low': int(data['low']),
            'adjusted_close': int(data['close'])
        }

    def start(self, skip_errors=False):
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
        current_coefficient = default_coefficient = Decimal(1)
        current_symbol = None
        total = 0

        for rows in chunked(self.clickhouse.execute(select_sql), size=self.chunk_size):
            items = []

            for row in rows:
                symbol, date, open, high, low, close, dividend, split_ratio = row
                total += 1

                if symbol != current_symbol:
                    current_symbol, current_coefficient = symbol, default_coefficient
                    precede, precede_date = None, None

                current = {
                    'open': Decimal(open),
                    'high': Decimal(high),
                    'low': Decimal(low),
                    'close': Decimal(close),
                    'dividend': self.empty_dividend if dividend == 0 else dividend,
                    'split_ratio': self.empty_split_ratio if split_ratio == 0 else split_ratio
                }

                if precede:
                    if precede['split_ratio'] != self.empty_split_ratio:
                        current_coefficient *= 1 / self.demultiplied(precede['split_ratio'])

                    if precede['dividend'] != self.empty_dividend:
                        dividend_coefficient = (1 - Decimal(precede['dividend']) / current['close'])

                        if dividend_coefficient <= 0:
                            template = "Dividend coefficient is less than or equal to zero, " \
                                       "please check data for symbol: {symbol} [{date}, {precede_date}]"
                            self.log(template.format(symbol=symbol, date=date, precede_date=precede_date), error=True)

                            if skip_errors:
                                dividend_coefficient = default_coefficient
                            else:
                                return

                        current_coefficient *= dividend_coefficient

                    current['adjusted'] = {price: current[price] * current_coefficient for price in price_fields}

                else:
                    current['adjusted'] = {price: current[price] for price in price_fields}

                items.append(self.serialize(current['adjusted'], symbol=symbol, date=date))

                precede, precede_date = current, date

            if items:
                self.clickhouse.execute(insert_sql, items)
                self.log("Adjusted: {total} rows".format(total=total))
