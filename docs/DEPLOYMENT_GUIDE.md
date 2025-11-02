# Aetherra Deployment Guide

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This guide covers deploying Aetherra OS and Hub in different environments, from local development to production. It includes configuration best practices, service orchestration, monitoring setup, and operational procedures.

## Purpose and scope

- Configure Aetherra for different deployment environments
- Set up production-grade infrastructure
- Implement monitoring and alerting
- Establish backup and disaster recovery procedures
- Secure production deployments

## Deployment tiers

Aetherra supports multiple deployment tiers, each with different requirements and guarantees:

| Tier            | Use Case                       | Availability | Data Persistence | Monitoring      |
| --------------- | ------------------------------ | ------------ | ---------------- | --------------- |
| **Development** | Local testing, experimentation | Best-effort  | Optional         | Console logs    |
| **Test**        | CI/CD, automated testing       | Best-effort  | Ephemeral        | Basic metrics   |
| **Staging**     | Pre-production validation      | High         | Persistent       | Full monitoring |
| **Production**  | Live deployments               | Critical     | Replicated       | Full + alerting |

---

## Prerequisites

### System Requirements

**Minimum (Development):**

- CPU: 2 cores
- RAM: 4 GB
- Disk: 10 GB free space
- OS: Windows 10/11, Linux, macOS

**Recommended (Production):**

- CPU: 4+ cores
- RAM: 8+ GB
- Disk: 50+ GB SSD
- OS: Linux (Ubuntu 22.04 LTS recommended)

### Software Dependencies

**Required:**

- Python 3.11 or 3.12
- pip (Python package manager)
- Git

**Optional:**

- Docker (for containerized deployment)
- PostgreSQL (for production memory backend)
- Redis (for distributed caching)
- nginx/Caddy (reverse proxy for production)
- systemd (for service management on Linux)

---

## Development Environment

### Quick Start

**1. Clone repository:**

```bash
git clone https://github.com/AetherraLabs/Aetherra.git
cd Aetherra
```

**2. Create virtual environment:**

```bash
# Windows
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux/macOS
python3 -m venv .venv
source .venv/bin/activate
```

**3. Install dependencies:**

```bash
pip install -r requirements.txt
```

**4. Create configuration:**

```bash
# Copy example config
cp config.example.json config.json

# Or create minimal config
cat > config.json << 'EOF'
{
  "hub_enabled": true,
  "gui_enabled": false,
  "log_level": "INFO"
}
EOF
```

**5. Start Aetherra OS:**

```bash
python aetherra_os_launcher.py --mode full -v
```

**6. Start Hub (in separate terminal):**

```bash
python tools/run_hub_ai_api.py --port 3001
```

**7. Verify:**

```bash
curl http://localhost:3001/api/stats
```

### Development Configuration

**config.json for development:**

```json
{
  "hub_enabled": true,
  "gui_enabled": false,
  "log_level": "DEBUG",
  "self_improvement": {
    "enabled": true
  },
  "homeostasis": {
    "enabled": true
  },
  "hmr_enabled": true,
  "plugins_enabled": true
}
```

**Environment variables:**

```bash
# Development settings
export AETHERRA_PROFILE=dev
export AETHERRA_LOG_LEVEL=DEBUG
export AETHERRA_QUIET=0

# Enable features
export AETHERRA_HMR_ENABLED=1
export AETHERRA_HMR_MODE=safe

# Relaxed security (development only!)
export AETHERRA_NET_STRICT=0
export AETHERRA_AI_API_REQUIRE_TOKEN=0
```

---

## Test Environment (CI/CD)

### Automated Testing Setup

**Test configuration:**

```json
{
  "hub_enabled": true,
  "gui_enabled": false,
  "log_level": "WARNING"
}
```

**Environment variables:**

```bash
# Test profile (deterministic behavior)
export AETHERRA_PROFILE=test
export AETHERRA_QUIET=1

# Disable features that need external services
export AETHERRA_AI_API_ENABLED=0
export AETHERRA_MEMORY_STORM=0

# Use in-memory databases
export AETHERRA_MEMORY_DB=:memory:
```

### CI/CD Pipeline Example (GitHub Actions)

**.github/workflows/test.yml:**

```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt

    - name: Run smoke tests
      env:
        AETHERRA_PROFILE: test
        AETHERRA_QUIET: 1
      run: |
        python tools/os_smoke.py

    - name: Run capability tests
      env:
        AETHERRA_PROFILE: test
      run: |
        pytest -q tests/capabilities/

    - name: Run unit tests with coverage
      run: |
        pytest --cov=Aetherra --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

---

## Staging Environment

### Purpose

Staging mirrors production configuration but uses test data. Use it to:

- Validate deployment procedures
- Test configuration changes
- Perform load testing
- Train new operators

### Infrastructure Setup

**Server configuration:**

- Dedicated server or VM
- Production-like resources (CPU, RAM, disk)
- Same OS as production
- Network isolation from production

**Service architecture:**

```
┌─────────────────────────────────────────────────────┐
│                   Staging Server                     │
│                                                      │
│  ┌──────────────┐     ┌──────────────┐             │
│  │   nginx      │────▶│  Aetherra    │             │
│  │  (Reverse    │     │     Hub      │             │
│  │   Proxy)     │     │  (Port 3001) │             │
│  └──────────────┘     └──────────────┘             │
│         │                     │                      │
│         │              ┌──────────────┐             │
│         └─────────────▶│  Aetherra    │             │
│                        │      OS      │             │
│                        └──────────────┘             │
│                               │                      │
│                        ┌──────────────┐             │
│                        │  PostgreSQL  │             │
│                        │   Database   │             │
│                        └──────────────┘             │
└─────────────────────────────────────────────────────┘
```

### Configuration

**config.json for staging:**

```json
{
  "environment": "staging",
  "hub_enabled": true,
  "gui_enabled": false,
  "log_level": "INFO",

  "database": {
    "type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "aetherra_staging",
    "user": "aetherra",
    "password_env": "AETHERRA_DB_PASSWORD"
  },

  "self_improvement": {
    "enabled": true,
    "require_approval": true
  },

  "homeostasis": {
    "enabled": true,
    "action_mode": "active_limited"
  },

  "security": {
    "strict_mode": true,
    "require_signatures": true,
    "network_allowlist": ["staging.aetherra.internal"]
  },

  "monitoring": {
    "prometheus_enabled": true,
    "metrics_port": 9090
  }
}
```

**Environment variables:**

```bash
# Staging profile
export AETHERRA_PROFILE=staging
export AETHERRA_ENV=staging

# Security
export AETHERRA_NET_STRICT=1
export AETHERRA_AI_API_REQUIRE_TOKEN=1
export AETHERRA_AI_API_TOKEN=$(cat /secrets/api_token)

# Database
export AETHERRA_DB_PASSWORD=$(cat /secrets/db_password)

# HMR (enabled but monitored)
export AETHERRA_HMR_ENABLED=1
export AETHERRA_HMR_AUDIT_PATH=/var/log/aetherra/hmr_audit.jsonl

# Metrics
export AETHERRA_PROMETHEUS_PORT=9090
```

### Deployment Script (staging-deploy.sh)

```bash
#!/bin/bash
set -euo pipefail

DEPLOY_DIR="/opt/aetherra"
BACKUP_DIR="/opt/aetherra/backups"
LOG_DIR="/var/log/aetherra"

echo "=== Aetherra Staging Deployment ==="

# 1. Backup current installation
echo "[1/8] Creating backup..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/aetherra_backup_$TIMESTAMP.tar.gz" \
    "$DEPLOY_DIR" \
    --exclude="$DEPLOY_DIR/.venv" \
    --exclude="$BACKUP_DIR"

# 2. Pull latest code
echo "[2/8] Pulling latest code..."
cd "$DEPLOY_DIR"
git fetch origin
git checkout main
git pull origin main

# 3. Update dependencies
echo "[3/8] Updating dependencies..."
source .venv/bin/activate
pip install -r requirements.txt --upgrade

# 4. Run database migrations (if any)
echo "[4/8] Running migrations..."
python tools/migrate_database.py --env staging

# 5. Validate configuration
echo "[5/8] Validating configuration..."
python tools/validate_config.py config.json

# 6. Stop services
echo "[6/8] Stopping services..."
sudo systemctl stop aetherra-hub
sudo systemctl stop aetherra-os

# 7. Start services
echo "[7/8] Starting services..."
sudo systemctl start aetherra-os
sleep 10
sudo systemctl start aetherra-hub

# 8. Health check
echo "[8/8] Running health check..."
for i in {1..30}; do
    if curl -sf http://localhost:3001/api/stats > /dev/null; then
        echo "✓ Services healthy"
        exit 0
    fi
    echo "Waiting for services... ($i/30)"
    sleep 2
done

echo "✗ Health check failed"
exit 1
```

---

## Production Environment

### Infrastructure Requirements

**Production-grade setup:**

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer / CDN                       │
│                    (Cloudflare, AWS ELB)                     │
└────────────────────────┬────────────────────────────────────┘
                         │
            ┌────────────┴────────────┐
            │                         │
┌───────────▼──────────┐   ┌─────────▼───────────┐
│   Production Node 1   │   │  Production Node 2   │
│                       │   │                       │
│  ┌─────────────────┐ │   │  ┌─────────────────┐ │
│  │  nginx (TLS)    │ │   │  │  nginx (TLS)    │ │
│  └────────┬────────┘ │   │  └────────┬────────┘ │
│           │          │   │            │          │
│  ┌────────▼────────┐ │   │  ┌─────────▼───────┐ │
│  │ Aetherra Hub    │ │   │  │  Aetherra Hub   │ │
│  └────────┬────────┘ │   │  └─────────┬───────┘ │
│           │          │   │            │          │
│  ┌────────▼────────┐ │   │  ┌─────────▼───────┐ │
│  │ Aetherra OS     │ │   │  │  Aetherra OS    │ │
│  └─────────────────┘ │   │  └─────────────────┘ │
└──────────┬───────────┘   └──────────┬───────────┘
           │                          │
           └──────────┬───────────────┘
                      │
         ┌────────────▼─────────────┐
         │  PostgreSQL Cluster      │
         │  (Primary + Replicas)    │
         └──────────────────────────┘
                      │
         ┌────────────▼─────────────┐
         │  Redis Cluster           │
         │  (Caching, Sessions)     │
         └──────────────────────────┘
```

### Production Configuration

**config.json for production:**

```json
{
  "environment": "production",
  "hub_enabled": true,
  "gui_enabled": false,
  "log_level": "WARNING",

  "database": {
    "type": "postgresql",
    "host": "postgres-primary.internal",
    "port": 5432,
    "database": "aetherra_prod",
    "user": "aetherra",
    "password_env": "AETHERRA_DB_PASSWORD",
    "pool_size": 20,
    "max_overflow": 10,
    "ssl_mode": "require"
  },

  "cache": {
    "type": "redis",
    "host": "redis-cluster.internal",
    "port": 6379,
    "password_env": "AETHERRA_REDIS_PASSWORD",
    "ssl": true
  },

  "self_improvement": {
    "enabled": true,
    "require_approval": true,
    "max_proposals_per_hour": 5
  },

  "homeostasis": {
    "enabled": true,
    "action_mode": "active_limited",
    "emergency_contact": "ops@aetherraalabs.com"
  },

  "security": {
    "strict_mode": true,
    "require_signatures": true,
    "network_allowlist": [
      "aetherra.ai",
      "*.aetherra.ai",
      "trusted-partner.com"
    ],
    "rate_limiting": {
      "enabled": true,
      "requests_per_minute": 100
    }
  },

  "monitoring": {
    "prometheus_enabled": true,
    "metrics_port": 9090,
    "alerting_enabled": true,
    "alert_webhook": "https://alerts.aetherra.ai/webhook"
  },

  "backup": {
    "enabled": true,
    "schedule": "0 2 * * *",
    "retention_days": 30,
    "s3_bucket": "aetherra-backups-prod"
  }
}
```

**Production environment variables:**

```bash
# Production profile
export AETHERRA_PROFILE=production
export AETHERRA_ENV=production

# Security (strict)
export AETHERRA_NET_STRICT=1
export AETHERRA_AI_API_REQUIRE_TOKEN=1
export AETHERRA_AGENTS_API_REQUIRE_TOKEN=1
export AETHERRA_AI_API_TOKEN=$(vault kv get -field=token secret/aetherra/api)

# Database (from secrets manager)
export AETHERRA_DB_PASSWORD=$(vault kv get -field=password secret/aetherra/database)
export AETHERRA_REDIS_PASSWORD=$(vault kv get -field=password secret/aetherra/redis)

# TLS/SSL
export AETHERRA_TLS_CERT=/etc/ssl/certs/aetherra.crt
export AETHERRA_TLS_KEY=/etc/ssl/private/aetherra.key

# HMR (disabled in production initially)
export AETHERRA_HMR_ENABLED=0

# Limits
export AETHERRA_PLUGIN_INVOKE_TIMEOUT_SEC=20
export AETHERRA_PLUGIN_CB_THRESHOLD=3
export AETHERRA_PLUGIN_MAX_CONCURRENCY=1

# Monitoring
export AETHERRA_PROMETHEUS_PORT=9090
export AETHERRA_METRICS_FLUSH_SEC=30

# Logging
export AETHERRA_LOG_LEVEL=WARNING
export AETHERRA_LOG_FILE=/var/log/aetherra/aetherra_os.log
```

### Systemd Service Files

**aetherra-os.service:**

```ini
[Unit]
Description=Aetherra OS
After=network.target postgresql.service redis.service
Wants=aetherra-hub.service

[Service]
Type=simple
User=aetherra
Group=aetherra
WorkingDirectory=/opt/aetherra
EnvironmentFile=/etc/aetherra/environment
ExecStart=/opt/aetherra/.venv/bin/python aetherra_os_launcher.py --mode full
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/aetherra/data /var/log/aetherra

# Resource limits
LimitNOFILE=65536
MemoryMax=8G
CPUQuota=400%

[Install]
WantedBy=multi-user.target
```

**aetherra-hub.service:**

```ini
[Unit]
Description=Aetherra Hub
After=network.target aetherra-os.service
Requires=aetherra-os.service

[Service]
Type=simple
User=aetherra
Group=aetherra
WorkingDirectory=/opt/aetherra
EnvironmentFile=/etc/aetherra/environment
ExecStart=/opt/aetherra/.venv/bin/python tools/run_hub_ai_api.py --port 3001
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true

# Resource limits
LimitNOFILE=65536
MemoryMax=4G
CPUQuota=200%

[Install]
WantedBy=multi-user.target
```

**Installation:**

```bash
# Copy service files
sudo cp aetherra-os.service /etc/systemd/system/
sudo cp aetherra-hub.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable services
sudo systemctl enable aetherra-os
sudo systemctl enable aetherra-hub

# Start services
sudo systemctl start aetherra-os
sudo systemctl start aetherra-hub

# Check status
sudo systemctl status aetherra-os
sudo systemctl status aetherra-hub
```

---

## Reverse Proxy Configuration

### nginx Configuration

**/etc/nginx/sites-available/aetherra:**

```nginx
upstream aetherra_hub {
    server 127.0.0.1:3001 fail_timeout=5s max_fails=3;
    keepalive 32;
}

# Rate limiting zones
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=stream_limit:10m rate=2r/s;

# HTTP redirect to HTTPS
server {
    listen 80;
    server_name aetherra.ai;
    return 301 https://$server_name$request_uri;
}

# HTTPS server
server {
    listen 443 ssl http2;
    server_name aetherra.ai;

    # TLS configuration
    ssl_certificate /etc/ssl/certs/aetherra.crt;
    ssl_certificate_key /etc/ssl/private/aetherra.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Logging
    access_log /var/log/nginx/aetherra_access.log combined;
    error_log /var/log/nginx/aetherra_error.log warn;

    # API endpoints
    location /api/ {
        limit_req zone=api_limit burst=20 nodelay;

        proxy_pass http://aetherra_hub;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # SSE streaming endpoints
    location ~ ^/api/ai/(stream|stream_ws) {
        limit_req zone=stream_limit burst=5 nodelay;

        proxy_pass http://aetherra_hub;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Disable buffering for streaming
        proxy_buffering off;
        proxy_cache off;

        # Long timeouts for streaming
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }

    # Metrics endpoint (restrict access)
    location /metrics {
        allow 10.0.0.0/8;      # Internal network
        deny all;

        proxy_pass http://aetherra_hub;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://aetherra_hub/api/stats;
    }

    # Static files (if serving frontend)
    location / {
        root /opt/aetherra/frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

**Enable and test:**

```bash
# Test configuration
sudo nginx -t

# Enable site
sudo ln -s /etc/nginx/sites-available/aetherra /etc/nginx/sites-enabled/

# Reload nginx
sudo systemctl reload nginx
```

---

## Database Setup

### PostgreSQL for Production

**Install PostgreSQL:**

```bash
sudo apt update
sudo apt install postgresql-14 postgresql-contrib
```

**Create database and user:**

```sql
-- Connect as postgres user
sudo -u postgres psql

-- Create user
CREATE USER aetherra WITH PASSWORD 'secure_password_here';

-- Create database
CREATE DATABASE aetherra_prod OWNER aetherra;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE aetherra_prod TO aetherra;

-- Enable required extensions
\c aetherra_prod
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

**Initialize schema:**

```bash
# Run schema migration
python tools/migrate_database.py --env production --init
```

**Backup configuration:**

```bash
# Add to crontab
0 2 * * * pg_dump -U aetherra aetherra_prod | gzip > /backups/aetherra_prod_$(date +\%Y\%m\%d).sql.gz
```

---

## Monitoring Setup

### Prometheus Configuration

**prometheus.yml:**

```yaml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

scrape_configs:
  - job_name: 'aetherra-hub'
    static_configs:
      - targets: ['localhost:3001']
    metrics_path: '/metrics'

  - job_name: 'aetherra-kernel'
    static_configs:
      - targets: ['localhost:3001']
    metrics_path: '/api/kernel/metrics'

  - job_name: 'node-exporter'
    static_configs:
      - targets: ['localhost:9100']

alerting:
  alertmanagers:
    - static_configs:
        - targets: ['localhost:9093']

rule_files:
  - '/etc/prometheus/rules/*.yml'
```

### Alert Rules

**/etc/prometheus/rules/aetherra.yml:**

```yaml
groups:
  - name: aetherra_alerts
    interval: 30s
    rules:
      # Service availability
      - alert: AetherraOSDown
        expr: up{job="aetherra-kernel"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Aetherra OS is down"
          description: "Aetherra OS has been down for more than 2 minutes"

      - alert: AetherraHubDown
        expr: up{job="aetherra-hub"} == 0
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Aetherra Hub is down"

      # Performance
      - alert: HighTaskLatency
        expr: aetherra_kernel_task_latency_p95_ms > 500
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High task latency detected"
          description: "P95 task latency is {{ $value }}ms"

      - alert: HighMemoryRTT
        expr: aetherra_memory_rtt_ms_avg > 100
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory RTT"

      # System health
      - alert: LowSystemHealth
        expr: aetherra_homeostasis_health_score < 0.7
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "System health degraded"
          description: "Health score: {{ $value }}"

      # Resource usage
      - alert: HighCPUUsage
        expr: rate(process_cpu_seconds_total{job="aetherra-hub"}[5m]) > 0.9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"

      - alert: HighMemoryUsage
        expr: process_resident_memory_bytes{job="aetherra-hub"} > 8e9
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
```

### Grafana Dashboards

**Import pre-built dashboard:**

```bash
# Download Aetherra dashboard
curl -o aetherra-dashboard.json \
  https://raw.githubusercontent.com/AetherraLabs/Aetherra/main/monitoring/grafana/aetherra-dashboard.json

# Import via Grafana UI or API
curl -X POST http://admin:admin@localhost:3000/api/dashboards/db \
  -H "Content-Type: application/json" \
  -d @aetherra-dashboard.json
```

---

## Backup and Disaster Recovery

### Automated Backups

**backup-aetherra.sh:**

```bash
#!/bin/bash
set -euo pipefail

BACKUP_DIR="/backups/aetherra"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# 1. Backup database
pg_dump -U aetherra aetherra_prod | gzip > \
  "$BACKUP_DIR/database_$TIMESTAMP.sql.gz"

# 2. Backup configuration
tar -czf "$BACKUP_DIR/config_$TIMESTAMP.tar.gz" \
  /opt/aetherra/config.json \
  /etc/aetherra/ \
  /opt/aetherra/.aetherra/

# 3. Backup state files
tar -czf "$BACKUP_DIR/state_$TIMESTAMP.tar.gz" \
  /opt/aetherra/data/

# 4. Upload to S3 (optional)
if command -v aws &> /dev/null; then
    aws s3 sync "$BACKUP_DIR" s3://aetherra-backups-prod/
fi

# 5. Clean old backups
find "$BACKUP_DIR" -name "*.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: $TIMESTAMP"
```

**Schedule with cron:**

```bash
# Daily at 2 AM
0 2 * * * /opt/aetherra/scripts/backup-aetherra.sh >> /var/log/aetherra/backup.log 2>&1
```

### Disaster Recovery Procedure

**1. Restore from backup:**

```bash
#!/bin/bash
BACKUP_FILE="$1"

# Stop services
sudo systemctl stop aetherra-hub aetherra-os

# Restore database
gunzip -c backups/database_YYYYMMDD_HHMMSS.sql.gz | \
  psql -U aetherra aetherra_prod

# Restore configuration
tar -xzf backups/config_YYYYMMDD_HHMMSS.tar.gz -C /

# Restore state
tar -xzf backups/state_YYYYMMDD_HHMMSS.tar.gz -C /opt/aetherra/

# Start services
sudo systemctl start aetherra-os aetherra-hub

# Verify
curl http://localhost:3001/api/stats
```

---

## Security Best Practices

### Production Checklist

- [ ] Change all default passwords
- [ ] Enable TLS/SSL for all connections
- [ ] Use secrets manager (Vault, AWS Secrets Manager)
- [ ] Enable network allowlist (`AETHERRA_NET_STRICT=1`)
- [ ] Require API authentication tokens
- [ ] Enable rate limiting
- [ ] Restrict metrics endpoint access
- [ ] Enable audit logging
- [ ] Set up automated security updates
- [ ] Configure firewall rules
- [ ] Enable intrusion detection
- [ ] Regular security audits

### Secrets Management

**Using HashiCorp Vault:**

```bash
# Store secrets
vault kv put secret/aetherra/api token="your_api_token"
vault kv put secret/aetherra/database password="your_db_password"

# Retrieve in scripts
export AETHERRA_AI_API_TOKEN=$(vault kv get -field=token secret/aetherra/api)
```

---

## Operational Procedures

### Deployment Checklist

**Pre-deployment:**

- [ ] Test in staging environment
- [ ] Review configuration changes
- [ ] Check dependency updates
- [ ] Verify database migrations
- [ ] Create backup
- [ ] Notify team of deployment window

**During deployment:**

- [ ] Put application in maintenance mode (if applicable)
- [ ] Stop services gracefully
- [ ] Apply updates
- [ ] Run migrations
- [ ] Start services
- [ ] Verify health checks

**Post-deployment:**

- [ ] Monitor logs for errors
- [ ] Check metrics dashboards
- [ ] Verify key functionality
- [ ] Remove maintenance mode
- [ ] Update documentation
- [ ] Notify team of completion

### Rollback Procedure

```bash
#!/bin/bash
# Emergency rollback script

echo "=== EMERGENCY ROLLBACK ==="

# 1. Stop current services
sudo systemctl stop aetherra-hub aetherra-os

# 2. Restore previous version
cd /opt/aetherra
git reset --hard HEAD~1

# 3. Restore previous virtual environment
rm -rf .venv
tar -xzf /backups/venv_previous.tar.gz

# 4. Restore configuration
cp /backups/config_previous.json config.json

# 5. Rollback database (if needed)
# psql -U aetherra aetherra_prod < /backups/db_previous.sql

# 6. Start services
sudo systemctl start aetherra-os aetherra-hub

# 7. Verify
sleep 10
curl -f http://localhost:3001/api/stats || echo "ROLLBACK FAILED!"
```

---

## Related Documentation

- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - Troubleshooting common issues
- [AETHERRA_HUB_API_REFERENCE.md](./AETHERRA_HUB_API_REFERENCE.md) - API documentation
- [AETHERRA_SECURITY_SYSTEM.md](./AETHERRA_SECURITY_SYSTEM.md) - Security architecture
- [METRICS_AND_MONITORING_GUIDE.md](./METRICS_AND_MONITORING_GUIDE.md) - Detailed monitoring (coming soon)
- [BACKUP_AND_RECOVERY.md](./BACKUP_AND_RECOVERY.md) - Backup strategies (coming soon)

---

Status: ✅ Complete - Comprehensive deployment guide covering dev, test, staging, and production environments

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
