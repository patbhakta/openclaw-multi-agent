#!/bin/bash
# Enhanced web fetcher with multiple fallback methods

set -e

URL="$1"
OUTPUT_FILE="$2"

if [ -z "$URL" ]; then
  echo "Usage: web-fetch.sh <url> [output_file]"
  exit 1
fi

TEMP_TEXT=$(mktemp /tmp/webfetch-XXXXXX.txt)

echo "📥 Fetching: $URL"

# Method 1: Try lynx (best for text)
if command -v lynx >/dev/null 2>&1; then
  curl -s -L \
    -A "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" \
    -H "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8" \
    --max-time 30 \
    "$URL" 2>/dev/null | \
    lynx -dump -stdin -nolist -width=120 > "$TEMP_TEXT" 2>/dev/null
fi

# Method 2: If lynx failed or empty, try direct text extraction
if [ ! -s "$TEMP_TEXT" ]; then
  curl -s -L "$URL" 2>/dev/null | \
    sed -e 's/<script[^>]*>.*<\/script>//gi' \
        -e 's/<style[^>]*>.*<\/style>//gi' \
        -e 's/<[^>]\+>//g' \
        -e 's/&nbsp;/ /g' \
        -e 's/&lt;/</g' \
        -e 's/&gt;/>/g' \
        -e 's/&amp;/\&/g' \
    | tr -s '[:space:]' '\n' | \
    sed '/^[[:space:]]*$/d' > "$TEMP_TEXT"
fi

# Output
if [ ! -s "$TEMP_TEXT" ]; then
  echo "❌ Failed to fetch or empty response"
  echo ""
  echo "Possible reasons:"
  echo "  • Site requires JavaScript (e.g., X.com, modern SPAs)"
  echo "  • Site blocked text browsers"
  echo "  • Network timeout or connectivity issue"
  echo "  • Captcha or rate limiting"
  echo ""
  echo "Workarounds:"
  echo "  • Use browser tool for JS-heavy sites"
  echo "  • Try Nitter instance for Twitter/X (e.g., https://nitter.net/)"
  echo "  • Copy content manually to file"
  rm -f "$TEMP_TEXT"
  exit 1
fi

if [ -n "$OUTPUT_FILE" ]; then
  cp "$TEMP_TEXT" "$OUTPUT_FILE"
  LINES=$(wc -l < "$OUTPUT_FILE")
  echo "✅ Saved to: $OUTPUT_FILE ($LINES lines)"
else
  cat "$TEMP_TEXT"
fi

rm -f "$TEMP_TEXT"
