# Web Fetching Tools for OpenClaw Agents

## Problem
Agents need to access web resources but the browser tool requires Chrome extension relay with attached tabs, and `web_fetch` has limitations with some sites.

## Solution
Shell-based web fetching tools installed on the VPS.

## Tools Installed

### 1. web-fetch.sh - Main Web Fetcher
**Location:** `/root/.openclaw/workspace/scripts/web-fetch.sh`

**Usage:**
```bash
# Fetch to stdout
/root/.openclaw/workspace/scripts/web-fetch.sh "https://example.com"

# Fetch to file
/root/.openclaw/workspace/scripts/web-fetch.sh "https://example.com" /tmp/output.txt
```

**Features:**
- Uses lynx for clean text extraction
- Falls back to curl if needed
- Browser-like user agent
- Handles compression
- Timeout protection (30s connect, 10s timeout)
- Preview output when saving to file

**Example:**
```bash
/root/.openclaw/workspace/scripts/web-fetch.sh "https://x.com/i/status/2017662163540971756" /tmp/tweet.txt
```

### 2. curl - Direct HTTP Requests
```bash
# Get page
curl -s -L "https://example.com"

# Get with headers
curl -s -L -H "Authorization: Bearer $TOKEN" "https://api.example.com/data"

# POST data
curl -X POST -H "Content-Type: application/json" -d '{"key":"value"}' "https://api.example.com"
```

### 3. lynx - Text Browser
```bash
# Browse in text mode
lynx "https://example.com"

# Dump page to text
lynx -dump "https://example.com"

# From pipe
curl -s "https://example.com" | lynx -dump -stdin
```

## Comparison to Browser Tool

| Feature          | Browser Tool | web-fetch.sh |
|------------------|--------------|--------------|
| Interactivity    | ✅ Click/type | ❌ Text only |
| Screenshots      | ✅           | ❌           |
| JavaScript exec  | ✅           | ❌           |
| Text extraction  | ❌ Manual     | ✅ Automatic |
| No browser req   | ❌ Needs Chrome | ✅ Works without |
| CLI automation   | ❌           | ✅           |

## When to Use Each

**Use web-fetch.sh when:**
- Reading articles, docs, blog posts
- Extracting text content
- Automated scripts
- Agent research tasks (Sage)

**Use browser tool when:**
- Need to interact with forms
- Need screenshots
- Testing web UI
- JavaScript-heavy apps

**Use curl when:**
- API requests
- Downloading files
- Raw content
- Custom headers/auth

## Examples by Agent

**Sage (Research):**
```bash
# Research a topic
/root/.openclaw/workspace/scripts/web-fetch.sh "https://example.com/article" /tmp/research.md
```

**CodeX (Dev):**
```bash
# Fetch API docs
/root/.openclaw/workspace/scripts/web-fetch.sh "https://api.example.com/docs" /tmp/api-docs.md
```

**Chronos (Calendar):**
```bash
# Get timezone info
curl -s "https://worldtimeapi.org/api/timezone" > /tmp/timezones.json
```

## Advanced Usage

### Extract specific sections
```bash
# Get only text after a marker
/root/.openclaw/workspace/scripts/web-fetch.sh "https://example.com" | grep -A 100 "Section Title"
```

### Save with timestamp
```bash
/root/.openclaw/workspace/scripts/web-fetch.sh "https://example.com" \
  "/tmp/fetched-$(date +%Y%m%d-%H%M%S).txt"
```

### Process with jq for APIs
```bash
curl -s "https://api.example.com/data" | jq '.items[] | select(.active == true)'
```

## Limitations

- No JavaScript execution
- No interaction with dynamic content
- Captchas will block access
- Some sites block text browsers
- Single-page apps (React/Vue) may not render fully

## Troubleshooting

**Empty output:**
- Site may require JavaScript
- Site may block text browsers
- Try curl directly for raw HTML

**Slow response:**
- Site may be rate-limiting
- Try adding delay between requests
- Check connectivity: `ping example.com`

**403 Forbidden:**
- User agent blocked
- Site requires authentication
- Try with browser-like headers

## Best Practices

1. **Cache results** - Save to files to avoid repeated fetches
2. **Rate limit** - Don't hammer sites
3. **Check size** - Limit large downloads
4. **Verify** - Always check if content looks valid
5. **Document sources** - Always note where content came from

## Integration with Agent System

Add to agent HEARTBEAT.md:
```markdown
## Research Tasks
When fetching web content:
1. Use: `/root/.openclaw/workspace/scripts/web-fetch.sh "URL"`
2. Save results to agent workspace
3. Always cite the source URL
4. If fails, note why and try alternative
```
