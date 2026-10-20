#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Multi-Chart Telemetry Analytics Generator for Mission CSA-15
Generates high-resolution standalone SVG engineering plots with valid XML headers and escaped entities:
1. csa-15_advanced_dashboard.svg (6-Panel Comprehensive Flight Operations Deck)
2. csa-15_dynamic_pressure_plot.svg (Dynamic Pressure Q & Structural G Envelope)
3. csa-15_attitude_steering_plot.svg (Guidance Attitude, Pitch Law & Azimuth Lock)
"""

import csv
import os
import xml.etree.ElementTree as ET

def load_flight_data():
    csv_file = "/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-15_telemetry.csv"
    with open(csv_file) as f:
        rows = list(csv.DictReader(f))

    liftoff_met = 1860.4

    data = []
    for r in rows:
        try:
            met = float(r['MET'])
            if met < liftoff_met:
                continue
            t = met - liftoff_met
            if t > 850.0:  # Focus on ascent to SECO-2 circularization
                break
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
    t_max = max(d['t'] for d in data) if data else 741.4

    step = max(1, len(data) // 600)
    sampled = data[::step]
    if sampled and sampled[-1] != data[-1]:
        sampled.append(data[-1])

    panels = [
        {"x": 60, "y": 70, "w": 460, "h": 180, "title": "ALTITUDE PROFILE &amp; KARMAN CROSSING", "unit": "km"},
        {"x": 580, "y": 70, "w": 460, "h": 180, "title": "SURFACE &amp; ORBITAL VELOCITIES", "unit": "m/s"},
        {"x": 60, "y": 290, "w": 460, "h": 180, "title": "AERODYNAMIC PRESSURE (MAX Q ENVELOPE)", "unit": "kPa"},
        {"x": 580, "y": 290, "w": 460, "h": 180, "title": "STRUCTURAL ACCELERATION (G-LOAD)", "unit": "G"},
        {"x": 60, "y": 510, "w": 460, "h": 180, "title": "GUIDANCE ATTITUDE (PITCH LAW &amp; AZIMUTH)", "unit": "deg"},
        {"x": 580, "y": 510, "w": 460, "h": 180, "title": "ORBITAL INSERTION (APOAPSIS &amp; PERIAPSIS)", "unit": "km"},
    ]

    def scale_x(t, p):
        return p['x'] + (t / t_max) * p['w']

    def scale_y(val, val_max, p):
        clamped = max(0.0, min(float(val), float(val_max)))
        return p['y'] + p['h'] - (clamped / val_max) * p['h']

    p1, p2, p3, p4, p5, p6 = panels

    # Panel 1: Alt (0-320 km)
    p1_path = "M " + " ".join(f"{scale_x(d['t'], p1):.1f},{scale_y(d['alt']/1000, 320, p1):.1f}" for d in sampled)

    # Panel 2: Spd & Orb Spd (0-2200 m/s)
    p2_srf = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['spd'], 2200, p2):.1f}" for d in sampled)
    p2_orb = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['orb_v'], 2200, p2):.1f}" for d in sampled)

    # Panel 3: Dynamic Pressure Q (0-35 kPa)
    p3_path = "M " + " ".join(f"{scale_x(d['t'], p3):.1f},{scale_y(d['q'], 35, p3):.1f}" for d in sampled)

    # Panel 4: G Force (0-4 G)
    p4_path = "M " + " ".join(f"{scale_x(d['t'], p4):.1f},{scale_y(d['g'], 4.0, p4):.1f}" for d in sampled)

    # Panel 5: Pitch (0-90 deg)
    p5_pitch = "M " + " ".join(f"{scale_x(d['t'], p5):.1f},{scale_y(max(0, d['pitch']), 90, p5):.1f}" for d in sampled)

    # Panel 6: Ap and Pe (0-320 km)
    p6_ap = "M " + " ".join(f"{scale_x(d['t'], p6):.1f},{scale_y(d['ap']/1000, 320, p6):.1f}" for d in sampled if d['ap'] > 0)
    p6_pe = "M " + " ".join(f"{scale_x(d['t'], p6):.1f},{scale_y(max(0, d['pe']/1000), 320, p6):.1f}" for d in sampled if d['pe'] > 0)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#060913; font-family:'Courier New', monospace;">
    <defs>
        <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
            <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="0.7" opacity="0.3"/>
        </pattern>
        <linearGradient id="headerGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#0284c7" stop-opacity="0.9" />
            <stop offset="100%" stop-color="#0f172a" stop-opacity="0.9" />
        </linearGradient>
    </defs>

    <rect width="{width}" height="{height}" fill="url(#grid)" />

    <!-- Top Banner -->
    <rect x="0" y="0" width="{width}" height="45" fill="url(#headerGrad)" stroke="#38bdf8" stroke-width="1" />
    <text x="25" y="28" fill="#ffffff" font-size="16" font-weight="bold" letter-spacing="1.5">COROLT SPACE AGENCY // FLIGHT OPERATIONS DECK: MISSION CSA-15</text>
    <text x="{width-380}" y="28" fill="#93c5fd" font-size="12">VEHICLE: COROLT-IV B #5 (COROLTSAT-1E SLOT 2)</text>

    <!-- Panel 1: Altitude -->
    <rect x="{p1['x']}" y="{p1['y']}" width="{p1['w']}" height="{p1['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p1['x']+12}" y="{p1['y']+20}" fill="#38bdf8" font-size="11" font-weight="bold">{p1['title']}</text>
    <text x="{p1['x']+p1['w']-130}" y="{p1['y']+20}" fill="#94a3b8" font-size="10">Final Alt: 300.4 km</text>
    <!-- Karman line at 70km -->
    <line x1="{p1['x']}" y1="{scale_y(70, 320, p1):.1f}" x2="{p1['x']+p1['w']}" y2="{scale_y(70, 320, p1):.1f}" stroke="#f43f5e" stroke-dasharray="3,3" stroke-width="1"/>
    <text x="{p1['x']+15}" y="{scale_y(70, 320, p1)-5:.1f}" fill="#f43f5e" font-size="9">Karman Line (70.0 km)</text>
    <path d="{p1_path}" fill="none" stroke="#38bdf8" stroke-width="2.5" />
    <text x="{p1['x']+15}" y="{p1['y']+p1['h']-12}" fill="#38bdf8" font-size="10">Target Apogee: 300.0 km (Equatorial Insertion)</text>

    <!-- Panel 2: Velocity -->
    <rect x="{p2['x']}" y="{p2['y']}" width="{p2['w']}" height="{p2['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p2['x']+12}" y="{p2['y']+20}" fill="#f43f5e" font-size="11" font-weight="bold">{p2['title']}</text>
    <text x="{p2['x']+p2['w']-180}" y="{p2['y']+20}" fill="#94a3b8" font-size="10">Orbital Speed: 1,982.2 m/s</text>
    <path d="{p2_srf}" fill="none" stroke="#f43f5e" stroke-width="2.0" />
    <path d="{p2_orb}" fill="none" stroke="#38bdf8" stroke-width="2.2"/>
    <text x="{p2['x']+15}" y="{p2['y']+p2['h']-12}" fill="#f43f5e" font-size="10">― Surface Vel</text>
    <text x="{p2['x']+180}" y="{p2['y']+p2['h']-12}" fill="#38bdf8" font-size="10">― Orbital Vel (Final: 1,982.2 m/s)</text>

    <!-- Panel 3: Q -->
    <rect x="{p3['x']}" y="{p3['y']}" width="{p3['w']}" height="{p3['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p3['x']+12}" y="{p3['y']+20}" fill="#f59e0b" font-size="11" font-weight="bold">{p3['title']}</text>
    <text x="{p3['x']+p3['w']-155}" y="{p3['y']+20}" fill="#94a3b8" font-size="10">Max Q: 22.70 kPa (T+48s)</text>
    <path d="{p3_path}" fill="none" stroke="#f59e0b" stroke-width="2.2" />
    <text x="{p3['x']+15}" y="{p3['y']+p3['h']-12}" fill="#f59e0b" font-size="10">Autonomous Throttle Governor (Ceiling: 32 kPa)</text>

    <!-- Panel 4: G -->
    <rect x="{p4['x']}" y="{p4['y']}" width="{p4['w']}" height="{p4['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p4['x']+12}" y="{p4['y']+20}" fill="#a855f7" font-size="11" font-weight="bold">{p4['title']}</text>
    <text x="{p4['x']+p4['w']-155}" y="{p4['y']+20}" fill="#94a3b8" font-size="10">Peak G: 3.27 G (T+137.5s)</text>
    <path d="{p4_path}" fill="none" stroke="#a855f7" stroke-width="2.2" />
    <text x="{p4['x']+15}" y="{p4['y']+p4['h']-12}" fill="#a855f7" font-size="10">Payload Structural Safety Ceiling: &lt; 3.80 G</text>

    <!-- Panel 5: Attitude -->
    <rect x="{p5['x']}" y="{p5['y']}" width="{p5['w']}" height="{p5['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p5['x']+12}" y="{p5['y']+20}" fill="#10b981" font-size="11" font-weight="bold">{p5['title']}</text>
    <text x="{p5['x']+p5['w']-160}" y="{p5['y']+20}" fill="#94a3b8" font-size="10">Azimuth: 90.0º (Inc 0.095º)</text>
    <path d="{p5_pitch}" fill="none" stroke="#10b981" stroke-width="2.5" />
    <text x="{p5['x']+15}" y="{p5['y']+p5['h']-12}" fill="#10b981" font-size="10">Pitch Law: 84º Kick (1.2 km) -&gt; 0º Prograde SECO-2</text>

    <!-- Panel 6: Insertion -->
    <rect x="{p6['x']}" y="{p6['y']}" width="{p6['w']}" height="{p6['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p6['x']+12}" y="{p6['y']+20}" fill="#22c55e" font-size="11" font-weight="bold">{p6['title']}</text>
    <text x="{p6['x']+p6['w']-180}" y="{p6['y']+20}" fill="#22c55e" font-size="10">Orbit: 302.6 x 299.6 km (e=0.0017)</text>
    <path d="{p6_ap}" fill="none" stroke="#a855f7" stroke-width="2.0" />
    <path d="{p6_pe}" fill="none" stroke="#10b981" stroke-width="2.2" />
    <text x="{p6['x']+15}" y="{p6['y']+p6['h']-12}" fill="#a855f7" font-size="10">― Apoapsis (302.6 km)</text>
    <text x="{p6['x']+200}" y="{p6['y']+p6['h']-12}" fill="#10b981" font-size="10">― Periapsis (299.6 km)</text>

    <!-- Footer timestamp -->
    <text x="25" y="{height-15}" fill="#64748b" font-size="10">CSA TELEMETRY RECORDER // LIFTOFF MET T+0.0s to T+{t_max:.1f}s // {len(data)} FLIGHT SAMPLES</text>
    <text x="{width-340}" y="{height-15}" fill="#10b981" font-size="10" font-weight="bold">MISSION SUCCESS: COROLTSAT-1E IN SLOT 2</text>
</svg>
"""

    with open(output_file, "w") as f:
        f.write(svg)
    ET.fromstring(svg)
    print(f"[✓] Dashboard generated & validated: {output_file}")

def generate_dynamic_pressure_plot(data, output_file):
    width, height = 900, 500
    t_max = 200.0  # Focus on atmospheric phase (0-200s)
    ascent_data = [d for d in data if d['t'] <= t_max]
    q_max = 35.0
    g_max = 4.0

    pad_l, pad_r, pad_t, pad_b = 70, 70, 60, 60
    pw = width - pad_l - pad_r
    ph = height - pad_t - pad_b

    def sx(t): return pad_l + (t / t_max) * pw
    def sy_q(q): return pad_t + ph - (q / q_max) * ph
    def sy_g(g): return pad_t + ph - (g / g_max) * ph

    q_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_q(d['q']):.1f}" for d in ascent_data)
    g_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_g(d['g']):.1f}" for d in ascent_data)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#090d16; font-family:'Courier New', monospace;">
    <defs>
        <pattern id="grid_q" width="30" height="30" patternUnits="userSpaceOnUse">
            <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" stroke-width="0.7" opacity="0.4"/>
        </pattern>
    </defs>
    <rect width="{width}" height="{height}" fill="url(#grid_q)" />

    <!-- Header -->
    <text x="{pad_l}" y="35" fill="#f59e0b" font-size="15" font-weight="bold">COROLT-IV B #5 // DYNAMIC PRESSURE (Q) &amp; ACCELERATION ENVELOPE</text>
    <text x="{width-pad_r-250}" y="35" fill="#94a3b8" font-size="11">MISSION CSA-15 (ATMOSPHERIC ASCENT)</text>

    <!-- Axes Box -->
    <rect x="{pad_l}" y="{pad_t}" width="{pw}" height="{ph}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />

    <!-- Grid lines -->
    <line x1="{pad_l}" y1="{sy_q(20):.1f}" x2="{pad_l+pw}" y2="{sy_q(20):.1f}" stroke="#334155" stroke-dasharray="2,2"/>
    <text x="{pad_l-45}" y="{sy_q(20)+4:.1f}" fill="#f59e0b" font-size="10">20 kPa</text>

    <line x1="{pad_l}" y1="{sy_g(3.0):.1f}" x2="{pad_l+pw}" y2="{sy_g(3.0):.1f}" stroke="#4c1d95" stroke-dasharray="2,2"/>
    <text x="{width-pad_r+10}" y="{sy_g(3.0)+4:.1f}" fill="#a855f7" font-size="10">3.0 G</text>

    <!-- Curves -->
    <path d="{q_path}" fill="none" stroke="#f59e0b" stroke-width="2.5" />
    <path d="{g_path}" fill="none" stroke="#a855f7" stroke-width="2.2" />

    <!-- Annotations -->
    <!-- Max Q -->
    <circle cx="{sx(48.5):.1f}" cy="{sy_q(22.70):.1f}" r="4" fill="#f59e0b"/>
    <text x="{sx(48.5)+10:.1f}" y="{sy_q(22.70)-8:.1f}" fill="#f59e0b" font-size="10" font-weight="bold">Max Q: 22.70 kPa (T+48.5s, 7.20 km)</text>

    <!-- SRB Staging -->
    <line x1="{sx(48.5):.1f}" y1="{pad_t}" x2="{sx(48.5):.1f}" y2="{pad_t+ph}" stroke="#fbbf24" stroke-dasharray="4,3" stroke-width="1.2"/>
    <text x="{sx(48.5)+5:.1f}" y="{pad_t+30}" fill="#fbbf24" font-size="9">SRB Jettison (T+48.5s)</text>

    <!-- Peak G -->
    <circle cx="{sx(137.5):.1f}" cy="{sy_g(3.27):.1f}" r="4" fill="#a855f7"/>
    <text x="{sx(137.5)-145:.1f}" y="{sy_g(3.27)-10:.1f}" fill="#a855f7" font-size="10" font-weight="bold">Peak G: 3.27 G (T+137.5s)</text>

    <!-- MECO -->
    <line x1="{sx(137.5):.1f}" y1="{pad_t}" x2="{sx(137.5):.1f}" y2="{pad_t+ph}" stroke="#38bdf8" stroke-dasharray="4,3" stroke-width="1.2"/>
    <text x="{sx(137.5)+5:.1f}" y="{pad_t+50}" fill="#38bdf8" font-size="9">Core MECO (T+137.5s)</text>

    <!-- Legend -->
    <rect x="{pad_l+20}" y="{pad_t+ph-45}" width="360" height="32" fill="#0f172a" stroke="#334155" stroke-width="1"/>
    <text x="{pad_l+35}" y="{pad_t+ph-25}" fill="#f59e0b" font-size="10">― Dynamic Pressure Q (kPa)</text>
    <text x="{pad_l+220}" y="{pad_t+ph-25}" fill="#a855f7" font-size="10">― Acceleration G (g)</text>
</svg>
"""

    with open(output_file, "w") as f:
        f.write(svg)
    ET.fromstring(svg)
    print(f"[✓] Dynamic pressure plot generated & validated: {output_file}")

def generate_attitude_steering_plot(data, output_file):
    width, height = 900, 500
    t_max = 600.0  # Guidance ascent phase up to SECO-1 + coast
    ascent_data = [d for d in data if d['t'] <= t_max]

    pad_l, pad_r, pad_t, pad_b = 70, 70, 60, 60
    pw = width - pad_l - pad_r
    ph = height - pad_t - pad_b

    def sx(t): return pad_l + (t / t_max) * pw
    def sy_deg(deg): return pad_t + ph - (deg / 100.0) * ph

    pitch_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_deg(max(0, d['pitch'])):.1f}" for d in ascent_data)
    hdg_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_deg(d['hdg']):.1f}" for d in ascent_data if 80 <= d['hdg'] <= 100)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#090d16; font-family:'Courier New', monospace;">
    <defs>
        <pattern id="grid_att" width="30" height="30" patternUnits="userSpaceOnUse">
            <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" stroke-width="0.7" opacity="0.4"/>
        </pattern>
    </defs>
    <rect width="{width}" height="{height}" fill="url(#grid_att)" />

    <!-- Header -->
    <text x="{pad_l}" y="35" fill="#10b981" font-size="15" font-weight="bold">COROLT-IV B #5 // AUTONOMOUS GUIDANCE ATTITUDE (kOS v4.6)</text>
    <text x="{width-pad_r-250}" y="35" fill="#94a3b8" font-size="11">MISSION CSA-15 (ASCENT STEERING)</text>

    <!-- Axes Box -->
    <rect x="{pad_l}" y="{pad_t}" width="{pw}" height="{ph}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />

    <!-- 90 deg Compass Reference line -->
    <line x1="{pad_l}" y1="{sy_deg(90.0):.1f}" x2="{pad_l+pw}" y2="{sy_deg(90.0):.1f}" stroke="#3b82f6" stroke-dasharray="2,2"/>
    <text x="{pad_l-55}" y="{sy_deg(90.0)+4:.1f}" fill="#3b82f6" font-size="10">90.0º East</text>

    <!-- Pitch Law Curve -->
    <path d="{pitch_path}" fill="none" stroke="#10b981" stroke-width="2.5" />
    <!-- Compass Heading Curve -->
    <path d="{hdg_path}" fill="none" stroke="#38bdf8" stroke-width="2.0" />

    <!-- Milestones -->
    <circle cx="{sx(21.1):.1f}" cy="{sy_deg(84.0):.1f}" r="4" fill="#10b981"/>
    <text x="{sx(21.1)+8:.1f}" y="{sy_deg(84.0)-6:.1f}" fill="#10b981" font-size="9">Pitch Kick (84.0º at 1.2 km)</text>

    <circle cx="{sx(137.5):.1f}" cy="{sy_deg(5.0):.1f}" r="4" fill="#38bdf8"/>
    <text x="{sx(137.5)+8:.1f}" y="{sy_deg(5.0)-8:.1f}" fill="#38bdf8" font-size="9">MECO-1: Pitch 5º (56.8 km)</text>

    <circle cx="{sx(245.8):.1f}" cy="{sy_deg(2.5):.1f}" r="4" fill="#a855f7"/>
    <text x="{sx(245.8)+8:.1f}" y="{sy_deg(2.5)-8:.1f}" fill="#a855f7" font-size="9">SECO-1: Ap 300.0 km (T+246s)</text>

    <!-- Legend -->
    <rect x="{pad_l+20}" y="{pad_t+ph-45}" width="380" height="32" fill="#0f172a" stroke="#334155" stroke-width="1"/>
    <text x="{pad_l+35}" y="{pad_t+ph-25}" fill="#10b981" font-size="10">― Pitch Angle (84º -&gt; 0º Prograde)</text>
    <text x="{pad_l+230}" y="{pad_t+ph-25}" fill="#38bdf8" font-size="10">― Compass Azimuth (90.0º East)</text>
</svg>
"""

    with open(output_file, "w") as f:
        f.write(svg)
    ET.fromstring(svg)
    print(f"[✓] Attitude steering plot generated & validated: {output_file}")

if __name__ == "__main__":
    data = load_flight_data()
    assets_dir = "/home/pablo-cortes/Documents/Corolt_Space_Agency/assets"
    os.makedirs(assets_dir, exist_ok=True)
    generate_flight_deck_dashboard(data, os.path.join(assets_dir, "csa-15_advanced_dashboard.svg"))
    generate_dynamic_pressure_plot(data, os.path.join(assets_dir, "csa-15_dynamic_pressure_plot.svg"))
    generate_attitude_steering_plot(data, os.path.join(assets_dir, "csa-15_attitude_steering_plot.svg"))
