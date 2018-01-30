from settings import CLICKHOUSE_TABLES, CLICKHOUSE_VIEWS
from .base import BaseAction


class Action(BaseAction):
    def start(self):
        for table in sorted(CLICKHOUSE_TABLES.keys()):
            self.remove_table(table)
            self.create_table(table)

        for view in sorted(CLICKHOUSE_VIEWS.keys()):
            self.remove_table(view)
            self.create_view(view)
