# `netatmo-customization`

This branch carries the fork-only changes of this Home Assistant Core setup: the tooling and documentation for the Netatmo custom component, plus the devcontainer tweaks this environment needs. It is based on the official repository's `dev` branch and is meant to stay in the fork rather than be submitted upstream.

It is not a starting point for feature development. Branch feature work off `upstream/dev` so it carries none of these changes.

The remotes are used as follows:

- `origin` is the personal fork: `https://github.com/wuede/home-assistant-core.git`
- `upstream` is the official repository: `https://github.com/home-assistant/core.git`

## Update from `upstream/dev`

Make sure local changes are committed or stashed, then run:

```sh
git fetch upstream dev
git rebase upstream/dev
```

This updates the branch base while preserving the commits that belong to `netatmo-customization`. Resolve any conflicts during the rebase before continuing — `.devcontainer/devcontainer.json` is the likely one, since it is modified here and maintained upstream; keep the upstream edits and re-apply the personal additions listed below. Push the rebased branch to your fork with `git push --force-with-lease origin netatmo-customization` if it has already been published there.

## Netatmo custom component

The Netatmo changes were rejected upstream, so they are deliberately not part of this branch — keeping them out avoids ever carrying them into an upstream pull request. They live on one branch per release tag, `feature/<tag>-netatmo-custom`, and are installed as a custom component. `latest-netatmo-custom` is a moving pointer to the newest of those branches, so it is always the commit to cherry-pick from. It currently points at `feature/2026.9.1-netatmo-custom` (commit `21f10c2e9df`, based on tag `2026.9.1`).

The pointer is never rebased onto `dev`: the patch is always applied to a release tag, which is behind `dev`, so keeping its context on the previous release minimises conflicts.

### Patching a new release

```sh
git fetch upstream --tags
git tag -l | grep -E '^20[0-9]{2}\.[0-9]+\.[0-9]+$' | sort -V | tail -1  # latest stable tag
git checkout -b feature/<tag>-netatmo-custom <tag>
git cherry-pick latest-netatmo-custom
```

Conflicts are usually limited to the `from .const import (...)` block in `climate.py`; keep the added names and drop imports upstream has removed. Then verify:

```sh
uv run --no-sync prek run --files homeassistant/components/netatmo/*
uv run --no-sync pytest tests/components/netatmo
```

Finally move the pointer to the new branch:

```sh
git branch -f latest-netatmo-custom feature/<tag>-netatmo-custom
git push --force-with-lease origin latest-netatmo-custom
```

### What the patch changes

It adds the `netatmo.set_scheduled_room_temperature` action, which writes a room's target temperature into a named zone of the active Netatmo schedule:

- `const.py`: `ATTR_ZONE_NAME` and `SERVICE_SET_SCHEDULED_ROOM_TEMPERATURE`. Do not add an `ATTR_TEMPERATURE` here — pylint rejects it as a duplicate of `homeassistant.const`; `climate.py` already imports that one.
- `climate.py`: register the entity service in `async_setup_entry` (required `zone_name` string and `temperature` float) plus `NetatmoThermostat._async_service_set_scheduled_room_temperature`, which resolves the zone by name in `home.get_selected_schedule()`, calls `home.async_set_schedule_temperatures()` and writes the new setpoint into the entity state right away.
- `services.yaml`: action targeting netatmo climate entities, `zone_name` as a select (Eco, Comfort, Comfort+, Night), `temperature` as a number between 10 and 30.
- `strings.json`: action name and descriptions, plus the `temperature` and `zone_name` labels under `device_automation.trigger_subtype` that the fields reference via `[%key:…]`.
- `icons.json`: `mdi:thermometer` for the new action.

### Installing

```sh
script/personal/install-netatmo-custom.sh
```

The script picks the highest `feature/<tag>-netatmo-custom` branch on `origin`, fetches it without touching the working tree, extracts `homeassistant/components/netatmo` from that commit and copies it over SSH to `custom_components/netatmo` in the Home Assistant configuration directory. It prints what it is about to do and waits for confirmation.

Custom integrations must declare a `version` in `manifest.json`, which upstream manifests do not have. The script inserts `<tag>+netatmo.<short sha>` (for example `2026.9.1+netatmo.21f10c2e9df`) so the Home Assistant logs and the integration page show which release the patch is based on and which commit produced it. AwesomeVersion parses this as SemVer with build metadata.

Before overwriting, the existing directory is archived to `netatmo-backups/netatmo-<timestamp>.tar.gz` in the configuration directory — outside `custom_components`, so Home Assistant never tries to load it as an integration. To roll back, extract it back into `custom_components` and restart.

The script refuses to install a branch whose `const.py` lacks `SERVICE_SET_SCHEDULED_ROOM_TEMPERATURE`, which catches a cherry-pick that silently dropped the patch.

Useful options: `--branch` and `--version` to override the defaults, `--yes` to skip the prompt, `--restart` to run `ha core restart` afterwards (otherwise restart Home Assistant manually). The SSH target and the Home Assistant home directory default to the personal setup and can be overridden with the `HA_SSH_HOST`, `HA_SSH_PORT` and `HA_HOME` environment variables (`CORE_REMOTE` picks the git remote to look for the branch on). Authentication is left to the SSH agent, so the key must be loaded (`ssh-add -l`) before running the script.