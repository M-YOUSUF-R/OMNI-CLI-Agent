## DuckDuckGo API Emulation: 
The duckduckgo_search package uses DDG's internal API endpoints. This bypasses the need to scrape complex HTML or solve Google reCAPTCHAs.
## Trafilatura vs Requests: 
Traditional requests downloads raw HTML, which often triggers Cloudflare protections. trafilatura includes robust fallback routines and strips out clutter (sidebars, footers, ads), leaving only the text data your agent actually needs to read.Throttling: The time.sleep(1) line creates a natural human delay between page loads, preventing your server from hitting rate limits.
