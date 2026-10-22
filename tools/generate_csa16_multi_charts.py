#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Multi-Chart Telemetry Analytics Generator for Mission CSA-16
Generates high-resolution standalone SVG engineering plots with valid XML headers:
1. csa-16_advanced_dashboard.svg (6-Panel Comprehensive Flight Operations Deck)
2. csa-16_dynamic_pressure_plot.svg (Dynamic Pressure Q & Structural G Envelope)
3. csa-16_attitude_steering_plot.svg (Guidance Attitude, Pitch Law & Azimuth Lock)
"""

import csv
import os
import xml.etree.ElementTree as ET

def load_flight_data():
    csv_file = "/home/pablo-cortes/Documents/Corolt_Space_Agency/missions/CSA-16_telemetry.csv"
    with open(csv_file, 'r', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))

    liftoff_met = 812.8

    data = []
    for r in rows:
        try:
            met = float(r['MET'])
            if met < liftoff_met:
                continue
            t = met - liftoff_met
            if t > 1480.0:  # Cover ascent, coast, SECO-2 circularization and deorbit
                break
            alt = float(r['altitude'])
            spd = float(r['surface_vel'])
            v_spd = float(r['vert_speed'])
            orb_v = float(r['orbital_vel'])
            q = float(r['dynamic_pressure']) / 1000.0 if float(r['dynamic_pressure']) > 100 else float(r['dynamic_pressure'])  # kPa
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
    t_max = max(d['t'] for d in data) if data else 1480.0

    step = max(1, len(data) // 600)
    sampled = data[::step]
    if sampled and sampled[-1] != data[-1]:
        sampled.append(data[-1])

    panels = [
        {"x": 60, "y": 70, "w": 460, "h": 180, "title": "ALTITUDE PROFILE &amp; 600 KM MKO CLIMB", "unit": "km"},
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

    # Panel 1: Alt (0-650 km)
    p1_path = "M " + " ".join(f"{scale_x(d['t'], p1):.1f},{scale_y(d['alt']/1000, 650, p1):.1f}" for d in sampled)

    # Panel 2: Spd & Orb Spd (0-2400 m/s)
    p2_srf = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['spd'], 2400, p2):.1f}" for d in sampled)
    p2_orb = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['orb_v'], 2400, p2):.1f}" for d in sampled)

    # Panel 3: Dynamic Pressure Q (0-35 kPa)
    p3_path = "M " + " ".join(f"{scale_x(d['t'], p3):.1f},{scale_y(d['q'], 35, p3):.1f}" for d in sampled)

    # Panel 4: G Force (0-4 G)
    p4_path = "M " + " ".join(f"{scale_x(d['t'], p4):.1f},{scale_y(d['g'], 4.0, p4):.1f}" for d in sampled)

    # Panel 5: Pitch (0-90 deg)
    p5_pitch = "M " + " ".join(f"{scale_x(d['t'], p5):.1f},{scale_y(max(0, d['pitch']), 90, p5):.1f}" for d in sampled)

    # Panel 6: Ap and Pe (0-650 km)
    p6_ap = "M " + " ".join(f"{scale_x(d['t'], p6):.1f},{scale_y(d['ap']/1000, 650, p6):.1f}" for d in sampled if d['ap'] > 0)
    p6_pe = "M " + " ".join(f"{scale_x(d['t'], p6):.1f},{scale_y(max(0, d['pe']/1000), 650, p6):.1f}" for d in sampled if d['pe'] > 0)

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
    <text x="25" y="28" fill="#ffffff" font-size="16" font-weight="bold" letter-spacing="1.5">COROLT SPACE AGENCY // FLIGHT OPERATIONS DECK: MISSION CSA-16</text>
    <text x="{width-420}" y="28" fill="#93c5fd" font-size="12">VEHICLE: COROLT-IV B #6 (COROLTSAT-1F MKO-600)</text>

    <!-- Panel 1: Altitude -->
    <rect x="{p1['x']}" y="{p1['y']}" width="{p1['w']}" height="{p1['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p1['x']+12}" y="{p1['y']+20}" fill="#38bdf8" font-size="11" font-weight="bold">{p1['title']}</text>
    <text x="{p1['x']+p1['w']-130}" y="{p1['y']+20}" fill="#94a3b8" font-size="10">Final Alt: 600.3 km</text>
    <!-- Karman line at 70km -->
    <line x1="{p1['x']}" y1="{scale_y(70, 650, p1):.1f}" x2="{p1['x']+p1['w']}" y2="{scale_y(70, 650, p1):.1f}" stroke="#f43f5e" stroke-dasharray="3,3" stroke-width="1"/>
    <text x="{p1['x']+15}" y="{scale_y(70, 650, p1)-5:.1f}" fill="#f43f5e" font-size="9">Karman Line (70.0 km)</text>
    <path d="{p1_path}" fill="none" stroke="#38bdf8" stroke-width="2.5" />
    <text x="{p1['x']+15}" y="{p1['y']+p1['h']-12}" fill="#38bdf8" font-size="10">Target Apogee: 600.0 km (Foundation Anchor Node 0)</text>

    <!-- Panel 2: Velocity -->
    <rect x="{p2['x']}" y="{p2['y']}" width="{p2['w']}" height="{p2['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p2['x']+12}" y="{p2['y']+20}" fill="#f43f5e" font-size="11" font-weight="bold">{p2['title']}</text>
    <text x="{p2['x']+p2['w']-180}" y="{p2['y']+20}" fill="#94a3b8" font-size="10">Orbital Speed: 1,715.5 m/s</text>
    <path d="{p2_srf}" fill="none" stroke="#f43f5e" stroke-width="2.0" />
    <path d="{p2_orb}" fill="none" stroke="#38bdf8" stroke-width="2.2"/>
    <text x="{p2['x']+15}" y="{p2['y']+p2['h']-12}" fill="#f43f5e" font-size="10">― Surface Vel</text>
    <text x="{p2['x']+180}" y="{p2['y']+p2['h']-12}" fill="#38bdf8" font-size="10">― Orbital Vel (600 km: 1,715.5 m/s)</text>

    <!-- Panel 3: Dynamic Pressure -->
    <rect x="{p3['x']}" y="{p3['y']}" width="{p3['w']}" height="{p3['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p3['x']+12}" y="{p3['y']+20}" fill="#fbbf24" font-size="11" font-weight="bold">{p3['title']}</text>
    <text x="{p3['x']+p3['w']-130}" y="{p3['y']+20}" fill="#94a3b8" font-size="10">Max Q: 23.27 kPa</text>
    <!-- Limit at 32 kPa -->
    <line x1="{p3['x']}" y1="{scale_y(32, 35, p3):.1f}" x2="{p3['x']+p3['w']}" y2="{scale_y(32, 35, p3):.1f}" stroke="#ef4444" stroke-dasharray="4,4" stroke-width="1.2"/>
    <text x="{p3['x']+15}" y="{scale_y(32, 35, p3)-5:.1f}" fill="#ef4444" font-size="9">Aero Ceiling (32.0 kPa)</text>
    <path d="{p3_path}" fill="none" stroke="#fbbf24" stroke-width="2.2" />
    <text x="{p3['x']+15}" y="{p3['y']+p3['h']-12}" fill="#fbbf24" font-size="10">Max Q at T+46.7s (6.49 km)</text>

    <!-- Panel 4: Acceleration -->
    <rect x="{p4['x']}" y="{p4['y']}" width="{p4['w']}" height="{p4['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p4['x']+12}" y="{p4['y']+20}" fill="#ec4899" font-size="11" font-weight="bold">{p4['title']}</text>
    <text x="{p4['x']+p4['w']-130}" y="{p4['y']+20}" fill="#94a3b8" font-size="10">Max G: 3.27 G</text>
    <!-- Limit at 3.8 G -->
    <line x1="{p4['x']}" y1="{scale_y(3.8, 4.0, p4):.1f}" x2="{p4['x']+p4['w']}" y2="{scale_y(3.8, 4.0, p4):.1f}" stroke="#ef4444" stroke-dasharray="4,4" stroke-width="1.2"/>
    <text x="{p4['x']+15}" y="{scale_y(3.8, 4.0, p4)-5:.1f}" fill="#ef4444" font-size="9">Structural Limit (3.80 G)</text>
    <path d="{p4_path}" fill="none" stroke="#ec4899" stroke-width="2.2" />
    <text x="{p4['x']+15}" y="{p4['y']+p4['h']-12}" fill="#ec4899" font-size="10">Peak Load at MECO-1 (T+137.5s)</text>

    <!-- Panel 5: Guidance Attitude -->
    <rect x="{p5['x']}" y="{p5['y']}" width="{p5['w']}" height="{p5['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p5['x']+12}" y="{p5['y']+20}" fill="#a855f7" font-size="11" font-weight="bold">{p5['title']}</text>
    <text x="{p5['x']+p5['w']-130}" y="{p5['y']+20}" fill="#94a3b8" font-size="10">Azimuth: 90.0º</text>
    <path d="{p5_pitch}" fill="none" stroke="#a855f7" stroke-width="2.2" />
    <text x="{p5['x']+15}" y="{p5['y']+p5['h']-12}" fill="#a855f7" font-size="10">Gravity Turn: 84º kick at 1.2 km to 15º at 48 km</text>

    <!-- Panel 6: Orbital Insertion -->
    <rect x="{p6['x']}" y="{p6['y']}" width="{p6['w']}" height="{p6['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p6['x']+12}" y="{p6['y']+20}" fill="#10b981" font-size="11" font-weight="bold">{p6['title']}</text>
    <text x="{p6['x']+p6['w']-160}" y="{p6['y']+20}" fill="#94a3b8" font-size="10">Orbit: 601.1 x 598.9 km</text>
    <path d="{p6_ap}" fill="none" stroke="#38bdf8" stroke-width="2.2" />
    <path d="{p6_pe}" fill="none" stroke="#10b981" stroke-width="2.0" />
    <text x="{p6['x']+15}" y="{p6['y']+p6['h']-12}" fill="#38bdf8" font-size="10">― Ap (601.1 km)</text>
    <text x="{p6['x']+160}" y="{p6['y']+p6['h']-12}" fill="#10b981" font-size="10">― Pe (598.9 km, e=0.00095)</text>

    <!-- Footer -->
    <text x="25" y="{height-15}" fill="#64748b" font-size="10">COROLT SPACE AGENCY // FLIGHT DYNAMICS DIVISION // MISSION CSA-16 HIGH-FIDELITY TELEMETRY DECK</text>
</svg>
"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg.strip() + "\n")
    print(f"[✓] Dashboard generated: {output_file}")

def generate_dynamic_pressure_plot(data, output_file):
    width, height = 900, 500
    t_max = 200.0  # Focus on atmospheric phase
    atmo_data = [d for d in data if d['t'] <= t_max]
    if not atmo_data:
        return

    pad_l, pad_r, pad_t, pad_b = 60, 60, 60, 60
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    def sx(t):
        return pad_l + (t / t_max) * plot_w

    def sy_q(q):
        return pad_t + plot_h - (min(35.0, max(0.0, q)) / 35.0) * plot_h

    def sy_g(g):
        return pad_t + plot_h - (min(4.0, max(0.0, g)) / 4.0) * plot_h

    step = max(1, len(atmo_data) // 300)
    sampled = atmo_data[::step]
    if sampled and sampled[-1] != atmo_data[-1]:
        sampled.append(atmo_data[-1])

    q_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_q(d['q']):.1f}" for d in sampled)
    g_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_g(d['g']):.1f}" for d in sampled)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0b1120; font-family:'Courier New', monospace;">
    <rect width="{width}" height="{height}" fill="#0b1120" />
    <rect x="{pad_l}" y="{pad_t}" width="{plot_w}" height="{plot_h}" fill="#0f172a" stroke="#334155" stroke-width="1.2" />

    <!-- Title Banner -->
    <text x="25" y="32" fill="#38bdf8" font-size="16" font-weight="bold">MISSION CSA-16 // DYNAMIC PRESSURE (Q) &amp; ACCELERATION (G) ENVELOPE</text>
    <text x="{width-320}" y="32" fill="#94a3b8" font-size="11">MAX Q: 23.27 kPa | MAX G: 3.27 G</text>

    <!-- Limit lines -->
    <line x1="{pad_l}" y1="{sy_q(32.0):.1f}" x2="{pad_l+plot_w}" y2="{sy_q(32.0):.1f}" stroke="#ef4444" stroke-dasharray="4,4" stroke-width="1.2"/>
    <text x="{pad_l+10}" y="{sy_q(32.0)-6:.1f}" fill="#ef4444" font-size="10">Max Dynamic Pressure Limit (32.0 kPa)</text>

    <line x1="{pad_l}" y1="{sy_g(3.8):.1f}" x2="{pad_l+plot_w}" y2="{sy_g(3.8):.1f}" stroke="#f43f5e" stroke-dasharray="4,4" stroke-width="1.2"/>
    <text x="{pad_l+plot_w-220}" y="{sy_g(3.8)-6:.1f}" fill="#f43f5e" font-size="10">Max Structural G-Ceiling (3.80 G)</text>

    <!-- Curves -->
    <path d="{q_path}" fill="none" stroke="#fbbf24" stroke-width="2.5" />
    <path d="{g_path}" fill="none" stroke="#ec4899" stroke-width="2.5" />

    <!-- Markers -->
    <!-- Max Q Marker at T+46.7s -->
    <circle cx="{sx(46.7):.1f}" cy="{sy_q(23.27):.1f}" r="4" fill="#fbbf24" />
    <text x="{sx(46.7)+8:.1f}" y="{sy_q(23.27)-8:.1f}" fill="#fbbf24" font-size="10" font-weight="bold">Max Q: 23.27 kPa (T+46.7s, 6.49 km)</text>

    <!-- MECO-1 Marker at T+137.5s -->
    <circle cx="{sx(137.5):.1f}" cy="{sy_g(3.27):.1f}" r="4" fill="#ec4899" />
    <text x="{sx(137.5)-160:.1f}" y="{sy_g(3.27)-8:.1f}" fill="#ec4899" font-size="10" font-weight="bold">MECO-1: 3.27 G (T+137.5s)</text>

    <!-- Legend -->
    <text x="{pad_l+15}" y="{pad_t+plot_h-15}" fill="#fbbf24" font-size="11">― Dynamic Pressure Q (kPa)</text>
    <text x="{pad_l+230}" y="{pad_t+plot_h-15}" fill="#ec4899" font-size="11">― Structural Acceleration (G)</text>

    <!-- Footer -->
    <text x="25" y="{height-15}" fill="#64748b" font-size="10">COROLT SPACE AGENCY // AERODYNAMICS &amp; STRUCTURES DIVISION // VEHICLE COROLT-IV B #6</text>
</svg>
"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg.strip() + "\n")
    print(f"[✓] Dynamic pressure plot generated: {output_file}")

def generate_attitude_steering_plot(data, output_file):
    width, height = 900, 500
    t_max = 200.0  # Atmospheric gravity turn phase
    atmo_data = [d for d in data if d['t'] <= t_max]
    if not atmo_data:
        return

    pad_l, pad_r, pad_t, pad_b = 60, 60, 60, 60
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    def sx(t):
        return pad_l + (t / t_max) * plot_w

    def sy_deg(deg):
        return pad_t + plot_h - (min(100.0, max(0.0, deg)) / 100.0) * plot_h

    step = max(1, len(atmo_data) // 300)
    sampled = atmo_data[::step]
    if sampled and sampled[-1] != atmo_data[-1]:
        sampled.append(atmo_data[-1])

    pitch_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_deg(d['pitch']):.1f}" for d in sampled)
    hdg_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_deg(d['hdg']):.1f}" for d in sampled)

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0b1120; font-family:'Courier New', monospace;">
    <rect width="{width}" height="{height}" fill="#0b1120" />
    <rect x="{pad_l}" y="{pad_t}" width="{plot_w}" height="{plot_h}" fill="#0f172a" stroke="#334155" stroke-width="1.2" />

    <!-- Title Banner -->
    <text x="25" y="32" fill="#38bdf8" font-size="16" font-weight="bold">MISSION CSA-16 // AUTONOMOUS GUIDANCE ATTITUDE &amp; GRAVITY TURN PROFILE</text>
    <text x="{width-320}" y="32" fill="#94a3b8" font-size="11">AZIMUTH: 90.0º DUE EAST | PITCH KICK: 84.0º</text>

    <!-- Pitch Kick marker at T+20.1s -->
    <line x1="{sx(20.1):.1f}" y1="{pad_t}" x2="{sx(20.1):.1f}" y2="{pad_t+plot_h}" stroke="#38bdf8" stroke-dasharray="3,3" stroke-width="1"/>
    <text x="{sx(20.1)+6:.1f}" y="{pad_t+25}" fill="#38bdf8" font-size="10">Pitch Kick (1.2 km, T+20s)</text>

    <!-- Curves -->
    <path d="{pitch_path}" fill="none" stroke="#a855f7" stroke-width="2.5" />
    <path d="{hdg_path}" fill="none" stroke="#38bdf8" stroke-width="2.0" />

    <!-- Legend -->
    <text x="{pad_l+15}" y="{pad_t+plot_h-15}" fill="#a855f7" font-size="11">― Pitch Angle (deg)</text>
    <text x="{pad_l+200}" y="{pad_t+plot_h-15}" fill="#38bdf8" font-size="11">― Heading Azimuth (90.0º Due East)</text>

    <!-- Footer -->
    <text x="25" y="{height-15}" fill="#64748b" font-size="10">COROLT SPACE AGENCY // GUIDANCE, NAVIGATION &amp; CONTROL (GNC) DIVISION</text>
</svg>
"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(svg.strip() + "\n")
    print(f"[✓] Attitude steering plot generated: {output_file}")

if __name__ == "__main__":
    flight_data = load_flight_data()
    print(f"Loaded {len(flight_data)} valid flight frames.")
    assets_dir = "/home/pablo-cortes/Documents/Corolt_Space_Agency/assets"
    generate_flight_deck_dashboard(flight_data, os.path.join(assets_dir, "csa-16_advanced_dashboard.svg"))
    generate_dynamic_pressure_plot(flight_data, os.path.join(assets_dir, "csa-16_dynamic_pressure_plot.svg"))
    generate_attitude_steering_plot(flight_data, os.path.join(assets_dir, "csa-16_attitude_steering_plot.svg"))
