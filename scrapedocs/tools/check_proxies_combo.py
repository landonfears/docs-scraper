#!/usr/bin/env python3

import requests
import concurrent.futures
import argparse

TEST_URL = "http://httpbin.org/ip"
TIMEOUT = 5

PROXY_TYPES = {
    "http": "HTTP",
    "socks4": "SOCKS4",
    "socks5": "SOCKS5"
}

def fetch_proxies_from_api(api_url, limit=None, verbose=False):
    try:
        res = requests.get(api_url, timeout=10)
        res.raise_for_status()
        proxies = res.text.strip().splitlines()
        if limit:
            proxies = proxies[:limit]
        if verbose:
            print(f"📥 {len(proxies)} proxies fetched")
        return proxies
    except Exception as e:
        print(f"❌ Failed to fetch proxies from {api_url}: {e}")
        return []

def test_proxy(proxy_url, proxy_type, verbose=False):
    proxy_schema = f"{proxy_type}://"
    proxy_dict = {"http": proxy_schema + proxy_url, "https": proxy_schema + proxy_url}
    try:
        response = requests.get(TEST_URL, proxies=proxy_dict, timeout=TIMEOUT)
        if response.status_code == 200:
            ip = response.json().get("origin")
            if verbose:
                print(f"✅ {proxy_type.upper()}: {proxy_url} → {ip}")
            return proxy_url
    except Exception:
        if verbose:
            print(f"❌ {proxy_type.upper()}: {proxy_url}")
    return None

def check_group(api_url, proxy_type, limit=None, verbose=False):
    print(f"\n🔎 Checking {PROXY_TYPES[proxy_type]} proxies...")
    proxies = fetch_proxies_from_api(api_url, limit, verbose)
    working = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(test_proxy, p, proxy_type, verbose): p for p in proxies}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                working.append(result)

    print(f"✅ {len(working)} working {proxy_type.upper()} proxies\n")
    return working

def main():
    parser = argparse.ArgumentParser(description="Check proxies from multiple proxy types and APIs.")
    parser.add_argument("--http-api", help="URL for HTTP proxies")
    parser.add_argument("--socks4-api", help="URL for SOCKS4 proxies")
    parser.add_argument("--socks5-api", help="URL for SOCKS5 proxies")
    parser.add_argument("--limit", type=int, help="Max proxies per type")
    parser.add_argument("--verbose", action="store_true", help="Show per-proxy logs")
    parser.add_argument("--save", action="store_true", help="Save working proxies to separate files")

    args = parser.parse_args()

    all_results = {}

    if args.http_api:
        all_results['http'] = check_group(args.http_api, "http", args.limit, args.verbose)

    if args.socks4_api:
        all_results['socks4'] = check_group(args.socks4_api, "socks4", args.limit, args.verbose)

    if args.socks5_api:
        all_results['socks5'] = check_group(args.socks5_api, "socks5", args.limit, args.verbose)

    if args.save:
        for proxy_type, proxies in all_results.items():
            filename = f"proxies_{proxy_type}.txt"
            with open(filename, "w") as f:
                f.write("\n".join(proxies))
            print(f"💾 Saved {len(proxies)} {proxy_type.upper()} proxies to {filename}")

if __name__ == "__main__":
    main()