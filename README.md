<p align="right">
  <a href="https://github.com/landonfears/docs-scraper/releases">
    <img alt="GitHub release" src="https://img.shields.io/github/v/release/landonfears/docs-scraper?label=version">
  </a>
  <a href="https://github.com/landonfears/docs-scraper/blob/main/LICENSE">
    <img alt="MIT License" src="https://img.shields.io/github/license/landonfears/docs-scraper">
  </a>
  <a href="https://github.com/landonfears/docs-scraper/actions/workflows/release.yml">
    <img alt="Build Status" src="https://github.com/landonfears/docs-scraper/actions/workflows/release.yml/badge.svg">
  </a>
  <a href="https://www.python.org/downloads/">
    <img alt="Python" src="https://img.shields.io/badge/python-3.7%2B-blue.svg">
  </a>
</p>

# docs-scraper

**Version:** `0.3.4`

A powerful CLI tool to scrape documentation websites into Markdown using rotating proxies, ScraperAPI, and local context injection for AI code editors.

---

## 🛠 Installation (Development Mode)

```bash
pip install -e .
```

You’ll then have access to the CLI tools globally.

## 🧰 One-time Dev Setup

To install both Python and Node dependencies:

```bash
./setup-dev.sh
```

---

## 🚀 Usage: Scrape Documentation (Static Sites)

```bash
scrape-docs \
  --url https://ui.shadcn.com/docs \
  --out ~/Documentation/docs-central/shadcn
```

### With Proxy & ScraperAPI Fallback

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

---

## 🌐 Usage: Scrape SPA Docs (JS-rendered sites)

```bash
spa-scrape \
  --url https://tailwindcss.com/docs \
  --out ~/Documentation/docs-central/tailwind \
  --proxy-mode both \
  --retries 5 \
  --delay 3 \
  --timeout 60000 \
  --skip-existing \
  --headless
```

### Proxy Modes:

- `premium` → Uses your authenticated proxy (e.g. PacketStream)
- `free` → Uses ProxyScrape API
- `both` → Try premium first, then free (default)

### Premium Proxy Setup (via `.env`)

```env
PREMIUM_PROXY_USER=your_proxy_username
PREMIUM_PROXY_PASS=your_proxy_password
```

### Optional Flags:

- `--log proxy_log.txt` → Logs proxy results
- `--headless false` → Opens a visible browser for debugging
- `--skip-existing` → Skip pages already saved in output folder
- `--timeout 60000` → Increase page load timeout in ms
- `--retry-failed` → Retry from a previous `failed_urls.txt`

After scraping, any permanently failed URLs will be written to `failed_urls.txt`.
You can rerun them like this:

```bash
spa-scrape \
  --url https://tailwindcss.com/docs \
  --out ~/Documentation/docs-central/tailwind \
  --retry-failed
```

---

## 📦 Usage: Copy Docs to a Project (for AI Code Editor Context)

```bash
copy-docs shadcn prisma \
  --from ~/Documentation/docs-central \
  --to ./apps/my-new-app/docs \
  --verbose
```

---

## 🧠 Recommended Dev Flow

1. Scrape docs:

   ```bash
   scrape-docs --url https://ui.shadcn.com/docs --out ~/Documentation/docs-central/shadcn
   spa-scrape --url https://tailwindcss.com/docs --out ~/Documentation/docs-central/tailwind
   ```

2. Scaffold a project:

   ```bash
   pnpm create t3-app@latest
   ```

3. Copy docs into the project:
   ```bash
   copy-docs shadcn tailwind --from ~/Documentation/docs-central --to ./apps/my-app/docs
   ```

---

## 🛡 Environment Setup

Create a `.env` file:

```env
SCRAPERAPI_KEY=your_scraperapi_key
SCRAPERAPI_ENDPOINT=http://api.scraperapi.com
PREMIUM_PROXY_USER=your_proxy_username
PREMIUM_PROXY_PASS=your_proxy_password
```

Then run:

```bash
cp .env.example .env
```

---

## 📄 License

MIT

---

Need help extending this with doc summarization, search indexing, or AI code editor config scaffolding? PRs & issues welcome!
