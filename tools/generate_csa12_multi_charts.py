#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Multi-Chart Telemetry Analytics Generator for Mission CSA-12
Generates high-resolution standalone SVG engineering plots:
1. csa-12_advanced_dashboard.svg (6-Panel Comprehensive Flight Operations Deck)
2. csa-12_dynamic_pressure_plot.svg (Dynamic Pressure Q & Structural G Envelope)
3. csa-12_attitude_steering_plot.svg (Guidance Attitude, Pitch Law & Azimuth Lock)
"""

import csv
import math
import os

def load_flight_data():
    csv_file = "/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-12_telemetry.csv"
    with open(csv_file) as f:
        rows = list(csv.DictReader(f))

    # Detect liftoff MET
    t0 = 370.7

    flight_rows = [r for r in rows if float(r['MET']) >= t0]

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
            ap = float(r['apoapsis']) if r['apoapsis'] else 0.0
            pe = float(r['periapsis']) if r['periapsis'] else 0.0
            ecc = float(r['eccentricity']) if r['eccentricity'] else 0.0
            th = float(r['throttle']) if r['throttle'] else 0.0
            data.append({
                't': t, 'alt': alt, 'spd': spd, 'v_spd': v_spd,
                'orb_v': orb_v, 'q': q, 'g': g,
                'pitch': pitch, 'hdg': hdg,
                'lat': lat, 'lon': lon,
                'ap': ap, 'pe': pe, 'ecc': ecc, 'th': th
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
        {"x": 580, "y": 530, "w": 460, "h": 180, "title": "ORBITAL INSERTION (APOAPSIS &amp; PERIAPSIS)", "unit": "km"}
    ]

    def scale_x(t, p): return p["x"] + (t / t_max) * p["w"]
    def scale_y(val, val_max, p): return p["y"] + p["h"] - (val / val_max) * p["h"]

    p1 = panels[0]
    p1_path = "M " + " ".join(f"{scale_x(d['t'], p1):.1f},{scale_y(d['alt']/1000.0, 320.0, p1):.1f}" for d in sampled)

    p2 = panels[1]
    p2_srf = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['spd'], 2200.0, p2):.1f}" for d in sampled)
    p2_orb = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['orb_v'], 2200.0, p2):.1f}" for d in sampled)

    p3 = panels[2]
    p3_path = "M " + " ".join(f"{scale_x(d['t'], p3):.1f},{scale_y(d['q'], 30.0, p3):.1f}" for d in sampled)

    p4 = panels[3]
    p4_path = "M " + " ".join(f"{scale_x(d['t'], p4):.1f},{scale_y(d['g'], 4.0, p4):.1f}" for d in sampled)

    p5 = panels[4]
    p5_pitch = "M " + " ".join(f"{scale_x(d['t'], p5):.1f},{scale_y(max(0, d['pitch']), 100.0, p5):.1f}" for d in sampled)

    p6 = panels[5]
    # Ap and Pe progression in km
    def clamp_pe(val): return max(0.0, val / 1000.0)
    p6_ap = "M " + " ".join(f"{scale_x(d['t'], p6):.1f},{scale_y(min(350.0, max(0.0, d['ap']/1000.0)), 350.0, p6):.1f}" for d in sampled)
    p6_pe = "M " + " ".join(f"{scale_x(d['t'], p6):.1f},{scale_y(clamp_pe(d['pe']), 350.0, p6):.1f}" for d in sampled)

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
    <text x="25" y="28" fill="#38bdf8" font-size="15" font-weight="bold">COROLT SPACE AGENCY // CSA-12 OPERATIONS DECK DASHBOARD</text>
    <text x="660" y="28" fill="#10b981" font-size="12" font-weight="bold">HISTORIC SUCCESS // 305.9 x 299.6 KM ORBIT INSERTION</text>

    <!-- 6 Panels -->
    <!-- Panel 1: Alt -->
    <rect x="{p1['x']}" y="{p1['y']}" width="{p1['w']}" height="{p1['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p1['x']+12}" y="{p1['y']+20}" fill="#38bdf8" font-size="11" font-weight="bold">{p1['title']}</text>
    <text x="{p1['x']+p1['w']-160}" y="{p1['y']+20}" fill="#94a3b8" font-size="10">Target Orbit: 300.0 km</text>
    <line x1="{p1['x']}" y1="{scale_y(70, 320.0, p1):.1f}" x2="{p1['x']+p1['w']}" y2="{scale_y(70, 320.0, p1):.1f}" stroke="#a855f7" stroke-dasharray="3,3" stroke-width="1"/>
    <text x="{p1['x']+p1['w']-115}" y="{scale_y(70, 320.0, p1)-4:.1f}" fill="#a855f7" font-size="9">Kármán (70 km)</text>
    <path d="{p1_path}" fill="none" stroke="#38bdf8" stroke-width="2.5" filter="url(#glow)"/>

    <!-- Panel 2: Speeds -->
    <rect x="{p2['x']}" y="{p2['y']}" width="{p2['w']}" height="{p2['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p2['x']+12}" y="{p2['y']+20}" fill="#f43f5e" font-size="11" font-weight="bold">{p2['title']}</text>
    <text x="{p2['x']+p2['w']-180}" y="{p2['y']+20}" fill="#94a3b8" font-size="10">Orbital Speed: 1,982.6 m/s</text>
    <path d="{p2_srf}" fill="none" stroke="#f43f5e" stroke-width="2.0" />
    <path d="{p2_orb}" fill="none" stroke="#38bdf8" stroke-width="2.2"/>
    <text x="{p2['x']+15}" y="{p2['y']+p2['h']-12}" fill="#f43f5e" font-size="10">― Surface Vel</text>
    <text x="{p2['x']+180}" y="{p2['y']+p2['h']-12}" fill="#38bdf8" font-size="10">― Orbital Vel (Final: 1,982.6 m/s)</text>

    <!-- Panel 3: Q -->
    <rect x="{p3['x']}" y="{p3['y']}" width="{p3['w']}" height="{p3['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p3['x']+12}" y="{p3['y']+20}" fill="#f59e0b" font-size="11" font-weight="bold">{p3['title']}</text>
    <text x="{p3['x']+p3['w']-150}" y="{p3['y']+20}" fill="#94a3b8" font-size="10">Max Q: 24.50 kPa (T+48s)</text>
    <path d="{p3_path}" fill="none" stroke="#f59e0b" stroke-width="2.2" />
    <text x="{p3['x']+15}" y="{p3['y']+p3['h']-12}" fill="#f59e0b" font-size="10">Autonomous Throttle Governor (Ceiling: 32 kPa)</text>

    <!-- Panel 4: G -->
    <rect x="{p4['x']}" y="{p4['y']}" width="{p4['w']}" height="{p4['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p4['x']+12}" y="{p4['y']+20}" fill="#a855f7" font-size="11" font-weight="bold">{p4['title']}</text>
    <text x="{p4['x']+p4['w']-150}" y="{p4['y']+20}" fill="#94a3b8" font-size="10">Peak G: 3.29 G (T+121s)</text>
    <path d="{p4_path}" fill="none" stroke="#a855f7" stroke-width="2.2" />
    <text x="{p4['x']+15}" y="{p4['y']+p4['h']-12}" fill="#a855f7" font-size="10">Payload Structural Safety Ceiling: &lt; 3.80 G</text>

    <!-- Panel 5: Attitude -->
    <rect x="{p5['x']}" y="{p5['y']}" width="{p5['w']}" height="{p5['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p5['x']+12}" y="{p5['y']+20}" fill="#10b981" font-size="11" font-weight="bold">{p5['title']}</text>
    <text x="{p5['x']+p5['w']-160}" y="{p5['y']+20}" fill="#94a3b8" font-size="10">Azimuth: 90.0º (Inc 0.13º)</text>
    <path d="{p5_pitch}" fill="none" stroke="#10b981" stroke-width="2.2" />
    <text x="{p5['x']+15}" y="{p5['y']+p5['h']-12}" fill="#10b981" font-size="10">Pitch Law: 84º Kick -&gt; 0º Prograde SECO-2</text>

    <!-- Panel 6: Insertion -->
    <rect x="{p6['x']}" y="{p6['y']}" width="{p6['w']}" height="{p6['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p6['x']+12}" y="{p6['y']+20}" fill="#22c55e" font-size="11" font-weight="bold">{p6['title']}</text>
    <text x="{p6['x']+p6['w']-180}" y="{p6['y']+20}" fill="#22c55e" font-size="10">Orbit: 305.9 x 299.6 km (e=0.0035)</text>
    <path d="{p6_ap}" fill="none" stroke="#a855f7" stroke-width="2.0" />
    <path d="{p6_pe}" fill="none" stroke="#10b981" stroke-width="2.2" />
    <text x="{p6['x']+15}" y="{p6['y']+p6['h']-12}" fill="#a855f7" font-size="10">― Apoapsis (305.9 km)</text>
    <text x="{p6['x']+200}" y="{p6['y']+p6['h']-12}" fill="#10b981" font-size="10">― Periapsis (299.6 km)</text>

    <!-- Footer timestamp -->
    <text x="25" y="{height-15}" fill="#64748b" font-size="10">CSA TELEMETRY RECORDER // LIFTOFF MET T+{t_max:.1f}s ({t_max/60:.2f} min) // 2526 FLIGHT SAMPLES</text>
    <text x="{width-320}" y="{height-15}" fill="#10b981" font-size="10" font-weight="bold">MISSION SUCCESS: COROLTSAT-1B ACTIVE</text>
    </svg>
    """

    with open(output_file, "w") as f:
        f.write(svg)
    print(f"[✓] Dashboard generated: {output_file}")

def generate_dynamic_pressure_plot(data, output_file):
    width, height = 900, 500
    t_max = 200.0  # Focus on atmospheric phase (0-200s)
    ascent_data = [d for d in data if d['t'] <= t_max]
    q_max = 30.0
    g_max = 4.0

    pad_l, pad_r, pad_t, pad_b = 70, 70, 60, 60
    pw = width - pad_l - pad_r
    ph = height - pad_t - pad_b

    def sx(t): return pad_l + (t / t_max) * pw
    def sy_q(q): return pad_t + ph - (q / q_max) * ph
    def sy_g(g): return pad_t + ph - (g / g_max) * ph

    q_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_q(d['q']):.1f}" for d in ascent_data)
    g_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_g(d['g']):.1f}" for d in ascent_data)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#090d16; font-family:'Courier New', monospace;">
    <defs>
        <pattern id="grid_q" width="30" height="30" patternUnits="userSpaceOnUse">
            <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" stroke-width="0.7" opacity="0.4"/>
        </pattern>
    </defs>
    <rect width="{width}" height="{height}" fill="url(#grid_q)" />

    <!-- Header -->
    <text x="{pad_l}" y="35" fill="#f59e0b" font-size="15" font-weight="bold">COROLT-IV B #2 // DYNAMIC PRESSURE (Q) &amp; ACCELERATION ENVELOPE</text>
    <text x="{width-pad_r-250}" y="35" fill="#94a3b8" font-size="11">MISSION CSA-12 (ATMOSPHERIC ASCENT)</text>

    <!-- Axes Box -->
    <rect x="{pad_l}" y="{pad_t}" width="{pw}" height="{ph}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />

    <!-- Grid lines -->
    <line x1="{pad_l}" y1="{sy_q(20):.1f}" x2="{pad_l+pw}" y2="{sy_q(20):.1f}" stroke="#334155" stroke-dasharray="2,2"/>
    <text x="{pad_l-35}" y="{sy_q(20)+4:.1f}" fill="#f59e0b" font-size="10">20 kPa</text>

    <!-- Curves -->
    <path d="{q_path}" fill="none" stroke="#f59e0b" stroke-width="2.5" />
    <path d="{g_path}" fill="none" stroke="#a855f7" stroke-width="2.2" />

    <!-- Annotations -->
    <circle cx="{sx(47.7):.1f}" cy="{sy_q(24.5):.1f}" r="4" fill="#f59e0b" />
    <text x="{sx(47.7)+10:.1f}" y="{sy_q(24.5)-5:.1f}" fill="#f59e0b" font-size="11" font-weight="bold">Max Q: 24.5 kPa (T+47.7s)</text>

    <circle cx="{sx(48.2):.1f}" cy="{sy_g(1.43):.1f}" r="4" fill="#fbbf24" />
    <text x="{sx(48.2)+10:.1f}" y="{sy_g(1.43)+18:.1f}" fill="#fbbf24" font-size="11">SRB Jettison: Full Burn (T+48s)</text>

    <circle cx="{sx(121.0):.1f}" cy="{sy_g(3.29):.1f}" r="4" fill="#a855f7" />
    <text x="{sx(121.0)-140:.1f}" y="{sy_g(3.29)-8:.1f}" fill="#a855f7" font-size="11" font-weight="bold">Peak Load: 3.29 G (T+121s)</text>

    <circle cx="{sx(125.0):.1f}" cy="{sy_q(0.0):.1f}" r="4" fill="#38bdf8" />
    <text x="{sx(125.0)-120:.1f}" y="{sy_q(0.0)-20:.1f}" fill="#38bdf8" font-size="11">Stage 1 MECO (T+125s)</text>

    <!-- Legend -->
    <rect x="{pad_l+20}" y="{pad_t+20}" width="280" height="50" fill="#0f172a" stroke="#334155" opacity="0.9"/>
    <text x="{pad_l+35}" y="{pad_t+40}" fill="#f59e0b" font-size="11">― Dynamic Pressure Q (kPa, Left)</text>
    <text x="{pad_l+35}" y="{pad_t+58}" fill="#a855f7" font-size="11">― Acceleration Load (G, Right)</text>
    </svg>
    """

    with open(output_file, "w") as f:
        f.write(svg)
    print(f"[✓] Dynamic Pressure plot generated: {output_file}")

def generate_attitude_steering_plot(data, output_file):
    width, height = 900, 500
    t_max = max(d['t'] for d in data)

    pad_l, pad_r, pad_t, pad_b = 70, 70, 60, 60
    pw = width - pad_l - pad_r
    ph = height - pad_t - pad_b

    def sx(t): return pad_l + (t / t_max) * pw
    def sy_pitch(p): return pad_t + ph - (max(0.0, min(95.0, p)) / 100.0) * ph

    step = max(1, len(data) // 500)
    sampled = data[::step]

    pitch_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_pitch(d['pitch']):.1f}" for d in sampled)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#090d16; font-family:'Courier New', monospace;">
    <defs>
        <pattern id="grid_att" width="30" height="30" patternUnits="userSpaceOnUse">
            <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" stroke-width="0.7" opacity="0.4"/>
        </pattern>
    </defs>
    <rect width="{width}" height="{height}" fill="url(#grid_att)" />

    <!-- Header -->
    <text x="{pad_l}" y="35" fill="#10b981" font-size="15" font-weight="bold">AUTONOMOUS GUIDANCE ATTITUDE (kOS v4.1 PITCH LAW &amp; AZIMUTH)</text>
    <text x="{width-pad_r-250}" y="35" fill="#94a3b8" font-size="11">MISSION CSA-12 (EQUATORIAL INSERTION)</text>

    <!-- Axes Box -->
    <rect x="{pad_l}" y="{pad_t}" width="{pw}" height="{ph}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />

    <!-- Horizontal Pitch Reference Lines -->
    <line x1="{pad_l}" y1="{sy_pitch(90):.1f}" x2="{pad_l+pw}" y2="{sy_pitch(90):.1f}" stroke="#334155" stroke-dasharray="2,2"/>
    <text x="{pad_l-35}" y="{sy_pitch(90)+4:.1f}" fill="#94a3b8" font-size="10">90º</text>

    <line x1="{pad_l}" y1="{sy_pitch(45):.1f}" x2="{pad_l+pw}" y2="{sy_pitch(45):.1f}" stroke="#334155" stroke-dasharray="2,2"/>
    <text x="{pad_l-35}" y="{sy_pitch(45)+4:.1f}" fill="#94a3b8" font-size="10">45º</text>

    <line x1="{pad_l}" y1="{sy_pitch(0):.1f}" x2="{pad_l+pw}" y2="{sy_pitch(0):.1f}" stroke="#334155" stroke-dasharray="2,2"/>
    <text x="{pad_l-35}" y="{sy_pitch(0)+4:.1f}" fill="#94a3b8" font-size="10">0º</text>

    <!-- Curve -->
    <path d="{pitch_path}" fill="none" stroke="#10b981" stroke-width="2.5" />

    <!-- Annotations -->
    <circle cx="{sx(20.5):.1f}" cy="{sy_pitch(84.0):.1f}" r="4" fill="#10b981" />
    <text x="{sx(20.5)+10:.1f}" y="{sy_pitch(84.0)-8:.1f}" fill="#10b981" font-size="11">Pitch Kick (84.0º at 1,200 m)</text>

    <circle cx="{sx(125.0):.1f}" cy="{sy_pitch(15.0):.1f}" r="4" fill="#38bdf8" />
    <text x="{sx(125.0)+10:.1f}" y="{sy_pitch(15.0)-8:.1f}" fill="#38bdf8" font-size="11">Gravity Turn Flatten (15.0º MECO)</text>

    <circle cx="{sx(240.2):.1f}" cy="{sy_pitch(0.0):.1f}" r="4" fill="#a855f7" />
    <text x="{sx(240.2)-40:.1f}" y="{sy_pitch(0.0)-15:.1f}" fill="#a855f7" font-size="11">SECO-1 (Ap 300 km)</text>

    <circle cx="{sx(789.7):.1f}" cy="{sy_pitch(0.0):.1f}" r="4" fill="#10b981" />
    <text x="{sx(789.7)-120:.1f}" y="{sy_pitch(0.0)-15:.1f}" fill="#10b981" font-size="11" font-weight="bold">SECO-2 Burn (Prograde 0.0º)</text>

    <!-- Legend -->
    <rect x="{pad_l+20}" y="{pad_t+20}" width="320" height="50" fill="#0f172a" stroke="#334155" opacity="0.9"/>
    <text x="{pad_l+35}" y="{pad_t+40}" fill="#10b981" font-size="11">― Pitch Steering Angle (º above Horizon)</text>
    <text x="{pad_l+35}" y="{pad_t+58}" fill="#94a3b8" font-size="11">Azimuth Lock: 090.0º East (Inclination 0.13º)</text>
    </svg>
    """

    with open(output_file, "w") as f:
        f.write(svg)
    print(f"[✓] Attitude steering plot generated: {output_file}")

def main():
    data = load_flight_data()
    print(f"Loaded {len(data)} flight data points.")
    base_dir = "/home/pablo-cortes/Documents/Corolt_Space_Agency/assets"
    generate_flight_deck_dashboard(data, os.path.join(base_dir, "csa-12_advanced_dashboard.svg"))
    generate_dynamic_pressure_plot(data, os.path.join(base_dir, "csa-12_dynamic_pressure_plot.svg"))
    generate_attitude_steering_plot(data, os.path.join(base_dir, "csa-12_attitude_steering_plot.svg"))

if __name__ == "__main__":
    main()
