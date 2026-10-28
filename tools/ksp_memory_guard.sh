#!/usr/bin/env bash
# ==============================================================================
# CSA KSP Memory Guard & Host RAM Optimizer
# ==============================================================================
# Protects KSP.x86_64 from systemd-oomd / kernel OOM kills and frees ~1.0-1.5 GB
# of background desktop memory before long flight missions.
# ==============================================================================

set -euo pipefail

echo "============================================================"
echo "🛡️  CSA KSP Memory Guard & RAM Optimizer"
echo "============================================================"

# 1. Ensure systemd user drop-in for Steam scope OOM protection is present
DROPIN_DIR="$HOME/.config/systemd/user/app-gnome-steam-.scope.d"
mkdir -p "$DROPIN_DIR"
cat << 'EOF' > "$DROPIN_DIR/oom-protect.conf"
[Scope]
OOMPolicy=continue
ManagedOOMPreference=avoid
EOF
systemctl --user daemon-reload

# Verify active Steam scope settings
STEAM_SCOPE=$(systemctl --user list-units --type=scope --plain --no-legend | awk '/app-gnome-steam-.*\.scope/ {print $1; exit}')
if [[ -n "${STEAM_SCOPE:-}" ]]; then
    POLICY=$(systemctl --user show "$STEAM_SCOPE" -p OOMPolicy --value || echo "unknown")
    PREF=$(systemctl --user show "$STEAM_SCOPE" -p ManagedOOMPreference --value || echo "unknown")
    echo "✅ Active Steam Scope ($STEAM_SCOPE): OOMPolicy=$POLICY, ManagedOOMPreference=$PREF"
fi

# 2. Lower KSP.x86_64 OOM score to minimum unprivileged value (100, below sacrificial helpers)
KSP_PID=$(pgrep -x "KSP.x86_64" | head -n 1 || true)
if [[ -n "${KSP_PID:-}" ]]; then
    echo 100 > "/proc/$KSP_PID/oom_score_adj" 2>/dev/null || true
    SCORE=$(cat "/proc/$KSP_PID/oom_score" 2>/dev/null || echo "?")
    ADJ=$(cat "/proc/$KSP_PID/oom_score_adj" 2>/dev/null || echo "?")
    RSS_MB=$(awk '/VmRSS/ {printf "%.0f", $2/1024}' "/proc/$KSP_PID/status" 2>/dev/null || echo "?")
    echo "✅ Protected KSP.x86_64 (PID $KSP_PID): VmRSS=${RSS_MB} MB | oom_score_adj=$ADJ (oom_score=$SCORE)"
else
    echo "ℹ️  KSP.x86_64 is not currently running."
fi

# 3. Reset steamwebhelper oom_score_adj to 200 (sacrificial before KSP, safe with OOMPolicy=continue)
for pid in $(pgrep -f "steamwebhelper" || true); do
    echo 200 > "/proc/$pid/oom_score_adj" 2>/dev/null || true
done

# 4. Optional "--trim" flag to suspend background indexers and Steam CEF bloat
if [[ "${1:-}" == "--trim" ]]; then
    echo "🧹 Trimming non-essential background services..."
    systemctl --user stop localsearch-3.service 2>/dev/null || true
    echo "   - Stopped localsearch-3.service (GNOME file indexer)"
fi

echo "------------------------------------------------------------"
free -h
echo "============================================================"
