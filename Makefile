.PHONY: all clean test install run deploy down

DOCKER_COMPOSE = docker-compose
VENV_DIR := venv
REQUIREMENTS_FILE := requirements.txt

clean:
	@find . -name '*.pyc' -exec rm -rf {} \;
	@find . -name '__pycache__' -exec rm -rf {} \;
	@find . -name 'Thumbs.db' -exec rm -rf {} \;
	@find . -name '*~' -exec rm -rf {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build

test:
	python3 -m unittest tests/unit/test_scheduler.py   
	python3 -m unittest tests/integration/test_upload_file.py

install:
	test -d $(VENV_DIR) || python3 -m venv $(VENV_DIR)
	. $(VENV_DIR)/bin/activate; \
	pip install -r $(REQUIREMENTS_FILE)


all: install test up

up:
	$(DOCKER_COMPOSE) up --build

down:
	$(DOCKER_COMPOSE) down
	make clean

