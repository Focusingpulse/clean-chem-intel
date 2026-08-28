#!/usr/bin/env bash
# Clean Chem Intel master cron job — ONE shot, do everything, report briefly.
# Family-aware: gates on should_run, reports stale siblings, checks in.
# Self-healing: clones the repo if missing (sandbox resets).
set -uo pipefail

REPO=/root/workspace/clean-chem-intel
GIT_URL=https://github.com/Focusingpulse/clean-chem-intel.git

# ---- [0] Bootstrap: ensure the repo is present ----
if [ ! -d "$REPO/.git" ]; then
  echo "[0] Repo missing — cloning"
  mkdir -p "$REPO"
  if ! git clone --quiet --depth 1 "$GIT_URL" "$REPO" 2>&1 | tail -2; then
    echo "CLONE_FAILED"
    exit 1
  fi
  echo "  cloned into $REPO"
fi
cd "$REPO"

# ---- Locate the shared coordination repo (attached shared memory) ----
FAMILY=""
for cand in \
  "$MEMORY_DIR/../cron-coordination/family.py" \
  /root/workspace/cron-coordination/family.py \
  /root/workspace/.letta/agents/agent-b73ac550-5671-471e-b3e1-721f948ea063/cron-coordination/family.py; do
  if [ -f "$cand" ]; then FAMILY="$cand"; break; fi
done
if [ -z "$FAMILY" ]; then
  echo "WARN: cron-coordination shared repo not found; running uncoordinated"
fi

# ---- [1] Family gate: gate on should_run before doing work ----
echo "[1] Family gate"
if [ -n "$FAMILY" ]; then
  if ! python3 "$FAMILY" run-gate --member clean-chem --essential 2>/dev/null; then
    MODE=$(python3 -c "import json,os;d=json.load(open(os.path.join('${FAMILY%/*}','cron_ledger.json')));print(d.get('family_budget',{}).get('mode','high'))" 2>/dev/null || echo high)
    if [ "$MODE" = "low" ]; then
      echo "  Family budget LOW — clean-chem skipping non-essential work this cycle"
      python3 "$FAMILY" check-in --member clean-chem --status skipped --summary "budget low, skipped" 2>/dev/null || true
      exit 0
    fi
  fi
  STALE=$(python3 "$FAMILY" staleness 2>/dev/null || echo "")
  if [ -n "$STALE" ]; then
    echo "  Watchdog: $STALE"
  fi
fi

echo "[2] Pull latest"
git stash --quiet 2>/dev/null || true
git pull --rebase --quiet origin main 2>&1 | tail -1 || git pull --quiet origin main 2>&1 | tail -1
git stash pop --quiet 2>/dev/null || true

echo "[3] Validate + rebuild"
# Validate data files, then regenerate index.html from data (living-system build)
MAINT=$(python3 chem_maintain.py 2>&1)
echo "$MAINT" | tail -8
BUILD=$(python3 build.py 2>&1)
echo "$BUILD" | tail -4
SUMMARY=$(echo "$BUILD" | head -1 | grep -oE '[0-9]+ products, [0-9]+ ingredients' || echo "clean-chem build run")

echo "[4] Commit and push (if anything changed)"
git add -A
if git diff --cached --quiet; then
  echo "  Nothing to commit this run; checking in clean"
else
  git commit -q -m "Clean Chem daily: maintenance + improvements

Co-Authored-By: Chris FocusAndExcell <user-9d03ff11-1357-46de-b0be-8561e6285f7c>"
  if [ -n "${CLEANCHEMKEY:-}" ]; then
    # Use the scoped fine-grained token via an inline credential helper so the
    # secret never appears in URLs, .git/config, or logs.
    git -c credential.helper= -c credential.username=x-access-token \
      -c 'credential.helper=!f() { echo username=x-access-token; echo "password=$CLEANCHEMKEY"; }; f' \
      push --quiet origin main 2>&1 | grep -iv "password\|token" | tail -2 || true
  else
    git push --quiet origin main 2>&1 | tail -2 || true
  fi
  SUMMARY=$(git log -1 --format=%s)
fi

echo "[5] Family check-in"
if [ -n "$FAMILY" ]; then
  python3 "$FAMILY" check-in --member clean-chem --status ok --summary "$SUMMARY" 2>/dev/null || true
fi

echo "DONE"