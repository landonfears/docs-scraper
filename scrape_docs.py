#!/usr/bin/env python3

import os
import requests
import random
import time
import argparse
import json
from urllib.parse import urljoin, urlparse, quote_plus
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

visited = set()

# ------------------ Proxy Utils ------------------ #
def fetch_proxies_from_api(api_url, proxy_type, limit=None, verbose=False):
    try:
        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        proxies = res.text.strip().splitlines()
        if limit:
            proxies = proxies[:limit]
        if verbose:
            print(f"✅ {len(proxies)} {proxy_type.upper()} proxies fetched")
        return proxies
    except Exception as e:
        print(f"❌ Failed to fetch {proxy_type.upper()} proxies: {e}")
        return []

def test_proxy(proxy_url, proxy_type, headers=None, verbose=False):
    schema = f"{proxy_type}://"
    proxy = {"http": schema + proxy_url, "https": schema + proxy_url}
    try:
        res = requests.get("http://httpbin.org/ip", proxies=proxy, headers=headers, timeout=5)
        if res.status_code == 200:
            if verbose:
                print(f"✅ Valid {proxy_type.upper()} proxy: {proxy_url}")
            return proxy_url
    except Exception:
        if verbose:
            print(f"❌ Failed {proxy_type.upper()} proxy: {proxy_url}")
    return None

def load_and_validate_proxies(args, headers):
    sources = {
        "http": args.http_api,
        "socks4": args.socks4_api,
        "socks5": args.socks5_api
    }

    valid_proxies = {}
    for proxy_type, api in sources.items():
        if not api:
            continue
        proxies = fetch_proxies_from_api(api, proxy_type, limit=args.limit, verbose=args.verbose)
        working = []
        for p in proxies:
            result = test_proxy(p, proxy_type, headers=headers, verbose=args.verbose)
            if result:
                working.append(result)
        if working:
            valid_proxies[proxy_type] = working

    if args.proxy_type:
        selected = args.proxy_type
        if selected not in valid_proxies:
            print(f"🚫 No valid proxies found for type: {selected.upper()}")
            return None, selected
        return valid_proxies[selected], selected

    if valid_proxies:
        auto_type = next(iter(valid_proxies))
        return valid_proxies[auto_type], auto_type

    print("🚫 No valid proxies found.")
    return None, None

def get_working_proxy(proxies, headers, proxy_type="http", verbose=False):
    random.shuffle(proxies)
    for proxy_url in proxies:
        proxy = {"http": f"{proxy_type}://{proxy_url}", "https": f"{proxy_type}://{proxy_url}"}
        try:
            if verbose:
                print(f"🔌 Trying proxy: {proxy_url}")
            res = requests.get("http://httpbin.org/ip", headers=headers, proxies=proxy, timeout=5)
            if res.status_code == 200:
                if verbose:
                    print(f"✅ Proxy OK: {proxy_url}")
                return proxy
        except Exception:
            if verbose:
                print(f"❌ Proxy failed: {proxy_url}")
    return None

# ------------------ Scraper ------------------ #
def is_valid_link(href, base_netloc, restrict_path=None):
    if not href:
        return False
    parsed = urlparse(href)
    if parsed.netloc and parsed.netloc != base_netloc:
        return False
    if any(x in href for x in ["#", "?"]):
        return False
    if restrict_path and not parsed.path.startswith(restrict_path):
        return False
    return True

def save_markdown(base_url, url, content, output_dir):
    rel_path = urlparse(url).path.strip("/")
    if rel_path == "":
        rel_path = "index"
    filename = rel_path.replace("/", "_") + ".md"
    filepath = os.path.join(output_dir, filename)

    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {urlparse(url).path or 'Home'}\n\n")
        f.write(content)

def try_request_with_fallback(full_url, headers, scraperapi_config, proxy, timeout=10, dry_run=False):
    if dry_run:
        print(f"[DRY-RUN] Would request: {full_url}")
        return None
    try:
        if scraperapi_config:
            req_url = f"{scraperapi_config['endpoint']}?api_key={scraperapi_config['key']}&url={quote_plus(full_url)}"
            if scraperapi_config.get("render"):
                req_url += "&render=true"
            if scraperapi_config.get("country_code"):
                req_url += f"&country_code={scraperapi_config['country_code']}"
            if scraperapi_config.get("session_number"):
                req_url += f"&session_number={scraperapi_config['session_number']}"
            res = requests.get(req_url, headers=headers, timeout=timeout)
            res.raise_for_status()
            return res
        else:
            res = requests.get(full_url, headers=headers, proxies=proxy, timeout=timeout)
            res.raise_for_status()
            return res
    except Exception:
        return None

def crawl(base_url, current_url, output_dir, base_netloc, headers=None, proxies=None,
          proxy_type="http", limit=None, verbose=False, follow_links=True, delay_range=None,
          scraperapi_config=None, dry_run=False, max_depth=None, depth=0, restrict_path=None):
    if limit is not None and len(visited) >= limit:
        return

    if max_depth is not None and depth > max_depth:
        return

    full_url = urljoin(base_url, current_url)
    if full_url in visited:
        return
    visited.add(full_url)

    if verbose:
        print(f"📄 Fetching: {full_url}")

    if delay_range:
        delay = random.uniform(*delay_range)
        if verbose:
            print(f"⏳ Waiting {delay:.2f}s before request...")
        time.sleep(delay)

    proxy = None
    if proxies:
        proxy = get_working_proxy(proxies, headers, proxy_type, verbose)

    res = try_request_with_fallback(full_url, headers, scraperapi_config, proxy, dry_run=dry_run)
    if dry_run:
        return

    if not res:
        print(f"❌ Failed to fetch with ScraperAPI. Trying with proxy fallback...")
        if proxy:
            try:
                res = requests.get(full_url, headers=headers, proxies=proxy, timeout=10)
                res.raise_for_status()
            except Exception as e:
                print(f"⚠️ Final fallback failed for {full_url}: {e}")
                return
        else:
            return

    soup = BeautifulSoup(res.text, "html.parser")
    main = soup.find("main")
    if not main:
        return

    markdown = md(str(main))
    save_markdown(base_url, full_url, markdown, output_dir)

    if follow_links:
        for link in main.find_all("a", href=True):
            href = link['href']
            if is_valid_link(href, base_netloc, restrict_path=restrict_path):
                crawl(base_url, href, output_dir, base_netloc, headers, proxies,
                      proxy_type, limit, verbose, follow_links, delay_range,
                      scraperapi_config, dry_run=dry_run, max_depth=max_depth, depth=depth + 1,
                      restrict_path=restrict_path)

# ------------------ Main CLI ------------------ #
def main():
    parser = argparse.ArgumentParser(
        description="Scrape documentation sites into Markdown using rotating proxies and optional ScraperAPI integration."
    )
    parser.add_argument("--url", required=True, help="Base URL of the docs site to start scraping")
    parser.add_argument("--out", required=True, help="Directory where Markdown files will be saved")
    parser.add_argument("--limit", type=int, help="Max number of pages to scrape")
    parser.add_argument("--max-depth", type=int, help="Max number of link levels to follow from the start URL")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    parser.add_argument("--skip-links", action="store_true", help="Do not follow internal links beyond the base page")
    parser.add_argument("--delay-min", type=float, default=0, help="Minimum delay (in seconds) between requests")
    parser.add_argument("--delay-max", type=float, default=0, help="Maximum delay (in seconds) between requests")
    parser.add_argument("--proxy-list", help="Path to file containing list of proxies to rotate through")
    parser.add_argument("--proxy-type", choices=["http", "socks4", "socks5"], help="Type of proxies in the proxy list")
    parser.add_argument("--http-api", help="URL to fetch live HTTP proxies")
    parser.add_argument("--socks4-api", help="URL to fetch live SOCKS4 proxies")
    parser.add_argument("--socks5-api", help="URL to fetch live SOCKS5 proxies")
    parser.add_argument("--save-proxies", help="File to save validated working proxies")
    parser.add_argument("--headers", help="Path to JSON file with custom HTTP headers")
    parser.add_argument("--render", action="store_true", help="Use JS rendering via ScraperAPI (costs credits)")
    parser.add_argument("--country", help="Geo-targeting via ScraperAPI (e.g., US, DE)")
    parser.add_argument("--session", help="Sticky session ID for ScraperAPI to reuse same IP")
    parser.add_argument("--dry-run", action="store_true", help="Print intended requests without making them")
    parser.add_argument("--restrict-path", help="Only crawl URLs that start with this path (e.g., /docs)")

    args = parser.parse_args()

    base_url = args.url.rstrip("/")
    output_dir = os.path.abspath(args.out)
    base_netloc = urlparse(base_url).netloc

    headers = None
    if args.headers:
        with open(args.headers, "r") as f:
            headers = json.load(f)
    else:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            )
        }

    delay_range = None
    if args.delay_min > 0 or args.delay_max > 0:
        delay_range = (args.delay_min, args.delay_max)

    proxies = None
    proxy_type = args.proxy_type or "http"

    if args.http_api or args.socks4_api or args.socks5_api:
        proxies, proxy_type = load_and_validate_proxies(args, headers)
    elif args.proxy_list:
        with open(args.proxy_list, "r") as f:
            proxies = [line.strip() for line in f if line.strip()]

    if proxies and args.save_proxies:
        with open(args.save_proxies, "w") as f:
            f.write("\n".join(proxies))
        print(f"📅 Saved {len(proxies)} working {proxy_type.upper()} proxies to {args.save_proxies}")

    scraperapi_config = None
    if os.getenv("SCRAPERAPI_KEY"):
        scraperapi_config = {
            "key": os.getenv("SCRAPERAPI_KEY"),
            "endpoint": os.getenv("SCRAPERAPI_ENDPOINT", "http://api.scraperapi.com"),
            "render": args.render,
            "country_code": args.country,
            "session_number": args.session
        }

    os.makedirs(output_dir, exist_ok=True)

    crawl(
        base_url,
        "/",
        output_dir,
        base_netloc,
        headers=headers,
        proxies=proxies,
        proxy_type=proxy_type,
        limit=args.limit,
        verbose=args.verbose,
        follow_links=not args.skip_links,
        delay_range=delay_range,
        scraperapi_config=scraperapi_config,
        dry_run=args.dry_run,
        max_depth=args.max_depth,
        restrict_path=args.restrict_path
    )

    print("\n✅ Done!")

if __name__ == "__main__":
    main()
