// puppeteer_scraper.js with --retry-failed mode

const puppeteer = require("puppeteer-extra");
const StealthPlugin = require("puppeteer-extra-plugin-stealth");
const fs = require("fs");
const path = require("path");
const TurndownService = require("turndown");

puppeteer.use(StealthPlugin());

const turndown = new TurndownService();

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
    if (visited.has(url)) continue;
    visited.add(url);

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
        const markdown = turndown.turndown(html);

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
            .map((a) => a.href)
            .filter((href) => href.includes("/docs") && href.startsWith("http"))
        );

        links.forEach((link) => {
          if (!visited.has(link) && link.startsWith(baseUrl)) {
            urls.push(link);
          }
        });

        break; // success
      } catch (err) {
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
  retryFailedOnly = false
) {
  const launchArgs = ["--no-sandbox", "--disable-setuid-sandbox"];
  let proxyHost = null;
  let auth = null;

  if (proxy) {
    const proxyPrefix = proxyType === "socks5" ? "socks5://" : "http://";
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

  const visited = new Set();
  const failedUrls = [];
  const toVisit = retryFailedOnly
    ? fs.readFileSync("failed_urls.txt", "utf-8").split("\n").filter(Boolean)
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

  if (!retryFailedOnly && failedUrls.length > 0) {
    console.log(`🔁 Retrying ${failedUrls.length} failed URLs...`);
    const retryFails = [];
    await scrapeUrls(
      page,
      failedUrls,
      baseUrl,
      outputDir,
      retries,
      delay,
      timeout,
      skipExisting,
      visited,
      retryFails
    );
    if (retryFails.length > 0) {
      fs.writeFileSync("failed_urls.txt", retryFails.join("\n"));
      console.log(
        `❌ ${retryFails.length} URLs failed after retry. Logged to failed_urls.txt`
      );
    }
  }

  await browser.close();
  console.log("✅ Done scraping.");
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
  const skipExisting = args.includes("--skip-existing");
  const retryFailedOnly = args.includes("--retry-failed");

  const retries = retriesArg ? parseInt(retriesArg.split("=")[1]) : 3;
  const delay = delayArg ? parseInt(delayArg.split("=")[1]) : 2000;
  const timeout = timeoutArg ? parseInt(timeoutArg.split("=")[1]) : 30000;
  const proxy = proxyArg ? proxyArg.split("=")[1] : null;
  const proxyType = proxyTypeArg ? proxyTypeArg.split("=")[1] : "http";

  if (!url || !outDir) {
    console.error(
      "Usage: node puppeteer_scraper.js <url> <outputDir> [--headless=false] [--retries=N] [--delay=MS] [--timeout=MS] [--proxy=ip:port] [--proxy-type=http|socks5] [--skip-existing] [--retry-failed]"
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
    retryFailedOnly
  );
}

module.exports = scrapeSite;
