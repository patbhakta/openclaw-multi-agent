# HEARTBEAT.md - Pipeline Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/pipeline/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions pipeline`
   - Review any mentions and responses needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks pipeline`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status pipeline "in_progress" "task_id"`
3. **Design or update CI/CD pipeline**
4. **Set up Docker deployment**
5. **Configure monitoring**
6. **Test deployment**
7. **Update task**: `./shared-state.sh update-task "task_id" "review"`
8. **Comment with pipeline details**
9. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## DevOps Workflow

1. Build: Docker image
2. Test: Run all tests
3. Security scan: Check vulnerabilities
4. Deploy: Staging
5. Smoke tests
6. Deploy: Production (with approval)

## Docker Deployment

- All services in Docker containers
- Use docker-compose for local dev
- Multi-stage builds for smaller images
- Tag images properly
- Use secrets management (not in images)
- Health checks for all services

## Notes

- Consult Archi on infrastructure decisions
- Work with Shield on security scanning
- Test rollbacks regularly
- Document deployment procedures
- Monitor container resource usage
