#!/usr/bin/env python3

import requests
import concurrent.futures
import argparse

TEST_URL = "http://httpbin.org/ip"
TIMEOUT = 5

def fetch_proxies_from_api(api_url, limit=None, verbose=False):
    print(f"📡 Fetching proxies from: {api_url}")
    try:
        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        proxies = res.text.strip().splitlines()
        if limit:
            proxies = proxies[:limit]
        print(f"🔍 Retrieved {len(proxies)} proxies to test.\n")
        return proxies
    except Exception as e:
        print(f"❌ Failed to fetch proxies: {e}")
        return []

def test_proxy(proxy_url, proxy_type, verbose=False):
    proxy_schema = f"{proxy_type}://"
    proxy_dict = {"http": proxy_schema + proxy_url, "https": proxy_schema + proxy_url}
    try:
        response = requests.get(TEST_URL, proxies=proxy_dict, timeout=TIMEOUT)
        if response.status_code == 200:
            ip = response.json().get("origin")
            if verbose:
                print(f"✅ {proxy_url} → {ip}")
            return proxy_url
    except Exception:
        if verbose:
            print(f"❌ {proxy_url}")
    return None

def main():
    parser = argparse.ArgumentParser(description="Check and validate proxies from a live API.")
    parser.add_argument("--api", required=True, help="Proxy API URL returning plain text list")
    parser.add_argument("--limit", type=int, help="Max number of proxies to check")
    parser.add_argument("--save", help="Save working proxies to a file (e.g., proxies_valid.txt)")
    parser.add_argument("--proxy-type", choices=["http", "socks4", "socks5"], default="http",
                        help="Type of proxies to test (default: http)")
    parser.add_argument("--verbose", action="store_true", help="Show results for each proxy")

    args = parser.parse_args()

    proxies = fetch_proxies_from_api(args.api, limit=args.limit, verbose=args.verbose)
    if not proxies:
        print("🚫 No proxies to check.")
        return

    print(f"🚀 Validating {len(proxies)} {args.proxy_type.upper()} proxies...\n")
    working = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(test_proxy, proxy, args.proxy_type, args.verbose): proxy for proxy in proxies}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                working.append(result)

    print(f"\n✅ {len(working)} working proxies found.")

    if args.save:
        with open(args.save, "w") as f:
            f.write("\n".join(working))
        print(f"💾 Saved to: {args.save}")

if __name__ == "__main__":
    main()