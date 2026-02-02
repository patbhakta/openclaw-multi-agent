#!/bin/bash
# Daily standup compilation script

WORKSPACE="/root/.openclaw/workspace"
SHARED="$WORKSPACE/shared"
TODAY=$(date +%Y-%m-%d)
STANDUP_FILE="$SHARED/daily-standup-$TODAY.md"

echo "📊 DAILY STANDUP — $(date '+%B %d, %Y')" > "$STANDUP_FILE"
echo "" >> "$STANDUP_FILE"

# Get all completed tasks
echo "✅ COMPLETED TODAY" >> "$STANDUP_FILE"
jq -r '.tasks[] | select(.status == "done" and (.updatedAt | split("T")[0]) == "'$TODAY'") |
  "• \(.assignee): \(.title)"' "$SHARED/tasks.json" 2>/dev/null | sort >> "$STANDUP_FILE"
echo "" >> "$STANDUP_FILE"

# Get tasks in progress
echo "🔄 IN PROGRESS" >> "$STANDUP_FILE"
jq -r '.tasks[] | select(.status == "in_progress") |
  "• \(.assignee): \(.title)"' "$SHARED/tasks.json" 2>/dev/null | sort >> "$STANDUP_FILE"
echo "" >> "$STANDUP_FILE"

# Get blocked tasks
echo "🚫 BLOCKED" >> "$STANDUP_FILE"
jq -r '.tasks[] | select(.status == "blocked") |
  "• \(.assignee): \(.title)"' "$SHARED/tasks.json" 2>/dev/null | sort >> "$STANDUP_FILE"
echo "" >> "$STANDUP_FILE"

# Get tasks in review
echo "👀 NEEDS REVIEW" >> "$STANDUP_FILE"
jq -r '.tasks[] | select(.status == "review") |
  "• \(.assignee): \(.title)"' "$SHARED/tasks.json" 2>/dev/null | sort >> "$STANDUP_FILE"
echo "" >> "$STANDUP_FILE"

# Get recent messages (last 24 hours)
echo "💬 RECENT COMMUNICATION" >> "$STANDUP_FILE"
jq -r '.messages[] | select((.timestamp | fromiso8601) > (now - 86400)) |
  "[\(.from)]: \(.content)"' "$SHARED/messages.json" 2>/dev/null | head -10 >> "$STANDUP_FILE"
echo "" >> "$STANDUP_FILE"

# Count tasks by status
echo "📈 TASK SUMMARY" >> "$STANDUP_FILE"
for status in inbox assigned in_progress review done blocked; do
  count=$(jq "[.tasks[] | select(.status == \"$status\")] | length" "$SHARED/tasks.json" 2>/dev/null)
  if [ "$count" -gt 0 ]; then
    echo "• $status: $count" >> "$STANDUP_FILE"
  fi
done
echo "" >> "$STANDUP_FILE"

# Get agent status
echo "🤖 AGENT STATUS" >> "$STANDUP_FILE"
jq -r '.agents | to_entries[] | "• \(.key): \(.value.status)"' "$SHARED/status.json" 2>/dev/null | sort >> "$STANDUP_FILE"

cat "$STANDUP_FILE"
