# Repository Cleanup and Size Reduction

If the repository has large binaries or accidentally committed virtual environments, use the steps below. Note that history rewriting affects all clones.

1. Backup your repo and ensure no unpushed work exists.
2. Install `git-filter-repo` (recommended over filter-branch):
   - macOS/Homebrew: `brew install git-filter-repo`
   - Python/pipx: `pipx install git-filter-repo`
3. Remove common offenders:
   - Large binaries (videos, models)
   - Virtual environments (`.venv/`, `venv/`)
   - `node_modules/` (should never be committed)
4. Run filter:
   - Remove dirs: `git filter-repo --path .venv --path venv --path-glob "**/node_modules" --invert-paths`
   - Remove by size: `git filter-repo --strip-blobs-bigger-than 10M`
5. Force push all branches/tags to remote (coordinate with team):
   - `git push --force --all`
   - `git push --force --tags`
6. Ask contributors to reclone or run `git fetch --all --prune` and reset local branches.

After cleanup, consider enabling Git LFS for legitimate large assets.
