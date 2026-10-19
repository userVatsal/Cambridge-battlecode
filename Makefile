# Hidden Gold Clusters — Cambridge Battlecode 2026 Autumn
# Run `make help` for the list of commands.

BOT      ?= goldrush-cpp
OPPONENT ?= starter-python
MAP      ?= expanse
JOBS     ?= 2

.PHONY: help setup build match eval snapshot bundle submit test lint view

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

setup:
	python -m pip install --upgrade cambc
	cambc init --yes .
	cambc maps pull

build:
	cambc build bots/$(BOT)

match: build
	cambc run bots/$(BOT) bots/$(OPPONENT) --map $(MAP)

eval:
	python tools/run_matches.py --bot $(BOT) --opponent $(OPPONENT) --jobs $(JOBS)

snapshot:
	@test -n "$(V)" || (echo "usage: make snapshot V=<number>" && exit 1)
	python tools/snapshot.py $(V) $(BOT)

bundle:
	mkdir -p dist
	cambc bundle bots/$(BOT) --output dist/$(BOT).zip

submit:
	cambc submit bots/$(BOT)

test:
	python -m pytest -q

lint:
	python -m ruff check bots/goldrush tools tests

view:
	cambc view
