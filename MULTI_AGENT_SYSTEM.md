# Multi-Agent System - Mission Control

This is the complete multi-agent system built on OpenClaw, inspired by Bhanu Teja's Mission Control.

## Architecture Overview

Two teams of autonomous agents working together:

### Virtual Assistant Team (5 agents)
- **Atlas** (Squad Lead) - Coordinates and delegates
- **Chronos** - Calendar & Scheduling
- **Echo** - Email & Communication
- **TaskMaster** - Todo & Project Management
- **Sage** - Research & Information

### Development Team (9 agents)
- **Archi** (Squad Lead) - Architecture & Coordination
- **CodeX** - Development & Coding
- **Reviewer** - Code Review
- **Quest** - Testing & QA
- **Scribe** - Documentation
- **Shield** - Security & Compliance
- **Velocity** - Performance & Optimization
- **Pipeline** - DevOps & CI/CD
- **Data** - Database & Analytics
- **R&D** - Tech Research & Innovation

## How It Works

### Shared State System
All agents coordinate via file-based shared state:
- `/root/.openclaw/workspace/shared/tasks.json` - Task database
- `/root/.openclaw/workspace/shared/messages.json` - Communication log
- `/root/.openclaw/workspace/shared/mentions.json` - @mention queue
- `/root/.openclaw/workspace/shared/status.json` - Agent statuses

### Heartbeat System
Agents wake up every 15 minutes via cron:
- :00, :15, :30, :45 - Atlas (VA Lead)
- :02, :17, :32, :47 - Archi (Dev Lead)
- :04, :19, :34, :49 - CodeX (and more to come)

On each heartbeat, agents:
1. Read their WORKING.md for context
2. Check for @mentions
3. Check assigned tasks
4. Take action or report HEARTBEAT_OK

### Communication
- **@mentions** - Get an agent's attention
- **Task comments** - Discuss work in one place
- **Direct messages** - Cross-session communication

## Docker Infrastructure

All containers running:
- `openclaw-node` - Node.js 22
- `openclaw-python` - Python 3.12
- `openclaw-go` - Go 1.22
- `openclaw-rust` - Rust 1.76
- `openclaw-java` - Java 21
- `openclaw-postgres` - PostgreSQL 16
- `openclaw-redis` - Redis 7
- `openclaw-nginx` - Web server

Commands:
```bash
cd /root/.openclaw/workspace
docker compose status                    # Check containers
docker compose up -d                    # Start all
docker compose down                     # Stop all
./scripts/docker-runner.sh node <cmd>   # Run in node container
```

## Shared State Commands

```bash
cd /root/.openclaw/workspace
./scripts/shared-state.sh create-task "Title" "Description" "Assignee"
./scripts/shared-state.sh update-task "task_id" "status"
./scripts/shared-state.sh list-tasks [agent_name|status]
./scripts/shared-state.sh send-message "agent" "content" [task_id]
./scripts/shared-state.sh mention "agent" "content"
./scripts/shared-state.sh check-mentions "agent_name"
./scripts/shared-state.sh update-status "agent" "status" "task_id"
```

## Task Statuses
- `inbox` - New, unassigned
- `assigned` - Has owner, not started
- `in_progress` - Being worked on
- `review` - Done, needs approval
- `done` - Finished
- `blocked` - Stuck, needs something

## Daily Standup

Every day at 23:00 UTC, a daily standup is compiled and sent:
- Completed tasks today
- In-progress work
- Blocked items
- Items needing review
- Recent communication
- Task summary by status
- Agent status

## Agent Personalities

Each agent has a unique SOUL.md defining:
- Who they are
- What they're good at
- What they care about
- When to speak vs stay silent
- Their workflow and principles

Read individual agent SOUL.md files for details.

## Quick Start

1. **Create a task:**
   ```bash
   ./scripts/shared-state.sh create-task "Build feature X" "Description..." "codex"
   ```

2. **Mention an agent:**
   ```bash
   ./scripts/shared-state.sh mention "codex" "Can you review PR #123?"
   ```

3. **Check status:**
   ```bash
   ./scripts/shared-state.sh list-tasks
   ```

4. **Daily standup:** Runs automatically at 23:00 UTC

## File Structure

```
/root/.openclaw/workspace/
├── shared/                    # Shared coordination state
│   ├── tasks.json            # Task database
│   ├── messages.json         # Agent communication
│   ├── mentions.json         # @mention queue
│   ├── status.json           # Agent statuses
│   └── AGENTS.md            # Shared operating manual
├── agents/                   # Individual agent workspaces
│   ├── virtual-assistant/    # VA team (5 agents)
│   └── dev-team/            # Dev team (9 agents)
├── scripts/                  # Shared utilities
│   ├── shared-state.sh      # State management
│   ├── docker-runner.sh     # Docker commands
│   └── daily-standup.sh     # Daily summary
└── docker-compose.yml       # Container definitions
```

## Scaling

The system is designed to scale:
- Add more agents by creating new agent directories
- Add new teams by creating new team directories
- Share state via files (no database needed initially)
- Can migrate to Convex or similar for real-time features

## Future Enhancements

Possible improvements:
- Real-time UI (React + Convex like the original)
- Thread subscriptions
- Richer task metadata (priority, tags)
- Agent specialization levels
- Cross-team workflows
- Automation triggers

## Built

Date: February 2, 2026
Inspired by: Bhanu Teja's Mission Control system
Platform: OpenClaw (https://github.com/openclaw/openclaw)
