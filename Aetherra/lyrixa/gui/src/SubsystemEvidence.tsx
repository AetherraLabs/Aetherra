type EvidenceValue = string | number | boolean | null | undefined;
type EvidenceMetrics = Record<string, string | number | boolean | null>;

interface Props {
    name?: string;
    metrics?: EvidenceMetrics;
    live: boolean;
}

function count(value: EvidenceValue): string {
    return typeof value === "number" && Number.isInteger(value) && value >= 0 ? String(value) : "Unknown";
}

function flag(value: EvidenceValue, yes = "Yes", no = "No"): string {
    return value === true ? yes : value === false ? no : "Unknown";
}

function status(value: EvidenceValue, allowed: string[], absent = "Not recorded"): string {
    if (value === "not_recorded" && allowed.includes("not_recorded")) return absent;
    return typeof value === "string" && allowed.includes(value)
        ? value.charAt(0).toUpperCase() + value.slice(1).replace(/_/g, " ") : "Unknown";
}

function reference(value: EvidenceValue): string {
    return typeof value === "string" && /^[a-f0-9]{16}$/.test(value) ? value : "Unknown";
}

function checkpointReference(value: EvidenceValue): string {
    return typeof value === "string" && /^[a-f0-9]{32}$/.test(value) ? value : "Unknown";
}

function recordReference(value: EvidenceValue): string {
    return typeof value === "string" && /^[A-Za-z0-9_-]{1,128}$/.test(value) ? value : "Unknown";
}

function duration(value: EvidenceValue): string {
    return typeof value === "number" && Number.isFinite(value) && value >= 0 && value <= Number.MAX_SAFE_INTEGER
        ? `${Number(value.toFixed(3))} s` : "Unknown";
}

function hostTime(value: EvidenceValue): string {
    if (typeof value !== "number" || !Number.isFinite(value) || value < 0 || value > 8.64e12) return "Unknown";
    return new Date(value * 1000).toISOString();
}

function consciousnessEvidence(observed: EvidenceMetrics): Array<[string, string]> {
    const restoredRecord = recordReference(observed.continuity_restored_record_id);
    const rows: Array<[string, string]> = [
        ["Current runtime", status(observed.runtime_state, ["starting", "running", "stopping", "stopped", "blocked", "failed", "stale"])],
        ["Current session ticks", count(observed.ticks_completed)],
        ["Checkpointing requested", flag(observed.continuity_enabled)],
        ["Continuity health", observed.continuity_health === "ok" ? "OK" : status(observed.continuity_health, ["disabled", "pending", "degraded"])],
        ["Checkpoint state", status(observed.continuity_state, ["disabled", "fresh", "restoring", "selected", "restored", "saving", "saved", "blocked", "failed", "uncertain", "retention_blocked"])],
        ["Checkpoint pending", flag(observed.continuity_outstanding)],
        ["Restored record", restoredRecord],
        ["Saved record", recordReference(observed.continuity_saved_record_id)],
        ["Action execution", flag(observed.action_execution_enabled, "Enabled", "Disabled")],
    ];
    if (observed.continuity_enabled !== true) return rows;

    const ownership = observed.continuity_ownership_state;
    rows.push(
        ["Persistence ownership", ownership === "lost"
            ? "Persistence ownership lost — checkpoint writes stopped."
            : status(ownership, ["disabled", "not_acquired", "last_observed_owned", "uncertain"])],
    );
    if (typeof observed.continuity_observed_writer_epoch === "number") {
        rows.push(
            ["Last observed writer epoch", count(observed.continuity_observed_writer_epoch)],
            ["Last observed head generation", count(observed.continuity_observed_generation)],
            ["Last ownership check (UTC)", hostTime(observed.continuity_ownership_checked_at_unix_s)],
        );
    }
    if (ownership === "lost") {
        rows.push(["Ownership loss observed (UTC)", hostTime(observed.continuity_ownership_lost_at_unix_s)]);
    }
    if (typeof observed.continuity_retention_needed === "boolean") {
        rows.push(["Retention required", flag(observed.continuity_retention_needed)]);
    }
    if (observed.continuity_error_code) {
        rows.push(["Checkpoint error", status(observed.continuity_error_code, [
            "busy", "denied", "audit_failed", "missing", "ambiguous", "invalid", "unavailable",
            "cancelled", "uncertain", "policy_not_ready", "core_not_ready", "tick_failed",
            "reflection_denied", "config_invalid", "stale", "corrupt", "conflict", "capacity", "writer_fenced",
        ])]);
    }

    const method = observed.continuity_recovery_method;
    const outcome = observed.continuity_recovery_outcome;
    const previousTerminationUnknown = observed.continuity_previous_shutdown_evidence === "unknown";
    const headRestoration = "Previous termination unknown; restored verified durable head";
    const recoveryOutcome = method === "durable_head" && outcome === "restored"
        && previousTerminationUnknown
        ? headRestoration
        : status(outcome, [
            "not_attempted", "fresh", "restored", "blocked", "corrupt", "committed_current",
            "committed_superseded", "conflict", "not_committed", "history_expired",
        ]);
    rows.push(
        ["Recovery method", status(method, ["none", "new_stream", "explicit_checkpoint", "durable_head", "exact_inspection"])],
        ["Recovery outcome", recoveryOutcome],
        ["Previous termination", status(observed.continuity_previous_shutdown_evidence, ["unknown"])],
        ["Previous save acceptance", status(observed.continuity_previous_save_acceptance, ["unknown"])],
    );
    if (method === "exact_inspection") {
        if (observed.continuity_matched_record_id) {
            rows.push(["Inspected operation record", recordReference(observed.continuity_matched_record_id)]);
        }
        if (restoredRecord !== "Unknown" && previousTerminationUnknown) {
            rows.push(["Head restoration", headRestoration]);
        }
    }

    const triggers = ["periodic", "orderly_stop"];
    const savedRecord = recordReference(observed.continuity_saved_record_id);
    const savedCheckpoint = checkpointReference(observed.continuity_saved_checkpoint_id);
    const trigger = observed.continuity_last_save_trigger;
    const acceptance = observed.continuity_last_save_acceptance;
    const savedTrigger = observed.continuity_saved_trigger;
    rows.push(
        ["Last save trigger", status(trigger, triggers)],
        ["Last save acceptance", status(acceptance, ["none", "pending", "acknowledged", "unacknowledged", "unknown"])],
    );
    if (savedRecord !== "Unknown" && savedCheckpoint !== "Unknown") {
        const final = trigger === "orderly_stop" && acceptance === "acknowledged" && savedTrigger === "orderly_stop";
        const receipt = final ? "Final checkpoint acknowledged" : "Historical receipt";
        rows.push(["Saved checkpoint", savedCheckpoint], ["Saved record evidence", receipt]);
        if (savedTrigger) rows.push(["Saved checkpoint trigger", status(savedTrigger, triggers)]);
        if (typeof observed.continuity_saved_generation === "number") {
            rows.push(["Saved generation", count(observed.continuity_saved_generation)]);
        }
    }

    rows.push(["Current session uptime", duration(observed.continuity_session_uptime_seconds)]);
    if (observed.continuity_session_started_at_unix_s != null) {
        rows.push(["Current session start (UTC)", hostTime(observed.continuity_session_started_at_unix_s)]);
    }
    const restored = observed.continuity_state === "restored" || outcome === "restored"
        || restoredRecord !== "Unknown";
    if (restored) {
        const restoredStart = hostTime(observed.continuity_restored_session_started_at_unix_s);
        const lastObservation = hostTime(observed.continuity_last_verified_observation_at_unix_s);
        const captured = hostTime(observed.continuity_captured_at_unix_s);
        if (lastObservation === "Unknown") {
            rows.push(["Restored snapshot provenance", "Unavailable"]);
        } else {
            rows.push(
                ["Restored session start (UTC)", restoredStart],
                ["Restored observation (UTC)", lastObservation],
                ["Restored capture (UTC)", captured],
            );
        }
        rows.push(
            ["Restored snapshot trigger", status(observed.continuity_restored_save_trigger, triggers)],
            ["Restored observation uptime", duration(observed.continuity_restored_observation_uptime_s)],
            ["Restored capture uptime", duration(observed.continuity_restored_capture_uptime_s)],
        );
    }
    const gapState = observed.continuity_observation_gap_state;
    const gap = gapState === "host_wall_clock_estimate" ? duration(observed.continuity_observation_gap_seconds)
        : gapState === "clock_inconsistent" ? "Clock inconsistent" : "Unknown";
    rows.push(["Observation gap (host-wall-clock estimate)", gap], ["Offline duration", "Unknown"]);
    return rows;
}

function persistence(value: EvidenceValue): string {
    switch (value) {
        case "error": return "Error; durability unknown";
        case "autosave_enabled": return "Autosave enabled; durability unverified";
        case "autosave_disabled": return "Autosave disabled";
        case "no_store": return "No store configured";
        default: return "Unknown";
    }
}

export default function SubsystemEvidence({ name, metrics, live }: Props) {
    const observed = live ? metrics ?? {} : {};
    let rows: Array<[string, string]>;
    let note: string;
    if (name === "homeostasis") {
        rows = [
            ["Effective mode", status(observed.controller_mode, ["observe_only", "advisory", "active_limited", "active", "emergency", "disabled"])],
            ["Observation requested", flag(observed.observe_only_requested)],
            ["Actuator attempts", count(observed.actuator_actions_attempted)],
            ["Actuator executions", count(observed.actuator_actions_executed)],
            ["Actuator blocks", count(observed.actuator_actions_blocked)],
            ["Orchestrator restarts", count(observed.restart_count)],
            ["Error recoveries", count(observed.error_recovery_count)],
        ];
        note = "The lifecycle badge describes whether Homeostasis is running. Effective mode and actuator counters show its operating behavior.";
    } else if (name === "maintenance") {
        rows = [
            ["Persistence", persistence(observed.persistence_state)],
            ["In-process cycles", count(observed.cycle_count)],
            ["Latest in-process cycle", observed.latest_cycle_present === false ? "No in-process cycle" : status(observed.latest_cycle_status, ["created", "observed", "observation_degraded", "diagnosed", "proposed", "approved", "denied", "contained", "security_enforced", "security_blocked", "executed", "execution_failed", "verified", "verification_failed", "learned"])],
        ];
        if (observed.latest_cycle_present === true) {
            rows.push(
                ["Observations", count(observed.latest_observations)],
                ["Diagnosis", flag(observed.latest_has_diagnosis, "Recorded", "Not recorded")],
                ["Proposal", flag(observed.latest_has_proposal, "Recorded", "Not recorded")],
                ["Guardian decision", status(observed.latest_guardian_status, ["allow", "allow_limited", "deny", "require_approval", "contain", "not_recorded"])],
                ["Security enforced", flag(observed.latest_security_enforced)],
                ["Execution", status(observed.latest_execution_status, ["applied", "accepted", "succeeded", "success", "failed", "blocked", "skipped", "denied", "not_recorded"], "No execution recorded")],
                ["Verification", status(observed.latest_verification_status, ["passed", "stable", "improved", "failed", "not_recorded"])],
                ["Cycle ref", reference(observed.latest_cycle_id_hash)],
                ["Proposal ref", observed.latest_has_proposal === false ? "Not recorded" : reference(observed.latest_proposal_id_hash)],
                ["Guardian audit ref", observed.latest_guardian_status === "not_recorded" ? "Not recorded" : reference(observed.latest_guardian_audit_id_hash)],
            );
            const updated = observed.latest_updated_at;
            rows.push(["Record updated", typeof updated === "string" && updated.length <= 64 && Number.isFinite(Date.parse(updated)) ? updated : "Unknown"]);
        }
        note = "Current in-process records only; store configuration does not verify durability. Guardian decides; Security enforces; Maintenance records. References identify related records without exposing their contents.";
    } else if (name === "consciousness") {
        rows = consciousnessEvidence(observed);
        note = "Current ticks describe this session. Restored observations and save receipts are historical. Checkpoints grant no action authority.";
    } else if (name === "guardian") {
        rows = [
            ["Enabled", flag(observed.enabled)],
            ["Effective mode", status(observed.mode, ["observe", "advisory", "enforcing", "strict", "emergency"])],
            ["Audit integrity", flag(observed.audit_integrity_ok, "Verified", "Failed")],
        ];
        note = "Configuration and audit integrity do not establish approval for an individual proposal.";
    } else if (name === "memory") {
        rows = [["Continuity", "Not verified"]];
        note = "Registry presence does not verify remembered content, persistence, or retrieval.";
    } else {
        return null;
    }
    return (
        <section className="subsystem-evidence" aria-label="Subsystem evidence">
            <p className="eyebrow">Observed evidence</p>
            <dl>
                {rows.map(([label, value]) => (
                    <div key={label}><dt>{label}</dt><dd>{value}</dd></div>
                ))}
            </dl>
            <p className="evidence-note">{note}</p>
        </section>
    );
}
