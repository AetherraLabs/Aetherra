# Supervised checkpoint retention

Use this foreground command when automatic checkpoint saves have paused for retention. It resumes one existing stream, inspects a prior attempt if supplied, and asks Guardian for one irreversible prune only when Memory finds eligible members. Each resume advances the writer epoch, pins the current head and installs the requested retention count, including on a run that finds nothing to delete.

## Stop the launcher and select the profile

1. Request orderly launcher shutdown. Confirm that the observer stopped, the Memory worker drained, and the launcher process exited successfully. A timeout or pending worker requires investigation before maintenance. Keep the launcher and other writers stopped until the command closes. A concurrent resume fences the maintenance writer.
2. Use two authorized terminals with the stopped launcher's normal service identity, working directory, interpreter, trusted source checkout and profile configuration. Preserve its existing principal, Guardian state and policy paths, capabilities policy, enforcing mode, and strict audit/signing configuration. Load these through the usual deployment setup. Keep credentials in their existing sources. The command needs no credential argument.
3. Select the same existing Guardian workspace and core Memory database. Guardian resolves `AETHERRA_WORKSPACE_ROOT`, then `AETHERRA_WORKSPACE`, then the working directory. The command requires the supplied profile to match that root and the database to be an existing file inside it. The full launcher's default core database filename is `lyrixa_memory.db`. Use the configured filename for your installation. The governed Memory worker opens it in SQLite read/write-existing mode. This avoids the general Memory constructor's database creation and schema setup.

In PowerShell in both terminals, activate the release's normal Python environment. For a source checkout, make the release importable from the normal working directory. Substitute the actual trusted checkout and profile paths.

```powershell
$python = (Get-Command python).Source
$release = (Resolve-Path 'C:\path\to\release').Path
$profileDir = (Resolve-Path 'C:\path\to\existing-profile').Path
$env:PYTHONPATH = $release + [IO.Path]::PathSeparator + $env:PYTHONPATH
```

In the first terminal enter the configured 32-character lowercase hexadecimal stream ID and the intended number of recent generations to keep (2–100). This example uses N=2.

```powershell
$stream = Read-Host 'Existing checkpoint stream ID'
& $python -m tools.checkpoint_retention --profile $profileDir --database lyrixa_memory.db --stream-id $stream --retain 2
```

When exact evidence from a prior attempt is available, add `--prior-attempt 'C:\path\to\attempt.json'` **on this same invocation**. Use the original nested recovery descriptor with `token`, `expected_head`, `operation_id`, `checkpoint_id`, `payload_digest` and `metadata_digest`. The tool accepts up to 8 KiB of descriptor JSON. It validates the stream, resumes once, and finishes inspection before requesting a prune. The reported inspection outcome describes that historical attempt. Prior receipt acceptance and prior clean shutdown remain unknown. Failed or unreadable inspection stops maintenance.

## Review and resolve the exact request

A `no_victim` result needs no approval. Otherwise the first terminal prints `approval_requested` with an exact request ID, fingerprint, stream, epoch, generation, full head digest and N. Leave that process running. Review these fields against the intended stream and retention count. The protected Hub also supports `GET /api/guardian/approvals/<request_id>` and `POST /api/guardian/approvals/<request_id>/resolve` with a JSON boolean `approved`, when it runs independently with the same profile.

With the launcher stopped, use Guardian's existing local operator API in the second terminal. Its authority comes from authorized access to the profile and Guardian state. Start Python with `& $python`, then enter the following in the interpreter. Supply the exact ID and fingerprint displayed in the first terminal. The digest covers the full intent, including the principal.

```python
import os
from Aetherra.guardian import IntentDeclaration
from Aetherra.guardian.approval import approval_status, intent_fingerprint, resolve_approval
rid = input("Exact request ID: ").strip()
fingerprint = input("Exact intent fingerprint: ").strip()
item = approval_status(rid)
if item["state"] != "pending_user":
    raise SystemExit("Request is not pending")

intent = IntentDeclaration(**item["intent"])
if intent_fingerprint(intent) != fingerprint:
    raise SystemExit("Fingerprint mismatch")

principal = os.environ.get("AETHERRA_PRINCIPAL", "").strip() or "consciousness:core"
if intent.requester != principal or intent.action != "consciousness.continuity_prune" or intent.reversible or intent.rollback_plan is not None:
    raise SystemExit("Requester or irreversible operation mismatch")

fields = ("stream_id", "writer_epoch", "generation", "expected_head_digest", "retain_checkpoints")
print({field: intent.metadata[field] for field in fields})
```

Compare the printed fields with the first terminal. This deletes eligible checkpoint payloads and their catalog rows permanently. To record your decision on this exact request, execute the following separately in the same Python interpreter.

```python
choice = input("Type approve or deny for the reviewed request: ").strip()
if choice not in ("approve", "deny"):
    raise SystemExit("No decision submitted")

reviewer = input("Authorized operator identity: ").strip()
if not reviewer:
    raise SystemExit("Operator identity required")

print(resolve_approval(rid, approved=(choice == "approve"), approver=reviewer)["state"])
```

The foreground command waits up to 900 seconds for the human decision, outside the Memory worker, transaction and attempt deadline. Guardian can expire the request earlier. Ctrl+C cancels the foreground attempt. A denied, expired, consumed or mismatched approval ends the attempt. The tool submits at most one prune, using its original token/head/N with a fresh one-second control and the worker's 250 ms SQLite busy limit. A change of writer or head blocks deletion under the old binding.

## Verify the result and restart

- Exit 0 with `pruned`, `closed: true` and `closed_in_budget: true` confirms an accepted receipt, consumed approval and worker close. Record the opaque binding, counts and pruning watermark. The two newest available generations and current restore pin stay protected. An independent Temporal history row can still reference an erased checkpoint. The integrity boundary is storage isolation within the selected profile.
- Exit 0 with `no_victim` and successful close means the acquisition found no eligible checkpoint. Logical row deletion makes no promise about SQLite file size.
- A nonzero exit or missing final receipt gives no positive deletion acknowledgement. A consumed approval or signed Guardian decision alone proves no transaction outcome. On `uncertain`, a commit may already be durable. Preserve the opaque fields and use exact recovery evidence before deciding on later maintenance. Guardian applies normal signed-audit redaction to decision details.
- `close_pending` marks a failed two-second close cutoff. The foreground process retains the worker solely to finish physical drain. Its eventual `closed: true, closed_in_budget: false` and nonzero exit preserve the missed cutoff. Leave it running until drained and investigate the failed stop before restarting.

After a verified maintenance close, explicitly restart the normal launcher with its original profile, resume configuration, and no maintenance approval ID. The foreground process scopes the ID to its single prune and restores its prior environment after drain. Resolving a request from a previously failed runtime and then restarting cannot resume that prune. The failure paused that session's saves, and a restart acquires a new writer epoch with a different intent fingerprint. A later eligible prune needs its own exact one-use approval. Unattended saves can pause again.
