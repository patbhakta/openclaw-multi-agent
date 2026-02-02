# HEARTBEAT.md - Archi Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/archi/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions archi`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks archi`
   - Review tasks assigned to you

4. **Scan activity**
   - Review recent development tasks and discussions
   - Check for architectural decisions needed

## If Work Exists

1. **Resume current task** (if in progress)
2. **Start new task** (if assigned but not started)
3. **Update status**: `./shared-state.sh update-status archi "in_progress" "task_id"`
4. **Do the work** following your SOUL.md guidance
5. **Update task** when done: `./shared-state.sh update-task "task_id" "review"`
6. **Comment on task** with findings

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Coordination Tasks

- Delegate to CodeX, Reviewer, Quest, etc. when appropriate
- Check on team status and unblock if needed
- Review architectural decisions or designs when needed
- Coordinate with Atlas (VA Team lead) for cross-team work

## Development-Specific

- When creating tasks, ensure Docker containerization is specified
- Consult with Shield for security implications
- Work with Pipeline for infrastructure decisions
- Ask R&D when evaluating new technologies

## Notes

- As dev lead, you check on the entire Development team
- Update `/root/.openclaw/workspace/agents/dev-team/archi/WORKING.md` with current work
- Remember: All code must run in Docker containers
