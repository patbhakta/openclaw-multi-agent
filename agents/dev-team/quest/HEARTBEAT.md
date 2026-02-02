# HEARTBEAT.md - Quest Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/quest/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions quest`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks quest`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status quest "in_progress" "task_id"`
3. **Design tests** for the feature/change
4. **Identify edge cases**
5. **Execute tests** in Docker containers
6. **Document bugs and issues**
7. **Update task**: `./shared-state.sh update-task "task_id" "review"`
8. **Comment with test results**
9. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Testing Workflow

1. Understand the feature or change
2. Identify critical paths and edge cases
3. Design test scenarios
4. Execute tests (automated + manual)
5. Document bugs with reproduction steps
6. Verify fixes
7. Work with CodeX to resolve issues

## Notes

- Test in Docker containers
- Test happy path AND sad path
- Report bugs clearly with reproduction steps
- Prioritize critical issues
- Work with CodeX to fix issues
- Use Docker postgres for database testing
