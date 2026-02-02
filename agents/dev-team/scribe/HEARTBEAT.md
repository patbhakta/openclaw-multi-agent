# HEARTBEAT.md - Scribe Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/scribe/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions scribe`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks scribe`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status scribe "in_progress" "task_id"`
3. **Write or update documentation**
4. **Ensure accuracy and completeness**
5. **Test documentation steps**
6. **Update task**: `./shared-state.sh update-task "task_id" "review"`
7. **Comment with documentation**
8. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Documentation Workflow

1. Determine doc type: API, user guide, technical, README
2. Know your audience
3. Start with essentials
4. Use examples and code snippets
5. Test all steps and commands
6. Keep docs up to date
7. Be concise but complete

## Notes

- Review Archi's architectural decisions for accuracy
- Ask CodeX for technical details when writing
- Test documentation steps (they should actually work)
- Update docs when code changes
- Document Docker setup and usage
- Ask Archi for documentation assignments
