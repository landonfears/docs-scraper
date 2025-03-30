install:
	pip install -e .

update-deps:
	pip freeze > requirements.txt

run:
	scrape-docs --help

changelog-update:
	git-cliff --latest --tag v$(VERSION) -o CHANGELOG.md

changelog:
	git-cliff --latest --tag v$(VERSION) -o CHANGELOG.md
	git add CHANGELOG.md
	git commit -m "docs(changelog): update for v$(VERSION)"

release: changelog
	git tag v$(VERSION)
	git push origin main --tags

VERSION := $(shell grep '^version =' pyproject.toml | head -1 | cut -d'"' -f2)
TAG := v$(VERSION)

sync-tag:
	@if git rev-parse $(TAG) >/dev/null 2>&1; then \
	  echo "✅ Tag $(TAG) already exists."; \
	else \
	  echo "🏷  Tagging version $(TAG)..."; \
	  git tag $(TAG); \
	  git push origin $(TAG); \
	fi

bump-patch:
	bump-my-version bump patch
	git push
	$(MAKE) sync-tag

bump-minor:
	bump-my-version bump minor
	git push
	$(MAKE) sync-tag

bump-major:
	bump-my-version bump major
	git push
	$(MAKE) sync-tag