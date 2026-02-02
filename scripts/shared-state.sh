#!/bin/bash
# Shared state manager for agent coordination

SHARED_DIR="/root/.openclaw/workspace/shared"
TASKS_FILE="$SHARED_DIR/tasks.json"
MESSAGES_FILE="$SHARED_DIR/messages.json"
MENTIONS_FILE="$SHARED_DIR/mentions.json"
STATUS_FILE="$SHARED_DIR/status.json"

case "$1" in
  create-task)
    # Usage: create-task "Title" "Description" "Assignee"
    TITLE="$2"
    DESC="$3"
    ASSIGNEE="$4"
    TASK_ID="task_$(date +%s)"

    TMP=$(mktemp)
    jq --arg tid "$TASK_ID" \
       --arg title "$TITLE" \
       --arg desc "$DESC" \
       --arg assignee "$ASSIGNEE" \
       '.tasks += [{
         id: $tid,
         title: $title,
         description: $desc,
         assignee: $assignee,
         status: "assigned",
         createdAt: (now | todate),
         updatedAt: (now | todate)
       }] | .lastUpdated = (now | todate)' "$TASKS_FILE" > "$TMP"
    mv "$TMP" "$TASKS_FILE"
    echo "Task created: $TASK_ID"
    ;;

  update-task)
    # Usage: update-task "task_id" "status"
    TASK_ID="$2"
    STATUS="$3"

    TMP=$(mktemp)
    jq --arg tid "$TASK_ID" \
       --arg status "$STATUS" \
       '(.tasks[] | select(.id == $tid)) |= (.status = $status | .updatedAt = (now | todate)) | .lastUpdated = (now | todate)' "$TASKS_FILE" > "$TMP"
    mv "$TMP" "$TASKS_FILE"
    echo "Task updated: $TASK_ID -> $STATUS"
    ;;

  list-tasks)
    # Usage: list-tasks [assignee|status]
    FILTER="$2"
    if [ -n "$FILTER" ]; then
      jq ".tasks[] | select(.assignee == \"$FILTER\" or .status == \"$FILTER\")" "$TASKS_FILE"
    else
      jq ".tasks" "$TASKS_FILE"
    fi
    ;;

  send-message)
    # Usage: send-message "agent" "content" [task_id]
    FROM="$2"
    CONTENT="$3"
    TASK_ID="$4"

    TMP=$(mktemp)
    jq --arg from "$FROM" \
       --arg content "$CONTENT" \
       --arg task "$TASK_ID" \
       '.messages += [{
         id: "msg_$(date +%s)",
         from: $from,
         content: $content,
         taskId: $task,
         timestamp: (now | todate)
       }] | .lastUpdated = (now | todate)' "$MESSAGES_FILE" > "$TMP"
    mv "$TMP" "$MESSAGES_FILE"
    echo "Message sent from $FROM"
    ;;

  mention)
    # Usage: mention "agent" "content"
    AGENT="$2"
    CONTENT="$3"

    TMP=$(mktemp)
    jq --arg agent "$AGENT" \
       --arg content "$CONTENT" \
       '.mentions += [{
         id: "mention_$(date +%s)",
         agent: $agent,
         content: $content,
         delivered: false,
         createdAt: (now | todate)
       }] | .lastUpdated = (now | todate)' "$MENTIONS_FILE" > "$TMP"
    mv "$TMP" "$MENTIONS_FILE"
    echo "Mention queued for @$AGENT"
    ;;

  check-mentions)
    # Usage: check-mentions "agent_name"
    AGENT="$2"

    TMP=$(mktemp)
    jq --arg agent "$AGENT" \
       '[.mentions[] | select(.agent == $agent and .delivered == false)] as $undelivered |
        (.mentions |= map(.delivered or (.agent != $agent))) |
        .lastUpdated = (now | todate) |
        {mentions: $undelivered}' "$MENTIONS_FILE" > "$TMP"
    cat "$TMP"
    mv "$TMP" "$MENTIONS_FILE"
    ;;

  update-status)
    # Usage: update-status "agent" "status" "task_id"
    AGENT="$2"
    STATUS="$3"
    TASK_ID="$4"

    TMP=$(mktemp)
    jq --arg agent "$AGENT" \
       --arg status "$STATUS" \
       --arg task "$TASK_ID" \
       '.agents[$agent] = {status: $status, currentTask: $task, updatedAt: (now | todate)} |
        .lastUpdated = (now | todate)' "$STATUS_FILE" > "$TMP"
    mv "$TMP" "$STATUS_FILE"
    echo "Status updated: $AGENT -> $STATUS"
    ;;

  *)
    echo "Usage: shared-state.sh {create-task|update-task|list-tasks|send-message|mention|check-mentions|update-status}"
    exit 1
    ;;
esac
