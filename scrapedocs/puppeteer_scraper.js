const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const fs = require("fs");
const path = require("path");
const TurndownService = require("turndown");

puppeteer.use(StealthPlugin());

const turndown = new TurndownService();

function sanitizeMarkdown(md, verbose = false) {
  const lines = md.split("\n");
  const result = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i].replace(/[\u200b\u200c\u200d\u2060]/g, "");
    const next = (lines[i + 1] || "").replace(
      /[\u200b\u200c\u200d\u2060]/g,
      ""
    );
    const trimmed = line.trim();

    const hasBalancedBrackets = /^\s*\[.*?\]\s*$/.test(trimmed);
    const isLikelyMarkdown =
      hasBalancedBrackets ||
      /^(\*+|#+|\d+\.|\[.*?\]\(.*?\)|```|>|-{3,}|_{3,})$/.test(trimmed) ||
      /^[\[\(]{1,2}$/.test(trimmed);

    const isBrokenMarkdownLink =
      /^\s*\[.*?\]\s*$/.test(trimmed) && /^\s*\]\(.*?\)/.test(next.trim());

    const shouldRemove =
      !isLikelyMarkdown &&
      !isBrokenMarkdownLink &&
      (trimmed.length > 200 ||
        /!function|window\.|document\.|:where\\|--/.test(trimmed) ||
        (trimmed.match(/[^\w\s]/g) || []).length / Math.max(trimmed.length, 1) >
          0.5);

    if (shouldRemove) {
      if (verbose) console.log("🗑️ Removing:", line.slice(0, 120));
    } else {
      result.push(line);
    }
  }

  return result.join("\n").trim();
}

async function scrapeUrls(
  page,
  urls,
  baseUrl,
  outputDir,
  retries,
  delay,
  timeout,
  skipExisting,
  visited,
  failedUrls
) {
  while (urls.length > 0) {
    const url = urls.pop();
    const cleanUrl = url.replace(/\/$/, ""); // normalize without trailing slash
    if (visited.has(cleanUrl)) continue;
    visited.add(cleanUrl);

    const urlPath = new URL(url).pathname.replace(/\/$/, "");
    const filename = urlPath.split("/").filter(Boolean).join("-") || "index";
    const outPath = path.join(outputDir, `${filename}.md`);

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        console.log(`📄 Scraping: ${url} (Attempt ${attempt})`);
        await page.goto(url, { waitUntil: "domcontentloaded", timeout });
        await page.waitForSelector("body", { timeout: 5000 });
        await page.waitForTimeout(3000);

        const html = await page.content();
        let markdown = turndown.turndown(html);
        markdown = sanitizeMarkdown(markdown, false);

        if (!html || html.length < 1000) {
          throw new Error(
            "Page content appears too short or failed to load properly."
          );
        }

        if (skipExisting && fs.existsSync(outPath)) {
          console.log(`⏩ Skipping save for already scraped: ${url}`);
        } else {
          fs.writeFileSync(outPath, markdown);
        }

        const links = await page.$$eval("a", (as) =>
          as
            .map((a) => a.href.split("#")[0])
            .filter((href) =>
              href.startsWith(location.origin + location.pathname)
            )
        );

        links.forEach((link) => {
          const cleanLink = link.replace(/\/$/, "");
          const filename = slugify(cleanLink);
          const outPath = path.join(outputDir, `${filename}.md`);

          if (!visited.has(cleanLink) && cleanLink.startsWith(baseUrl)) {
            if (!skipExisting || !fs.existsSync(outPath)) {
              urls.push(cleanLink);
            } else {
              console.log(`✅ Already scraped: ${cleanLink}`);
            }
          }
        });

        break; // success
      } catch (err) {
        if (err.message.toLowerCase().includes("tunnel")) {
          throw err;
        }

        console.warn(
          `⚠️ Failed to scrape ${url} (Attempt ${attempt}): ${err.message}`
        );
        if (attempt === retries) {
          console.error(`❌ Giving up on ${url}`);
          failedUrls.push(url);
        } else {
          await new Promise((res) => setTimeout(res, delay));
        }
      }
    }
  }

  if (failedUrls.length > 0) {
    const failLogPath = path.join(outputDir, "failed_urls.txt");
    fs.writeFileSync(failLogPath, failedUrls.join("\n"));
    console.log(`📝 Failed URLs logged to ${failLogPath}`);
  }
}

function slugify(url) {
  const pathname = new URL(url).pathname;
  return (
    pathname.replace(/\/$/, "").split("/").filter(Boolean).join("-") || "index"
  );
}

async function getLinks(url, page, selector, timeout) {
  await page.goto(url, { waitUntil: "domcontentloaded", timeout });
  await page.waitForTimeout(3000);

  return await page.evaluate((selector) => {
    const anchors = Array.from(document.querySelectorAll(selector));
    return anchors.map((a) => ({
      href: new URL(a.getAttribute("href"), location.origin).href,
      text: a.textContent.trim(),
    }));
  }, selector);
}

function filterByOrigin(links, baseUrl) {
  return links.filter((link) => isSameDomain(link.href, baseUrl));
}

function isSameDomain(url, baseUrl) {
  const urlObj = new URL(url);
  const baseUrlObj = new URL(baseUrl);
  return (
    urlObj?.origin === baseUrlObj?.origin &&
    urlObj?.pathname?.startsWith(baseUrlObj?.pathname)
  );
}

async function scrapeViaClicks(
  page,
  baseUrl,
  outputDir,
  retries,
  delay,
  timeout,
  skipExisting,
  navSelector = ".sidebar a"
) {
  const visited = new Set();
  const visitedPrevious = new Set();
  const failed = [];

  // Only add existing files to visited if skipExisting is true
  if (skipExisting) {
    const baseUrlObj = new URL(baseUrl);
    const baseUrlWithoutPath = `${baseUrlObj.origin}`;

    const existingFiles = fs
      .readdirSync(outputDir)
      .filter((file) => file.endsWith(".md"))
      .map((file) => {
        const filename = path.basename(file, ".md");
        // Reconstruct the URL by splitting the filename and joining with slashes
        const urlPath = filename.split("-").join("/");
        return `${baseUrlWithoutPath}/${urlPath}`;
      });
    existingFiles.forEach((url) => visitedPrevious.add(url));
  }

  let links = filterByOrigin(
    await getLinks(baseUrl, page, navSelector, timeout),
    baseUrl
  );

  while (links.length > 0) {
    const link = links.shift();
    const href = link.href;

    if (visited.has(href)) {
      console.log(`✅ Already scraped: ${href}`);
      continue;
    }
    visited.add(href);
    links = [
      ...links,
      ...filterByOrigin(await getLinks(href, page, navSelector), baseUrl),
    ];
    if (visitedPrevious.has(href)) {
      console.log(`✅ Already scraped in the past: ${href}`);
      continue;
    }

    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        console.log(`🖱️ Clicking and scraping: ${href} (Attempt ${attempt})`);
        await page.evaluate((targetHref) => {
          const link = Array.from(document.querySelectorAll("a[href]")).find(
            (a) => new URL(a.href, location.origin).href === targetHref
          );
          if (link) link.click();
        }, href);

        await page.waitForTimeout(3000);
        await page.waitForSelector("main, .content, article, div.flex", {
          timeout: 5000,
        });

        const html = await page.content();
        let markdown = turndown.turndown(html);
        markdown = sanitizeMarkdown(markdown, false);
        const filename = slugify(href);
        const outPath = path.join(outputDir, `${filename}.md`);

        if (!html || html.length < 1000) {
          throw new Error("Page content too short");
        }

        if (skipExisting && fs.existsSync(outPath)) {
          console.log(`⏩ Skipping existing: ${href}`);
        } else {
          fs.writeFileSync(outPath, markdown);
        }

        break;
      } catch (err) {
        console.warn(
          `⚠️ Failed to click/scrape ${href} (Attempt ${attempt}): ${err.message}`
        );
        if (attempt === retries) failed.push(href);
        else await new Promise((res) => setTimeout(res, delay));
      }
    }
  }

  if (failed.length > 0) {
    fs.writeFileSync("failed_clicks.txt", failed.join("\n"));
    console.log(`❌ Some pages failed via click: logged to failed_clicks.txt`);
  }
}

async function scrapeSite(
  baseUrl,
  outputDir,
  headless = true,
  retries = 3,
  delay = 2000,
  proxy = null,
  proxyType = "http",
  timeout = 30000,
  skipExisting = false,
  retryFailedOnly = false,
  clickNav = false,
  navSelector = ".sidebar a"
) {
  async function launchAndScrape(useProxy = true) {
    const launchArgs = ["--no-sandbox", "--disable-setuid-sandbox"];
    let proxyHost = null;
    let auth = null;

    if (useProxy && proxy) {
      let proxyPrefix = "http://";
      if (proxyType === "socks5") {
        proxyPrefix = "socks5://";
      } else if (proxyType === "socks4") {
        proxyPrefix = "socks4://";
      }
      if (proxy.includes("@")) {
        const [creds, host] = proxy.split("@");
        const [username, password] = creds.split(":");
        auth = { username, password };
        proxyHost = host;
      } else {
        proxyHost = proxy;
      }
      launchArgs.push(`--proxy-server=${proxyType}://${proxyHost}`);
      console.log(`🌍 Using proxy: ${proxyType}://${proxyHost}`);
    }

    const browser = await puppeteer.launch({
      headless: headless ? "new" : false,
      args: launchArgs,
    });
    const context = await browser.createIncognitoBrowserContext();
    const page = await context.newPage();

    await page.setUserAgent(
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    );
    await page.setExtraHTTPHeaders({ "Accept-Language": "en-US,en;q=0.9" });
    if (auth) await page.authenticate(auth);

    page.on("error", (err) => {
      console.error("🔥 Page crashed:", err);
      throw new Error("Page crashed");
    });

    await page.setRequestInterception(true);
    page.on("request", (req) => {
      if (["image", "stylesheet", "font"].includes(req.resourceType())) {
        req.abort();
      } else {
        req.continue();
      }
    });

    fs.mkdirSync(outputDir, { recursive: true });

    try {
      if (clickNav) {
        await scrapeViaClicks(
          page,
          baseUrl,
          outputDir,
          retries,
          delay,
          timeout,
          skipExisting,
          navSelector
        );
      } else {
        const visited = new Set();
        const failedUrls = [];
        const toVisit = retryFailedOnly
          ? fs
              .readFileSync(path.join(outputDir, "failed_urls.txt"), "utf-8")
              .split("\n")
              .filter(Boolean)
          : [baseUrl];
        await scrapeUrls(
          page,
          toVisit,
          baseUrl,
          outputDir,
          retries,
          delay,
          timeout,
          skipExisting,
          visited,
          failedUrls
        );
      }
    } catch (error) {
      await browser.close();
      if (useProxy && error.message.toLowerCase().includes("tunnel")) {
        console.warn(
          "⚠️ Proxy failed due to tunnel error. Retrying without proxy..."
        );
        return await launchAndScrape(false);
      } else {
        throw error;
      }
    }

    await browser.close();
    console.log("✅ Done scraping.");
  }

  try {
    await launchAndScrape(proxy ? true : false);
  } catch (error) {
    console.error("❌ Scrape Site Error:", error);
  }
}

if (require.main === module) {
  const args = process.argv.slice(2);
  const url = args[0];
  const outDir = args[1];

  const headless = !args.includes("--headless=false");
  const retriesArg = args.find((arg) => arg.startsWith("--retries="));
  const delayArg = args.find((arg) => arg.startsWith("--delay="));
  const timeoutArg = args.find((arg) => arg.startsWith("--timeout="));
  const proxyArg = args.find((arg) => arg.startsWith("--proxy="));
  const proxyTypeArg = args.find((arg) => arg.startsWith("--proxy-type="));
  const retryFailedOnly = args.includes("--retry-failed");
  const clickNav = args.includes("--click-nav");
  const skipExisting = args.includes("--skip-existing");
  const navSelectorArg = args.find((arg) => arg.startsWith("--nav-selector="));

  const retries = retriesArg ? parseInt(retriesArg.split("=")[1]) : 3;
  const delay = delayArg ? parseInt(delayArg.split("=")[1]) : 2000;
  const timeout = timeoutArg ? parseInt(timeoutArg.split("=")[1]) : 30000;
  const proxy = proxyArg ? proxyArg.split("=")[1] : null;
  const proxyType = proxyTypeArg ? proxyTypeArg.split("=")[1] : "http";
  const navSelector = navSelectorArg
    ? navSelectorArg.split("=")[1]
    : ".sidebar a";

  if (!url || !outDir) {
    console.error(
      "Usage: node puppeteer_scraper.js <url> <outputDir> [--headless=false] [--retries=N] [--delay=MS] [--timeout=MS] [--proxy=ip:port] [--proxy-type=http|socks4|socks5] [--skip-existing] [--retry-failed] [--click-nav] [--nav-selector='selector']"
    );
    process.exit(1);
  }

  scrapeSite(
    url,
    outDir,
    headless,
    retries,
    delay,
    proxy,
    proxyType,
    timeout,
    skipExisting,
    retryFailedOnly,
    clickNav,
    navSelector
  );
}

module.exports = scrapeSite;
module.exports.sanitizeMarkdown = sanitizeMarkdown;
