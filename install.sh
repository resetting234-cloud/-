#!/usr/bin/env bash
# MeetionRC modpack installer (Linux/macOS)
# Reads modpack.json and downloads every mod + resource pack from Modrinth
# into per-version folders: 1.20.1/mods/, 1.20.1/resourcepacks/, etc.
#
# Usage:
#   ./install.sh                 # install all versions
#   ./install.sh 1.21.8          # install only one version
#   ./install.sh 1.20.1 1.21.5   # install several versions

set -euo pipefail

# ---------- locate self ----------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG="$SCRIPT_DIR/modpack.json"

# ---------- deps ----------
need() { command -v "$1" >/dev/null 2>&1 || { echo "ERROR: '$1' is not installed. Install it and re-run." >&2; exit 1; }; }
need curl
need jq

[[ -f "$CONFIG" ]] || { echo "ERROR: $CONFIG not found"; exit 1; }

UA=$(jq -r '.user_agent' "$CONFIG")
LOADER=$(jq -r '.loader' "$CONFIG")
ALL_VERSIONS=$(jq -r '.versions[]' "$CONFIG")

# pick versions to install
if [[ $# -gt 0 ]]; then
  VERSIONS=("$@")
else
  mapfile -t VERSIONS < <(echo "$ALL_VERSIONS")
fi

# ---------- helpers ----------

# Resolve newest compatible version of a Modrinth project.
# Args: <slug> <mc_version> [loader_filter:fabric|none]
# Echoes: "<download_url>\t<filename>"  on success
# Returns: 1 with no output if no compatible version found
resolve_modrinth() {
  local slug="$1"
  local mc="$2"
  local loader_filter="${3:-fabric}"

  # URL-encode '+' in slug (e.g. "marlowww+")
  local slug_enc="${slug//+/%2B}"
  local url="https://api.modrinth.com/v2/project/${slug_enc}/version?game_versions=%5B%22${mc}%22%5D"
  if [[ "$loader_filter" == "fabric" ]]; then
    url="${url}&loaders=%5B%22fabric%22%5D"
  fi

  local resp
  resp=$(curl -sS -H "User-Agent: $UA" "$url") || return 1

  # If project doesn't exist Modrinth returns an error object
  if [[ "$resp" == *"\"error\""* || -z "$resp" ]]; then
    return 1
  fi

  # Pick newest release (sorted by date_published desc), prefer "release" type, fall back to any
  local file
  file=$(echo "$resp" | jq -c '
      ( ([.[] | select(.version_type=="release")] // []) as $rel
      | (if ($rel|length) > 0 then $rel else . end) )
      | sort_by(.date_published) | reverse | .[0]
      | (.files[] | select(.primary==true)) // .files[0]
    ' 2>/dev/null) || return 1

  if [[ "$file" == "null" || -z "$file" ]]; then
    return 1
  fi

  local dl fn
  dl=$(echo "$file" | jq -r '.url')
  fn=$(echo "$file" | jq -r '.filename')
  [[ -z "$dl" || "$dl" == "null" ]] && return 1
  printf '%s\t%s\n' "$dl" "$fn"
}

download() {
  local url="$1" out="$2"
  if [[ -f "$out" ]]; then
    echo "    SKIP  (already downloaded) $(basename "$out")"
    return 0
  fi
  curl -sS -L --fail -H "User-Agent: $UA" -o "$out.part" "$url" \
    && mv "$out.part" "$out"
}

install_for_version() {
  local mc="$1"
  echo
  echo "================================================================"
  echo " Installing for Minecraft $mc (loader: $LOADER)"
  echo "================================================================"

  local mods_dir="$SCRIPT_DIR/$mc/mods"
  local rp_dir="$SCRIPT_DIR/$mc/resourcepacks"
  mkdir -p "$mods_dir" "$rp_dir"

  # ---- mods ----
  echo
  echo "[$mc] Mods:"
  local total=0 ok=0 skipped=0
  while IFS=$'\t' read -r slug category desc; do
    total=$((total+1))
    printf "  %-28s " "$slug"
    if line=$(resolve_modrinth "$slug" "$mc" "fabric"); then
      url=$(echo "$line" | cut -f1)
      fn=$(echo "$line"  | cut -f2)
      echo "[$category] -> $fn"
      if download "$url" "$mods_dir/$fn"; then
        ok=$((ok+1))
      else
        echo "      ! download failed"
      fi
    else
      echo "[$category] -- no compatible version, skipped"
      skipped=$((skipped+1))
    fi
  done < <(jq -r '.mods[] | [.slug, .category, .desc] | @tsv' "$CONFIG")
  echo "  --- mods: $ok installed, $skipped skipped, of $total ---"

  # ---- resource packs (no loader filter) ----
  echo
  echo "[$mc] Resource packs:"
  local rtotal=0 rok=0 rskipped=0
  while IFS=$'\t' read -r slug desc; do
    rtotal=$((rtotal+1))
    printf "  %-32s " "$slug"
    if line=$(resolve_modrinth "$slug" "$mc" "none"); then
      url=$(echo "$line" | cut -f1)
      fn=$(echo "$line"  | cut -f2)
      echo "-> $fn"
      if download "$url" "$rp_dir/$fn"; then
        rok=$((rok+1))
      else
        echo "      ! download failed"
      fi
    else
      echo "-- no compatible version, skipped"
      rskipped=$((rskipped+1))
    fi
  done < <(jq -r '.resourcepacks[] | [.slug, .desc] | @tsv' "$CONFIG")
  echo "  --- resourcepacks: $rok installed, $rskipped skipped, of $rtotal ---"
}

# ---------- run ----------
for v in "${VERSIONS[@]}"; do
  install_for_version "$v"
done

cat <<EOF

================================================================
 Done.
 Move the contents of <version>/mods/ into your Minecraft mods folder:
   Windows:  %APPDATA%\\.minecraft\\mods
   Linux:    ~/.minecraft/mods
   macOS:    ~/Library/Application Support/minecraft/mods

 And <version>/resourcepacks/ into:
   .minecraft/resourcepacks

 Make sure you have Fabric Loader installed for the same MC version
 (https://fabricmc.net/use/installer/).
================================================================
EOF
