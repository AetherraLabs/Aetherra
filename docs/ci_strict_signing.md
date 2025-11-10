# CI/CD Integration for Strict .aether Script Verification

Add the following to your CI pipeline (GitHub Actions, GitLab CI, etc.) to enforce strict script signing:

## GitHub Actions Example

```yaml
name: Aether Script Verification

on: [push, pull_request]

jobs:
  verify-scripts:
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

      - name: Verify .aether script signatures (strict mode)
        env:
          AETHERRA_SCRIPT_VERIFY_STRICT: "1"
          AETHERRA_PROFILE: "test"
        run: |
          python tools/verify_aether_scripts.py --strict --root . --fail-on-any-risk
```

## GitLab CI Example

```yaml
verify-aether-scripts:
  stage: test
  image: python:3.11
  script:
    - pip install -r requirements.txt
    - export AETHERRA_SCRIPT_VERIFY_STRICT=1
    - export AETHERRA_PROFILE=test
    - python tools/verify_aether_scripts.py --strict --root . --fail-on-any-risk
  only:
    - branches
    - merge_requests
```

## Environment Variables

- `AETHERRA_SCRIPT_VERIFY_STRICT=1`: Enforces signature validation on all .aether scripts
- `AETHERRA_PROFILE=test`: Uses deterministic test profile for reproducible results

## Verification Tool Options

```bash
python tools/verify_aether_scripts.py \
  --strict \                    # Enable strict signature verification
  --root . \                    # Root directory to scan
  --fail-on-any-risk \          # Exit non-zero if any risk detected
  --risk-threshold 5 \          # Custom risk score threshold
  --output report.md            # Write detailed report
```

## Pre-commit Hook (Optional)

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
export AETHERRA_SCRIPT_VERIFY_STRICT=1
python tools/verify_aether_scripts.py --strict --root . --fail-on-any-risk
if [ $? -ne 0 ]; then
    echo "❌ .aether script verification failed"
    echo "Run: python tools/sign_aether.py <script.aether>"
    exit 1
fi
```

Make executable: `chmod +x .git/hooks/pre-commit`

## Signing Workflow

1. Create/edit .aether script
2. Sign it: `python tools/sign_aether.py workflows/my_script.aether`
3. Commit signed script
4. CI verifies signature automatically

## Related Documentation

- [AETHERRA_CLAIMS_VALIDATION.md](../AETHERRA_CLAIMS_VALIDATION.md) - Capability validation status
- [Aetherra Script Language Specification.md](../Aetherra%20Script%20Language%20Specification.md) - Language reference
- `Aetherra/security/script_signing.py` - Signing implementation
