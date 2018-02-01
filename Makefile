# Settings
VENV = ".venv"
PYTHON = "$(VENV)/bin/python"
PYTHON_REQUIREMENTS = "requirements.txt"
DOCKER = "docker"
MANAGE = "./manage.sh"
EXAMPLE_AAPL_MSFT_CSV = "_example/WIKI-AAPL-MSFT.csv"

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

# Clickhouse
clickhouse-server:
	@$(DOCKER) run -d -p 9000:9000 --name storage-clickhouse --ulimit nofile=262144:262144 yandex/clickhouse-server

clickhouse-client:
	@$(DOCKER) run -it --rm --link storage-clickhouse:clickhouse-server yandex/clickhouse-client --host clickhouse-server

clickhouse-server-stop:
	@$(DOCKER) stop storage-clickhouse

clickhouse-server-start:
	@$(DOCKER) start storage-clickhouse

# Storage
reset:
	@$(MANAGE) reset

merge:
	@$(MANAGE) merge

adjust:
	@$(MANAGE) adjust

# Examples
import-example:
	@$(MANAGE) import "$(EXAMPLE_AAPL_MSFT_CSV)"

get-example:
	@cat "$(EXAMPLE_AAPL_MSFT_CSV)" | head -1
	@cat "$(EXAMPLE_AAPL_MSFT_CSV)" | grep "AAPL,1980-12-12" | head -1
	@cat "$(EXAMPLE_AAPL_MSFT_CSV)" | grep "MSFT,1986-03-13" | head -1

	@echo
	@$(MANAGE) get AAPL 1980-12-12

	@echo
	@$(MANAGE) get MSFT 1986-03-13
