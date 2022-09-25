# Makefile PII Codex
# Can be used from github workflow or locally
default: install test lint

test: lint test.all
test.cov: test.coverage

install:
	@poetry install
	@python3 -m spacy download en_core_web_lg

jupyter.attach.venv:
	@python3 -m ipykernel install --user --name=venv

test.all:
	@pytest tests

test.coverage:
	@poetry run coverage run -m pytest -vv tests && coverage report -m --omit="*/test*,config/*.conf" --fail-under=95

lint:
	@poetry run pylint pii_codex tests

format.check:
	@black . --check

format.fix:
	@black .

version.bump.patch:
	@poetry version patch

version.bump.minor:
	@poetry version minor

version.bump.major:
	@poetry version major

package:
	@poetry build

deployment: package

