# Workflow Failure Classification

Total: 5  Failures: 3  Failure Rate: 60.00%

## Categories
| Category | Count | Example(s) |
|----------|-------|-----------|
| VALIDATION_ERROR | 3 | /home/runner/work/Aetherra/Aetherra/Aetherra/aetherra_core/system/agents.aether, /home/runner/work/Aetherra/Aetherra/Aetherra/aetherra_core/system/agent_diagnostics.aether, /home/runner/work/Aetherra/Aetherra/Aetherra/aetherra_core/system/daily_maintenance.aether |
| SUCCESS | 2 | /home/runner/work/Aetherra/Aetherra/Aetherra/aetherra_core/system/bootstrap.aether, /home/runner/work/Aetherra/Aetherra/Aetherra/aetherra_core/system/agent_sync.aether |

## Notes

- This is an initial pass. Categories are heuristic (stderr pattern based).
- Consider adding structured failure codes to the interpreter for precision.