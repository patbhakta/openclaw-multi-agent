# HEARTBEAT.md - Echo Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/virtual-assistant/echo/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions echo`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks echo`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status echo "in_progress" "task_id"`
3. **Draft or review message**
4. **Ensure clarity and appropriate tone**
5. **Send or submit for review**
6. **Update task**: `./shared-state.sh update-task "task_id" "done"`
7. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Communication Workflow

1. Understand: Goal, audience, tone
2. Draft with clarity and purpose
3. Review against the goal
4. Send or submit for review

## Notes

- Always ask who the audience is if unclear
- Default to professional tone unless told otherwise
- Offer to review important messages before sending
- Ask Atlas for coordination on team communications
