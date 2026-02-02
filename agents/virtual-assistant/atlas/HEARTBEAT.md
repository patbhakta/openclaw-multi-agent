# HEARTBEAT.md - Atlas Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/virtual-assistant/atlas/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions atlas`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks atlas`
   - Review tasks assigned to you

4. **Scan activity**
   - Review recent messages: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks`

## If Work Exists

1. **Resume current task** (if in progress)
2. **Start new task** (if assigned but not started)
3. **Update status**: `./shared-state.sh update-status atlas "in_progress" "task_id"`
4. **Do the work** following your SOUL.md guidance
5. **Update task** when done: `./shared-state.sh update-task "task_id" "review"`
6. **Comment on task** with findings

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Coordination Tasks

- Delegate to Chronos, Echo, TaskMaster, or Sage when appropriate
- Check on team status and unblock if needed
- Coordinate with Archi (Dev Team lead) for cross-team work
- Compile and send team status updates

## Notes

- As squad lead, you check on the entire Virtual Assistant team
- Update `/root/.openclaw/workspace/agents/virtual-assistant/atlas/WORKING.md` with current work
- Remember: You can assign tasks to any VA team member
