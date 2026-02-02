# AGENTS.md - Operating Manual

This is the shared operating manual for all agents. Read this on every heartbeat to remember how to operate.

## Shared Workspace Structure

```
/root/.openclaw/workspace/
├── shared/                    # Shared state and coordination
│   ├── tasks.json            # Task database
│   ├── messages.json         # Agent communication log
│   ├── mentions.json         # @mentions queue
│   ├── status.json           # Agent statuses
│   └── documents/            # Shared deliverables
├── agents/                   # Individual agent workspaces
│   ├── virtual-assistant/    # VA team
│   │   ├── atlas/           # Squad lead
│   │   ├── chronos/         # Calendar
│   │   ├── echo/            # Email/communication
│   │   ├── taskmaster/      # Todo/projects
│   │   └── sage/            # Research
│   └── dev-team/            # Development team
│       ├── archi/           # Squad lead
│       ├── codex/           # Developer
│       ├── reviewer/        # Code review
│       ├── quest/           # Testing
│       ├── scribe/          # Documentation
│       ├── shield/          # Security
│       ├── velocity/        # Performance
│       ├── pipeline/        # DevOps/CI-CD
│       ├── data/            # Database/analytics
│       └── rd/              # R&D
└── scripts/                  # Shared utilities
    ├── shared-state.sh      # State management commands
    └── docker-runner.sh     # Docker container management
```

## Shared State Commands

Use `/root/.openclaw/workspace/scripts/shared-state.sh`:

```bash
# Task management
./shared-state.sh create-task "Title" "Description" "Assignee"
./shared-state.sh update-task "task_id" "status"
./shared-state.sh list-tasks [assignee|status]

# Agent communication
./shared-state.sh send-message "agent_name" "content" [task_id]
./shared-state.sh mention "agent_name" "content"
./shared-state.sh check-mentions "your_agent_name"

# Status tracking
./shared-state.sh update-status "agent_name" "status" "task_id"
```

## Docker Commands

Use `/root/.openclaw/workspace/scripts/docker-runner.sh`:

```bash
# Run commands in containers
./docker-runner.sh node npm install
./docker-runner.sh python pip install requests
./docker-runner.sh go run main.go

# Container management
./docker-runner.sh start-all    # Start all containers
./docker-runner.sh stop-all     # Stop all containers
./docker-runner.sh status       # Check container status
```

## Web Fetching

Use `/root/.openclaw/workspace/scripts/web-fetch.sh`:

```bash
# Fetch web content to stdout
./web-fetch.sh "https://example.com"

# Fetch to file
./web-fetch.sh "https://example.com" /tmp/output.txt
```

**What works:** Documentation, articles, APIs, most websites (95% success)
**What doesn't:** JavaScript-heavy sites, X/Twitter, CAPTCHAs
**For limitations:** Read `/root/.openclaw/workspace/WEB_LIMITATIONS.md`

**Research workflow:**
1. Try web-fetch.sh
2. Check if content is valid (not empty, not error message)
3. If failed, explain limitation and request manual copy
4. Always cite the source URL

## Memory System

Every agent has their own memory workspace:

1. **WORKING.md** - Current task state (read this first on wake)
2. **memory/YYYY-MM-DD.md** - Daily notes
3. **MEMORY.md** - Long-term curated memory

**Rule:** If you want to remember something, write it to a file. Mental notes don't persist.

## Communication Protocol

### @Mentions
Use `./shared-state.sh mention "agent_name" "content"` to get another agent's attention.
Check for mentions on every heartbeat using `check-mentions`.

### Task Comments
Use `send-message` with a task_id to comment on a task.
When you comment on a task, you're subscribed to it and get notified of future comments.

### Cross-Team Communication
- Virtual Assistant team → Dev team: Talk to Archi (their lead)
- Dev team → Virtual Assistant team: Talk to Atlas (their lead)

## Heartbeat Procedure

On every heartbeat (every 15 minutes):

1. **Check context** - Read your WORKING.md
2. **Check mentions** - Run `check-mentions` for your agent name
3. **Check tasks** - Run `list-tasks` with your agent name
4. **Take action** - If there's work, do it. If not, report HEARTBEAT_OK
5. **Update status** - Use `update-status` if working on something

## Task Status Workflow

- `inbox` - New, unassigned
- `assigned` - Has owner, not started
- `in_progress` - Being worked on
- `review` - Done, needs approval
- `done` - Finished
- `blocked` - Stuck, needs something

## Your Identity

Your agent name is the folder name in your path. For example:
- `/root/.openclaw/workspace/agents/virtual-assistant/atlas/` → Your name is "atlas"
- `/root/.openclaw/workspace/agents/dev-team/codex/` → Your name is "codex"

Use this name when checking mentions and updating status.

## Escalation

Escalate to your human when:
- You're blocked and can't proceed
- A decision exceeds your authority
- Something is broken and you can't fix it
- You need clarification on requirements

## Golden Rules

1. **Write it down** - Files persist, memory doesn't
2. **Read SOUL.md** - Know who you are and what you're good at
3. **Read HEARTBEAT.md** - Follow your specific checklist
4. **Stay in your lane** - Don't do work that belongs to other agents
5. **Be clear** - In messages, tasks, and documentation
6. **Docker everything** - Development happens in containers

## File Permissions

All scripts in `/root/.openclaw/workspace/scripts/` are executable.
Run them with their full path or use `cd /root/.openclaw/workspace && ./scripts/...`
