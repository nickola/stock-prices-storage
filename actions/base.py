from pprint import pformat
from clickhouse_driver import Client
from utilities import multiplied, demultiplied
from settings import (NUMBER_MULTIPLIER, CLICKHOUSE_HOST, CLICKHOUSE_PORT, CLICKHOUSE_DATABASE,
                      CLICKHOUSE_USER, CLICKHOUSE_PASSWORD, CLICKHOUSE_TABLES, CLICKHOUSE_VIEWS)


class BaseAction(object):
    empty_split_ratio = multiplied(1, NUMBER_MULTIPLIER)
    empty_dividend = 0
    chunk_size = 100000

    @property
    def clickhouse(self):
        if not hasattr(self, '_clickhouse'):
            self._clickhouse = Client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, database=CLICKHOUSE_DATABASE,
                                      user=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD)

        return self._clickhouse

    @staticmethod
    def multiplied(value):
        return multiplied(value, NUMBER_MULTIPLIER)

    @staticmethod
    def demultiplied(value):
        return demultiplied(value, NUMBER_MULTIPLIER)

    @staticmethod
    def get_table_data(table):
        return CLICKHOUSE_TABLES[table]

    @staticmethod
    def get_view_data(view):
        return CLICKHOUSE_VIEWS[view]

    @classmethod
    def get_table_fields(cls, table):
        return tuple(sorted(map(lambda item: item['name'], cls.get_table_data(table)['fields'])))

    def remove_table(self, table):
        self.log("Removing table: {table}".format(table=table))
        self.clickhouse.execute('DROP TABLE IF EXISTS {table}'.format(table=table))

    def create_table(self, table):
        data = self.get_table_data(table)

        engine = data['engine']
        fields = ', '.join(sorted(map(lambda item: '{name} {type}'.format(**item), data['fields'])))

        self.log("Creating table: {table}".format(table=table))
        self.clickhouse.execute('CREATE TABLE {table} ({fields}) ENGINE = {engine}'.format(table=table,
                                                                                           fields=fields,
                                                                                           engine=engine))

    def create_view(self, view):
        query = self.get_view_data(view)

        self.log("Creating view: {view}".format(view=view))
        self.clickhouse.execute('CREATE VIEW {view} AS {query}'.format(view=view, query=query))

    def log(self, text, error=False, warning=False, data=None, pretty=False):
        if error:
            text = "[ERROR] {text}".format(text=text)

        elif warning:
            text = "[WARNING] {text}".format(text=text)

        if data:
            if pretty:
                text += "\n-- [DATA] --\n{data}\n-- [/DATA] --".format(data=pformat(data))

            else:
                data_text = ', '.join(map(lambda pair: '{}: {!r}'.format(*pair), sorted(data.items())))
                text += ' [{data}]'.format(data=data_text)

        print(text)

    def start(self, *args, **kwargs):
        raise NotImplementedError
