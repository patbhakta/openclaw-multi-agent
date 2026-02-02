# Web Access Limitations & Workarounds

## Current Status

✅ **What Works:**
- Most websites, documentation, articles
- APIs with curl
- JSON/XML data
- Static HTML content
- GitHub, documentation sites, blogs

❌ **What Doesn't Work (Limited):**
- JavaScript-heavy sites (React/Vue SPAs)
- X/Twitter (requires JS)
- Sites with captchas
- Some authenticated platforms
- Cloudflare-protected sites

## Tools Available

### 1. web-fetch.sh (Primary Tool)
```bash
/root/.openclaw/workspace/scripts/web-fetch.sh "https://example.com" [output_file]
```
Best for: Documentation, articles, blog posts, API docs

### 2. curl (Direct HTTP)
```bash
curl -s -L "https://api.example.com/data" | jq '.'
```
Best for: APIs, downloads, raw data

### 3. lynx (Text Browser)
```bash
lynx -dump "https://example.com"
```
Best for: Quick text extraction, browsing

### 4. Browser Tool (When Available)
```bash
browser action=snapshot targetUrl="https://example.com"
```
Best for: JS-heavy sites, interactivity, screenshots

**Requirements:** Chrome extension + attached tab

## Workarounds for Problematic Sites

### X/Twitter
**Problem:** Requires JavaScript

**Solutions:**
1. **Copy content manually** - Copy text from browser and paste to file
2. **Use Nitter instances** (may be unreliable):
   - `https://nitter.net`
   - `https://nitter.poast.org`
   - `https://nitter.privacydev.net`
3. **Twitter API** - Requires API key
4. **Ask user to copy** - Agent can't fetch, user provides content

Example workaround:
```bash
# User: Please fetch this tweet: https://x.com/status/12345
# Agent: I cannot access X.com directly due to JavaScript requirements.
# Please copy the tweet content and paste it, and I'll process it.
```

### Single Page Apps (React/Vue/Angular)
**Problem:** Content rendered via JS

**Solutions:**
1. **Use browser tool** (requires Chrome extension)
2. **Find API endpoints** - Call API directly with curl
3. **Use alternative UI** - Some sites have API-only access
4. **Manual copy** - User provides content

### Captcha/Protected Sites
**Problem:** Bot detection

**Solutions:**
1. **Use browser tool** - Bypasses some protections
2. **Provide credentials** - If site has API access
3. **Manual intervention** - User completes CAPTCHA

## Agent Guidelines

### When Fetching Web Content

**Sage (Researcher), R&D, All Agents:**

1. **Try web-fetch.sh first**
   ```bash
   /root/.openclaw/workspace/scripts/web-fetch.sh "https://example.com" /tmp/research.txt
   ```

2. **Check if content is valid**
   - If empty/small: "Site may require JavaScript"
   - If error message: Note the error
   - If valid: Proceed with analysis

3. **Handle failures gracefully**
   ```
   "I couldn't fetch https://x.com/status/12345 because it requires JavaScript.
   Please copy the content and I'll process it."
   ```

4. **Always cite sources**
   ```
   "Source: https://example.com/article
   Fetched: [timestamp]
   ```
   
5. **Cache results**
   ```bash
   /root/.openclaw/workspace/scripts/web-fetch.sh "URL" \
     "/root/.openclaw/workspace/cache/fetched-$(date +%s).txt"
   ```

### For JavaScript Sites

**Don't:**
- Keep retrying with curl/lynx
- Pretend you can access it
- Make up content

**Do:**
- Explain limitation clearly
- Request manual copy or alternative
- Suggest alternative sources
- Use browser tool if available

## Testing Access

Before assuming a site is blocked:

```bash
# Quick test
/root/.openclaw/workspace/scripts/web-fetch.sh "https://example.com" | head -20

# Check if we got HTML vs error
/root/.openclaw/workspace/scripts/web-fetch.sh "https://example.com" | grep -i "javascript\|captcha\|blocked"
```

## Future Improvements

**To add more capabilities:**

1. **Puppeteer/Playwright** - Headless browser for JS rendering
2. **Twitter API** - Direct access to tweets
3. **Nitter self-hosted** - Twitter alternative
4. **Tor/Proxy rotation** - Bypass rate limits
5. **Browser automation** - Chrome Remote Debugger protocol

## Summary

| Need                        | Tool                              | Success Rate |
|-----------------------------|-----------------------------------|--------------|
| Documentation/Articles       | web-fetch.sh                       | 95%          |
| APIs                        | curl + jq                         | 100%         |
| X/Twitter                   | Browser tool / Manual copy           | 0-20%        |
| React/Vue apps              | Browser tool / API endpoints         | 20-50%       |
| Captcha/Protected           | Browser tool / Manual intervention   | 10-30%       |

**Rule of thumb:** If you can't fetch it, ask the user to provide the content. Don't guess or make things up.
