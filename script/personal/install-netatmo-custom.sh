#!/usr/bin/env bash
# Install the patched netatmo integration as a custom component on Home Assistant.
#
# See README.netatmo-customization.md for how the feature/<tag>-netatmo-custom branches are maintained.
set -euo pipefail

HA_SSH_HOST="${HA_SSH_HOST:-hassio@oberiberg.internet-box.ch}"
HA_SSH_PORT="${HA_SSH_PORT:-33}"
HA_HOME="${HA_HOME:-/homeassistant}"
GIT_REMOTE="${GIT_REMOTE:-origin}"

BRANCH=""
VERSION=""
ASSUME_YES=false
RESTART=false

usage() {
  cat <<'EOF'
Usage: script/personal/install-netatmo-custom.sh [options]

Fetches the newest feature/<tag>-netatmo-custom branch, stamps a version into
manifest.json and installs it as custom_components/netatmo on Home Assistant.

Options:
  -b, --branch NAME     Branch to install (default: highest feature/<tag>-netatmo-custom)
  -v, --version VER     manifest.json version (default: <tag>+netatmo.<short sha>)
  -y, --yes             Skip the confirmation prompt
  -r, --restart         Run "ha core restart" after installing
  -h, --help            Show this help

Environment overrides:
  HA_SSH_HOST (default hassio@oberiberg.internet-box.ch)
  HA_SSH_PORT (default 33)
  HA_HOME (default /homeassistant, expanded on the remote)
  GIT_REMOTE (default origin)
  HA_SUDO (default: "sudo -n" unless the SSH user is already root, set to
           the empty string to never escalate)
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -b | --branch)
      BRANCH="$2"
      shift 2
      ;;
    -v | --version)
      VERSION="$2"
      shift 2
      ;;
    -y | --yes)
      ASSUME_YES=true
      shift
      ;;
    -r | --restart)
      RESTART=true
      shift
      ;;
    -h | --help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

REPO_ROOT="$(git -C "$(dirname "${BASH_SOURCE[0]}")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

ssh_ha() {
  ssh -p "$HA_SSH_PORT" "$HA_SSH_HOST" "$@"
}

if [[ -z $BRANCH ]]; then
  echo "Looking for netatmo branches on $GIT_REMOTE..."
  BRANCH="$(
    git ls-remote --heads "$GIT_REMOTE" 'refs/heads/feature/*-netatmo-custom' \
      | sed -E 's#^[0-9a-f]+[[:space:]]+refs/heads/(feature/(.+)-netatmo-custom)$#\2\t\1#' \
      | sort -V \
      | tail -1 \
      | cut -f2
  )"
  [[ -n $BRANCH ]] || {
    echo "No feature/<tag>-netatmo-custom branch found on $GIT_REMOTE" >&2
    exit 1
  }
fi

TAG="${BRANCH#feature/}"
TAG="${TAG%-netatmo-custom}"

echo "Fetching $GIT_REMOTE/$BRANCH..."
git fetch --quiet "$GIT_REMOTE" "refs/heads/$BRANCH"
COMMIT="$(git rev-parse FETCH_HEAD)"
SHORT_COMMIT="$(git rev-parse --short FETCH_HEAD)"

[[ -n $VERSION ]] || VERSION="$TAG+netatmo.$SHORT_COMMIT"

STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT
mkdir "$STAGE/netatmo"
git archive "FETCH_HEAD:homeassistant/components/netatmo" | tar -x -C "$STAGE/netatmo"

# Guard against installing a branch that lost the patch during a cherry-pick.
grep -q "SERVICE_SET_SCHEDULED_ROOM_TEMPERATURE" "$STAGE/netatmo/const.py" || {
  echo "$BRANCH does not contain the netatmo customization - refusing to install" >&2
  exit 1
}

python3 - "$STAGE/netatmo/manifest.json" "$VERSION" <<'PY'
import json
import sys

path, version = sys.argv[1], sys.argv[2]
with open(path, encoding="utf-8") as file:
    manifest = json.load(file)

# Custom integrations must declare a version; upstream manifests do not have one.
patched = {}
for key, value in manifest.items():
    patched[key] = value
    if key == "domain":
        patched["version"] = version
patched.setdefault("version", version)

with open(path, "w", encoding="utf-8") as file:
    json.dump(patched, file, indent=2)
    file.write("\n")
PY

TIMESTAMP="$(date +%Y%m%d-%H%M%S)"
REMOTE_STAGE="\$HOME/.netatmo-install-$TIMESTAMP"

# The add-on escalates to root from ~/.zprofile ("exec sudo -i"), which only
# login shells read - "ssh host cmd" stays the unprivileged "hassio" user and
# cannot write below $HA_HOME. HA_SUDO_LOGIN additionally picks up root's login
# environment, where /etc/profile.d/homeassistant.sh exports SUPERVISOR_TOKEN
# for the "ha" CLI.
HA_SUDO_LOGIN=""
if [[ -z ${HA_SUDO+x} ]]; then
  case "$(ssh_ha 'if [ "$(id -u)" -eq 0 ]; then echo root; elif sudo -n true 2>/dev/null; then echo sudo; else echo none; fi')" in
    root) HA_SUDO="" ;;
    sudo)
      HA_SUDO="sudo -n"
      HA_SUDO_LOGIN="sudo -n -i"
      ;;
    *)
      echo "$HA_SSH_HOST is neither root nor allowed passwordless sudo - cannot write to $HA_HOME" >&2
      exit 1
      ;;
  esac
fi

cat <<EOF

  branch     $BRANCH ($SHORT_COMMIT, based on $TAG)
  subject    $(git log -1 --format=%s FETCH_HEAD)
  version    $VERSION
  files      $(find "$STAGE/netatmo" -type f | wc -l | tr -d ' ') files, $(du -sh "$STAGE/netatmo" | cut -f1)
  host       $HA_SSH_HOST:$HA_SSH_PORT
  escalate   ${HA_SUDO:-none (already root)}
  target     $HA_HOME/custom_components/netatmo
  backup     $HA_HOME/netatmo-backups/netatmo-$TIMESTAMP.tar.gz
  restart    $RESTART

EOF

if [[ $ASSUME_YES == false ]]; then
  read -r -p "Install now? [y/N] " reply
  [[ $reply =~ ^[Yy]([Ee][Ss])?$ ]] || {
    echo "Aborted."
    exit 1
  }
fi

echo "Copying to $HA_SSH_HOST..."
ssh_ha "mkdir -p $REMOTE_STAGE"
tar -cf - -C "$STAGE" netatmo | ssh_ha "tar -xf - -C $REMOTE_STAGE"

echo "Installing..."
ssh_ha "$HA_SUDO sh -s -- $HA_HOME $REMOTE_STAGE $TIMESTAMP" <<'REMOTE'
set -eu
ha_home=$1
stage=$2
timestamp=$3

if [ ! -d "$ha_home" ]; then
  echo "Home Assistant directory $ha_home does not exist on the remote" >&2
  rm -rf "$stage"
  exit 1
fi

target="$ha_home/custom_components/netatmo"
# The backup lives outside custom_components so Home Assistant never scans it.
backup_dir="$ha_home/netatmo-backups"

mkdir -p "$ha_home/custom_components"

if [ -d "$target" ]; then
  mkdir -p "$backup_dir"
  tar -czf "$backup_dir/netatmo-$timestamp.tar.gz" -C "$ha_home/custom_components" netatmo
  echo "Backed up to $backup_dir/netatmo-$timestamp.tar.gz"
  rm -rf "$target"
fi

mv "$stage/netatmo" "$target"
rm -rf "$stage"
echo "Installed $(grep -o '"version": "[^"]*"' "$target/manifest.json") in $target"
REMOTE

if [[ $RESTART == true ]]; then
  echo "Restarting Home Assistant Core..."
  ssh_ha "$HA_SUDO_LOGIN ha core restart"
else
  echo "Done. Restart Home Assistant to load the new version."
fi
