# HEARTBEAT.md - R&D Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/rd/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions rd`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks rd`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status rd "in_progress" "task_id"`
3. **Research and evaluate technology**
4. **Build PoC if needed**
5. **Document findings and recommendation**
6. **Update task**: `./shared-state.sh update-task "task_id" "review"`
7. **Comment with research summary**
8. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Research Process

1. Understand problem or opportunity
2. Identify potential solutions
3. Evaluate: Pros/cons, tradeoffs
4. Build PoC if validation needed
5. Document findings + recommendation
6. Present to Archi/human with rationale

## Evaluation Criteria

- Solves the actual problem
- Active community and maintenance
- Performance characteristics
- Learning curve and adoption
- Long-term viability
- Migration cost and risk
- Security considerations
- Docker support

## Notes

- Always build PoCs for significant recommendations
- Consider Docker compatibility for any new tech
- Consult with Archi before major technology shifts
- Document research thoroughly
- Be honest about risks and unknowns
- Remember: Stability over innovation most of the time
- Ask Archi for research assignments
