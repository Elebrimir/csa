import csv
import os

csv_path = '/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-05b_telemetry.csv'
out_svg = '/home/pablo-cortes/Documents/Corolt_Space_Agency/assets/csa-05b_telemetry_plot.svg'
out_summary = '/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-05b_summary.md'

with open(csv_path, 'r') as f:
    rows = list(csv.DictReader(f))

# Filter rows until impact (velocity drops to 0 at MET ~1011.8)
valid_rows = []
for r in rows:
    met = float(r['MET'])
    alt = float(r['altitude'])
    vel = float(r['surface_vel'])
    if met > 1012:
        break
    valid_rows.append(r)

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

impact_time = times[-1]
impact_alt = alts[-1]
impact_vel = vels[-2] if len(vels) > 1 else vels[-1]

# Time in space (> 70,000m)
space_times = [t for t, a in zip(times, alts) if a >= 70000]
time_in_space = (space_times[-1] - space_times[0]) if space_times else 0

summary_content = f"""# Telemetry Summary of Mission CSA-05b

- **Vehicle**: Corolt-III (Unit 02 - Tandem)
- **Objective**: Atmospheric / Suborbital Flight and Payload Capacity Test
- **Outcome**: Space propulsion success (240 km) | Loss on reentry due to impact

## Critical Recorded Parameters
- **Maximum Altitude (Apoapsis)**: {max_alt:,.1f} m ({max_alt/1000:.2f} km) at T+{max_alt_time:.1f}s
- **Maximum Surface Speed**: {max_vel:,.1f} m/s ({max_vel*3.6:,.1f} km/h) at T+{max_vel_time:.1f}s
- **Maximum Dynamic Pressure (Max Q)**: {max_q:,.1f} Pa ({max_q/1000:.2f} kPa)
- **Maximum Acceleration**: {max_g:.2f} G
- **Time in Outer Space (>70 km)**: {time_in_space:.1f} seconds ({time_in_space/60:.1f} minutes)
- **Total Flight Time until Impact**: {impact_time:.1f} seconds ({impact_time/60:.2f} minutes)
- **Impact Speed**: {impact_vel:.1f} m/s at elevation {impact_alt:.1f} m
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
alt_ceil = 260000.0  # 260 km
vel_ceil = 1800.0    # 1800 m/s

# Subsample points for SVG cleanliness
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

# Key points
peak_x = pad_l + (max_alt_time / max_t) * plot_w
peak_y = pad_t + plot_h - (max_alt / alt_ceil) * plot_h

# 70km line
y_70k = pad_t + plot_h - (70000.0 / alt_ceil) * plot_h

# Grid
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
    grid_lines.append(f'<text x="{x:.1f}" y="{h - pad_b + 20}" font-size="11" fill="#94a3b8" text-anchor="middle" font-family="monospace">{int(val_t)}s</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" style="background:#0b0f19; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">
  <rect width="{w}" height="{h}" fill="#0b0f19" rx="8"/>
  
  <!-- Title & Legend -->
  <text x="{pad_l}" y="28" font-size="14" font-weight="bold" fill="#f8fafc">CSA-05b: Suborbital Flight to Outer Space (Apoapsis 240.3 km and Impact)</text>
  <circle cx="{w - 260}" cy="24" r="5" fill="#38bdf8"/>
  <text x="{w - 250}" y="28" font-size="12" fill="#38bdf8">Altitude (km)</text>
  <circle cx="{w - 140}" cy="24" r="5" fill="#f43f5e"/>
  <text x="{w - 130}" y="28" font-size="12" fill="#f43f5e">Velocity (m/s)</text>

  <!-- Space boundary 70km -->
  <line x1="{pad_l}" y1="{y_70k:.1f}" x2="{w - pad_r}" y2="{y_70k:.1f}" stroke="#a855f7" stroke-dasharray="6,4" stroke-width="1.5"/>
  <text x="{w - pad_r - 10}" y="{y_70k - 6:.1f}" font-size="11" fill="#a855f7" font-weight="bold" text-anchor="end">Space Boundary (Kármán 70 km)</text>

  <!-- Grid & Ticks -->
  {"".join(grid_lines)}

  <!-- Axes -->
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>
  <line x1="{w - pad_r}" y1="{pad_t}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>
  <line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>

  <!-- Plot curves -->
  <polyline fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" points="{str_alt}"/>
  <polyline fill="none" stroke="#f43f5e" stroke-width="2" stroke-linecap="round" points="{str_vel}"/>

  <!-- Apogee Marker -->
  <circle cx="{peak_x:.1f}" cy="{peak_y:.1f}" r="5" fill="#38bdf8" stroke="#ffffff" stroke-width="2"/>
  <text x="{peak_x:.1f}" y="{peak_y - 12:.1f}" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="middle">Apogee: 240.34 km (T+{max_alt_time:.0f}s)</text>

  <!-- Impact Marker -->
  <circle cx="{pad_l + plot_w:.1f}" cy="{pad_t + plot_h:.1f}" r="5" fill="#ef4444" stroke="#ffffff" stroke-width="2"/>
  <text x="{w - pad_r - 10}" y="{pad_t + plot_h - 15:.1f}" font-size="11" font-weight="bold" fill="#ef4444" text-anchor="end">Ground Impact: 116 m/s (T+{impact_time:.0f}s)</text>

  <!-- Axis Titles -->
  <text x="{w / 2}" y="{h - 15}" font-size="12" fill="#94a3b8" text-anchor="middle">Mission Elapsed Time (MET) in seconds (~16.8 min)</text>
  <text transform="rotate(-90)" x="{- (pad_t + plot_h/2)}" y="24" font-size="11" fill="#38bdf8" text-anchor="middle">Altitude (km)</text>
  <text transform="rotate(90)" x="{pad_t + plot_h/2}" y="{-w + 24}" font-size="11" fill="#f43f5e" text-anchor="middle">Velocity (m/s)</text>
</svg>
'''

with open(out_svg, 'w') as f:
    f.write(svg)

print(f"Generated {out_svg} successfully!")
