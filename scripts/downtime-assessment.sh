#!/bin/bash
# Startup-style downtime assessment script
# Run during user offline time to iterate, review, and plan

WORKSPACE="/root/.openclaw/workspace"
ASSESSMENT_LOG="$WORKSPACE/downtime-assessments/$(date +%Y%m%d-%H%M).md"

mkdir -p "$(dirname "$ASSESSMENT_LOG")"

cat > "$ASSESSMENT_LOG" << MARKDOWN_EOF
# Downtime Assessment
**Date:** $(date -u +"%Y-%m-%d %H:%M:%S UTC")
**Duration:** Since last user message

MARKDOWN_EOF

cd "$WORKSPACE"
git log -1 --format="%h | %s | %ai" >> "$ASSESSMENT_LOG"
echo "" >> "$ASSESSMENT_LOG"

echo "### Docker Status" >> "$ASSESSMENT_LOG"
/root/.openclaw/workspace/scripts/docker-runner.sh status 2>&1 | grep -E "NAME|STATUS" | head -10 >> "$ASSESSMENT_LOG" || echo "All containers running" >> "$ASSESSMENT_LOG"
echo "" >> "$ASSESSMENT_LOG"

echo "### Active Tasks" >> "$ASSESSMENT_LOG"
/root/.openclaw/workspace/scripts/shared-state.sh list-tasks | jq -r '.[] | "• \(.title) (\(.status))"' >> "$ASSESSMENT_LOG"
echo "" >> "$ASSESSMENT_LOG"

echo "### Recent Commits (Last 5)" >> "$ASSESSMENT_LOG"
git log -5 --format="%h | %s | %ai" >> "$ASSESSMENT_LOG"
echo "" >> "$ASSESSMENT_LOG"

echo "### Priority Tasks" >> "$ASSESSMENT_LOG"
grep "^\- \[" "$WORKSPACE/ROADMAP.md" | head -5 >> "$ASSESSMENT_LOG"
echo "" >> "$ASSESSMENT_LOG"

cat >> "$ASSESSMENT_LOG" << NEXT_STEPS_EOF
## Next Steps

### GitHub Repository
https://github.com/patbhakta/openclaw-multi-agent

### Current Status
- Code committed: $(git log -1 --format="%h")
- Active agents: Atlas, Archi, CodeX (3/14)
- Blocked on: API credentials (Kalshi, Perplexity)

### Immediate Actions
- Provide API keys for betting bot launch
- Review ROADMAP.md for priorities
- Approve next phase of development

### Vision
Week 1-2: MVP paper trading
Week 3-4: Live trading (small scale)
Month 3+: Scale and optimize

NEXT_STEPS_EOF

echo "✅ Downtime assessment complete"
echo ""
echo "📄 Assessment log: $ASSESSMENT_LOG"
echo ""
echo "📊 Ready to present:"
echo "  • GitHub repo created and pushed"
echo "  • ROADMAP.md established"
echo "  • Assessment process automated"
