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
