install:
	pip install -e .

update-deps:
	pip freeze > requirements.txt

run:
	scrape-docs --help

VERSION ?= $(shell grep '^version =' pyproject.toml | head -1 | cut -d'"' -f2)

changelog:
	git-cliff -o CHANGELOG.md
	git add CHANGELOG.md
	git commit -m "docs(changelog): update for v$(VERSION)"

release: changelog
	git tag v$(VERSION)
	git push origin main --tags

# make release v=0.2.0