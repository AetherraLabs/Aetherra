# STORM Shadow Mode Monitoring Schedule

**Phase 1 Duration:** 2 weeks (October 22 - November 5, 2025)
**Status:** 🟢 ACTIVE
**Deployment Date:** October 22, 2025

---

## Overview

STORM shadow mode is now deployed and operational. This schedule outlines the monitoring tasks required during the 2-week Phase 1 period to validate STORM performance before proceeding to Phase 2 (Hybrid Mode).

### Phase 1 Goals

- ✅ STORM running in parallel with baseline
- ✅ Collecting comparison metrics
- ⏳ Validating latency and quality
- ⏳ Building confidence for hybrid rollout

---

## Daily Monitoring Tasks

**Frequency:** Every day (Mon-Fri) + spot checks (weekends)

### Morning Check (9:00 AM)

```powershell
# 1. Quick health check
python tools/monitor_storm_shadow.py --check

# 2. Check for alerts
python tools/monitor_storm_shadow.py --alert

# 3. Generate daily report
python tools/monitor_storm_shadow.py --save "reports/daily/$(Get-Date -Format 'yyyy-MM-dd')_report.txt"
```

**Expected time:** ~2 minutes

### Afternoon Review (3:00 PM)

```powershell
# Check metrics endpoint directly
curl http://localhost:3001/metrics | Select-String -Pattern "storm_"

# View Hub health
curl http://localhost:3001/health | ConvertFrom-Json | Format-List
```

**Expected time:** ~1 minute

### Daily Checklist

- [ ] Hub is healthy and responding
- [ ] No critical alerts triggered
- [ ] STORM metrics are being collected
- [ ] Error rate remains low
- [ ] Log any anomalies in monitoring log

---

## Weekly Monitoring Tasks

**Frequency:** End of each week (Fridays)

### Week 1: October 25, 2025

```powershell
# Generate weekly summary
python tools/storm_weekly_summary.py --save "reports/weekly/week1_summary.md"

# Review metrics trends
python tools/monitor_storm_shadow.py --detailed --save "reports/weekly/week1_detailed.txt"
```

**Analysis Tasks:**

1. **Agreement Rate Trend**
   - Calculate daily agreement rates
   - Identify any patterns or anomalies
   - Target: Trending toward >80%

2. **Error Rate Analysis**
   - Review all shadow errors
   - Categorize error types
   - Target: <1% overall

3. **Latency Performance**
   - Review p50, p95, p99 latencies
   - Compare STORM vs baseline
   - Target: p95 <500ms

4. **Sheaf Health**
   - Monitor inconsistency metric
   - Check for drift patterns
   - Target: <0.3 inconsistency

**Expected time:** ~30 minutes

### Week 2: November 1, 2025

Same as Week 1, plus:

```powershell
# Phase 2 readiness check
python tools/storm_weekly_summary.py --readiness
```

**Additional Tasks:**

1. **Success Criteria Validation**
   - Verify all 7 Phase 1 criteria met
   - Document any exceptions
   - Prepare Phase 2 decision

2. **Stakeholder Report**
   - Compile 2-week summary
   - Highlight key metrics
   - Recommendation for Phase 2

**Expected time:** ~1 hour

---

## Alert Response Procedures

### Critical Alerts 🚨

**Alert:** Shadow error rate >1%

**Response:**
1. Check Hub logs for error details
2. Review recent recalls that failed
3. Investigate STORM engine health
4. Consider temporary rollback if >5%

**Alert:** Sheaf inconsistency >0.5

**Response:**
1. Check STORM status API: `curl http://localhost:3001/api/memory/status`
2. Review sheaf health metrics
3. Verify OT backend functioning
4. Consider reducing TT rank if needed

### Warning Alerts ⚠️

**Alert:** Agreement rate <70%

**Response:**
1. Review recent comparisons
2. Check if baseline changed
3. Analyze disagreement patterns
4. Document findings for review

**Alert:** Latency p95 >400ms

**Response:**
1. Review OT cost distribution
2. Check if coarse filtering working
3. Monitor system resources
4. Consider increasing K_COARSE if needed

---

## Metrics to Track

### Primary KPIs

| Metric              | Target | Current | Trend |
| ------------------- | ------ | ------- | ----- |
| Agreement Rate      | >80%   | TBD     | -     |
| Shadow Error Rate   | <1%    | TBD     | -     |
| Latency p95         | <500ms | TBD     | -     |
| Sheaf Inconsistency | <0.3   | TBD     | -     |

### Secondary Metrics

- Total STORM recalls
- Transport cost distribution
- Approximate vs exact recall ratio
- Memory efficiency (cells count)

---

## Tools Reference

### Monitoring Scripts

| Script                    | Purpose                | Frequency |
| ------------------------- | ---------------------- | --------- |
| `monitor_storm_shadow.py` | Daily health check     | Daily     |
| `storm_weekly_summary.py` | Weekly trend analysis  | Weekly    |
| `check_metrics.py`        | Raw metrics inspection | As needed |
| `test_storm_metrics.py`   | Manual recall test     | As needed |

### Quick Commands

```powershell
# Health check
python tools/monitor_storm_shadow.py --check

# Alert check
python tools/monitor_storm_shadow.py --alert

# Full daily report
python tools/monitor_storm_shadow.py

# Weekly summary
python tools/storm_weekly_summary.py

# Metrics inspection
python check_metrics.py

# Manual recall test
python test_storm_metrics.py
```

---

## Monitoring Log

**Location:** `reports/monitoring_log.md`

### Week 1 Log

#### Day 1: October 22, 2025

- ✅ Phase 1 deployment completed
- ✅ Hub started successfully
- ✅ Monitoring tools created and tested
- ⚠️ STORM metrics not yet visible (expected)
- **Action:** Continue monitoring for metrics to appear

#### Day 2: October 23, 2025

- [ ] Morning check
- [ ] Afternoon review
- [ ] STORM metrics status
- [ ] Any issues or anomalies

_(Continue daily entries...)_

### Week 2 Log

#### Day 8: October 29, 2025

- [ ] Week 1 summary completed
- [ ] Trend analysis reviewed
- [ ] Any adjustments made

_(Continue daily entries...)_

---

## Phase 2 Readiness Decision

**Target Date:** November 5, 2025 (end of Week 2)

### Success Criteria Checklist

- [ ] **Shadow error rate <1%** - Stable operation verified
- [ ] **STORM latency p95 <500ms** - Performance within threshold
- [ ] **Agreement rate >80%** - STORM and baseline aligned
- [ ] **No production impact** - Baseline serving correctly
- [ ] **Metrics collecting** - All 13 STORM series visible
- [ ] **No security incidents** - Audit logs clean
- [ ] **No user complaints** - Transparent operation

### Decision Matrix

| Criteria Met | Decision                          |
| ------------ | --------------------------------- |
| All 7        | ✅ PROCEED to Phase 2              |
| 5-6          | ⚠️ EVALUATE - Review exceptions    |
| <5           | ❌ EXTEND Phase 1 - Address issues |

### Next Steps After Phase 2 Approval

1. Update environment: Set `AETHERRA_STORM_SHADOW_MODE=0`
2. Plan gradual traffic shift: 10% → 25% → 50% → 75%
3. Prepare Phase 2 monitoring dashboards
4. Schedule Phase 2 kickoff meeting

---

## Contact & Escalation

### Issue Reporting

- **Critical issues:** Immediate investigation required
- **Warnings:** Document and review within 24 hours
- **Informational:** Track in monitoring log

### Documentation

- Daily reports: `reports/daily/`
- Weekly summaries: `reports/weekly/`
- Monitoring log: `reports/monitoring_log.md`
- Phase 1 final report: `docs/STORM_PHASE1_FINAL_REPORT.md`

---

## Notes

- STORM metrics may take 24-48 hours to appear after deployment
- This is expected behavior as the system needs to process recalls first
- Continue monitoring even before metrics are visible
- Document any unexpected behaviors or patterns
- Maintain regular backup of reports and logs

---

**Last Updated:** October 22, 2025
**Next Review:** October 25, 2025 (Week 1 summary)
**Phase 2 Target:** November 6, 2025 (if approved)
