import csv
import os

csv_path = '/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/Corolt-I_telemetry.csv'
out_svg = '/home/pablo-cortes/Documents/Corolt_Space_Agency/assets/csa-01_telemetry_plot.svg'

with open(csv_path, 'r') as f:
    rows = list(csv.DictReader(f))

times = [float(r['MET']) for r in rows]
alts = [float(r['altitude']) for r in rows]
vels = [float(r['surface_vel']) for r in rows]
gs = [float(r['g_force']) for r in rows]

# Downsample for SVG if needed (492 points is small and fine)
w = 800
h = 360
pad_l = 65
pad_r = 65
pad_t = 40
pad_b = 45

plot_w = w - pad_l - pad_r
plot_h = h - pad_t - pad_b

max_t = max(times) or 1.0
max_alt = max(alts) or 1.0
max_vel = max(vels) or 1.0

# Generate polyline points
pts_alt = []
pts_vel = []

for t, a, v in zip(times, alts, vels):
    x = pad_l + (t / max_t) * plot_w
    y_alt = pad_t + plot_h - (a / max_alt) * plot_h
    y_vel = pad_t + plot_h - (v / max_vel) * plot_h
    pts_alt.append(f"{x:.1f},{y_alt:.1f}")
    pts_vel.append(f"{x:.1f},{y_vel:.1f}")

str_alt = " ".join(pts_alt)
str_vel = " ".join(pts_vel)

# Grid lines
grid_lines = []
for i in range(5):
    y = pad_t + (i / 4.0) * plot_h
    grid_lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>')
    val_a = (1.0 - i / 4.0) * max_alt
    val_v = (1.0 - i / 4.0) * max_vel
    grid_lines.append(f'<text x="{pad_l - 8}" y="{y + 4:.1f}" font-size="11" fill="#38bdf8" text-anchor="end" font-family="monospace">{val_a:.0f}m</text>')
    grid_lines.append(f'<text x="{w - pad_r + 8}" y="{y + 4:.1f}" font-size="11" fill="#f43f5e" text-anchor="start" font-family="monospace">{val_v:.0f}m/s</text>')

# Time axis labels
for i in range(6):
    x = pad_l + (i / 5.0) * plot_w
    val_t = (i / 5.0) * max_t
    grid_lines.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{h - pad_b}" stroke="#334155" stroke-dasharray="3,3" stroke-width="1"/>')
    grid_lines.append(f'<text x="{x:.1f}" y="{h - pad_b + 18}" font-size="11" fill="#94a3b8" text-anchor="middle" font-family="monospace">{val_t:.0f}s</text>')

svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" style="background:#0f172a; border-radius: 8px; font-family: sans-serif;">
  <rect width="{w}" height="{h}" fill="#0b0f19" rx="8"/>
  
  <!-- Title & Legend -->
  <text x="{pad_l}" y="25" font-size="14" font-weight="bold" fill="#f8fafc">CSA-01: Perfil de Vol Telemetrat (Altitud vs Velocitat)</text>
  <circle cx="{w - 220}" cy="20" r="5" fill="#38bdf8"/>
  <text x="{w - 210}" y="24" font-size="12" fill="#38bdf8">Altitud (m)</text>
  <circle cx="{w - 110}" cy="20" r="5" fill="#f43f5e"/>
  <text x="{w - 100}" y="24" font-size="12" fill="#f43f5e">Velocitat (m/s)</text>

  <!-- Grid & Ticks -->
  {"".join(grid_lines)}

  <!-- Axes -->
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" stroke="#64748b" stroke-width="1.5"/>
  <line x1="{w - pad_r}" y1="{pad_t}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#64748b" stroke-width="1.5"/>
  <line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#64748b" stroke-width="1.5"/>

  <!-- Plot curves -->
  <polyline fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" points="{str_alt}"/>
  <polyline fill="none" stroke="#f43f5e" stroke-width="2" stroke-linecap="round" points="{str_vel}"/>

  <!-- Axis Titles -->
  <text x="{w / 2}" y="{h - 10}" font-size="12" fill="#94a3b8" text-anchor="middle">Temps de Missió Transcorregut (MET) en segons</text>
</svg>
'''

with open(out_svg, 'w') as f:
    f.write(svg_content)

print(f"Generated {out_svg} successfully!")
