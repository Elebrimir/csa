import csv
import os

csv_path = '/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-07_telemetry.csv'
out_svg = '/home/pablo-cortes/Documents/Corolt_Space_Agency/assets/csa-07_telemetry_plot.svg'
out_summary = '/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-07_summary.md'

with open(csv_path, 'r') as f:
    rows = list(csv.DictReader(f))

# Filter rows until splashdown
valid_rows = []
for r in rows:
    try:
        met = float(r['MET'])
        alt = float(r['altitude'])
        vel = float(r['surface_vel'])
        valid_rows.append(r)
        if alt <= 0.0 and met > 500:
            break
    except:
        pass

times = [float(r['MET']) for r in valid_rows]
alts = [float(r['altitude']) for r in valid_rows]
vels = [float(r['surface_vel']) for r in valid_rows]
dyn_press = [float(r['dynamic_pressure']) for r in valid_rows]
g_forces = [float(r['g_force']) for r in valid_rows]

max_alt = max(alts)
max_vel = max(vels)
max_q = max(dyn_press)
max_g = max(g_forces)

max_alt_idx = alts.index(max_alt)
max_alt_time = times[max_alt_idx]

max_vel_idx = vels.index(max_vel)
max_vel_time = times[max_vel_idx]

landing_time = times[-1]
landing_alt = alts[-1]

space_times = [t for t, a in zip(times, alts) if a >= 70000]
time_in_space = (space_times[-1] - space_times[0]) if space_times else 0

summary_content = f"""# Telemetry Summary of Mission CSA-07

- **Vehicle**: Corolt-IIIb (First flight with Movable Control Surfaces)
- **Objective**: Aerodynamic Actuation Validation, Eastward Inclined Trajectory and Ocean Recovery
- **Outcome**: 🟢 Total Success | Apoapsis of {max_alt/1000:.1f} km | Soft splashdown under parachutes and full recovery

## Critical Recorded Parameters
- **Maximum Altitude (Apoapsis)**: {max_alt:,.1f} m ({max_alt/1000:.2f} km) at T+{max_alt_time:.1f}s
- **Maximum Surface Speed**: {max_vel:,.1f} m/s ({max_vel*3.6:,.1f} km/h, Mach ~{max_vel/310:.1f}) at T+{max_vel_time:.1f}s
- **Maximum Dynamic Pressure (Max Q)**: {max_q:,.1f} Pa ({max_q/1000:.2f} kPa)
- **Maximum Acceleration**: {max_g:.2f} G
- **Time in Outer Space (>70 km)**: {time_in_space:.1f} seconds ({time_in_space/60:.1f} minutes)
- **Total Flight Time until Splashdown**: {landing_time:.1f} seconds ({landing_time/60:.2f} minutes)
- **Water Impact Velocity**: {vels[-1]:.2f} m/s at elevation {landing_alt:.1f} m
"""

with open(out_summary, 'w') as f:
    f.write(summary_content)

print(summary_content)

# Generate SVG
w = 880
h = 420
pad_l = 80
pad_r = 80
pad_t = 50
pad_b = 60

plot_w = w - pad_l - pad_r
plot_h = h - pad_t - pad_b

max_t = times[-1]
alt_ceil = 160000.0  # 160 km
vel_ceil = 1600.0    # 1600 m/s

step = max(1, len(valid_rows) // 400)
sub_rows = valid_rows[::step]
if valid_rows[-1] not in sub_rows:
    sub_rows.append(valid_rows[-1])

pts_alt = []
pts_vel = []

for r in sub_rows:
    t = float(r['MET'])
    a = float(r['altitude'])
    v = float(r['surface_vel'])
    x = pad_l + (t / max_t) * plot_w
    y_alt = pad_t + plot_h - (a / alt_ceil) * plot_h
    y_vel = pad_t + plot_h - (v / vel_ceil) * plot_h
    pts_alt.append(f"{x:.1f},{y_alt:.1f}")
    pts_vel.append(f"{x:.1f},{y_vel:.1f}")

str_alt = " ".join(pts_alt)
str_vel = " ".join(pts_vel)

peak_x = pad_l + (max_alt_time / max_t) * plot_w
peak_y = pad_t + plot_h - (max_alt / alt_ceil) * plot_h

y_70k = pad_t + plot_h - (70000.0 / alt_ceil) * plot_h

grid_lines = []
for i in range(6):
    y = pad_t + (i / 5.0) * plot_h
    val_a = (1.0 - i / 5.0) * alt_ceil
    val_v = (1.0 - i / 5.0) * vel_ceil
    grid_lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
    grid_lines.append(f'<text x="{pad_l - 10}" y="{y + 4:.1f}" font-size="11" fill="#38bdf8" text-anchor="end" font-family="monospace">{val_a/1000:.0f} km</text>')
    grid_lines.append(f'<text x="{w - pad_r + 10}" y="{y + 4:.1f}" font-size="11" fill="#f43f5e" text-anchor="start" font-family="monospace">{val_v:.0f} m/s</text>')

for i in range(7):
    x = pad_l + (i / 6.0) * plot_w
    val_t = (i / 6.0) * max_t
    grid_lines.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{h - pad_b}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
    grid_lines.append(f'<text x="{x:.1f}" y="{h - pad_b + 20}" font-size="11" fill="#94a3b8" text-anchor="middle" font-family="monospace">T+{val_t:.0f}s</text>')

grid_svg = "\n    ".join(grid_lines)

svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%" style="background:#0b0f19; border-radius:8px; font-family:-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <defs>
    <linearGradient id="altGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.3"/>
      <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.0"/>
    </linearGradient>
  </defs>

  <!-- Title -->
  <text x="{w/2}" y="28" font-size="16" font-weight="bold" fill="#f8fafc" text-anchor="middle">COROLT SPACE AGENCY  |  FLIGHT TELEMETRY: MISSION CSA-07</text>
  <text x="{w/2}" y="44" font-size="11" fill="#64748b" text-anchor="middle">Corolt-IIIb (Movable Control Surfaces) • Apoapsis: {max_alt/1000:.1f} km • Full Ocean Recovery</text>

  <!-- Grid -->
  {grid_svg}

  <!-- Karman Line -->
  <line x1="{pad_l}" y1="{y_70k:.1f}" x2="{w - pad_r}" y2="{y_70k:.1f}" stroke="#a855f7" stroke-width="1.5" stroke-dasharray="5,5"/>
  <text x="{w - pad_r - 10}" y="{y_70k - 6:.1f}" font-size="11" fill="#c084fc" text-anchor="end" font-weight="bold">Kármán Line (70 km)</text>

  <!-- Velocity Line -->
  <polyline fill="none" stroke="#f43f5e" stroke-width="2" points="{str_vel}"/>

  <!-- Altitude Line -->
  <polyline fill="none" stroke="#38bdf8" stroke-width="2.5" points="{str_alt}"/>

  <!-- Peak indicator -->
  <circle cx="{peak_x:.1f}" cy="{peak_y:.1f}" r="4" fill="#38bdf8"/>
  <rect x="{peak_x - 65:.1f}" y="{peak_y - 28:.1f}" width="130" height="20" rx="4" fill="#0f172a" stroke="#38bdf8" stroke-width="1"/>
  <text x="{peak_x:.1f}" y="{peak_y - 14:.1f}" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle">Apogee: {max_alt/1000:.1f} km</text>

  <!-- Legends -->
  <g transform="translate({pad_l}, {h - 22})">
    <line x1="0" y1="0" x2="20" y2="0" stroke="#38bdf8" stroke-width="2.5"/>
    <text x="25" y="4" font-size="11" fill="#94a3b8">Altitude (km)</text>

    <line x1="120" y1="0" x2="140" y2="0" stroke="#f43f5e" stroke-width="2"/>
    <text x="145" y="4" font-size="11" fill="#94a3b8">Surface Velocity (m/s)</text>

    <line x1="330" y1="0" x2="350" y2="0" stroke="#a855f7" stroke-width="1.5" stroke-dasharray="4,4"/>
    <text x="355" y="4" font-size="11" fill="#94a3b8">Outer Space (>70 km)</text>
  </g>
</svg>"""

with open(out_svg, 'w') as f:
    f.write(svg)

print(f"SVG plot generated successfully at: {out_svg}")
