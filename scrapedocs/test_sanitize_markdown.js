const { sanitizeMarkdown } = require("./puppeteer_scraper");

const cases = [
  {
    name: "✅ Valid Markdown link split over lines",
    input: `(/docs/common/concepts/access-anywhere)

[​

](#get-in-touch)`,
  },
  {
    name: "❌ Minified JS line",
    input: `!function(t,e){window.posthog=e,e._i=[],e.init=function(i,s,a){...}`,
  },
  {
    name: "❌ Minified CSS with custom props",
    input: `:where([data-sonner-toaster][dir=ltr]){--toast-icon-margin-start:-3px;--toast-icon-margin-end:4px;}`,
  },
  {
    name: "✅ Regular heading",
    input: `### Welcome to the docs`,
  },
  {
    name: "✅ Bracket-only line (preserve)",
    input: `[`,
  },
  {
    name: "✅ Empty Markdown link with ZWSP",
    input: `[​](#invisible)`,
  },
];

console.log("\n=== Markdown Sanitizer Test ===\n");

cases.forEach(({ name, input }) => {
  const output = sanitizeMarkdown(input, true);
  const passed =
    output.includes("posthog") || output.includes("--toast")
      ? "❌ Failed"
      : "✅ Passed";
  console.log(
    `\n${name}\n${"-".repeat(
      name.length
    )}\nInput:\n${input}\n\nOutput:\n${output}\n\nResult: ${passed}\n`
  );
});
