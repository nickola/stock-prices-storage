from decimal import Decimal
from datetime import datetime
from traceback import format_exc
from importlib import import_module


def multiplied(value, multiplier):
    return int(Decimal(value) * multiplier)


def demultiplied(value, multiplier):
    return Decimal(value) / multiplier


def parse_date(value, format='%Y-%m-%d'):
    return datetime.strptime(value, format).date()


def import_symbol(module, symbol):
    try:
        return getattr(import_module(module), symbol)
    except (ModuleNotFoundError, AttributeError):
        error = "Unable to load \"{module}.{symbol}\"\n\n{error}"
        raise Exception(error.format(module=module, symbol=symbol, error=format_exc()))


def chunked(items, size=1000):
    chunk = []

    for number, item in enumerate(items, 1):
        chunk.append(item)

        if number % size == 0:
            yield chunk

            chunk = []

    if chunk:
        yield chunk
