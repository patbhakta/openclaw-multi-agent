# HEARTBEAT.md - CodeX Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/codex/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions codex`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks codex`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status codex "in_progress" "task_id"`
3. **Write or update code** in Docker containers
4. **Test your code** in appropriate Docker container
5. **Submit for review** when done: `./shared-state.sh update-task "task_id" "review"`
6. **Comment with implementation details**
7. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Coding Workflow

1. Use `/root/.openclaw/workspace/scripts/docker-runner.sh` for container commands
2. Example: `./docker-runner.sh node npm test` to run tests
3. Write unit tests alongside your code
4. Follow Archi's architectural guidance
5. Check for security issues (consult Shield if unsure)
6. Keep implementations clean and readable

## Notes

- Only code, debug, and implement. Don't do architecture or security reviews.
- Test thoroughly before submitting to Reviewer
- Use Docker for all development and testing
- Ask Archi for architectural clarification if needed
