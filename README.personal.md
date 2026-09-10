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

## Netatmo custom component

The Netatmo changes were rejected upstream, so they are not part of `dev-personal`. They live on one branch per release tag, `feature/<tag>-netatmo-custom`, and are installed as a custom component. The most recent one is `feature/2026.9.1-netatmo-custom` (commit `21f10c2e9df`, based on tag `2026.9.1`).

### Patching a new release

```sh
git fetch upstream --tags
git tag -l | grep -E '^20[0-9]{2}\.[0-9]+\.[0-9]+$' | sort -V | tail -1  # latest stable tag
git checkout -b feature/<tag>-netatmo-custom <tag>
git cherry-pick <tip commit of the previous feature/*-netatmo-custom branch>
```

Conflicts are usually limited to the `from .const import (...)` block in `climate.py`; keep the added names and drop imports upstream has removed. Then verify:

```sh
uv run --no-sync prek run --files homeassistant/components/netatmo/*
uv run --no-sync pytest tests/components/netatmo
```

### What the patch changes

It adds the `netatmo.set_scheduled_room_temperature` action, which writes a room's target temperature into a named zone of the active Netatmo schedule:

- `const.py`: `ATTR_ZONE_NAME` and `SERVICE_SET_SCHEDULED_ROOM_TEMPERATURE`. Do not add an `ATTR_TEMPERATURE` here — pylint rejects it as a duplicate of `homeassistant.const`; `climate.py` already imports that one.
- `climate.py`: register the entity service in `async_setup_entry` (required `zone_name` string and `temperature` float) plus `NetatmoThermostat._async_service_set_scheduled_room_temperature`, which resolves the zone by name in `home.get_selected_schedule()`, calls `home.async_set_schedule_temperatures()` and writes the new setpoint into the entity state right away.
- `services.yaml`: action targeting netatmo climate entities, `zone_name` as a select (Eco, Comfort, Comfort+, Night), `temperature` as a number between 10 and 30.
- `strings.json`: action name and descriptions, plus the `temperature` and `zone_name` labels under `device_automation.trigger_subtype` that the fields reference via `[%key:…]`.
- `icons.json`: `mdi:thermometer` for the new action.

### Installing

Copy `homeassistant/components/netatmo` to `custom_components/netatmo` in the Home Assistant configuration directory. Custom integrations must declare a `version` in `manifest.json`, so add one (upstream manifests do not have it) before restarting Home Assistant.

## Local-only devcontainer changes

`.devcontainer/devcontainer.json` is tracked upstream, but this environment adds `CLAUDE_CONFIG_DIR`, a read-only bind mount of `~/.aws`, a volume for `/home/vscode/.claude`, and the `anthropic.claude-code` extension. Committing them conflicts on every rebase, so they live in the working tree only, hidden from git with:

```sh
git update-index --skip-worktree .devcontainer/devcontainer.json
```

Claude's Bedrock variables (`CLAUDE_CODE_USE_BEDROCK`, `AWS_REGION`, `AWS_PROFILE`) are deliberately not in this file; they live in `~/.claude/settings.json`, which persists in the `claude-code-config-*` volume across rebuilds.

Git refuses to overwrite a `skip-worktree` file, so a rebase that touches `devcontainer.json` stops with `Entry '...' not uptodate. Cannot merge.` <!-- codespell:ignore uptodate --> To recover:

```sh
cp .devcontainer/devcontainer.json /tmp/devcontainer.personal.json
git update-index --no-skip-worktree .devcontainer/devcontainer.json
git checkout -- .devcontainer/devcontainer.json  # discards the working tree version
git rebase upstream/dev
# Re-apply the personal lines by hand to keep genuine upstream changes, then hide them again:
git update-index --skip-worktree .devcontainer/devcontainer.json
```