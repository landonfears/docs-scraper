install:
	pip install -e .

update-deps:
	pip freeze > requirements.txt

run:
	scrape-docs --help