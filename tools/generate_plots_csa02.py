import csv
import os

csv_path = '/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-02_telemetry.csv'
out_svg = '/home/pablo-cortes/Documents/Corolt_Space_Agency/assets/csa-02_telemetry_plot.svg'

with open(csv_path, 'r') as f:
    rows = list(csv.DictReader(f))

# Filter flight data between liftoff (alt > 76, surf_vel > 2) and touchdown
liftoff_idx = 0
for i, r in enumerate(rows):
    if float(r['surface_vel']) > 3.0 and float(r['altitude']) > 75.0:
        liftoff_idx = i
        break

touchdown_idx = len(rows) - 1
for i in range(len(rows) - 1, liftoff_idx, -1):
    if float(r['altitude']) > 65.0:
        touchdown_idx = i
        break

flight_rows = rows[liftoff_idx:touchdown_idx+1]
t0 = float(flight_rows[0]['MET'])

times = [float(r['MET']) - t0 for r in flight_rows]
alts = [float(r['altitude']) for r in flight_rows]
vels = [float(r['surface_vel']) for r in flight_rows]

w = 820
h = 380
pad_l = 70
pad_r = 70
pad_t = 45
pad_b = 55

plot_w = w - pad_l - pad_r
plot_h = h - pad_t - pad_b

max_t = times[-1] or 1.0
max_alt = 4500.0  # nice ceiling for 4057m
max_vel = 200.0   # nice ceiling for 163m/s

pts_alt = []
pts_vel = []

# Downsample points for smooth rendering
step = max(1, len(times) // 250)
sample_indices = list(range(0, len(times), step))
if sample_indices[-1] != len(times) - 1:
    sample_indices.append(len(times) - 1)

for idx in sample_indices:
    t = times[idx]
    a = alts[idx]
    v = vels[idx]
    x = pad_l + (t / max_t) * plot_w
    y_alt = pad_t + plot_h - (a / max_alt) * plot_h
    y_vel = pad_t + plot_h - (v / max_vel) * plot_h
    pts_alt.append(f"{x:.1f},{y_alt:.1f}")
    pts_vel.append(f"{x:.1f},{y_vel:.1f}")

str_alt = " ".join(pts_alt)
str_vel = " ".join(pts_vel)

# Key points:
# 1. Apogee
peak_idx = alts.index(max(alts))
peak_t = times[peak_idx]
peak_alt = alts[peak_idx]
peak_x = pad_l + (peak_t / max_t) * plot_w
peak_y = pad_t + plot_h - (peak_alt / max_alt) * plot_h

# 2. Max velocity / Burnout
maxv_idx = vels.index(max(vels))
maxv_t = times[maxv_idx]
maxv_val = vels[maxv_idx]
maxv_x = pad_l + (maxv_t / max_t) * plot_w
maxv_y = pad_t + plot_h - (maxv_val / max_vel) * plot_h

# 3. Parachute deployment (MET ~ 263.8 => t ~ 76s, alt ~ 1898m)
chute_idx = 0
for i in range(peak_idx, len(times)):
    if alts[i] < 2000.0:
        chute_idx = i
        break
chute_t = times[chute_idx]
chute_alt = alts[chute_idx]
chute_x = pad_l + (chute_t / max_t) * plot_w
chute_y = pad_t + plot_h - (chute_alt / max_alt) * plot_h

# Grid lines & ticks
grid_lines = []
for i in range(5):
    y = pad_t + (i / 4.0) * plot_h
    val_a = (1.0 - i / 4.0) * max_alt
    val_v = (1.0 - i / 4.0) * max_vel
    grid_lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
    grid_lines.append(f'<text x="{pad_l - 8}" y="{y + 4:.1f}" font-size="11" fill="#38bdf8" text-anchor="end" font-family="monospace">{val_a:.0f}m</text>')
    grid_lines.append(f'<text x="{w - pad_r + 8}" y="{y + 4:.1f}" font-size="11" fill="#f43f5e" text-anchor="start" font-family="monospace">{val_v:.0f}m/s</text>')

for i in range(6):
    x = pad_l + (i / 5.0) * plot_w
    val_t = (i / 5.0) * max_t
    grid_lines.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{h - pad_b}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
    grid_lines.append(f'<text x="{x:.1f}" y="{h - pad_b + 20}" font-size="11" fill="#94a3b8" text-anchor="middle" font-family="monospace">T+{val_t:.0f}s</text>')

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" style="background:#0b0f19; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">
  <rect width="{w}" height="{h}" fill="#0b0f19" rx="8"/>
  
  <!-- Title & Legend -->
  <text x="{pad_l}" y="26" font-size="14" font-weight="bold" fill="#f8fafc">CSA-02 «Corolt-Ib»: Complete Flight & Touchdown Profile</text>
  <circle cx="{w - 240}" cy="22" r="5" fill="#38bdf8"/>
  <text x="{w - 230}" y="26" font-size="12" fill="#38bdf8">Altitude (m)</text>
  <circle cx="{w - 120}" cy="22" r="5" fill="#f43f5e"/>
  <text x="{w - 110}" y="26" font-size="12" fill="#f43f5e">Velocity (m/s)</text>

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
  <circle cx="{peak_x:.1f}" cy="{peak_y:.1f}" r="4" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5"/>
  <text x="{peak_x + 10:.1f}" y="{peak_y - 8:.1f}" font-size="11" font-weight="bold" fill="#38bdf8" text-anchor="start">Apogee: {peak_alt:.0f}m (T+{peak_t:.0f}s)</text>

  <!-- Burnout / Max Speed Marker -->
  <circle cx="{maxv_x:.1f}" cy="{maxv_y:.1f}" r="4" fill="#f43f5e" stroke="#ffffff" stroke-width="1.5"/>
  <text x="{maxv_x + 10:.1f}" y="{maxv_y - 6:.1f}" font-size="10" font-weight="bold" fill="#f43f5e" text-anchor="start">Vmax: {maxv_val:.0f} m/s (T+{maxv_t:.0f}s)</text>

  <!-- Parachute Deployment Marker -->
  <circle cx="{chute_x:.1f}" cy="{chute_y:.1f}" r="4" fill="#10b981" stroke="#ffffff" stroke-width="1.5"/>
  <text x="{chute_x + 8:.1f}" y="{chute_y + 16:.1f}" font-size="11" font-weight="bold" fill="#10b981" text-anchor="start">Parachutes ({chute_alt:.0f}m)</text>

  <!-- Axis Titles -->
  <text x="{w / 2}" y="{h - 12}" font-size="12" fill="#94a3b8" text-anchor="middle">Flight Time Since Liftoff (s)</text>
  <text transform="rotate(-90)" x="{- (pad_t + plot_h/2)}" y="20" font-size="11" fill="#38bdf8" text-anchor="middle">Altitude (m)</text>
  <text transform="rotate(90)" x="{pad_t + plot_h/2}" y="{-w + 20}" font-size="11" fill="#f43f5e" text-anchor="middle">Velocity (m/s)</text>
</svg>
'''

with open(out_svg, 'w') as f:
    f.write(svg_content)

print(f"Generated {out_svg} successfully!")
