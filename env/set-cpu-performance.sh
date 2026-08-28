#!/usr/bin/env bash
# Pin the CPU to the `performance` governor and make it survive reboots.
# Run as root:  sudo bash /home/linjiw/lucid/env/set-cpu-performance.sh
#
# Why: on amd-pstate-epp (active mode) the `powersave` governor is NOT slow --
# with EPP=performance the hardware already boosts to near max. What the
# `performance` governor adds is a floor: scaling_min_freq is raised to the max,
# so clocks stop varying. That removes a source of run-to-run variance from
# throughput measurements, which this program's campaign sizing depends on.
set -euo pipefail
[ "$EUID" -eq 0 ] || { echo "must run as root: sudo bash $0" >&2; exit 1; }

echo "before: governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor) \
EPP=$(cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference) \
min=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq)kHz"

cpupower frequency-set -g performance >/dev/null
for f in /sys/devices/system/cpu/cpu*/cpufreq/energy_performance_preference; do
  echo performance > "$f" 2>/dev/null || true
done

# Persist across reboots.
cat > /etc/systemd/system/cpu-performance.service <<'UNIT'
[Unit]
Description=Pin CPU scaling governor to performance
After=multi-user.target

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStart=/usr/bin/cpupower frequency-set -g performance

[Install]
WantedBy=multi-user.target
UNIT
systemctl daemon-reload
systemctl enable cpu-performance.service >/dev/null 2>&1
systemctl start cpu-performance.service

echo "after:  governor=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor) \
EPP=$(cat /sys/devices/system/cpu/cpu0/cpufreq/energy_performance_preference) \
min=$(cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_min_freq)kHz"
echo "governors now: $(cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor | sort -u | tr '\n' ' ')"
echo "persisted via systemd unit cpu-performance.service (enabled)"
