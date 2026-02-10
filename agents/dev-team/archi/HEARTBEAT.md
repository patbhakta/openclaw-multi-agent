# HEARTBEAT.md - Archi Checklist

## On Wake (Every 15 minutes)

1. **Read context**
   - Read `/root/.openclaw/workspace/agents/dev-team/archi/WORKING.md`
   - Read `/root/.openclaw/workspace/shared/AGENTS.md`

2. **Check for urgent items**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh check-mentions archi`
   - Review any mentions and respond if needed

3. **Check assigned tasks**
   - Run: `/root/.openclaw/workspace/scripts/shared-state.sh list-tasks archi`
   - Review tasks assigned to you

4. **Scan activity**
   - Review recent development tasks and discussions
   - Check for architectural decisions needed

## If Work Exists

1. **Resume current task** (if in progress)
2. **Start new task** (if assigned but not started)
3. **Update status**: `./shared-state.sh update-status archi "in_progress" "task_id"`
4. **Do the work** following your SOUL.md guidance
5. **Update task** when done: `./shared-state.sh update-task "task_id" "review"`
6. **Comment on task** with findings

## If No Work

- If nothing urgent: Reply with `HEARTBEAT_OK`

## Coordination Tasks

- Delegate to CodeX, Reviewer, Quest, etc. when appropriate
- Check on team status and unblock if needed
- Review architectural decisions or designs when needed
- Coordinate with Atlas (VA Team lead) for cross-team work

## Development-Specific

- When creating tasks, ensure Docker containerization is specified
- Consult with Shield for security implications
- Work with Pipeline for infrastructure decisions
- Ask R&D when evaluating new technologies

## Notes

- As dev lead, you check on the entire Development team
- Update `/root/.openclaw/workspace/agents/dev-team/archi/WORKING.md` with current work
- Remember: All code must run in Docker containers

---

## Heartbeat Summary (2026-02-07 07:17 UTC)

**Completed:**
1. ✅ Read WORKING.md and AGENTS.md (context)
2. ✅ Checked for mentions - none
3. ✅ Checked assigned tasks - all done (task_1769992432, task_1770310052, task_1770356818)
4. ✅ Reviewed team status and task queue
5. ✅ Checked container health - all healthy
6. ✅ Scanned recent activity - last team activity ~12 hours ago (19:09 UTC on Feb 6)
7. ✅ Updated WORKING.md timestamp

**Key Findings:**
- No active tasks for archi
- No mentions received
- task_1770358653 decision: DONE ✓ (accepted at 19:09 UTC on Feb 6)
- Super Bowl deadline: Feb 8, 2026 (~24.7 hours away)
- All containers healthy and running (15-21 hours uptime)
- Team monitoring active - last team activity ~12 hours ago (19:09 UTC on Feb 6)
- System stable, all Phase 1 tasks blocked or done, Option A (security + dashboard) DONE

**Super Bowl Deployment Readiness:**
- ✅ Option A (security + dashboard) DONE
- ✅ Phase 2 implementation complete (codex)
- ✅ All containers healthy (betting-dashboard, betting-jupyter, betting-kalshi-bot, betting-db)
- ⏳ Deadline: Feb 8, 2026 (~24.7 hours)
- ⏳ Remaining: Final test deployment Saturday

**Team Status (from status.json):**
- archi: monitoring (no active task)
- codex: idle (last update ~15.5 hours ago)
- atlas: idle (last update ~1 minute ago)
- pipeline: active - system_monitoring (last update ~31 minutes ago)

**Container Status (07:17 UTC):**
- betting-dashboard: Up 16 hours (healthy) - port 8888
- betting-jupyter: Up 21 hours (healthy)
- betting-kalshi-bot: Up 15 hours
- betting-db: Up 21 hours (healthy) - port 5433 (localhost only)

**Next Heartbeat:** Check for team responses, monitor container health, verify Super Bowl deployment readiness
