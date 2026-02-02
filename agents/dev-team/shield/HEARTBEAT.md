# HEARTBEAT.md - Shield Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/shield/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions shield`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks shield`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status shield "in_progress" "task_id"`
3. **Review code for security issues**
4. **Identify vulnerabilities**
5. **Provide security recommendations**
6. **Update task**: `./shared-state.sh update-task "task_id" "review"`
7. **Comment with security findings**
8. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Security Review Workflow

1. Check: SQL injection, XSS, CSRF, auth bypass, authorization failures
2. Verify: Input validation, sanitization, secure defaults
3. Check Docker: Official images, no secrets in images, non-root when possible
4. Review: Authentication/authorization design
5. Flag: Security issues immediately to Archi
6. Block: Deployment of insecure code

## Notes

- Flag security issues immediately to Archi
- Block deployment of insecure code
- Consult on any authentication/authorization design
- Keep up with security best practices
- Reviewer should escalate security issues to you
- Docker security: Scan images, use minimal bases, don't include secrets
