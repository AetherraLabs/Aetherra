# Aetherra Backup and Recovery Guide

> Maintained and officially operated by **Aetherra Labs**.
> **Powered by Aetherra Labs.**

Updated: 2025-11-01

This guide covers comprehensive backup strategies and disaster recovery procedures for Aetherra OS deployments. Protect your data and ensure business continuity.

## Purpose and Scope

- Understand backup requirements and strategies
- Implement automated backup systems
- Restore from backups after failures
- Test disaster recovery procedures
- Define Recovery Time Objective (RTO) and Recovery Point Objective (RPO)
- Maintain business continuity

## What Needs Backing Up?

**Critical Aetherra Components:**

| Component          | Data Type                    | Frequency | Priority |
| ------------------ | ---------------------------- | --------- | -------- |
| **Memory Events**  | Event history, learning data | Hourly    | Critical |
| **Configuration**  | System settings, policies    | Daily     | Critical |
| **Plugin Data**    | Custom plugins, states       | Daily     | High     |
| **Database**       | Persistent storage           | Hourly    | Critical |
| **Aether Scripts** | Workflows, automations       | Daily     | High     |
| **Logs**           | Audit trails, diagnostics    | Daily     | Medium   |
| **Certificates**   | TLS/SSL certificates         | Weekly    | High     |

---

## Quick Start

### Minimal Backup Setup (10 Minutes)

**1. Create backup script:**

```bash
#!/bin/bash
# minimal_backup.sh - Quick backup script

BACKUP_DIR="/backups/aetherra"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"

mkdir -p "$BACKUP_PATH"

# Backup memory events
cp -r data/memory/* "$BACKUP_PATH/memory/"

# Backup configuration
cp config.json "$BACKUP_PATH/"
cp -r policies/ "$BACKUP_PATH/policies/"

# Backup Aether scripts
cp -r workflows/ "$BACKUP_PATH/workflows/"

# Backup plugins
cp -r Aetherra/plugins/ "$BACKUP_PATH/plugins/"

# Create archive
tar -czf "$BACKUP_PATH.tar.gz" -C "$BACKUP_DIR" "backup_$TIMESTAMP"
rm -rf "$BACKUP_PATH"

echo "Backup complete: $BACKUP_PATH.tar.gz"
```

**2. Make executable and run:**

```bash
chmod +x minimal_backup.sh
./minimal_backup.sh
```

**3. Schedule with cron:**

```bash
# Add to crontab (hourly backups)
crontab -e

# Add this line:
0 * * * * /path/to/minimal_backup.sh >> /var/log/aetherra_backup.log 2>&1
```

**4. Test restore:**

```bash
# Extract backup
tar -xzf /backups/aetherra/backup_TIMESTAMP.tar.gz -C /tmp/

# Verify contents
ls -la /tmp/backup_TIMESTAMP/
```

---

## Backup Architecture

### Backup Strategy Overview

```
┌──────────────────────────────────────────────────────────┐
│                 Backup Strategy Flow                      │
└──────────────────────────────────────────────────────────┘

1. CONTINUOUS (Hot)
   ├─ Database replication (streaming)
   ├─ Transaction logs
   └─ Real-time sync to standby

2. INCREMENTAL (Warm)
   ├─ Changed files only (hourly)
   ├─ Differential backups
   └─ Lower storage overhead

3. FULL (Cold)
   ├─ Complete system snapshot (daily/weekly)
   ├─ All data and configuration
   └─ Independent restore points

4. OFFSITE
   ├─ Remote storage (S3, Azure Blob)
   ├─ Geographic redundancy
   └─ Disaster protection

5. ARCHIVE
   ├─ Long-term retention (yearly)
   ├─ Compliance requirements
   └─ Compressed storage
```

### 3-2-1 Backup Rule

Follow industry best practice:

- **3** copies of your data
- **2** different storage media types
- **1** copy offsite

**Example Implementation:**

1. **Primary data** - Live Aetherra OS installation
2. **Local backup** - Daily backups on attached storage
3. **Remote backup** - Hourly sync to cloud storage (S3/Azure)

---

## Automated Backup System

### Comprehensive Backup Script

**aetherra_backup.sh:**

```bash
#!/bin/bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Comprehensive Aetherra OS backup script

set -e  # Exit on error

# Configuration
AETHERRA_ROOT="/opt/aetherra"
BACKUP_ROOT="/backups/aetherra"
RETENTION_DAYS=30
S3_BUCKET="s3://aetherra-backups-prod"
NOTIFICATION_EMAIL="ops@example.com"

# Logging
LOG_FILE="/var/log/aetherra_backup.log"
exec > >(tee -a "$LOG_FILE")
exec 2>&1

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

error() {
    log "ERROR: $*"
    exit 1
}

# Generate timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="aetherra_backup_$TIMESTAMP"
BACKUP_PATH="$BACKUP_ROOT/$BACKUP_NAME"

log "Starting Aetherra backup: $BACKUP_NAME"

# Create backup directory
mkdir -p "$BACKUP_PATH"/{memory,config,plugins,scripts,database,logs}

# 1. Backup Memory System
log "Backing up memory system..."
if [ -d "$AETHERRA_ROOT/data/memory" ]; then
    cp -r "$AETHERRA_ROOT/data/memory"/* "$BACKUP_PATH/memory/" || error "Memory backup failed"
    log "Memory backup: $(du -sh $BACKUP_PATH/memory | cut -f1)"
fi

# 2. Backup Configuration
log "Backing up configuration..."
cp "$AETHERRA_ROOT/config.json" "$BACKUP_PATH/config/"
cp -r "$AETHERRA_ROOT/policies" "$BACKUP_PATH/config/"
log "Configuration backup complete"

# 3. Backup Plugins
log "Backing up plugins..."
cp -r "$AETHERRA_ROOT/Aetherra/plugins" "$BACKUP_PATH/plugins/"
cp -r "$AETHERRA_ROOT/plugins" "$BACKUP_PATH/plugins/custom"
log "Plugins backup complete"

# 4. Backup Aether Scripts
log "Backing up Aether scripts..."
cp -r "$AETHERRA_ROOT/workflows" "$BACKUP_PATH/scripts/"
log "Scripts backup complete"

# 5. Backup Database (if using PostgreSQL)
log "Backing up database..."
if command -v pg_dump &> /dev/null; then
    pg_dump -U aetherra -F c -b -v -f "$BACKUP_PATH/database/aetherra_db.dump" aetherra || log "WARNING: Database backup failed"
fi

# 6. Backup Logs (last 7 days)
log "Backing up logs..."
find "$AETHERRA_ROOT/logs" -name "*.log" -mtime -7 -exec cp {} "$BACKUP_PATH/logs/" \;

# 7. Create manifest
log "Creating backup manifest..."
cat > "$BACKUP_PATH/manifest.json" <<EOF
{
  "backup_name": "$BACKUP_NAME",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "aetherra_version": "$(cat $AETHERRA_ROOT/VERSION 2>/dev/null || echo 'unknown')",
  "hostname": "$(hostname)",
  "backup_size_mb": $(du -sm "$BACKUP_PATH" | cut -f1),
  "components": {
    "memory": true,
    "config": true,
    "plugins": true,
    "scripts": true,
    "database": true,
    "logs": true
  }
}
EOF

# 8. Create compressed archive
log "Creating compressed archive..."
cd "$BACKUP_ROOT"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME" || error "Archive creation failed"
ARCHIVE_SIZE=$(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)
log "Archive created: ${BACKUP_NAME}.tar.gz ($ARCHIVE_SIZE)"

# 9. Calculate checksums
log "Calculating checksums..."
sha256sum "${BACKUP_NAME}.tar.gz" > "${BACKUP_NAME}.tar.gz.sha256"

# 10. Upload to S3 (if configured)
if [ -n "$S3_BUCKET" ] && command -v aws &> /dev/null; then
    log "Uploading to S3..."
    aws s3 cp "${BACKUP_NAME}.tar.gz" "$S3_BUCKET/" || log "WARNING: S3 upload failed"
    aws s3 cp "${BACKUP_NAME}.tar.gz.sha256" "$S3_BUCKET/" || log "WARNING: S3 checksum upload failed"
fi

# 11. Clean up old backups
log "Cleaning up old backups (retention: $RETENTION_DAYS days)..."
find "$BACKUP_ROOT" -name "aetherra_backup_*.tar.gz" -mtime +$RETENTION_DAYS -delete
log "Old backups cleaned"

# 12. Remove temporary directory
rm -rf "$BACKUP_PATH"

# 13. Send notification
log "Backup completed successfully: ${BACKUP_NAME}.tar.gz ($ARCHIVE_SIZE)"

if command -v mail &> /dev/null; then
    echo "Aetherra backup completed: ${BACKUP_NAME}.tar.gz ($ARCHIVE_SIZE)" | \
        mail -s "Aetherra Backup Success" "$NOTIFICATION_EMAIL"
fi

log "Backup process complete"
```

### Incremental Backup Script

**aetherra_incremental_backup.sh:**

```bash
#!/bin/bash
# Incremental backup using rsync

AETHERRA_ROOT="/opt/aetherra"
BACKUP_ROOT="/backups/aetherra/incremental"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create incremental backup with hard links
rsync -av --link-dest="$BACKUP_ROOT/latest" \
    --exclude='*.log' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.git' \
    "$AETHERRA_ROOT/" \
    "$BACKUP_ROOT/backup_$TIMESTAMP/"

# Update latest symlink
ln -nsf "backup_$TIMESTAMP" "$BACKUP_ROOT/latest"

echo "Incremental backup complete: backup_$TIMESTAMP"
```

### Database-Specific Backups

**PostgreSQL continuous archiving:**

```bash
#!/bin/bash
# PostgreSQL WAL archiving for point-in-time recovery

# In postgresql.conf:
# wal_level = replica
# archive_mode = on
# archive_command = '/path/to/archive_wal.sh %p %f'

WAL_FILE="$1"
WAL_FILENAME="$2"
ARCHIVE_DIR="/backups/aetherra/wal_archive"

# Copy WAL file to archive
cp "$WAL_FILE" "$ARCHIVE_DIR/$WAL_FILENAME"

# Optional: Upload to S3
aws s3 cp "$ARCHIVE_DIR/$WAL_FILENAME" "s3://aetherra-wal-archive/"

exit 0
```

**PostgreSQL base backup:**

```bash
#!/bin/bash
# Create PostgreSQL base backup

BACKUP_DIR="/backups/aetherra/pg_basebackup"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

pg_basebackup \
    -U replication_user \
    -D "$BACKUP_DIR/base_$TIMESTAMP" \
    -F tar \
    -z \
    -P \
    -X stream

echo "Base backup complete: base_$TIMESTAMP"
```

---

## Restoration Procedures

### Full System Restore

**restore_aetherra.sh:**

```bash
#!/bin/bash
# Full Aetherra OS restoration

set -e

BACKUP_ARCHIVE="$1"
RESTORE_ROOT="${2:-/opt/aetherra}"

if [ -z "$BACKUP_ARCHIVE" ]; then
    echo "Usage: $0 <backup_archive.tar.gz> [restore_root]"
    exit 1
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "Starting Aetherra restoration from: $BACKUP_ARCHIVE"

# 1. Verify checksum
if [ -f "$BACKUP_ARCHIVE.sha256" ]; then
    log "Verifying checksum..."
    sha256sum -c "$BACKUP_ARCHIVE.sha256" || exit 1
    log "Checksum verified"
fi

# 2. Stop Aetherra services
log "Stopping Aetherra services..."
systemctl stop aetherra-os || true
systemctl stop aetherra-hub || true

# 3. Create restore directory
TEMP_RESTORE="/tmp/aetherra_restore_$$"
mkdir -p "$TEMP_RESTORE"

# 4. Extract backup
log "Extracting backup..."
tar -xzf "$BACKUP_ARCHIVE" -C "$TEMP_RESTORE"
BACKUP_DIR=$(ls -1 "$TEMP_RESTORE" | head -1)

# 5. Restore memory system
log "Restoring memory system..."
mkdir -p "$RESTORE_ROOT/data/memory"
cp -r "$TEMP_RESTORE/$BACKUP_DIR/memory"/* "$RESTORE_ROOT/data/memory/"

# 6. Restore configuration
log "Restoring configuration..."
cp "$TEMP_RESTORE/$BACKUP_DIR/config/config.json" "$RESTORE_ROOT/"
cp -r "$TEMP_RESTORE/$BACKUP_DIR/config/policies" "$RESTORE_ROOT/"

# 7. Restore plugins
log "Restoring plugins..."
cp -r "$TEMP_RESTORE/$BACKUP_DIR/plugins/plugins"/* "$RESTORE_ROOT/Aetherra/plugins/"
cp -r "$TEMP_RESTORE/$BACKUP_DIR/plugins/custom"/* "$RESTORE_ROOT/plugins/"

# 8. Restore Aether scripts
log "Restoring Aether scripts..."
cp -r "$TEMP_RESTORE/$BACKUP_DIR/scripts/workflows" "$RESTORE_ROOT/"

# 9. Restore database
log "Restoring database..."
if [ -f "$TEMP_RESTORE/$BACKUP_DIR/database/aetherra_db.dump" ]; then
    sudo -u postgres pg_restore -C -d postgres "$TEMP_RESTORE/$BACKUP_DIR/database/aetherra_db.dump"
fi

# 10. Fix permissions
log "Fixing permissions..."
chown -R aetherra:aetherra "$RESTORE_ROOT"
chmod -R 755 "$RESTORE_ROOT"

# 11. Clean up
rm -rf "$TEMP_RESTORE"

log "Restoration complete. You can now start Aetherra services."
log "Run: systemctl start aetherra-os aetherra-hub"
```

### Point-in-Time Recovery (PostgreSQL)

```bash
#!/bin/bash
# Point-in-time recovery to specific timestamp

TARGET_TIME="$1"  # Format: '2025-01-15 14:30:00'
BASE_BACKUP="/backups/aetherra/pg_basebackup/base_20250115"
WAL_ARCHIVE="/backups/aetherra/wal_archive"

if [ -z "$TARGET_TIME" ]; then
    echo "Usage: $0 'YYYY-MM-DD HH:MM:SS'"
    exit 1
fi

# 1. Stop database
systemctl stop postgresql

# 2. Move current data
mv /var/lib/postgresql/data /var/lib/postgresql/data.old

# 3. Extract base backup
mkdir -p /var/lib/postgresql/data
tar -xzf "$BASE_BACKUP/base.tar.gz" -C /var/lib/postgresql/data

# 4. Configure recovery
cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = 'cp $WAL_ARCHIVE/%f %p'
recovery_target_time = '$TARGET_TIME'
recovery_target_action = 'promote'
EOF

# 5. Start database (will perform recovery)
chown -R postgres:postgres /var/lib/postgresql/data
systemctl start postgresql

echo "Point-in-time recovery initiated to: $TARGET_TIME"
echo "Monitor: tail -f /var/log/postgresql/postgresql.log"
```

### Selective Component Restore

```bash
#!/bin/bash
# Restore only specific components

COMPONENT="$1"  # memory|config|plugins|scripts
BACKUP_ARCHIVE="$2"
AETHERRA_ROOT="/opt/aetherra"

case "$COMPONENT" in
    memory)
        tar -xzf "$BACKUP_ARCHIVE" -C /tmp
        BACKUP_DIR=$(ls -1 /tmp | grep aetherra_backup)
        cp -r "/tmp/$BACKUP_DIR/memory"/* "$AETHERRA_ROOT/data/memory/"
        ;;
    config)
        tar -xzf "$BACKUP_ARCHIVE" -C /tmp
        BACKUP_DIR=$(ls -1 /tmp | grep aetherra_backup)
        cp "/tmp/$BACKUP_DIR/config/config.json" "$AETHERRA_ROOT/"
        cp -r "/tmp/$BACKUP_DIR/config/policies" "$AETHERRA_ROOT/"
        ;;
    plugins)
        tar -xzf "$BACKUP_ARCHIVE" -C /tmp
        BACKUP_DIR=$(ls -1 /tmp | grep aetherra_backup)
        cp -r "/tmp/$BACKUP_DIR/plugins"/* "$AETHERRA_ROOT/plugins/"
        ;;
    scripts)
        tar -xzf "$BACKUP_ARCHIVE" -C /tmp
        BACKUP_DIR=$(ls -1 /tmp | grep aetherra_backup)
        cp -r "/tmp/$BACKUP_DIR/scripts/workflows" "$AETHERRA_ROOT/"
        ;;
    *)
        echo "Usage: $0 {memory|config|plugins|scripts} <backup_archive>"
        exit 1
        ;;
esac

echo "$COMPONENT restore complete"
```

---

## Cloud Backup Integration

### AWS S3 Backup

**Configure AWS CLI:**

```bash
# Install AWS CLI
pip install awscli

# Configure credentials
aws configure
# AWS Access Key ID: YOUR_KEY
# AWS Secret Access Key: YOUR_SECRET
# Default region: us-east-1
```

**S3 Backup Script:**

```bash
#!/bin/bash
# Backup to AWS S3 with lifecycle management

BACKUP_FILE="$1"
S3_BUCKET="s3://aetherra-backups-prod"
S3_LIFECYCLE_POLICY="glacier-transition"

# Upload with encryption
aws s3 cp "$BACKUP_FILE" "$S3_BUCKET/" \
    --storage-class STANDARD_IA \
    --server-side-encryption AES256 \
    --metadata "backup-date=$(date -u +%Y-%m-%d),hostname=$(hostname)"

# Apply lifecycle policy (transition to Glacier after 30 days)
aws s3api put-bucket-lifecycle-configuration \
    --bucket aetherra-backups-prod \
    --lifecycle-configuration file://s3-lifecycle.json
```

**s3-lifecycle.json:**

```json
{
  "Rules": [
    {
      "Id": "Archive old backups",
      "Status": "Enabled",
      "Filter": {
        "Prefix": "aetherra_backup_"
      },
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "GLACIER"
        },
        {
          "Days": 90,
          "StorageClass": "DEEP_ARCHIVE"
        }
      ],
      "Expiration": {
        "Days": 365
      }
    }
  ]
}
```

### Azure Blob Storage Backup

```bash
#!/bin/bash
# Backup to Azure Blob Storage

BACKUP_FILE="$1"
STORAGE_ACCOUNT="aetherrabackups"
CONTAINER="prod-backups"
BLOB_NAME=$(basename "$BACKUP_FILE")

# Upload with Azure CLI
az storage blob upload \
    --account-name "$STORAGE_ACCOUNT" \
    --container-name "$CONTAINER" \
    --name "$BLOB_NAME" \
    --file "$BACKUP_FILE" \
    --tier Cool \
    --metadata "backup-date=$(date -u +%Y-%m-%d)" "hostname=$(hostname)"
```

### Google Cloud Storage Backup

```bash
#!/bin/bash
# Backup to Google Cloud Storage

BACKUP_FILE="$1"
GCS_BUCKET="gs://aetherra-backups-prod"

# Upload with gsutil
gsutil -m cp -r "$BACKUP_FILE" "$GCS_BUCKET/"

# Set lifecycle policy (nearline after 30 days, coldline after 90)
gsutil lifecycle set lifecycle.json "$GCS_BUCKET"
```

---

## Disaster Recovery Planning

### Recovery Time Objective (RTO)

**Target RTO by Severity:**

| Scenario                     | Target RTO   | Procedure           |
| ---------------------------- | ------------ | ------------------- |
| **Service crash**            | < 5 minutes  | Service restart     |
| **Configuration corruption** | < 15 minutes | Config restore      |
| **Plugin failure**           | < 30 minutes | Plugin restore      |
| **Database corruption**      | < 1 hour     | Database restore    |
| **Complete system failure**  | < 4 hours    | Full system restore |
| **Data center failure**      | < 24 hours   | Offsite restore     |

### Recovery Point Objective (RPO)

**Target RPO by Component:**

| Component            | Target RPO  | Backup Frequency       |
| -------------------- | ----------- | ---------------------- |
| **Memory events**    | < 1 hour    | Hourly backups + WAL   |
| **Configuration**    | < 1 day     | Daily backups          |
| **Transaction data** | < 5 minutes | Continuous replication |
| **Plugins**          | < 1 day     | Daily backups          |
| **Logs**             | < 1 hour    | Hourly archival        |

### Disaster Recovery Runbook

**DR Runbook Template:**

```markdown
# Aetherra Disaster Recovery Runbook

## Scenario: Complete System Failure

### Detection
- Alert: Aetherra OS not responding
- Symptoms: All services down, no health checks passing
- Severity: Critical

### Assessment (5 minutes)
1. Verify system is truly down (ping, SSH, health endpoints)
2. Check monitoring dashboards
3. Identify failure scope (service vs. infrastructure)
4. Notify incident team

### Recovery Steps (Target: 4 hours)

#### Phase 1: Infrastructure (30 minutes)
1. Provision new infrastructure:
   - VM: 16 vCPU, 32GB RAM, 500GB SSD
   - OS: Ubuntu 22.04 LTS
   - Network: Public IP, security groups
2. Install base dependencies
3. Configure firewall rules

#### Phase 2: System Restore (1 hour)
1. Download latest backup from S3
2. Verify backup integrity (checksum)
3. Extract backup to /opt/aetherra
4. Restore database from backup
5. Configure system services

#### Phase 3: Service Startup (30 minutes)
1. Start PostgreSQL
2. Start Aetherra Registry
3. Start Aetherra Hub
4. Start Aetherra OS
5. Verify service health

#### Phase 4: Verification (1 hour)
1. Run smoke tests
2. Verify API endpoints
3. Check memory system
4. Test self-improvement
5. Verify plugins loaded

#### Phase 5: Monitoring (ongoing)
1. Enable monitoring
2. Watch error rates
3. Monitor performance
4. Notify stakeholders of recovery

### Rollback Plan
If recovery fails:
1. Take snapshot of attempted recovery
2. Start fresh with previous backup
3. Escalate to senior engineers

### Post-Recovery
1. Root cause analysis
2. Update runbook
3. Improve backup procedures
4. Schedule DR test
```

---

## Backup Testing

### Regular Backup Tests

**Monthly backup verification:**

```bash
#!/bin/bash
# Test backup integrity and restore capability

TEST_BACKUP="$1"
TEST_DIR="/tmp/backup_test_$$"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*"
}

log "Starting backup test: $TEST_BACKUP"

# 1. Verify archive integrity
log "Testing archive integrity..."
tar -tzf "$TEST_BACKUP" > /dev/null || exit 1
log "✓ Archive is valid"

# 2. Extract to test directory
log "Extracting backup..."
mkdir -p "$TEST_DIR"
tar -xzf "$TEST_BACKUP" -C "$TEST_DIR"
BACKUP_DIR=$(ls -1 "$TEST_DIR" | head -1)

# 3. Verify manifest
log "Checking manifest..."
if [ ! -f "$TEST_DIR/$BACKUP_DIR/manifest.json" ]; then
    log "✗ Manifest missing"
    exit 1
fi
log "✓ Manifest present"

# 4. Verify components
log "Verifying components..."
COMPONENTS=("memory" "config" "plugins" "scripts")
for component in "${COMPONENTS[@]}"; do
    if [ -d "$TEST_DIR/$BACKUP_DIR/$component" ]; then
        log "✓ $component present"
    else
        log "✗ $component missing"
        exit 1
    fi
done

# 5. Verify file counts
MEMORY_FILES=$(find "$TEST_DIR/$BACKUP_DIR/memory" -type f | wc -l)
log "Memory files: $MEMORY_FILES"

if [ "$MEMORY_FILES" -eq 0 ]; then
    log "⚠ Warning: No memory files in backup"
fi

# 6. Clean up
rm -rf "$TEST_DIR"

log "✓ Backup test passed: $TEST_BACKUP"
```

### Disaster Recovery Drills

**Quarterly DR drill procedure:**

```bash
#!/bin/bash
# Disaster recovery drill

DRILL_DATE=$(date +%Y%m%d)
DRILL_LOG="/var/log/aetherra_dr_drill_$DRILL_DATE.log"

exec > >(tee -a "$DRILL_LOG")
exec 2>&1

echo "=== Disaster Recovery Drill: $DRILL_DATE ==="
echo "Start time: $(date)"

# 1. Select random backup
LATEST_BACKUP=$(ls -1t /backups/aetherra/aetherra_backup_*.tar.gz | head -1)
echo "Testing backup: $LATEST_BACKUP"

# 2. Provision test environment
echo "Provisioning test environment..."
# (Use Terraform, CloudFormation, or manual provisioning)

# 3. Perform restore
echo "Performing restore..."
START_TIME=$(date +%s)
./restore_aetherra.sh "$LATEST_BACKUP" /opt/aetherra-test
RESTORE_EXIT=$?
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "Restore completed in $DURATION seconds (exit code: $RESTORE_EXIT)"

# 4. Start services
echo "Starting services..."
cd /opt/aetherra-test
./aetherra_os_launcher.py --mode full &
AETHERRA_PID=$!
sleep 30

# 5. Run health checks
echo "Running health checks..."
curl -f http://localhost:9090/health || echo "Health check failed"
curl -f http://localhost:3001/api/health || echo "Hub health check failed"

# 6. Run smoke tests
echo "Running smoke tests..."
pytest -q tests/smoke/ || echo "Smoke tests failed"

# 7. Clean up
echo "Cleaning up test environment..."
kill $AETHERRA_PID
# (Destroy test infrastructure)

echo "End time: $(date)"
echo "=== DR Drill Complete ==="
echo "Review log: $DRILL_LOG"
```

---

## Backup Monitoring

### Backup Success Metrics

```python
# Monitor backup health with Prometheus metrics
from prometheus_client import Counter, Gauge, Histogram

backup_total = Counter(
    'aetherra_backup_total',
    'Total backup operations',
    ['status', 'type']
)

backup_duration = Histogram(
    'aetherra_backup_duration_seconds',
    'Backup duration in seconds',
    ['type']
)

backup_size_bytes = Gauge(
    'aetherra_backup_size_bytes',
    'Backup size in bytes',
    ['type']
)

last_backup_timestamp = Gauge(
    'aetherra_last_backup_timestamp',
    'Timestamp of last successful backup',
    ['type']
)
```

### Backup Alerting Rules

**prometheus/backup_alerts.yml:**

```yaml
groups:
  - name: backup_alerts
    interval: 5m
    rules:
      # Alert if no backup in 24 hours
      - alert: BackupMissing
        expr: |
          (time() - aetherra_last_backup_timestamp{type="full"}) > 86400
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "No backup in 24 hours"
          description: "Last backup was {{ $value | humanizeDuration }} ago"

      # Alert on backup failures
      - alert: BackupFailed
        expr: |
          rate(aetherra_backup_total{status="failed"}[1h]) > 0
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Backup failures detected"
          description: "Backup failure rate: {{ $value }}"

      # Alert on backup size anomaly
      - alert: BackupSizeAnomaly
        expr: |
          abs(
            aetherra_backup_size_bytes{type="full"} -
            avg_over_time(aetherra_backup_size_bytes{type="full"}[7d])
          ) / avg_over_time(aetherra_backup_size_bytes{type="full"}[7d]) > 0.5
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Backup size anomaly detected"
          description: "Backup size differs by >50% from 7-day average"
```

---

## Best Practices

### 1. Encryption at Rest

```bash
# Encrypt backup before upload
BACKUP_FILE="aetherra_backup.tar.gz"
ENCRYPTED_FILE="$BACKUP_FILE.enc"

# Encrypt with GPG
gpg --symmetric --cipher-algo AES256 --output "$ENCRYPTED_FILE" "$BACKUP_FILE"

# Upload encrypted backup
aws s3 cp "$ENCRYPTED_FILE" s3://backups/
```

### 2. Backup Verification

Always verify backups:

```bash
# Checksum verification
sha256sum -c backup.tar.gz.sha256

# Test extraction
tar -tzf backup.tar.gz > /dev/null

# Restore to test environment monthly
```

### 3. Retention Policies

Implement graduated retention:

```
- Hourly backups: Keep 24 hours
- Daily backups: Keep 7 days
- Weekly backups: Keep 4 weeks
- Monthly backups: Keep 12 months
- Yearly backups: Keep 7 years (compliance)
```

### 4. Documentation

Maintain backup documentation:

- Backup procedures
- Restore procedures
- DR runbooks
- Contact information
- Escalation procedures

---

## Troubleshooting

### Backup Failures

**Issue: Backup script fails with "disk full"**

```bash
# Check disk space
df -h /backups

# Clean old backups
find /backups -name "*.tar.gz" -mtime +30 -delete

# Compress older backups
find /backups -name "*.tar.gz" -mtime +7 -exec gzip -9 {} \;
```

**Issue: S3 upload fails**

```bash
# Check AWS credentials
aws sts get-caller-identity

# Test S3 access
aws s3 ls s3://aetherra-backups-prod/

# Check network
curl -I https://s3.amazonaws.com
```

### Restore Issues

**Issue: Database restore fails**

```bash
# Check PostgreSQL logs
tail -f /var/log/postgresql/postgresql.log

# Verify dump file
pg_restore --list aetherra_db.dump

# Restore with verbose mode
pg_restore -v -d aetherra aetherra_db.dump
```

---

## Related Documentation

- [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) - Production deployment
- [METRICS_AND_MONITORING_GUIDE.md](./METRICS_AND_MONITORING_GUIDE.md) - Monitoring backups
- [SECURITY_OPERATIONS_GUIDE.md](./SECURITY_OPERATIONS_GUIDE.md) - Backup security
- [TROUBLESHOOTING_GUIDE.md](./TROUBLESHOOTING_GUIDE.md) - General troubleshooting

---

Status: ✅ Complete - Comprehensive backup and disaster recovery guide with automation scripts

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
