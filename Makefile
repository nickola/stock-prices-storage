# Settings
VENV = ".venv"
PYTHON = "$(VENV)/bin/python"
PYTHON_REQUIREMENTS = "requirements.txt"
DOCKER = "docker"
MANAGE = "./manage.sh"

# Example data
EXAMPLE_DATA = "_example"

# Python virtual environment
venv-setup:
	@python3 -m venv $(VENV)
	@echo "[list]\nformat = columns" > $(VENV)/pip.conf
	@$(VENV)/bin/pip --isolated install --upgrade pip setuptools

venv-remove:
	@rm -rf $(VENV)

venv-update:
	@$(VENV)/bin/pip --isolated install -r $(PYTHON_REQUIREMENTS)

venv-outdated:
	@$(VENV)/bin/pip --isolated list --outdated

venv-recreate: venv-remove venv-setup venv-update

# Lint
lint:
	@$(VENV)/bin/flake8 --max-line-length=120 --exclude="_*,$(VENV)" .

# Clickhouse
clickhouse-server:
	@$(DOCKER) run -d -p 9000:9000 --name storage-clickhouse --ulimit nofile=262144:262144 yandex/clickhouse-server

clickhouse-client:
	@$(DOCKER) run -it --rm --link storage-clickhouse:clickhouse-server yandex/clickhouse-client --host clickhouse-server

clickhouse-server-stop:
	@$(DOCKER) stop storage-clickhouse

clickhouse-server-start:
	@$(DOCKER) start storage-clickhouse

clickhouse-server-remove:
	@$(DOCKER) rm storage-clickhouse

# Storage
reset:
	@$(MANAGE) reset

merge:
	@$(MANAGE) merge

adjust:
	@$(MANAGE) adjust

# Example: Days (Quandl)
example-quandl-import:
	@$(MANAGE) import days "$(EXAMPLE_DATA)/quandl-WIKI-AAPL-MSFT.csv" --remove

example-quandl-get:
	@echo "QUANDL DATA:"
	@cat "$(EXAMPLE_DATA)/quandl-WIKI-AAPL-MSFT.csv" | head -1
	@cat "$(EXAMPLE_DATA)/quandl-WIKI-AAPL-MSFT.csv" | grep "AAPL,1980-12-12" | head -1
	@cat "$(EXAMPLE_DATA)/quandl-WIKI-AAPL-MSFT.csv" | grep "MSFT,1986-03-13" | head -1

	@echo
	@$(MANAGE) get day AAPL "1980-12-12"

	@echo
	@$(MANAGE) get day MSFT "1986-03-13"

example-quandl: reset example-quandl-import merge adjust example-quandl-get

# Example: Minutes (custom)
example-custom-import:
	@$(MANAGE) import minutes AAL "$(EXAMPLE_DATA)/minutes/AAL.csv" --remove
	@$(MANAGE) import minutes AAPL "$(EXAMPLE_DATA)/minutes/AAPL.csv"

	@$(MANAGE) import adjustments AAL "$(EXAMPLE_DATA)/minutes/adj_AAL.txt" --remove
	@$(MANAGE) import adjustments AAPL "$(EXAMPLE_DATA)/minutes/adj_AAPL.txt"

example-custom-get:
	@echo "QUANDL DATA:"
	@echo "ticker,date,open,high,low,close,volume,ex-dividend,split_ratio,adj_open,adj_high,adj_low,adj_close,adj_volume"
	@echo "AAL,2013-12-09,23.95,25.44,23.4501,24.6,115810456.0,0.0,0.373,23.211899447197,24.655980039111,22.727405562702,23.84186749065,115810456.0"
	@echo "AAPL,2007-04-27,98.18,99.95,97.69,99.92,24978700.0,0.0,1.0,12.617498398532,12.844968068173,12.554526569083,12.841112650044,174850900.0"

	@echo
	@$(MANAGE) get minute AAL "2013-12-09 12:00:00"

	@echo
	@$(MANAGE) get minute AAPL "2007-04-27 12:00:00"

example-custom: reset example-custom-import merge adjust example-custom-get
