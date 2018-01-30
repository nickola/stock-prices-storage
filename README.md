# Stock Prices Storage

Stock Prices Storage is a simple storage
([Clickhouse](https://clickhouse.yandex) is used as a database) for stock prices with adjusted prices calculaton
(see [Josh Schertz article](https://joshschertz.com/2016/08/27/Vectorizing-Adjusted-Close-with-Python/) for more details).

Storage is managed with `make.sh` (wrapper around `manage.py`), run `make.sh` to see a list of all supported actions.
Also, most common actions can be performed with `make` command (see `Makefile` for more details).


## Clickhouse

Basic versions of Clickhouse server and client can be started with [Docker](https://www.docker.com).

Clickhouse server can be started with (it will be started in detached mode):
```bash
make clickhouse-server
```

Clickhouse client can be started with:
```bash
make clickhouse-client
```

## Virtual Python environment

Virtual Python environment with all required packages can be created with:
```
make venv-recreate
```

## Working with storage

Recreating DB schema:
```
make reset
```

Importing example [Quandl WIKI Prices](https://www.quandl.com/databases/WIKIP) for Apple (AAPL) and Microsoft (MSFT)
from `_example/WIKI-AAPL-MSFT.csv`:
```
make import-example
```

Merging imported data into internal tables, duplicates control:
```
make merge
```

Recalculating all adjusted prices:
```
make adjust
```

Getting calculated adjusted prices and comparing them with original Quandl WIKI Prices:
```
make get-example
```

Output of final `make get-example` is shown below.
As you can see, calculated adjusted prices are very similar to the adjusted prices from Quandl.

```
ticker,date,open,high,low,close,volume,ex-dividend,split_ratio,adj_open,adj_high,adj_low,adj_close,adj_volume
AAPL,1980-12-12,28.75,28.87,28.75,28.75,2093900.0,0.0,1.0,0.42270591588018,0.42447025361603,0.42270591588018,0.42270591588018,117258400.0
MSFT,1986-03-13,25.5,29.25,25.5,28.0,3582600.0,0.0,1.0,0.058941410012893,0.067609264426554,0.058941410012893,0.064719979622,1031788800.0

FOUND:
  - symbol: AAPL
  - date: 1980-12-12
  - open: 28.75
  - high: 28.87
  - low: 28.75
  - close: 28.75
  - adjusted_open: 0.423
  - adjusted_high: 0.4257
  - adjusted_low: 0.4219
  - adjusted_close: 0.4228

FOUND:
  - symbol: MSFT
  - date: 1986-03-13
  - open: 25.5
  - high: 29.25
  - low: 25.5
  - close: 28
  - adjusted_open: 0.0588
  - adjusted_high: 0.0676
  - adjusted_low: 0.0586
  - adjusted_close: 0.0645
```
