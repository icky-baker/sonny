.DEFAULT_GOAL := help

base_python := python3.8
virtualenv_dir := .venv
python := $(virtualenv_dir)/bin/$(base_python)
project_source_dir := client naming storage

pyenv := source $(virtualenv_dir)/bin/activate

.PHONY: help
help:
	@echo "======================================================================================="
	@echo "                                  build tools                                  "
	@echo "======================================================================================="
	@echo "Environment:"
	@echo "    help: Show this message"
	@echo "    install: Install development dependencies"
	@echo "    clean: Delete temporary files"
	@echo ""
	@echo "Code quality:"
	@echo "    isort: Run isort tool"
	@echo "    black: Run black tool"
	@echo "    flake8: Run flake8 tool"
	@echo "    flake8-report: Run flake8 with HTML reporting"
	@echo "    lint: Run isort, black, flake8 and mypy tools"
	@echo ""
	@echo "Tests:"
	@echo "    test: Run tests"
	@echo "    test-coverage: Run tests with HTML reporting (results + coverage)"
	@echo "    test-coverage-report: Open coverage report in default system web browser"
	@echo ""


# =================================================================================================
# Environment
# =================================================================================================

.PHONY: install
install:
	$(base_python) -m pip install --user -U virtualenv
	$(base_python) -m virtualenv .venv
	$(pyenv); pip install -r requirements.txt
	$(pyenv); pre-commit install
	$(pyenv); pre-commit install -t pre-push
	echo "Everything is installed!"

.PHONY: clean
clean:
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -rf `find . -name .pytest_cache`
	rm -rf *.egg-info
	rm -f .coverage
	rm -f report.html
	rm -f .coverage.*
	rm -rf {build,dist,site,.cache,.mypy_cache,reports}


# =================================================================================================
# Code quality
# =================================================================================================

.PHONY: isort
isort:
	$(pyenv); isort $(project_source_dir)

.PHONY: black
black:
	$(pyenv); black $(project_source_dir)

.PHONY: flake8
flake8:
	$(pyenv); flake8 $(project_source_dir)


.PHONY: lint
lint: isort black flake8

# =================================================================================================
# Naming project
# =================================================================================================

.PHONY: naming_migrate
naming_migrate: |
	$(python) naming/manage.py migrate

.PHONY: naming
naming: |
	$(python) naming/manage.py runserver

.PHONY: naming_preprod
naming_preprod: |
	 sleep 5; $(base_python) manage.py migrate; $(base_python) manage.py runserver 0.0.0.0:80

.PHONY: naming_prod
naming_prod: |
	 sleep 5;
	$(base_python) manage.py migrate; gunicorn -b 0.0.0.0:80 naming.wsgi

.PHONY: build_and_push
build_and_push: |
	docker-compose build && docker-compose push

.PHONY: pull_and_up
pull_and_up: |
	docker-compose pull && docker-compose up -d

.PHONY: storage
storage: |
	$(python) storage/manage.py runserver

.PHONY: storage_prod
storage_prod: |
	sleep 7	;
	$(base_python) manage.py migrate;
	$(base_python) manage.py register;
	gunicorn -w 4 -b 0.0.0.0:8000 dfs.wsgi

.PHONY: up
up: |
	docker-compose down; docker-compose up --build

.PHONY: check
check: |
	$(base_python) manage.py check_storage_servers_health &>> /tmp/healthcheck.log

.PHONY: ss_sync
ss_sync: |
	$(base_python) manage.py register;

.PHONE: client_entrypoint
client_entrypoint: |
	./client.sh
