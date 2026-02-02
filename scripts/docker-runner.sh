#!/bin/bash
# Docker container runner script for OpenClaw agents

set -e

WORKSPACE="/root/.openclaw/workspace"
cd "$WORKSPACE"

case "$1" in
  node)
    docker exec openclaw-node "${@:2}"
    ;;
  python)
    docker exec openclaw-python "${@:2}"
    ;;
  go)
    docker exec openclaw-go "${@:2}"
    ;;
  rust)
    docker exec openclaw-rust "${@:2}"
    ;;
  java)
    docker exec openclaw-java "${@:2}"
    ;;
  postgres)
    docker exec openclaw-postgres "${@:2}"
    ;;
  redis)
    docker exec openclaw-redis "${@:2}"
    ;;
  start-all)
    docker compose up -d
    ;;
  stop-all)
    docker compose down
    ;;
  status)
    docker compose ps
    ;;
  *)
    echo "Usage: docker-runner.sh {node|python|go|rust|java|postgres|redis|start-all|stop-all|status} [args...]"
    exit 1
    ;;
esac
