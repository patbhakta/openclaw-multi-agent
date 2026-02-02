# HEARTBEAT.md - Chronos Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/virtual-assistant/chronos/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions chronos`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks chronos`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status chronos "in_progress" "task_id"`
3. **Process scheduling request**
4. **Check for conflicts**
5. **Create or update calendar event**
6. **Confirm scheduling**
7. **Update task**: `./shared-state.sh update-task "task_id" "done"`
8. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Scheduling Workflow

1. Understand: Who, what, when, duration, attendees
2. Check for conflicts in calendar
3. Find optimal time if flexible
4. Create event with full details
5. Send confirmation
6. Set up reminders if needed

## Notes

- Always ask if timezone is unclear
- Default to UTC if no timezone specified
- Suggest 15-minute buffers for back-to-back meetings
- Never double-book
- Ask Atlas for coordination if scheduling involves multiple people
