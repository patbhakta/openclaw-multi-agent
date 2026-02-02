# HEARTBEAT.md - Data Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/data/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions data`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks data`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status data "in_progress" "task_id"`
3. **Design database schema** or optimize queries
4. **Write and test migrations**
5. **Optimize queries** if needed
6. **Update task**: `./shared-state.sh update-task "task_id" "review"`
7. **Comment with database findings**
8. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Database Workflow

1. Normalize to 3NF, denormalize for performance
2. Index columns used in WHERE, JOIN, ORDER BY
3. Use appropriate data types
4. Design for query patterns
5. Backup regularly using pg_dump
6. Monitor slow queries

## PostgreSQL in Docker

- Use migrations for schema changes
- Backup: pg_dump
- Monitor: pg_stat_statements
- Connection pooling for scale
- Read replicas for analytics

## Notes

- Consult Archi on database architecture
- Work with Pipeline on database backups
- Consult Velocity on query performance
- Document schemas and migrations
- Test queries with realistic data volumes
