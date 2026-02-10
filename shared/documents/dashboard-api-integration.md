# Dashboard API Integration & Secure Key Management

**Date:** February 6, 2026
**Status:** Active - Implementing secure key fetching from dashboard

---

## 🔴 Security Response to Data Breaches

### Acknowledged Security Incidents
Your reports of multiple data breaches and unauthorized database accesses are taken seriously and drive our security hardening:

**Historical Context (Per Your Reports):**
- Unauthorized SQL injection attempts on PostgreSQL (Feb 4, 2026)
- Multiple data exposures through plaintext storage
- Attackers exploiting exposed services
- System vulnerabilities from rapid deployment

**Root Causes Identified:**
1. Plaintext credential storage in databases/files
2. Exposed database ports to public internet
3. Lack of encryption at rest
4. Insufficient access controls and auditing
5. Rapid deployment without security review

---

## 🛡️ Dashboard API Integration Plan

### Overview
The user's existing login dashboard provides API endpoints for secure key management, eliminating the need to store sensitive data in our codebase.

### API Endpoints Required

#### 1. Authentication
```
POST /api/auth/login
Content-Type: application/json

Request:
{
  "username": "user@example.com",
  "password": "user_password",
  "mfa_code": "123456" (if 2FA enabled)
}

Response (200 OK):
{
  "token": "jwt_token_here",
  "expires_in": 3600,
  "refresh_token": "refresh_token_here",
  "user": {
    "id": "user_123",
    "email": "user@example.com",
    "accounts": ["account_1", "account_2"]
  }
}
```

#### 2. Fetch API Keys
```
GET /api/keys/{service}
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "service": "kalshi_api",
  "key": "kalshi_api_key_placeholder",
  "key_type": "production",
  "expires_at": "2026-03-01T00:00:00Z",
  "last_rotated": "2026-01-15T00:00:00Z",
  "permissions": ["read", "write", "trade"]
}
```

**Supported Services:**
- `kalshi_api` - Kalshi prediction market API key
- `perplexity_api` - Perplexity Sonar AI API key
- `openai_api` - OpenAI API key (if needed for research)
- `anthropic_api` - Claude AI API key (if needed)
- Any other services added to dashboard

#### 3. Rotate API Keys
```
POST /api/keys/{service}/rotate
Authorization: Bearer {jwt_token}
Content-Type: application/json

Request:
{
  "reason": "Scheduled rotation",
  "account_id": "account_123"
}

Response (200 OK):
{
  "new_key": "new_key_placeholder",
  "expires_at": "2026-04-01T00:00:00Z",
  "rotated_at": "2026-02-06T04:06:00Z"
}
```

#### 4. Revoke API Key
```
DELETE /api/keys/{service}
Authorization: Bearer {jwt_token}

Response (200 OK):
{
  "revoked": true,
  "revoked_at": "2026-02-06T04:06:00Z",
  "reason": "User requested revocation"
}
```

---

## 🔐 Secure Storage Architecture

### Key Storage (Hashed)

**When fetching from dashboard:**
1. Receive API key from dashboard API
2. Generate SHA-256 hash of the key
3. Store only the hash in our database
4. Never store plaintext key in files, environment variables, or code

**Database Schema (Enhanced):**
```sql
CREATE TABLE api_keys (
  id SERIAL PRIMARY KEY,
  account_id INTEGER NOT NULL REFERENCES accounts(id),
  service VARCHAR(50) NOT NULL,
  key_hash VARCHAR(64) NOT NULL,  -- SHA-256 hash of API key
  key_type VARCHAR(20) NOT NULL,       -- 'dashboard', 'manual', 'rotated'
  permissions TEXT,                    -- JSON array of permissions
  expires_at TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_access_at TIMESTAMP,
  is_active BOOLEAN DEFAULT TRUE,
  UNIQUE(account_id, service, key_hash)
);

-- Index for lookups
CREATE INDEX idx_api_keys_active ON api_keys(account_id, service, is_active)
WHERE is_active = TRUE;

-- For security auditing
CREATE TABLE key_usage_logs (
  id SERIAL PRIMARY KEY,
  key_hash VARCHAR(64) NOT NULL,
  accessed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  accessed_by VARCHAR(50),  -- 'bot_service', 'user_dashboard'
  purpose VARCHAR(100)
  ip_address VARCHAR(45),
  user_agent VARCHAR(200)
);
```

**Python Implementation:**
```python
import hashlib
import json

class KeyManager:
    def __init__(self, db_connection):
        self.db = db_connection
    
    def fetch_from_dashboard(self, service, jwt_token, dashboard_url):
        """
        Fetch API key from user's dashboard
        Returns: key_hash, expires_at, permissions
        """
        import requests
        
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{dashboard_url}/api/keys/{service}",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            api_key = data['key']
            expires_at = data['expires_at']
            permissions = data.get('permissions', [])
            
            # Hash the key using SHA-256
            key_hash = hashlib.sha256(api_key.encode('utf-8')).hexdigest()
            
            return {
                'success': True,
                'key_hash': key_hash,
                'expires_at': expires_at,
                'permissions': permissions,
                'key_type': 'dashboard'
            }
        else:
            return {
                'success': False,
                'error': response.status_code,
                'message': response.text
            }
    
    def store_key_hash(self, account_id, service, key_hash, expires_at, permissions, key_type='dashboard'):
        """
        Store only the hash in database
        NEVER store plaintext key
        """
        with self.db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO api_keys 
                (account_id, service, key_hash, key_type, permissions, expires_at, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (account_id, service) 
                DO UPDATE SET 
                    key_hash = EXCLUDED.key_hash,
                    permissions = EXCLUDED.permissions,
                    expires_at = EXCLUDED.expires_at,
                    last_access_at = NOW(),
                    is_active = TRUE
            """, (account_id, service, key_hash, json.dumps(permissions), expires_at, json.dumps(permissions)))
            self.db.commit()
            
        # Log the key fetch
        self._log_key_usage(account_id, key_hash, 'dashboard', 'fetch_from_api', service)
    
    def get_key_for_use(self, account_id, service):
        """
        Retrieve key hash for API calls
        Note: We cannot retrieve the plaintext key
        We must make API calls with the dashboard acting as key proxy
        """
        with self.db.cursor() as cursor:
            cursor.execute("""
                SELECT key_hash, key_type, permissions, expires_at 
                FROM api_keys 
                WHERE account_id = %s AND service = %s AND is_active = TRUE
                AND expires_at > NOW()
                ORDER BY created_at DESC LIMIT 1
            """, (account_id, service))
            
            result = cursor.fetchone()
            
        if result:
            key_hash, key_type, permissions, expires_at = result
            return {
                'success': True,
                'key_hash': key_hash,
                'key_type': key_type,
                'permissions': permissions,
                'expires_at': expires_at
            }
        
        return {'success': False, 'error': 'No active key found'}
    
    def mark_key_expired(self, account_id, service):
        """
        Mark key as expired when it's no longer valid
        """
        with self.db.cursor() as cursor:
            cursor.execute("""
                UPDATE api_keys 
                SET is_active = FALSE 
                WHERE account_id = %s AND service = %s
            """, (account_id, service))
            self.db.commit()
    
    def _log_key_usage(self, account_id, key_hash, used_by, purpose, ip_address='auto', user_agent='api_service'):
        """
        Log key access for security auditing
        """
        with self.db.cursor() as cursor:
            cursor.execute("""
                INSERT INTO key_usage_logs 
                (key_hash, accessed_at, accessed_by, purpose, ip_address, user_agent)
                VALUES (%s, NOW(), %s, %s, %s, %s)
            """, (key_hash, used_by, purpose, ip_address, user_agent))
            self.db.commit()
```

---

## 🎯 API Call Strategies

### Strategy 1: Dashboard Key Proxy (Recommended)
**How it works:**
- Our bot makes API calls to dashboard with our authentication
- Dashboard uses its stored keys to make the actual API call to external service (Kalshi, Perplexity, etc.)
- We never see the actual API keys

**Architecture:**
```
┌─────────────────────────────────┐
│   Our Bot              │
│         │                 │
│         ▼                 │
│   Dashboard API           │ (Has keys)
│         │                 │
│         ▼                 │
│   External API            │
│  (Kalshi, Perplexity)    │
└─────────────────────────────────┘

Request: GET /api/kalshi/markets
          ↓
Response: Markets data
```

**Benefits:**
✅ Zero security risk for us (we never have keys)
✅ Automatic key rotation handled by dashboard
✅ Centralized access control
✅ Better audit trail
✅ Easy permission management

**Implementation:**
```python
class DashboardAPIProxy:
    def __init__(self, jwt_token, dashboard_url):
        self.jwt_token = jwt_token
        self.dashboard_url = dashboard_url
    
    def call_external_service(self, service, endpoint, method='GET', data=None, params=None):
        """
        Proxy call through dashboard
        """
        import requests
        
        url = f"{self.dashboard_url}/api/proxy/{service}/{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.jwt_token}",
            "Content-Type": "application/json"
        }
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response.json()
    
    def get_kalshi_markets(self, market_type='nfl'):
        """
        Get Kalshi markets through dashboard proxy
        """
        return self.call_external_service('kalshi', 'markets', params={'type': market_type})
    
    def get_perplexity_search(self, query):
        """
        Get Perplexity search results through dashboard proxy
        """
        return self.call_external_service('perplexity', 'search', data={'query': query})
```

### Strategy 2: Direct Key Fetch (Fallback)
**When dashboard is unavailable:**
- Use manual key input by user
- Store hash only
- Keep in memory for session duration only

**Use Cases:**
- Testing without dashboard access
- Emergency manual override
- Development with temporary keys

---

## 🚨 Empty Databases (Critical Security)

### Database Vacuums and Analysis

**Policy:**
```bash
# Run weekly or after suspected breach
VACUUM FULL VERBOSE ANALYZE api_keys;
```

**Why This Matters:**
- ✅ Removes old data completely
- ✅ Updates statistics for query optimization
- ✅ Detects bloat and corruption
- ✅ Returns space to OS
- ✅ Logs analysis for security review

**Automated Schedule:**
```bash
# Add to cron (weekly)
0 3 * * * /path/to/vacuum-script.sh
```

---

## 🔒 Enhanced Security Procedures

### 1. Credential Hygiene

**What We Store:**
- ✅ SHA-256 hashes of API keys only
- ✅ JWT tokens (short-lived, revocable)
- ✅ Non-sensitive metadata (service type, permissions, expiry)

**What We DON'T Store:**
- ❌ API keys in plaintext
- ❌ Passwords or secrets
- ❌ Private keys (SSH, GPG, etc.)
- ❌ Environment variables with secrets
- ❌ Configuration files with credentials

### 2. Key Lifecycle Management

**Key Fetch:**
- Fetch from dashboard API
- Generate hash
- Store hash in database
- Set expiry tracking
- Log access

**Key Usage:**
- Check expiry before each API call
- Use most recent active key
- Validate permissions
- Log every access for audit trail

**Key Expiry:**
- Monitor expires_at field
- Mark inactive when expired
- Auto-request refresh through dashboard
- Fallback to next available key if dashboard unavailable

**Key Rotation:**
- Dashboard handles automatic rotation
- We detect new hashes and update database
- Old keys remain in DB but marked inactive
- Audit log shows rotation history

### 3. Database Security

**Connection Security:**
- Use SSL/TLS for all database connections
- Connection pooling with secure credentials
- Separate database user for each service/tenant
- Least privilege: Each user gets their own DB user

**Query Security:**
- Parameterized queries only (prevent SQL injection)
- Whitelist allowed columns
- Row-level security (user_id)
- Database user without super privileges for app queries

**Access Control:**
- Row-level security on all tables (account_id)
- Users can only access their own data
- API keys are never returned in queries
- Only hashes are returned, never plaintext keys

**Auditing:**
- All key fetches logged (who, when, why, IP)
- All API calls logged (service, endpoint, duration)
- Failed access attempts logged
- Regular audit reports generated

---

## 📊 Security Audit Trail

### Audit Log Queries

```sql
-- Recent key fetches by account
SELECT 
    a.email,
    ak.service,
    ak.created_at,
    ak.accessed_at,
    ak.accessed_by
    COUNT(*) as fetch_count
FROM accounts a
JOIN api_keys ak ON a.id = ak.account_id
JOIN key_usage_logs kl ON ak.key_hash = kl.key_hash
WHERE a.id = $1
GROUP BY a.id, ak.service
ORDER BY kl.accessed_at DESC
LIMIT 20;

-- Failed access attempts
SELECT 
    kl.key_hash,
    COUNT(*) as fail_count,
    MAX(kl.accessed_at) as last_attempt
FROM key_usage_logs kl
WHERE kl.accessed_by = 'bot_service'
AND kl.purpose LIKE 'fetch%'
AND kl.accessed_at > NOW() - INTERVAL '7 days'
GROUP BY kl.key_hash
HAVING COUNT(*) > 3;

-- Active vs expired keys
SELECT 
    ak.service,
    COUNT(*) FILTER (WHERE ak.expires_at > NOW()) as active,
    COUNT(*) FILTER (WHERE ak.expires_at <= NOW()) as expired
FROM api_keys ak
WHERE ak.account_id = $1
GROUP BY ak.service;
```

### Automated Security Alerts

**Triggers for Alerts:**
- Multiple failed access attempts (>3 in 1 hour)
- Key expiry approaching (<24 hours)
- Unusual IP address for API access
- Suspicious API call patterns

**Alert Delivery:**
```python
def send_security_alert(severity, title, details):
    """
    Send security alert via WhatsApp or dashboard
    """
    # Implementation depends on available alert mechanisms
    # Could be dashboard API call, email, or webhook
    pass
```

---

## 🎯 Super Bowl Preparation with Secure Keys

### Key Management for Super Bowl

**Phase 1: Get Keys (via Dashboard)**
```python
# Fetch Kalshi API key for live Super Bowl trading
kalshi_response = key_manager.fetch_from_dashboard(
    service='kalshi_api',
    jwt_token=user_jwt_token,
    dashboard_url=dashboard_api_url
)

if kalshi_response['success']:
    kalshi_key_hash = kalshi_response['key_hash']
    expires_at = kalshi_response['expires_at']
    
    # Store hash
    key_manager.store_key_hash(
        account_id=user_account_id,
        service='kalshi_api',
        key_hash=kalshi_key_hash,
        expires_at=expires_at,
        permissions=['read', 'write', 'trade'],
        key_type='dashboard'
    )
    
    print("✅ Kalshi API key stored securely (hashed)")
else:
    print(f"❌ Failed to fetch Kalshi key: {kalshi_response['error']}")

# Fetch Perplexity API key for enhanced research
perplexity_response = key_manager.fetch_from_dashboard(
    service='perplexity_api',
    jwt_token=user_jwt_token,
    dashboard_url=dashboard_api_url
)

if perplexity_response['success']:
    perplexity_key_hash = perplexity_response['key_hash']
    
    key_manager.store_key_hash(
        account_id=user_account_id,
        service='perplexity_api',
        key_hash=perplexity_key_hash,
        expires_at=perplexity_response['expires_at'],
        permissions=['search', 'completion'],
        key_type='dashboard'
    )
    
    print("✅ Perplexity API key stored securely (hashed)")
```

**Phase 2: Use Keys via Proxy**
```python
# Dashboard proxy for Kalshi API calls
kalshi_proxy = DashboardAPIProxy(jwt_token, dashboard_url)

# Get Super Bowl markets
markets = kalshi_proxy.get_kalshi_markets(market_type='nfl_superbowl')

# The proxy handles key management - our bot never sees plaintext keys
print(f"✅ Found {len(markets)} Super Bowl markets")

# Use Perplexity for research (via proxy)
perplexity_results = kalshi_proxy.get_perplexity_search(
    "Super Bowl 2026 betting trends and strategies"
)

print("✅ Perplexity research completed via dashboard proxy")
```

---

## 🛡️ Additional Security Measures

### 1. Environment Variables (Critical)
```bash
# Never do this in your code:
export KALSHI_API_KEY="your_actual_key_here"
export PERPLEXITY_API_KEY="your_actual_key_here"

# Instead, use:
# 1. Fetch from dashboard API (hashed storage)
# 2. Use only hashes in memory for session duration
# 3. Never log or print plaintext keys
```

### 2. File Security
```bash
# Secure file permissions
chmod 700 /root/.openclaw/credentials
chmod 700 /root/.openclaw/workspace/shared

# Ensure sensitive files are not readable by others
find /root/.openclaw -type f -name "*.key" -o -name "*.secret" -exec chmod 600 {} \;
```

### 3. Network Security
```bash
# Continue using Tailscale for remote access
# Never expose database ports publicly
# Keep Jupyter on localhost if not needed externally
# Use firewall rules to restrict access
```

### 4. Docker Security
```yaml
# In docker-compose.yml:
services:
  postgres:
    # NO exposed ports (remove 'ports:' section)
    networks:
      - internal-only
      internal: true

  jupyter:
    # Bind to localhost only
    ports:
      - "127.0.0.1:8888:8888"
    networks:
      - internal-only
      internal: true
```

---

## 📊 Security Metrics & Monitoring

### Key Security Metrics to Track

1. **Database Security**
   - Number of keys fetched (by user, by service)
   - Key rotation frequency
   - Failed access attempts
   - Time since last database vacuum

2. **API Security**
   - Number of API calls per service
   - Response time averages
   - Failed API calls
   - Rate limiting triggers

3. **System Security**
   - Unauthorized access attempts
   - Exposed port detections
   - Failed login attempts
   - SSL certificate expiry

4. **Compliance**
   - GDPR data requests (if applicable)
   - Key retention policy
   - Audit log retention policy

---

## 🚀 Implementation Steps

### Step 1: Dashboard API Integration (This Week)
- [ ] Design and document dashboard API endpoints
- [ ] Implement authentication flow (JWT handling)
- [ ] Implement key fetch API client
- [ ] Update database schema for key management
- [ ] Build KeyManager class with dashboard integration
- [ ] Create DashboardAPIProxy for external API calls
- [ ] Add security audit logging

### Step 2: Super Bowl Preparation (Using Secure Keys)
- [ ] Document dashboard key integration
- [ ] Configure environment variables for dashboard URL
- [ ] Test key fetch from dashboard (sandbox mode)
- [ ] Update Super Bowl strategy to use dashboard proxy
- [ ] Validate that no plaintext keys are stored
- [ ] Test that empty databases are maintained

### Step 3: Security Hardening (Ongoing)
- [ ] Implement automated database vacuums
- [ ] Add security monitoring and alerting
- [ ] Conduct security audit of codebase
- [ ] Implement rate limiting for dashboard API calls
- [ ] Add audit trail for all key operations

---

## 🎯 Success Criteria

**Security:**
- ✅ No plaintext API keys in database
- ✅ No plaintext API keys in code
- ✅ No plaintext API keys in environment variables
- ✅ No plaintext API keys in logs
- ✅ Database empty of sensitive data
- ✅ All keys fetched via dashboard API and hashed
- ✅ Key usage logged for every operation

**Functionality:**
- ✅ Bot can fetch keys from dashboard API
- ✅ Bot can make API calls via dashboard proxy
- ✅ Bot can handle key rotation from dashboard
- ✅ Bot never has access to plaintext keys
- ✅ All key operations are audited

**Performance:**
- ✅ Minimal overhead for dashboard proxy (one extra hop)
- ✅ Efficient key lookup from database
- ✅ Automatic key refresh when approaching expiry

---

## 📝 Notes for Implementation

**Critical Security Principle:**
> "We NEVER have access to plaintext API keys. All keys are fetched from user's dashboard API and stored as hashes only. The dashboard manages the actual keys and makes the API calls. Our system is architecturally secure by design."

**Database State:**
- Tables exist but should be empty (no keys yet)
- All sensitive data (actual keys) stored in dashboard
- Only hashes and metadata stored locally
- This is the secure architecture the user requested

**Next Actions:**
1. Get dashboard API documentation from user
2. Implement authentication flow (JWT)
3. Implement key fetch and hash storage
4. Build dashboard API proxy for external service calls
5. Update Super Bowl bot to use secure key management
6. Test entire flow with sandbox keys
7. Prepare for real Super Bowl deployment

---

**Status:** Ready for implementation
**Priority:** High security, medium complexity
**Timeline:** 1-2 weeks for full implementation
**Dependencies:** Dashboard API documentation from user

---

**Created by:** OpenClaw Security Team (Pipeline + Shield collaboration)
**Version:** 1.0 - Secure Key Management Architecture
**Date:** February 6, 2026
