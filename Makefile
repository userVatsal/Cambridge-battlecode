# Hidden Gold Clusters — Cambridge Battlecode 2026 Autumn
# Run `make help` for the list of commands.

BOT      ?= goldrush-cpp
OPPONENT ?= starter-python
MAP      ?= expanse
JOBS     ?= 2
# macOS has python3 but no plain python unless a virtual environment is active.
PYTHON   ?= $(shell command -v python >/dev/null 2>&1 && echo python || echo python3)

.PHONY: help setup build match eval snapshot bundle submit test lint view scout

help:
	@echo "make setup                 install cambc, SDK, starters and the map pool"
	@echo "make build    [BOT=]       compile a bot (default goldrush-cpp; BOT=goldrush for Python)"
	@echo "make match    [BOT= OPPONENT= MAP=]  play one match and print the result"
	@echo "make eval     [BOT= OPPONENT=]       play every map from both sides"
	@echo "make snapshot V=6 [BOT=]   freeze a bot as bots/<bot>-v6 (regression baseline)"
	@echo "make bundle   [BOT=]       build the upload ZIP in dist/"
	@echo "make submit   [BOT=]       upload to the ladder (needs 'cambc login' first)"
	@echo "make test / make lint      unit tests and style checks (no engine needed)"
	@echo "make view                  open the most recent replay in the visualiser"
	@echo "make scout   [TOP=12]      download all matches of the top ladder teams as JSON (needs cambc login)"

setup:
	$(PYTHON) -m pip install --upgrade cambc
	cambc init --yes .
	cambc maps pull

build:
	cambc build bots/$(BOT)

match: build
	cambc run bots/$(BOT) bots/$(OPPONENT) --map $(MAP)

eval:
	$(PYTHON) tools/run_matches.py --bot $(BOT) --opponent $(OPPONENT) --jobs $(JOBS)

snapshot:
	@test -n "$(V)" || (echo "usage: make snapshot V=<number>" && exit 1)
	$(PYTHON) tools/snapshot.py $(V) $(BOT)

bundle:
	mkdir -p dist
	cambc bundle bots/$(BOT) --output dist/$(BOT).zip

submit:
	cambc submit bots/$(BOT)

test:
	$(PYTHON) -m pytest -q

lint:
	$(PYTHON) -m ruff check bots/goldrush tools tests

view:
	cambc view

TOP ?= 12
scout:
	$(PYTHON) tools/fetch_matches.py fetch --top $(TOP)
	$(PYTHON) tools/fetch_matches.py report
	$(PYTHON) tools/analyse_scout.py data
