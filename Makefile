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

bump-patch:
	bump-my-version bump patch && git push

bump-minor:
	bump-my-version bump minor && git push

bump-major:
	bump-my-version bump major && git push