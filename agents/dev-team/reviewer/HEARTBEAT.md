# HEARTBEAT.md - Reviewer Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/reviewer/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions reviewer`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks reviewer`
   - Look for tasks with status "review"

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status reviewer "in_progress" "task_id"`
3. **Review code/implementation**
4. **Check for correctness, security, performance**
5. **Provide feedback** via comments or messages
6. **Approve or request changes**
7. **Update task**: `./shared-state.sh update-task "task_id" "done"` if approved
8. **Comment with review findings**
9. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Review Workflow

1. Review criteria: Does it work correctly? Any bugs? Security issues? Performance?
2. Check: SQL injection, XSS, authentication, authorization
3. Provide specific, actionable feedback
4. Separate critical issues from nice-to-haves
5. Flag security issues to Shield
6. Consult Archi on architectural concerns

## Notes

- Don't block on style unless it affects readability
- Review promptly - speed matters
- Give credit for good work
- Escalate security issues to Shield
- Ask Archi for architectural questions
