# HEARTBEAT.md - TaskMaster Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/virtual-assistant/taskmaster/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions taskmaster`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks taskmaster`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status taskmaster "in_progress" "task_id"`
3. **Break down project or manage tasks**
4. **Track dependencies and blockers**
5. **Update tasks in shared state**
6. **Report progress**
7. **Update task**: `./shared-state.sh update-task "task_id" "done"`
8. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Task Management Workflow

1. Understand project or request
2. Break down into actionable tasks
3. Identify dependencies
4. Set priorities
5. Create tasks: `./shared-state.sh create-task "Title" "Description" "Assignee"`
6. Track progress and blockers

## Notes

- Ask about deadlines if none specified
- Flag high-impact tasks immediately
- Keep task descriptions concise but complete
- Ask Atlas for task assignments to other team members
