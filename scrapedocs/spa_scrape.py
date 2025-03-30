# spa_scrape.py
# Enhanced: retries, throttling, timeout, SOCKS5/premium proxy fallback, logging, and skip-existing

import argparse
import subprocess
import time
import requests
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


def fetch_proxies_from_api(api_url: str, limit: int = 10):
    try:
        print(f"🌐 Fetching proxies from: {api_url}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        proxies = [line.strip() for line in response.text.splitlines() if line.strip()]
        return proxies[:limit]
    except Exception as e:
        print(f"❌ Failed to fetch proxies: {e}")
        return []


def log_proxy_result(proxy: str, status: str, logfile: Path):
    with open(logfile, "a") as f:
        f.write(f"{proxy} - {status}\n")


def run_puppeteer_scraper(url: str, out_dir: str, headless: bool = True, retries: int = 3, delay: int = 2, proxy: str = None, proxy_type: str = "http", timeout: int = 60000, skip_existing: bool = False):
    script_path = Path(__file__).parent / "puppeteer_scraper.js"
    args = ["node", str(script_path), url, out_dir]

    if not headless:
        args.append("--headless=false")
    if proxy:
        args.append(f"--proxy={proxy}")
        args.append(f"--proxy-type={proxy_type}")
    args.append(f"--retries={retries}")
    args.append(f"--delay={delay * 1000}")
    args.append(f"--timeout={timeout}")
    if skip_existing:
        args.append("--skip-existing")

    subprocess.run(args, check=True)


def main():
    parser = argparse.ArgumentParser(description="Scrape SPA docs using Puppeteer and convert to Markdown")
    parser.add_argument("--url", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--headless", action="store_false")
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--delay", type=int, default=2)
    parser.add_argument("--timeout", type=int, default=60000)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--proxy-mode", choices=["premium", "free", "both"], default="both")
    parser.add_argument("--proxy-type", choices=["http", "socks5"], default="http")
    parser.add_argument("--premium-user", default=os.getenv("PREMIUM_PROXY_USER"))
    parser.add_argument("--premium-pass", default=os.getenv("PREMIUM_PROXY_PASS"))
    parser.add_argument("--log", default="proxy_log.txt")
    args = parser.parse_args()

    log_path = Path(args.log).expanduser().resolve()
    log_path.write_text("")

    if args.proxy_mode == "premium" and args.premium_user and args.premium_pass:
        scheme = "socks5" if args.proxy_type == "socks5" else "http"
        premium_proxy = f"{args.premium_user}:{args.premium_pass}@proxy.packetstream.io:31112"
        try:
            print(f"🌐 Using Premium proxy: {scheme}://{premium_proxy}")
            run_puppeteer_scraper(
                args.url,
                args.out,
                headless=args.headless,
                retries=args.retries,
                delay=args.delay,
                proxy=premium_proxy,
                proxy_type=args.proxy_type,
                timeout=args.timeout,
                skip_existing=args.skip_existing
            )
            log_proxy_result(premium_proxy, "SUCCESS", log_path)
            return
        except subprocess.CalledProcessError:
            print("❌ Premium proxy failed.\n")
            log_proxy_result(premium_proxy, "FAILED", log_path)

    proxy_sources = []
    if args.proxy_mode in ("free", "both"):
        proxy_sources.append("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text")

    for source_url in proxy_sources:
        proxies = fetch_proxies_from_api(source_url, limit=20)
        for i, proxy in enumerate(proxies):
            try:
                print(f"🌐 Trying proxy [{i+1}/{len(proxies)}]: {proxy}")
                run_puppeteer_scraper(
                    args.url,
                    args.out,
                    headless=args.headless,
                    retries=args.retries,
                    delay=args.delay,
                    proxy=proxy,
                    proxy_type=args.proxy_type,
                    timeout=args.timeout,
                    skip_existing=args.skip_existing
                )
                log_proxy_result(proxy, "SUCCESS", log_path)
                return
            except subprocess.CalledProcessError:
                print(f"❌ Proxy failed: {proxy}\n")
                log_proxy_result(proxy, "FAILED", log_path)
                continue

    print("⚠️ All proxies failed. Trying without proxy...")
    try:
        run_puppeteer_scraper(
            args.url,
            args.out,
            headless=args.headless,
            retries=args.retries,
            delay=args.delay,
            proxy=None,
            timeout=args.timeout,
            skip_existing=args.skip_existing
        )
        log_proxy_result("NO_PROXY", "SUCCESS", log_path)
    except subprocess.CalledProcessError:
        log_proxy_result("NO_PROXY", "FAILED", log_path)
        print("❌ Final fallback without proxy failed.")


if __name__ == "__main__":
    main()