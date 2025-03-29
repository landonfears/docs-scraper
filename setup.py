from setuptools import setup

setup(
    name="scrape-docs",
    version="0.1",
    py_modules=["scrape_docs"],
    install_requires=[
        "requests",
        "beautifulsoup4",
        "markdownify",
        "python-dotenv"
    ],
    entry_points={
        "console_scripts": [
            "scrape-docs=scrape_docs:main",
        ],
    },
    author="Landon Fears",
    description="CLI tool to scrape documentation sites into markdown using proxies and ScraperAPI.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.7",
)