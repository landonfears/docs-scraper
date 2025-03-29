# scrape-docs

A CLI tool to scrape technical documentation into markdown using rotating proxies and optional ScraperAPI support.

## Usage

```bash
scrape-docs --url https://example.com/docs --out ./docs
```

<!---
USAGE
scrape-docs \
  --url https://docs.firecrawl.dev \
  --out ./docs/firecrawl \
  --proxy-list proxies.txt \
  --proxy-type http \
  --render \
  --session 42 \
  --country US \
  --verbose

SCRAPERAPI USAGE
scrape-docs \
  --url https://docs.firecrawl.dev \
  --out ./docs/firecrawl \
  --delay-min 1 \
  --delay-max 2 \
  --verbose

scrape-docs \
  --url https://ui.shadcn.com/docs \
  --out ./docs/shadcn \
  --restrict-path /docs \
  --verbose

python check_proxies_combo.py \
  --http-api "https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text" \
  --socks4-api "https://api.proxyscrape.com/v2/socks4?request=displayproxies&format=text" \
  --socks5-api "https://api.proxyscrape.com/v2/socks5?request=displayproxies&format=text" \
  --limit 30 \
  --verbose \
  --save

If you ever want to move or update the tool:
 	1.	Just git clone or copy the folder to another machine
 	2.	Run pip install -e . again
--->
