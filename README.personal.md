# `dev-personal`

This branch contains personal development setup changes for the Home Assistant Core fork. It is based on the official repository's `dev` branch and is intended to remain in the fork rather than being submitted upstream.

The remotes are used as follows:

- `origin` is the personal fork: `https://github.com/wuede/home-assistant-core.git`
- `upstream` is the official repository: `https://github.com/home-assistant/core.git`

## Update from `upstream/dev`

Before starting development, make sure local changes are committed or stashed, then run:

```sh
git fetch upstream dev
git rebase upstream/dev
```

This updates the branch base while preserving the commits that belong to `dev-personal`. Resolve any conflicts during the rebase before continuing. Push the rebased branch to your fork with `git push --force-with-lease origin dev-personal` if it has already been published there. If the rebase aborts because of `.devcontainer/devcontainer.json`, see the recovery steps below.

## Local-only devcontainer changes

`.devcontainer/devcontainer.json` is tracked upstream, but this environment needs a few personal additions: `CLAUDE_CONFIG_DIR`, a read-only bind mount of `~/.aws`, a named volume for `/home/vscode/.claude`, and the `anthropic.claude-code` extension. Committing them causes a conflict on every rebase, so they live in the working tree only and are hidden from git with:

```sh
git update-index --skip-worktree .devcontainer/devcontainer.json
```

The committed version of the file therefore stays identical to `upstream/dev`, and `git status` reports a clean tree even though the file on disk differs. Claude's Bedrock environment variables (`CLAUDE_CODE_USE_BEDROCK`, `AWS_REGION`, `AWS_PROFILE`) are deliberately not in this file; they live under the `env` key in `~/.claude/settings.json`, which persists in the `claude-code-config-*` volume across container rebuilds.

The flag has one consequence: git refuses to overwrite a `skip-worktree` file, so if `upstream/dev` ever modifies `devcontainer.json`, the rebase stops with `Entry '.devcontainer/devcontainer.json' not uptodate. Cannot merge.` <!-- codespell:ignore uptodate --> To recover, set the personal version aside, drop the flag so the rebase can proceed, then merge the personal lines back in:

```sh
cp .devcontainer/devcontainer.json /tmp/devcontainer.personal.json
git update-index --no-skip-worktree .devcontainer/devcontainer.json
git checkout -- .devcontainer/devcontainer.json
git rebase upstream/dev
# Re-apply the personal lines from /tmp/devcontainer.personal.json, then hide them again:
git update-index --skip-worktree .devcontainer/devcontainer.json
```

Note that `git checkout -- <file>` discards the working tree version, which is why it is copied out first. Re-applying by hand rather than restoring the copy wholesale keeps any genuine upstream changes to the file.