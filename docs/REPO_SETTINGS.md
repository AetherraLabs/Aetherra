# Recommended Repository Settings

Apply these in GitHub repository settings (cannot be versioned here):

- Branch protection (main):
  - Require pull request reviews before merging (1+)
  - Require status checks to pass before merging (select CI jobs)
  - Require branches to be up to date before merging
  - Require linear history (optional but recommended)
  - Automatically delete head branches after merge
- Merging strategy:
  - Prefer squash merge by default
- Security features:
  - Enable Secret scanning and Push Protection
  - Enable Code scanning (CodeQL workflow is included)
  - Enable Dependabot alerts and updates (config included)
- Pages:
  - Use gated deploy workflow; do not auto-deploy on push

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->

<!-- SPDX-License-Identifier: GPL-3.0-or-later -->
<!-- SPDX-FileCopyrightText: 2025 Aetherra Labs and Contributors -->
