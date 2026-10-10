#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Multi-Chart Telemetry Analytics Generator for Mission CSA-11
Generates high-resolution standalone SVG engineering plots:
1. csa-11_advanced_dashboard.svg (6-Panel Comprehensive Flight Operations Deck)
2. csa-11_dynamic_pressure_plot.svg (Dynamic Pressure Q & Structural G Envelope)
3. csa-11_attitude_steering_plot.svg (Guidance Attitude, Pitch Law & Azimuth Lock)
"""

import csv
import math
import os

def load_flight_data():
    csv_file = "/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-11_telemetry.csv"
    with open(csv_file) as f:
        rows = list(csv.DictReader(f))

    # Detect liftoff MET
    t0 = None
    for r in rows:
        if float(r['altitude']) > 88.0 and float(r['MET']) > 800:
            t0 = float(r['MET']) - 1.0
            break

    if t0 is None:
        t0 = 834.7

    flight_rows = [r for r in rows if float(r['MET']) >= t0]

    # Stop after ground impact / vessel rest
    impact_idx = len(flight_rows) - 1
    for i, r in enumerate(flight_rows):
        t_flight = float(r['MET']) - t0
        alt = float(r['altitude'])
        if alt <= 833.0 and t_flight > 1378.0:
            impact_idx = i
            break

    flight_rows = flight_rows[:impact_idx + 1]

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
            lat = float(r['latitude'])
            lon = float(r['longitude'])
            data.append({
                't': t, 'alt': alt, 'spd': spd, 'v_spd': v_spd,
                'orb_v': orb_v, 'q': q, 'g': g,
                'pitch': pitch, 'hdg': hdg,
                'lat': lat, 'lon': lon
            })
        except (ValueError, TypeError):
            continue

    return data

def generate_flight_deck_dashboard(data, output_file):
    width, height = 1100, 780
    t_max = max(d['t'] for d in data)
    alt_max = max(d['alt'] for d in data) / 1000.0
    spd_max = max(d['spd'] for d in data)
    orb_max = max(d['orb_v'] for d in data)
    v_ceil = max(spd_max, orb_max)
    q_max = max(d['q'] for d in data)
    g_max = max(d['g'] for d in data)

    step = max(1, len(data) // 600)
    sampled = data[::step]
    if sampled[-1] != data[-1]:
        sampled.append(data[-1])

    panels = [
        {"x": 60, "y": 70, "w": 460, "h": 180, "title": "ALTITUDE PROFILE &amp; KARMAN CROSSING", "unit": "km"},
        {"x": 580, "y": 70, "w": 460, "h": 180, "title": "SURFACE &amp; ORBITAL VELOCITIES", "unit": "m/s"},
        {"x": 60, "y": 300, "w": 460, "h": 180, "title": "DYNAMIC PRESSURE (Q) ENVELOPE", "unit": "kPa"},
        {"x": 580, "y": 300, "w": 460, "h": 180, "title": "STRUCTURAL G-FORCE LOAD PROFILE", "unit": "g"},
        {"x": 60, "y": 530, "w": 460, "h": 180, "title": "GUIDANCE ATTITUDE (PITCH &amp; HEADING)", "unit": "deg"},
        {"x": 580, "y": 530, "w": 460, "h": 180, "title": "DOWNRANGE LONGITUDE PROGRESSION", "unit": "deg"}
    ]

    def scale_x(t, p): return p["x"] + (t / t_max) * p["w"]
    def scale_y(val, val_max, p): return p["y"] + p["h"] - (val / val_max) * p["h"]

    p1 = panels[0]
    p1_path = "M " + " ".join(f"{scale_x(d['t'], p1):.1f},{scale_y(d['alt']/1000.0, alt_max*1.08, p1):.1f}" for d in sampled)

    p2 = panels[1]
    p2_srf = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['spd'], v_ceil*1.08, p2):.1f}" for d in sampled)
    p2_orb = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['orb_v'], v_ceil*1.08, p2):.1f}" for d in sampled)

    p3 = panels[2]
    p3_path = "M " + " ".join(f"{scale_x(d['t'], p3):.1f},{scale_y(d['q'], q_max*1.15, p3):.1f}" for d in sampled)

    p4 = panels[3]
    p4_path = "M " + " ".join(f"{scale_x(d['t'], p4):.1f},{scale_y(d['g'], g_max*1.15, p4):.1f}" for d in sampled)

    p5 = panels[4]
    p5_pitch = "M " + " ".join(f"{scale_x(d['t'], p5):.1f},{scale_y(max(0, d['pitch']), 100.0, p5):.1f}" for d in sampled)

    p6 = panels[5]
    # Longitude starts at -74.56 and goes to +28.76
    lon_min = min(d['lon'] for d in data)
    lon_max = max(d['lon'] for d in data)
    lon_span = max(1.0, lon_max - lon_min)
    p6_path = "M " + " ".join(f"{scale_x(d['t'], p6):.1f},{scale_y(d['lon'] - lon_min, lon_span*1.1, p6):.1f}" for d in sampled)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#090d16; font-family:'Courier New', monospace;">
    <defs>
        <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#1e293b" stroke-width="0.7" opacity="0.4"/>
        </pattern>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="2.5" result="blur"/>
            <feComposite in="SourceGraphic" in2="blur" operator="over"/>
        </filter>
    </defs>

    <rect width="{width}" height="{height}" fill="url(#grid)" />

    <!-- Header Block -->
    <rect x="0" y="0" width="{width}" height="45" fill="#0f172a" />
    <text x="25" y="28" fill="#38bdf8" font-size="15" font-weight="bold">COROLT SPACE AGENCY // CSA-11 OPERATIONS DECK DASHBOARD</text>
    <text x="680" y="28" fill="#fbbf24" font-size="12" font-weight="bold">HISTORIC APOGEE: 269.1 KM // ENGINE ANOMALY RCA</text>

    <!-- 6 Panels -->
    <!-- Panel 1: Alt -->
    <rect x="{p1['x']}" y="{p1['y']}" width="{p1['w']}" height="{p1['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p1['x']+12}" y="{p1['y']+20}" fill="#38bdf8" font-size="11" font-weight="bold">{p1['title']}</text>
    <text x="{p1['x']+p1['w']-140}" y="{p1['y']+20}" fill="#94a3b8" font-size="10">Peak Apo: {alt_max:.2f} km</text>
    <line x1="{p1['x']}" y1="{scale_y(70, alt_max*1.08, p1):.1f}" x2="{p1['x']+p1['w']}" y2="{scale_y(70, alt_max*1.08, p1):.1f}" stroke="#a855f7" stroke-dasharray="3,3" stroke-width="1"/>
    <text x="{p1['x']+p1['w']-115}" y="{scale_y(70, alt_max*1.08, p1)-4:.1f}" fill="#a855f7" font-size="9">Kármán (70 km)</text>
    <path d="{p1_path}" fill="none" stroke="#38bdf8" stroke-width="2.5" filter="url(#glow)"/>

    <!-- Panel 2: Speeds -->
    <rect x="{p2['x']}" y="{p2['y']}" width="{p2['w']}" height="{p2['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p2['x']+12}" y="{p2['y']+20}" fill="#f43f5e" font-size="11" font-weight="bold">{p2['title']}</text>
    <text x="{p2['x']+p2['w']-160}" y="{p2['y']+20}" fill="#94a3b8" font-size="10">Max Orb: {orb_max:.1f} m/s</text>
    <path d="{p2_srf}" fill="none" stroke="#f43f5e" stroke-width="2.2" />
    <path d="{p2_orb}" fill="none" stroke="#38bdf8" stroke-width="1.5" stroke-dasharray="4,2"/>
    <text x="{p2['x']+15}" y="{p2['y']+p2['h']-12}" fill="#f43f5e" font-size="10">― Surface Vel ({spd_max:.0f} m/s)</text>
    <text x="{p2['x']+200}" y="{p2['y']+p2['h']-12}" fill="#38bdf8" font-size="10">-- Orbital Vel ({orb_max:.0f} m/s)</text>

    <!-- Panel 3: Q -->
    <rect x="{p3['x']}" y="{p3['y']}" width="{p3['w']}" height="{p3['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p3['x']+12}" y="{p3['y']+20}" fill="#f59e0b" font-size="11" font-weight="bold">{p3['title']}</text>
    <text x="{p3['x']+p3['w']-160}" y="{p3['y']+20}" fill="#94a3b8" font-size="10">Ascent: 17.8 | Entry: {q_max:.1f} kPa</text>
    <path d="{p3_path}" fill="none" stroke="#f59e0b" stroke-width="2.2" />

    <!-- Panel 4: G -->
    <rect x="{p4['x']}" y="{p4['y']}" width="{p4['w']}" height="{p4['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p4['x']+12}" y="{p4['y']+20}" fill="#a855f7" font-size="11" font-weight="bold">{p4['title']}</text>
    <text x="{p4['x']+p4['w']-150}" y="{p4['y']+20}" fill="#94a3b8" font-size="10">Ascent: 3.32 | Entry: {g_max:.2f} G</text>
    <path d="{p4_path}" fill="none" stroke="#a855f7" stroke-width="2.2" />

    <!-- Panel 5: Attitude -->
    <rect x="{p5['x']}" y="{p5['y']}" width="{p5['w']}" height="{p5['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p5['x']+12}" y="{p5['y']+20}" fill="#10b981" font-size="11" font-weight="bold">{p5['title']}</text>
    <text x="{p5['x']+p5['w']-160}" y="{p5['y']+20}" fill="#94a3b8" font-size="10">Azimuth: 90.0º East (Inc 0.09º)</text>
    <path d="{p5_pitch}" fill="none" stroke="#10b981" stroke-width="2.2" />
    <text x="{p5['x']+15}" y="{p5['y']+p5['h']-12}" fill="#10b981" font-size="10">Guided Pitch Arc (84.0º Kick -> 15.0º MECO)</text>

    <!-- Panel 6: Ground Track -->
    <rect x="{p6['x']}" y="{p6['y']}" width="{p6['w']}" height="{p6['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p6['x']+12}" y="{p6['y']+20}" fill="#22c55e" font-size="11" font-weight="bold">{p6['title']}</text>
    <text x="{p6['x']+p6['w']-180}" y="{p6['y']+20}" fill="#22c55e" font-size="10">Downrange: 1,082 km (+103.3º E)</text>
    <path d="{p6_path}" fill="none" stroke="#22c55e" stroke-width="2.2" />
    <text x="{p6['x']+15}" y="{p6['y']+p6['h']-12}" fill="#22c55e" font-size="10">Equatorial Transit (Lon -74.56º -> +28.76º)</text>

    <!-- Footer timestamp -->
    <text x="25" y="{height-15}" fill="#64748b" font-size="10">CSA TELEMETRY RECORDER // MET RECORDED: {t_max:.1f}s ({t_max/60:.2f} min) // 2909 FLIGHT SAMPLES</text>
    <text x="{width-320}" y="{height-15}" fill="#64748b" font-size="10">COROLT SPACE AGENCY // AD ASTRA PER SCIENTIAM</text>
</svg>"""

    with open(output_file, 'w') as f:
        f.write(svg)
    print(f"[✓] Generated: {output_file}")

def generate_dynamic_pressure_plot(data, output_file):
    width, height = 880, 420
    pad_l, pad_r, pad_t, pad_b = 80, 80, 50, 60
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    t_max = max(d['t'] for d in data)
    q_max = max(d['q'] for d in data) * 1.15
    g_max = max(d['g'] for d in data) * 1.15

    step = max(1, len(data) // 400)
    sampled = data[::step]

    pts_q = []
    pts_g = []
    for d in sampled:
        x = pad_l + (d['t'] / t_max) * plot_w
        y_q = pad_t + plot_h - (d['q'] / q_max) * plot_h
        y_g = pad_t + plot_h - (d['g'] / g_max) * plot_h
        pts_q.append(f"{x:.1f},{y_q:.1f}")
        pts_g.append(f"{x:.1f},{y_g:.1f}")

    str_q = " ".join(pts_q)
    str_g = " ".join(pts_g)

    # Grid
    grid_lines = []
    for i in range(6):
        y = pad_t + (i / 5.0) * plot_h
        val_q = (1.0 - i / 5.0) * q_max
        val_g = (1.0 - i / 5.0) * g_max
        grid_lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - pad_r}" y2="{y:.1f}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
        grid_lines.append(f'<text x="{pad_l - 10}" y="{y + 4:.1f}" font-size="11" fill="#f59e0b" text-anchor="end" font-family="monospace">{val_q:.0f} kPa</text>')
        grid_lines.append(f'<text x="{width - pad_r + 10}" y="{y + 4:.1f}" font-size="11" fill="#a855f7" text-anchor="start" font-family="monospace">{val_g:.1f} G</text>')

    for i in range(7):
        x = pad_l + (i / 6.0) * plot_w
        val_t = (i / 6.0) * t_max
        grid_lines.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{height - pad_b}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
        grid_lines.append(f'<text x="{x:.1f}" y="{height - pad_b + 20}" font-size="11" fill="#94a3b8" text-anchor="middle" font-family="monospace">T+{val_t:.0f}s</text>')

    grid_svg = "\n    ".join(grid_lines)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0b101b; font-family:'Courier New', monospace;">
    <!-- Title -->
    <text x="{width/2}" y="28" font-size="14" fill="#f1f5f9" font-weight="bold" text-anchor="middle">CSA-11: DYNAMIC PRESSURE (Q) &amp; ACCELERATION LOAD ENVELOPE</text>

    <!-- Legend -->
    <line x1="{pad_l}" y1="40" x2="{pad_l+30}" y2="40" stroke="#f59e0b" stroke-width="2.5"/>
    <text x="{pad_l+36}" y="44" font-size="11" fill="#f59e0b">Dynamic Pressure Q (kPa)</text>
    <line x1="{width-pad_r-160}" y1="40" x2="{width-pad_r-130}" y2="40" stroke="#a855f7" stroke-width="2.5"/>
    <text x="{width-pad_r-124}" y="44" font-size="11" fill="#a855f7">Acceleration (G-Force)</text>

    {grid_svg}

    <polyline fill="none" stroke="#f59e0b" stroke-width="2.2" points="{str_q}"/>
    <polyline fill="none" stroke="#a855f7" stroke-width="2.2" points="{str_g}"/>

    <!-- Markers -->
    <circle cx="{pad_l + (62.0/t_max)*plot_w:.1f}" cy="{pad_t + plot_h - (17.77/q_max)*plot_h:.1f}" r="4" fill="#f59e0b"/>
    <text x="{pad_l + (62.0/t_max)*plot_w + 8:.1f}" y="{pad_t + plot_h - (17.77/q_max)*plot_h - 8:.1f}" font-size="10" fill="#f59e0b">Ascent Max Q: 17.8 kPa (T+62s)</text>

    <circle cx="{pad_l + (1306.2/t_max)*plot_w:.1f}" cy="{pad_t + plot_h - (64.29/q_max)*plot_h:.1f}" r="4" fill="#ef4444"/>
    <text x="{pad_l + (1306.2/t_max)*plot_w - 10:.1f}" y="{pad_t + plot_h - (64.29/q_max)*plot_h - 10:.1f}" font-size="10" fill="#ef4444" text-anchor="end">Re-entry Peak Q: 64.3 kPa (T+1306s)</text>
</svg>"""

    with open(output_file, 'w') as f:
        f.write(svg)
    print(f"[✓] Generated: {output_file}")

def generate_attitude_steering_plot(data, output_file):
    width, height = 880, 420
    pad_l, pad_r, pad_t, pad_b = 80, 80, 50, 60
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    t_max = max(d['t'] for d in data)

    step = max(1, len(data) // 400)
    sampled = data[::step]

    pts_pitch = []
    pts_hdg = []
    for d in sampled:
        x = pad_l + (d['t'] / t_max) * plot_w
        y_pitch = pad_t + plot_h - (max(0, d['pitch']) / 100.0) * plot_h
        y_hdg = pad_t + plot_h - (d['hdg'] / 360.0) * plot_h
        pts_pitch.append(f"{x:.1f},{y_pitch:.1f}")
        pts_hdg.append(f"{x:.1f},{y_hdg:.1f}")

    str_pitch = " ".join(pts_pitch)
    str_hdg = " ".join(pts_hdg)

    grid_lines = []
    for i in range(6):
        y = pad_t + (i / 5.0) * plot_h
        val_pitch = (1.0 - i / 5.0) * 100.0
        val_hdg = (1.0 - i / 5.0) * 360.0
        grid_lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{width - pad_r}" y2="{y:.1f}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
        grid_lines.append(f'<text x="{pad_l - 10}" y="{y + 4:.1f}" font-size="11" fill="#10b981" text-anchor="end" font-family="monospace">{val_pitch:.0f}º</text>')
        grid_lines.append(f'<text x="{width - pad_r + 10}" y="{y + 4:.1f}" font-size="11" fill="#38bdf8" text-anchor="start" font-family="monospace">{val_hdg:.0f}º</text>')

    for i in range(7):
        x = pad_l + (i / 6.0) * plot_w
        val_t = (i / 6.0) * t_max
        grid_lines.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{height - pad_b}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
        grid_lines.append(f'<text x="{x:.1f}" y="{height - pad_b + 20}" font-size="11" fill="#94a3b8" text-anchor="middle" font-family="monospace">T+{val_t:.0f}s</text>')

    grid_svg = "\n    ".join(grid_lines)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0b101b; font-family:'Courier New', monospace;">
    <text x="{width/2}" y="28" font-size="14" fill="#f1f5f9" font-weight="bold" text-anchor="middle">CSA-11: GUIDANCE ATTITUDE (PITCH LAW &amp; COMPASS AZIMUTH)</text>

    <!-- Legend -->
    <line x1="{pad_l}" y1="40" x2="{pad_l+30}" y2="40" stroke="#10b981" stroke-width="2.5"/>
    <text x="{pad_l+36}" y="44" font-size="11" fill="#10b981">Pitch Angle (0º to 90º)</text>
    <line x1="{width-pad_r-160}" y1="40" x2="{width-pad_r-130}" y2="40" stroke="#38bdf8" stroke-width="2.5"/>
    <text x="{width-pad_r-124}" y="44" font-size="11" fill="#38bdf8">Heading Azimuth (0º to 360º)</text>

    {grid_svg}

    <polyline fill="none" stroke="#10b981" stroke-width="2.2" points="{str_pitch}"/>
    <polyline fill="none" stroke="#38bdf8" stroke-width="2.2" points="{str_hdg}"/>

    <!-- Markers -->
    <circle cx="{pad_l + (20.5/t_max)*plot_w:.1f}" cy="{pad_t + plot_h - (84.0/100.0)*plot_h:.1f}" r="4" fill="#10b981"/>
    <text x="{pad_l + (20.5/t_max)*plot_w + 8:.1f}" y="{pad_t + plot_h - (84.0/100.0)*plot_h - 6:.1f}" font-size="10" fill="#10b981">Kick to 84.0º (T+20s)</text>

    <circle cx="{pad_l + (125.1/t_max)*plot_w:.1f}" cy="{pad_t + plot_h - (19.4/100.0)*plot_h:.1f}" r="4" fill="#10b981"/>
    <text x="{pad_l + (125.1/t_max)*plot_w + 8:.1f}" y="{pad_t + plot_h - (19.4/100.0)*plot_h + 14:.1f}" font-size="10" fill="#10b981">MECO Pitch: 19.4º (T+125s)</text>
</svg>"""

    with open(output_file, 'w') as f:
        f.write(svg)
    print(f"[✓] Generated: {output_file}")

def main():
    data = load_flight_data()
    print(f"Loaded {len(data)} flight points from CSA-11 telemetry.")
    assets_dir = "/home/pablo-cortes/Documents/Corolt_Space_Agency/assets"
    
    generate_flight_deck_dashboard(data, os.path.join(assets_dir, "csa-11_advanced_dashboard.svg"))
    generate_dynamic_pressure_plot(data, os.path.join(assets_dir, "csa-11_dynamic_pressure_plot.svg"))
    generate_attitude_steering_plot(data, os.path.join(assets_dir, "csa-11_attitude_steering_plot.svg"))

if __name__ == "__main__":
    main()
