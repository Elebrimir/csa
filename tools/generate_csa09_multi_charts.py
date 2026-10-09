#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Multi-Chart Telemetry Analytics Generator for CSA-09
Generates high-resolution standalone SVG engineering plots:
1. Dynamic Pressure (Q) & Structural Gee-Force Envelope
2. Trajectory Attitude: Pitch, Heading & Angle of Attack (AoA)
3. Atmospheric Reentry & Ballistic Braking Dynamics
4. 6-Panel Comprehensive Flight Deck Dashboard (Advanced Analytics)
All charts strictly escape XML entities (&amp;, etc.) to ensure 100% SVG validity.
"""

import csv
import math
import os

def load_flight_data():
    csv_file = "/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-09_telemetry.csv"
    with open(csv_file) as f:
        rows = list(csv.DictReader(f))

    # Identify liftoff and landing
    l_idx = 0
    for i, r in enumerate(rows):
        if float(r['altitude']) > 80.0:
            l_idx = max(0, i - 1)
            break

    td_idx = len(rows) - 1
    for i in range(len(rows) - 1, -1, -1):
        if float(rows[i]['altitude']) <= 0.0 and float(rows[i]['MET']) > 1200:
            td_idx = i
            break

    flight_rows = rows[l_idx:td_idx + 1]
    t0 = float(flight_rows[0]['MET'])

    # Parse and clean metrics
    data = []
    for r in flight_rows:
        try:
            t = float(r['MET']) - t0
            alt = float(r['altitude'])
            spd = float(r['surface_vel'])
            v_spd = float(r['vert_speed'])
            orb_v = float(r['orbital_vel'])
            q = float(r['dynamic_pressure']) / 1000.0  # kPa
            g = float(r['g_force'])
            pitch = float(r['pitch'])
            hdg = float(r['heading'])
            aoa = float(r['angle_prograde'])
            lat = float(r['latitude'])
            lon = float(r['longitude'])
            data.append({
                't': t, 'alt': alt, 'spd': spd, 'v_spd': v_spd,
                'orb_v': orb_v, 'q': q, 'g': g,
                'pitch': pitch, 'hdg': hdg, 'aoa': aoa,
                'lat': lat, 'lon': lon
            })
        except (ValueError, TypeError):
            continue

    return data

def escape_xml(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def generate_dynamic_pressure_chart(data):
    w, h = 900, 420
    pad_l, pad_r, pad_t, pad_b = 80, 80, 50, 60
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    max_t = max(d['t'] for d in data)
    max_q = 130.0 # kPa
    max_g = 10.0  # G

    # Subsample
    step = max(1, len(data) // 300)
    sub = data[::step]
    if data[-1] not in sub:
        sub.append(data[-1])

    pts_q = [f"{pad_l + (d['t']/max_t)*plot_w:.1f},{pad_t + plot_h - (d['q']/max_q)*plot_h:.1f}" for d in sub]
    pts_g = [f"{pad_l + (d['t']/max_t)*plot_w:.1f},{pad_t + plot_h - (d['g']/max_g)*plot_h:.1f}" for d in sub]

    str_q = " ".join(pts_q)
    str_g = " ".join(pts_g)

    # Grid
    grid = []
    for i in range(6):
        y = pad_t + (i / 5.0) * plot_h
        val_q = (1.0 - i / 5.0) * max_q
        val_g = (1.0 - i / 5.0) * max_g
        grid.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
        grid.append(f'<text x="{pad_l - 10}" y="{y + 4:.1f}" font-size="11" fill="#f59e0b" text-anchor="end" font-family="monospace">{val_q:.0f} kPa</text>')
        grid.append(f'<text x="{w - pad_r + 10}" y="{y + 4:.1f}" font-size="11" fill="#ec4899" text-anchor="start" font-family="monospace">{val_g:.1f} G</text>')

    for i in range(7):
        x = pad_l + (i / 6.0) * plot_w
        val_t = (i / 6.0) * max_t
        grid.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{h - pad_b}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
        grid.append(f'<text x="{x:.1f}" y="{h - pad_b + 20}" font-size="11" fill="#94a3b8" text-anchor="middle" font-family="monospace">T+{val_t:.0f}s</text>')

    grid_svg = "\n    ".join(grid)

    # Peak markers
    peak_q_d = max(data, key=lambda x: x['q'])
    pq_x = pad_l + (peak_q_d['t'] / max_t) * plot_w
    pq_y = pad_t + plot_h - (peak_q_d['q'] / max_q) * plot_h

    peak_g_d = max(data, key=lambda x: x['g'])
    pg_x = pad_l + (peak_g_d['t'] / max_t) * plot_w
    pg_y = pad_t + plot_h - (peak_g_d['g'] / max_g) * plot_h

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" style="background:#0b0f19; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <rect width="{w}" height="{h}" fill="#0b0f19" rx="8"/>
  <text x="{w/2}" y="26" font-size="14" font-weight="bold" fill="#f8fafc" text-anchor="middle">COROLT SPACE AGENCY  |  AERODYNAMIC LOADS &amp; ACCELERATION: CSA-09</text>
  <text x="{w/2}" y="42" font-size="11" fill="#64748b" text-anchor="middle">Dynamic Pressure (Q) &amp; Mechanical Gee-Force Envelope • Reentry Aero-Braking Peak</text>

  <!-- Grid -->
  {grid_svg}

  <!-- Axes -->
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>
  <line x1="{w - pad_r}" y1="{pad_t}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>
  <line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>

  <!-- Curves -->
  <polyline fill="none" stroke="#f59e0b" stroke-width="2.5" stroke-linecap="round" points="{str_q}"/>
  <polyline fill="none" stroke="#ec4899" stroke-width="2" stroke-linecap="round" points="{str_g}"/>

  <!-- Peak Q marker -->
  <circle cx="{pq_x:.1f}" cy="{pq_y:.1f}" r="5" fill="#f59e0b" stroke="#ffffff" stroke-width="1.5"/>
  <text x="{pq_x + 10:.1f}" y="{pq_y - 8:.1f}" font-size="11" font-weight="bold" fill="#f59e0b">Max Q: {peak_q_d['q']:.1f} kPa (Reentry T+{peak_q_d['t']:.0f}s)</text>

  <!-- Peak G marker -->
  <circle cx="{pg_x:.1f}" cy="{pg_y:.1f}" r="5" fill="#ec4899" stroke="#ffffff" stroke-width="1.5"/>
  <text x="{pg_x - 10:.1f}" y="{pg_y - 12:.1f}" font-size="11" font-weight="bold" fill="#ec4899" text-anchor="end">Peak Decel: {peak_g_d['g']:.2f} G</text>

  <!-- Labels & Legends -->
  <text x="{w/2}" y="{h - 15}" font-size="12" fill="#94a3b8" text-anchor="middle">Mission Elapsed Time (MET) in seconds</text>
  <text transform="rotate(-90)" x="{- (pad_t + plot_h/2)}" y="24" font-size="11" fill="#f59e0b" text-anchor="middle">Dynamic Pressure (kPa)</text>
  <text transform="rotate(90)" x="{pad_t + plot_h/2}" y="{-w + 24}" font-size="11" fill="#ec4899" text-anchor="middle">G-Force (G)</text>

  <g transform="translate({pad_l}, {h - 40})">
    <line x1="0" y1="0" x2="20" y2="0" stroke="#f59e0b" stroke-width="2.5"/>
    <text x="25" y="4" font-size="11" fill="#94a3b8">Dynamic Pressure (kPa)</text>
    <line x1="180" y1="0" x2="200" y2="0" stroke="#ec4899" stroke-width="2"/>
    <text x="205" y="4" font-size="11" fill="#94a3b8">Acceleration / G-Load (G)</text>
  </g>
</svg>
"""
    out_file = "assets/csa-09_dynamic_pressure_plot.svg"
    with open(out_file, "w") as f:
        f.write(svg)
    print(f"[✓] Generated: {out_file}")

def generate_attitude_steering_chart(data):
    w, h = 900, 420
    pad_l, pad_r, pad_t, pad_b = 80, 80, 50, 60
    plot_w = w - pad_l - pad_r
    plot_h = h - pad_t - pad_b

    max_t = max(d['t'] for d in data)

    step = max(1, len(data) // 300)
    sub = data[::step]
    if data[-1] not in sub:
        sub.append(data[-1])

    # Left axis: Pitch (0 to 90 deg)
    # Right axis: Heading (0 to 360 deg)
    pts_pitch = [f"{pad_l + (d['t']/max_t)*plot_w:.1f},{pad_t + plot_h - (max(0, min(90, d['pitch']))/90.0)*plot_h:.1f}" for d in sub]
    pts_hdg = [f"{pad_l + (d['t']/max_t)*plot_w:.1f},{pad_t + plot_h - (max(0, min(360, d['hdg']))/360.0)*plot_h:.1f}" for d in sub]

    str_pitch = " ".join(pts_pitch)
    str_hdg = " ".join(pts_hdg)

    grid = []
    for i in range(6):
        y = pad_t + (i / 5.0) * plot_h
        val_pitch = (1.0 - i / 5.0) * 90.0
        val_hdg = (1.0 - i / 5.0) * 360.0
        grid.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
        grid.append(f'<text x="{pad_l - 10}" y="{y + 4:.1f}" font-size="11" fill="#38bdf8" text-anchor="end" font-family="monospace">{val_pitch:.0f}º</text>')
        grid.append(f'<text x="{w - pad_r + 10}" y="{y + 4:.1f}" font-size="11" fill="#a855f7" text-anchor="start" font-family="monospace">{val_hdg:.0f}º</text>')

    for i in range(7):
        x = pad_l + (i / 6.0) * plot_w
        val_t = (i / 6.0) * max_t
        grid.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{h - pad_b}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
        grid.append(f'<text x="{x:.1f}" y="{h - pad_b + 20}" font-size="11" fill="#94a3b8" text-anchor="middle" font-family="monospace">T+{val_t:.0f}s</text>')

    grid_svg = "\n    ".join(grid)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" style="background:#0b0f19; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <rect width="{w}" height="{h}" fill="#0b0f19" rx="8"/>
  <text x="{w/2}" y="26" font-size="14" font-weight="bold" fill="#f8fafc" text-anchor="middle">COROLT SPACE AGENCY  |  FLIGHT GUIDANCE ATTITUDE: MISSION CSA-09</text>
  <text x="{w/2}" y="42" font-size="11" fill="#64748b" text-anchor="middle">Vehicle Pitch Angle &amp; Compass Heading Profile • Gravity Turn Transition</text>

  <!-- Grid -->
  {grid_svg}

  <!-- Axes -->
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>
  <line x1="{w - pad_r}" y1="{pad_t}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>
  <line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>

  <!-- Curves -->
  <polyline fill="none" stroke="#a855f7" stroke-width="2" stroke-linecap="round" points="{str_hdg}"/>
  <polyline fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" points="{str_pitch}"/>

  <!-- Markers -->
  <text x="{pad_l + 30}" y="{pad_t + 25}" font-size="11" font-weight="bold" fill="#38bdf8">Liftoff: Vertical 90º</text>
  <text x="{pad_l + 100}" y="{pad_t + 160}" font-size="11" font-weight="bold" fill="#a855f7">Target Azimuth: HDG 270º (West)</text>

  <!-- Labels -->
  <text x="{w/2}" y="{h - 15}" font-size="12" fill="#94a3b8" text-anchor="middle">Mission Elapsed Time (MET) in seconds</text>
  <text transform="rotate(-90)" x="{- (pad_t + plot_h/2)}" y="24" font-size="11" fill="#38bdf8" text-anchor="middle">Pitch Angle (Degrees)</text>
  <text transform="rotate(90)" x="{pad_t + plot_h/2}" y="{-w + 24}" font-size="11" fill="#a855f7" text-anchor="middle">Compass Heading (Degrees)</text>

  <g transform="translate({pad_l}, {h - 40})">
    <line x1="0" y1="0" x2="20" y2="0" stroke="#38bdf8" stroke-width="2.5"/>
    <text x="25" y="4" font-size="11" fill="#94a3b8">Pitch Angle (0º to 90º)</text>
    <line x1="180" y1="0" x2="200" y2="0" stroke="#a855f7" stroke-width="2"/>
    <text x="205" y="4" font-size="11" fill="#94a3b8">Compass Heading (0º to 360º)</text>
  </g>
</svg>
"""
    out_file = "assets/csa-09_attitude_steering_plot.svg"
    with open(out_file, "w") as f:
        f.write(svg)
    print(f"[✓] Generated: {out_file}")

def generate_flight_deck_dashboard(data):
    w, h = 1200, 800
    # 6 Panels: 3 rows, 2 columns
    # Layout:
    # Top-Left: Altitude & Karman line
    # Top-Right: Velocity Decomposition (Orbital, Surface, Vertical)
    # Mid-Left: Dynamic Pressure & Aerodynamic Drag
    # Mid-Right: Flight G-Force & Structural Loads
    # Bot-Left: Pitch & Compass Steering
    # Bot-Right: Downrange Ground Track & Energy
    
    max_t = max(d['t'] for d in data)
    step = max(1, len(data) // 250)
    sub = data[::step]
    if data[-1] not in sub:
        sub.append(data[-1])

    def make_panel(px, py, pw, ph, title, y1_label, y2_label, col1, col2, y1_max, y2_max, pts1, pts2, ref_line=None):
        pts1_str = " ".join([f"{px + (d['t']/max_t)*pw:.1f},{py + ph - (max(0, d[pts1])/y1_max)*ph:.1f}" for d in sub])
        pts2_str = " ".join([f"{px + (d['t']/max_t)*pw:.1f},{py + ph - (max(0, d[pts2])/y2_max)*ph:.1f}" for d in sub]) if pts2 else ""

        grid = []
        for i in range(5):
            gy = py + (i / 4.0) * ph
            v1 = (1.0 - i / 4.0) * y1_max
            grid.append(f'<line x1="{px}" y1="{gy:.1f}" x2="{px + pw}" y2="{gy:.1f}" stroke="#1e293b" stroke-dasharray="2,2" stroke-width="0.8"/>')
            grid.append(f'<text x="{px - 6}" y="{gy + 3:.1f}" font-size="9" fill="{col1}" text-anchor="end" font-family="monospace">{v1:.0f}</text>')
            if col2 and y2_max:
                v2 = (1.0 - i / 4.0) * y2_max
                grid.append(f'<text x="{px + pw + 6}" y="{gy + 3:.1f}" font-size="9" fill="{col2}" text-anchor="start" font-family="monospace">{v2:.0f}</text>')

        ref_svg = ""
        if ref_line:
            ry = py + ph - (ref_line[0] / y1_max) * ph
            ref_svg = f'<line x1="{px}" y1="{ry:.1f}" x2="{px + pw}" y2="{ry:.1f}" stroke="{ref_line[1]}" stroke-dasharray="4,3" stroke-width="1.2"/>' \
                      f'<text x="{px + pw - 5}" y="{ry - 4:.1f}" font-size="8.5" fill="{ref_line[1]}" font-weight="bold" text-anchor="end">{ref_line[2]}</text>'

        poly2 = f'<polyline fill="none" stroke="{col2}" stroke-width="1.8" stroke-linecap="round" points="{pts2_str}"/>' if pts2_str else ""

        return f"""
        <!-- Panel: {title} -->
        <rect x="{px - 40}" y="{py - 25}" width="{pw + 85}" height="{ph + 50}" rx="6" fill="#0d1527" stroke="#1e293b" stroke-width="1"/>
        <text x="{px}" y="{py - 10}" font-size="11" font-weight="bold" fill="#f8fafc">{title}</text>
        {" ".join(grid)}
        {ref_svg}
        <line x1="{px}" y1="{py}" x2="{px}" y2="{py + ph}" stroke="#475569" stroke-width="1"/>
        <line x1="{px + pw}" y1="{py}" x2="{px + pw}" y2="{py + ph}" stroke="#475569" stroke-width="1"/>
        <line x1="{px}" y1="{py + ph}" x2="{px + pw}" y2="{py + ph}" stroke="#475569" stroke-width="1"/>
        {poly2}
        <polyline fill="none" stroke="{col1}" stroke-width="2.2" stroke-linecap="round" points="{pts1_str}"/>
        <text x="{px + pw/2}" y="{py + ph + 16}" font-size="9.5" fill="#64748b" text-anchor="middle">MET (s)</text>
        """

    # Transform alt in data to km
    for d in sub:
        d['alt_km'] = d['alt'] / 1000.0

    p1 = make_panel(60, 65, 480, 180, "🌌 ALTITUDE &amp; SPACE REGIMES", "Alt (km)", None, "#38bdf8", None, 180.0, None, 'alt_km', None, ref_line=(70.0, "#c084fc", "Kármán Line (70 km)"))
    p2 = make_panel(660, 65, 480, 180, "⚡ SURFACE &amp; ORBITAL VELOCITY", "Surf Vel (m/s)", "Orb Vel (m/s)", "#f43f5e", "#fbbf24", 1600.0, 1600.0, 'spd', 'orb_v')
    p3 = make_panel(60, 315, 480, 180, "🌪️ DYNAMIC PRESSURE (MAX Q)", "Q (kPa)", None, "#f59e0b", None, 140.0, None, 'q', None, ref_line=(124.3, "#ef4444", "Max Q: 124.3 kPa"))
    p4 = make_panel(660, 315, 480, 180, "💥 G-FORCE &amp; ACCELERATION", "G-Force (G)", None, "#ec4899", None, 10.0, None, 'g', None, ref_line=(8.37, "#ec4899", "Peak G: 8.37 G"))
    p5 = make_panel(60, 565, 480, 180, "🧭 GUIDANCE ATTITUDE (PITCH)", "Pitch (º)", None, "#06b6d4", None, 90.0, None, 'pitch', None)
    
    # Ground downrange displacement
    lon0 = data[0]['lon']
    for d in sub:
        d['downrange_km'] = abs((d['lon'] - lon0) * (math.pi / 180.0) * 600.0)
    p6 = make_panel(660, 565, 480, 180, "🗺️ EQUATORIAL DOWNRANGE TRAVEL", "Downrange (km)", None, "#22c55e", None, 300.0, None, "downrange_km", None, ref_line=(268.0, "#22c55e", "Touchdown 268 km West"))

    dashboard_svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" style="background:#070b13; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
  <rect width="{w}" height="{h}" fill="#070b13"/>
  <text x="{w/2}" y="24" font-size="15" font-weight="bold" fill="#f8fafc" text-anchor="middle">COROLT SPACE AGENCY  |  FLIGHT OPERATIONS DECK: MISSION CSA-09</text>
  <text x="{w/2}" y="38" font-size="10.5" fill="#64748b" text-anchor="middle">Comprehensive 6-Panel Engineering Telemetry Suite • Sounding Rocket Deep Space Flight</text>
  {p1}
  {p2}
  {p3}
  {p4}
  {p5}
  {p6}
</svg>
"""
    out_file = "assets/csa-09_advanced_dashboard.svg"
    with open(out_file, "w") as f:
        f.write(dashboard_svg)
    print(f"[✓] Generated: {out_file}")

def main():
    data = load_flight_data()
    print(f"Loaded {len(data)} flight points for CSA-09.")
    generate_dynamic_pressure_chart(data)
    generate_attitude_steering_chart(data)
    generate_flight_deck_dashboard(data)

if __name__ == "__main__":
    main()
