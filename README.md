<p align="right">
  <a href="https://github.com/landonfears/scrape-docs/releases">
    <img alt="GitHub release" src="https://img.shields.io/github/v/release/landonfears/scrape-docs?label=version">
  </a>
  <a href="https://github.com/landonfears/scrape-docs/blob/main/LICENSE">
    <img alt="MIT License" src="https://img.shields.io/github/license/landonfears/scrape-docs">
  </a>
  <a href="https://github.com/landonfears/scrape-docs/actions/workflows/release.yml">
    <img alt="Build Status" src="https://github.com/landonfears/scrape-docs/actions/workflows/release.yml/badge.svg">
  </a>
  <a href="https://www.python.org/downloads/">
    <img alt="Python" src="https://img.shields.io/badge/python-3.7%2B-blue.svg">
  </a>
</p>

# scrape-docs

**Version:** `0.2.2`

A powerful CLI tool to scrape documentation websites into Markdown using rotating proxies, ScraperAPI, and local context injection for GitHub Copilot.

---

## 🛠 Installation (Development Mode)

```bash
pip install -e .
```

You’ll then have access to the `scrape-docs` command globally.

---

## 🚀 Usage: Scrape Documentation

### Basic Example

```bash
scrape-docs \
  --url https://ui.shadcn.com/docs \
  --out ~/Documentation/docs-central/shadcn
```

### With Proxy Fetching & ScraperAPI Fallback

```bash
scrape-docs \
  --url https://docs.firecrawl.dev \
  --out ~/Documentation/docs-central/firecrawl \
  --http-api "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text" \
  --render \
  --session 42 \
  --country US \
  --restrict-path /docs \
  --limit 100 \
  --verbose
```

### Optional Flags

- `--dry-run` → Print URLs without scraping (estimate credit usage)
- `--max-depth` → Limit crawl depth from root
- `--restrict-path` → Only scrape URLs that begin with `/docs`

---

## 📦 Usage: Copy Docs to a Project (for Copilot Context)

Use this tool to copy relevant documentation folders into a new project after scaffolding:

```bash
copy-docs shadcn prisma \
  --from ~/Documentation/docs-central \
  --to ./apps/my-new-app/docs \
  --verbose
```

### Options

- `--skip-existing` → Skip if the destination folder already exists
- Prompts to overwrite if not skipped

---

## 💡 Recommended Dev Flow

1. Scrape docs into a local central archive:

   ```bash
   scrape-docs --url https://ui.shadcn.com/docs --out ~/Documentation/docs-central/shadcn
   ```

2. Scaffold a new project:

   ```bash
   pnpm create t3-app@latest
   ```

3. Inject relevant context:
   ```bash
   copy-docs shadcn tailwind --from ~/Documentation/docs-central --to ./apps/new-project/docs
   ```

Now GitHub Copilot Chat will understand your tooling’s docs directly in your project! ⚡

---

## 🛡 Environment Setup

Create a `.env` file:

```env
SCRAPERAPI_KEY=your_api_key_here
SCRAPERAPI_ENDPOINT=http://api.scraperapi.com
```

Then run:

```bash
cp .env.example .env
```

---

## 📄 License

MIT

---

Need help extending this with doc summarization, search indexing, or Copilot config scaffolding? PRs & issues welcome!
