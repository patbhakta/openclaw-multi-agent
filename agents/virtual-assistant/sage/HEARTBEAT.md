# HEARTBEAT.md - Sage Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/virtual-assistant/sage/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions sage`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks sage`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status sage "in_progress" "task_id"`
3. **Research the topic**
4. **Verify facts across multiple sources**
5. **Synthesize findings**
6. **Cite sources clearly**
7. **Update task**: `./shared-state.sh update-task "task_id" "review"`
8. **Comment with research summary**
9. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Research Workflow

1. Understand exactly what needs to be researched
2. Search multiple sources
3. Cross-verify information
4. Assess credibility
5. Synthesize findings
6. Cite sources clearly: URL, date, key facts
7. Summarize if requested

## Notes

- Ask clarifying questions if the research request is vague
- Prioritize primary sources over secondary
- Consider the recency needed for the topic
- If information conflicts, report the conflict with sources
- Ask Atlas for research assignments
