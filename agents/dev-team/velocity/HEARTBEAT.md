# HEARTBEAT.md - Velocity Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/velocity/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`
   - Read your SOUL.md

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions velocity`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks velocity`
   - Review tasks assigned to you

## If Work Exists

1. **Start or resume task**
2. **Update status**: `./shared-state.sh update-status velocity "in_progress" "task_id"`
3. **Profile performance**
4. **Identify bottlenecks**
5. **Optimize what matters**
6. **Update task**: `./shared-state.sh update-task "task_id" "review"`
7. **Comment with optimization findings**
8. **Update WORKING.md** with current work

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Performance Workflow

1. Measure first (profile before optimizing)
2. Identify bottlenecks (N+1 queries, missing indexes, cache opportunities)
3. Optimize critical path
4. Cache effectively with proper invalidation
5. Consider async operations for non-blocking code
6. Document tradeoffs

## Docker Performance

- Optimize image size (alpine, multi-stage builds)
- Limit container resources appropriately
- Use volume caching for builds
- Monitor container resource usage

## Notes

- Don't optimize without measurements
- Profile before optimizing
- Consult Archi on architectural optimizations
- Consider security implications of caching
- Document tradeoffs when optimizing
