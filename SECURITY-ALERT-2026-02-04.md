# SECURITY ALERT - Database Under Attack

**Date:** February 4, 2026
**Time:** 11:07 PM UTC
**Severity:** CRITICAL
**Status:** Active attack in progress

---

## Incident Summary

**What happened:**
OpenClaw Postgres database (openclaw-postgres) is under active SQL injection attack from external sources.

**Root cause:**
- Postgres container exposed on port 5432 to 0.0.0.0 (public internet)
- Server has public IP: 208.84.102.243
- Automated scanners found the exposed database
- Attackers are attempting SQL injection exploits

---

## Attack Evidence

**From Postgres logs (docker logs openclaw-postgres):**

1. **Cross-database reference attempts:**
   ```
   ERROR:  cross-database references are not implemented: "tmp.public.t1"
   ```

2. **System file access attempts:**
   ```
   ERROR:  could not access file "/lib/x86_64-linux-gnu/libc.so.6": No such file or directory
   ```

3. **Base64-encoded payload (decoded):**
   - Reverse shell creation attempt
   - Backdoor installation
   - Connections to external IP: 185.186.25.120
   - Process killing (watchdogs, monitoring tools)
   - Remote command execution

4. **Authentication failures:**
   ```
   FATAL:  password authentication failed for user "postgres"
   (multiple repeated attempts)
   ```

---

## Impact Assessment

**Current impact:**
- Postgres CPU: 778% (from attack load)
- System load: 8.41 (elevated)
- Attack ongoing as of 11:07 PM UTC

**Potential risk:**
- Data theft (if successful)
- Database compromise
- System takeover
- Botnet enrollment

**Good news:**
- Attacks are failing (Postgres rejecting malicious queries)
- No evidence of successful compromise
- Database password "postgres" is weak but basic auth is blocking

---

## Exposed Ports Identified

All these ports are accessible from the public internet:

| Port | Service | Risk |
|------|---------|------|
| 5432 | openclaw-postgres | 🔴 Under attack |
| 5433 | betting-db | 🔴 Exposed DB |
| 6379 | openclaw-redis | 🔴 Exposed cache |
| 8888 | betting-jupyter | 🔴 Web interface |
| 8080 | openclaw-nginx | ✅ Web server (OK) |

---

## Immediate Mitigation Steps

### Step 1: Close Exposed Ports

**Edit `/root/.openclaw/workspace/docker-compose.yml`:**

```yaml
services:
  # Postgres - REMOVE public exposure
  postgres:
    # - "5432:5432"  ← REMOVE THIS LINE
    ports: []  ← ADD THIS

  # Redis - REMOVE public exposure
  redis:
    # - "6379:6379"  ← REMOVE THIS LINE
    ports: []  ← ADD THIS

  # Nginx - KEEP (web server)
  nginx:
    - "8080:80"  ← THIS IS OK

  # Jupyter - REMOVE or restrict to localhost
  betting-jupyter:
    # - "8888:8888"  ← REMOVE THIS LINE
    # OR: "127.0.0.1:8888:8888"  ← Local only
```

### Step 2: Restart Containers

```bash
cd /root/.openclaw/workspace
docker-compose down
docker-compose up -d
```

### Step 3: Verify Fix

```bash
# Check only nginx should have 0.0.0.0
docker ps --format "{{.Names}}: {{.Ports}}" | grep "0.0.0.0"
# Expected: Only nginx: 0.0.0.0:8080->80/tcp
```

### Step 4: Monitor Postgres CPU

```bash
docker stats openclaw-postgres
# Should drop to < 5% after restart
```

---

## Additional Security Recommendations

### 1. Use Tailscale for Remote Access

You already have Tailscale running (`ip-208-84-102-243-1.emerald-geological.ts.net`). Use it for remote database access:

```bash
# Connect via Tailscale instead of public ports
tailscale up
# Then access databases at:
# postgres: openclaw-postgres-1:5432 (via Tailnet)
```

### 2. Strengthen Database Credentials

**Postgres:**
```yaml
environment:
  POSTGRES_USER: strong_username_here
  POSTGRES_PASSWORD: strong_random_password_here  # Use a password manager
  POSTGRES_DB: openclaw
```

**Redis:**
```yaml
command: redis-server --requirepass strong_redis_password_here
```

### 3. Configure Firewall

Add UFW rules to block external DB access:

```bash
sudo ufw default deny incoming
sudo ufw allow 80/tcp   # Web
sudo ufw allow 443/tcp  # HTTPS
sudo ufw allow from 100.64.0.0/10  # Tailscale
sudo ufw deny 5432      # Block Postgres
sudo ufw deny 6379      # Block Redis
sudo ufw enable
```

### 4. Enable PostgreSQL Logging for Auditing

```yaml
postgres:
  command: >
    postgres
    -c log_connections=on
    -c log_disconnections=on
    -c log_statement=all
```

---

## After Mitigation

### Monitor Attack Logs

```bash
# Watch for continued attempts
docker logs -f openclaw-postgres | grep -i "error\|fatal\|warning"
```

### Check System Load

```bash
uptime
# Should drop below 2.0
```

### Verify No New Connections

```bash
docker exec openclaw-postgres psql -U postgres -c "
  SELECT * FROM pg_stat_activity WHERE state = 'active';
"
```

---

## Timeline

- **11:00 PM UTC** - Hourly status update detected Postgres CPU at 778%
- **11:01 PM UTC** - Investigated Postgres logs
- **11:05 PM UTC** - First security alert sent (SQL injection detected)
- **11:07 PM UTC** - Second alert sent (all exposed ports identified)
- **Pending** - User action to close ports

---

## Status

**Current:** 🔴 Active attack ongoing
**Awaiting:** User action to secure exposed ports
**Estimated resolution time:** 5-10 minutes once user responds

---

## References

- Docker compose file: `/root/.openclaw/workspace/docker-compose.yml`
- Postgres logs: `docker logs openclaw-postgres`
- System status: `openclaw status`
- Port exposure: `docker ps --format "{{.Names}}: {{.Ports}}"`

---

**Document created:** Feb 4, 2026 @ 11:07 PM UTC
**Last updated:** Feb 4, 2026 @ 11:07 PM UTC
