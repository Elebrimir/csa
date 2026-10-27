#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Universal Mission Analytics & SVG Asset Suite v4.0
Automatically extracts flight events from any <MISSION>_telemetry.csv and generates:
  1. assets/<mission>_advanced_dashboard.svg (6-Panel Comprehensive Flight Operations Deck)
  2. assets/<mission>_dynamic_pressure_plot.svg (Dynamic Pressure Q & Structural G Envelope)
  3. assets/<mission>_attitude_steering_plot.svg (Guidance Attitude, Pitch Law & Azimuth)
  4. assets/<mission>_kaa_hazard_map.svg (KAA Spaceflight Clearance & Ground Track Map)
  5. assets/<mission>_telemetry_plot.svg + missions/<MISSION>_summary.md (via rocket_families)

Usage Examples:
    python3 tools/generate_mission_assets.py CSA-16
    python3 tools/generate_mission_assets.py CSA-17 --vehicle "Corolt-IV B #7" --payload "CoroltSat-1G"
    python3 tools/generate_mission_assets.py --all
"""

import argparse
import csv
import json
import math
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

MANIFEST_PATH = os.path.join(REPO_ROOT, "missions", "missions_manifest.json")
KERBIN_SOLAR_DAY = 21600.0


def load_manifest():
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def get_mission_metadata(mission_code, vehicle_override=None, payload_override=None, target_alt_override=None):
    code = mission_code.upper().replace("_", "-")
    manifest = load_manifest()
    meta = dict(manifest.get(code, {}))
    meta["code"] = code
    meta["family"] = meta.get("family", "Corolt-IV")
    meta["vehicle"] = vehicle_override or meta.get("vehicle", f"Corolt-IV B ({code})")
    meta["payload"] = payload_override or meta.get("payload", f"{code} Spacecraft")
    meta["target_alt_km"] = float(target_alt_override or meta.get("target_alt_km", 600.0))
    meta["objective"] = meta.get("objective", f"Orbital insertion and deployment for mission {code}")
    meta["outcome"] = meta.get("outcome", f"🟢 100% Mission Success | {code} Operational")
    return meta


def analyze_mission_telemetry(mission_code):
    """
    Loads missions/<MISSION>_telemetry.csv, automatically detects liftoff, pitch kick,
    Max Q, SRB separation, Stage 1 MECO / Max G, SECO-1, SECO-2 circularization,
    and upper stage deorbit, and returns normalized flight frames + event dictionary.
    """
    code = mission_code.upper().replace("_", "-")
    csv_path = os.path.join(REPO_ROOT, "missions", f"{code}_telemetry.csv")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Telemetry CSV not found: {csv_path}")

    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"Telemetry CSV is empty: {csv_path}")

    # 1. Detect Liftoff (first frame with vertical speed > 2.0 m/s or altitude > 95 m)
    liftoff_idx = 0
    for i, r in enumerate(rows):
        try:
            alt = float(r.get("altitude", 0) or 0)
            vspd = float(r.get("vert_speed", 0) or 0)
            if vspd > 2.0 or alt > 95.0:
                liftoff_idx = max(0, i - 1)
                break
        except (ValueError, TypeError):
            continue

    ut0 = float(rows[liftoff_idx].get("UT", 0) or 0)
    met0 = float(rows[liftoff_idx].get("MET", 0) or 0)

    flight = []
    for r in rows[liftoff_idx:]:
        try:
            met = float(r.get("MET", 0) or 0)
            t = max(0.0, met - met0)
            ut = float(r.get("UT", 0) or 0)
            alt = float(r.get("altitude", 0) or 0)
            spd = float(r.get("surface_vel", 0) or 0)
            v_spd = float(r.get("vert_speed", 0) or 0)
            orb_v = float(r.get("orbital_vel", 0) or 0)
            q_pa = float(r.get("dynamic_pressure", 0) or 0)
            q = q_pa / 1000.0  # Convert Pa to kPa
            g = float(r.get("g_force", 0) or 0)
            pitch = float(r.get("pitch", 90) or 90)
            hdg = float(r.get("heading", 90) or 90)
            lat = float(r.get("latitude", 0) or 0)
            lon = float(r.get("longitude", 0) or 0)
            ap = float(r.get("apoapsis", 0) or 0)
            pe = float(r.get("periapsis", 0) or 0)
            ecc = float(r.get("eccentricity", 1.0) or 1.0)
            inc = float(r.get("inclination", 0.0) or 0.0)
            th = float(r.get("throttle", 0) or 0)
            sf = float(r.get("solid_fuel", 0) or 0)
            lf = float(r.get("liquid_fuel", 0) or 0)

            # Skip invalid zeroed frames at end of recording if vessel switched/destroyed
            if t > 300 and alt == 0.0 and ap == 0.0 and lon == 0.0:
                continue

            flight.append({
                "t": t, "ut": ut, "alt": alt, "spd": spd, "v_spd": v_spd,
                "orb_v": orb_v, "q": q, "g": g, "pitch": pitch, "hdg": hdg,
                "lat": lat, "lon": lon, "ap": ap, "pe": pe, "ecc": ecc,
                "inc": inc, "th": th, "sf": sf, "lf": lf,
            })
        except (ValueError, TypeError):
            continue

    if not flight:
        raise ValueError(f"No valid flight frames parsed from {csv_path}")

    # Detect key flight milestones automatically
    # Pitch Kick: first point where altitude >= 1100m and pitch < 88.5 deg
    pitch_kick = next((d for d in flight if d["alt"] >= 1100 and d["pitch"] < 88.5), flight[0])

    # Max Q (within atmospheric ascent t <= 120s and alt < 35 km)
    atmo_q = [d for d in flight if d["t"] <= 120.0 and d["alt"] < 35000.0]
    max_q_pt = max(atmo_q, key=lambda d: d["q"]) if atmo_q else flight[0]

    # SRB Burnout / Staging (where solid_fuel drops < 1.0 after T+15s, or fallback to max_q_pt)
    srb_pt = next((d for d in flight if d["t"] > 15.0 and d["sf"] < 1.0), max_q_pt)

    # Stage 1 MECO / Max G (between T+75s and T+185s)
    meco_window = [d for d in flight if 75.0 <= d["t"] <= 185.0]
    max_g_pt = max(meco_window, key=lambda d: d["g"]) if meco_window else flight[0]
    meco_pt = next((d for d in meco_window if d["t"] >= max_g_pt["t"] and d["th"] == 0.0), max_g_pt)

    # SECO-1 Cutoff (between T+160s and T+450s when throttle drops to 0 near peak transfer apogee)
    seco1_window = [d for d in flight if 160.0 <= d["t"] <= 450.0 and d["alt"] > 65000.0]
    if seco1_window:
        peak_ap_s1 = max(d["ap"] for d in seco1_window)
        seco1_pt = next(
            (d for d in seco1_window if d["th"] == 0.0 and d["ap"] >= peak_ap_s1 * 0.95),
            seco1_window[-1],
        )
    else:
        seco1_pt = flight[min(len(flight) - 1, len(flight) // 3)]

    # SECO-2 Circularization Cutoff (minimum eccentricity after T+350s and before deorbit)
    seco2_window = [d for d in flight if d["t"] > 350.0 and d["ap"] > 100000.0 and d["pe"] > 70000.0]
    if seco2_window:
        min_ecc = min(d["ecc"] for d in seco2_window)
        seco2_pt = next(
            (d for d in seco2_window if d["ecc"] <= min_ecc + 0.00015 and d["th"] == 0.0),
            min(seco2_window, key=lambda d: d["ecc"]),
        )
    else:
        seco2_pt = max(flight, key=lambda d: d["alt"])

    # Stage 2 Deorbit Burn (after SECO-2 where periapsis drops <= 0 km and lon != 0)
    deorbit_pt = next(
        (d for d in flight if d["t"] > seco2_pt["t"] + 15.0 and d["pe"] <= 0.0 and abs(d["lon"]) > 0.01),
        None,
    )

    # Trim flight data to 30 seconds after deorbit or SECO-2+120s so plots are clean
    t_cutoff = (deorbit_pt["t"] + 25.0) if deorbit_pt else (seco2_pt["t"] + 120.0)
    trimmed_flight = [d for d in flight if d["t"] <= t_cutoff]
    if not trimmed_flight:
        trimmed_flight = flight

    launch_day = int(ut0 // KERBIN_SOLAR_DAY) + 1 if ut0 > 0 else 1

    events = {
        "ut0": ut0,
        "met0": met0,
        "launch_day": f"Y1-D{launch_day}",
        "liftoff": flight[0],
        "pitch_kick": pitch_kick,
        "max_q": max_q_pt,
        "srb_sep": srb_pt,
        "max_g": max_g_pt,
        "meco1": meco_pt,
        "seco1": seco1_pt,
        "seco2": seco2_pt,
        "deorbit": deorbit_pt,
    }

    return trimmed_flight, events


def generate_flight_deck_dashboard(data, events, meta, output_file):
    width, height = 1100, 780
    t_max = max(d["t"] for d in data) if data else 1000.0
    max_alt_km = max(d["alt"] for d in data) / 1000.0
    max_ap_km = max(d["ap"] for d in data) / 1000.0
    alt_ceil_km = max(350.0, math.ceil(max(max_alt_km, max_ap_km, meta["target_alt_km"]) / 50.0) * 50.0 + 50.0)
    vel_ceil = max(2400.0, math.ceil(max(d["orb_v"] for d in data) / 200.0) * 200.0 + 200.0)

    step = max(1, len(data) // 600)
    sampled = data[::step]
    if sampled and sampled[-1] != data[-1]:
        sampled.append(data[-1])

    regime_label = f"{meta['target_alt_km']:.0f} KM MKO" if meta["target_alt_km"] >= 450 else f"{meta['target_alt_km']:.0f} KM LEO"

    panels = [
        {"x": 60, "y": 70, "w": 460, "h": 180, "title": f"ALTITUDE PROFILE &amp; {regime_label} CLIMB", "unit": "km"},
        {"x": 580, "y": 70, "w": 460, "h": 180, "title": "SURFACE &amp; ORBITAL VELOCITIES", "unit": "m/s"},
        {"x": 60, "y": 290, "w": 460, "h": 180, "title": "AERODYNAMIC PRESSURE (MAX Q ENVELOPE)", "unit": "kPa"},
        {"x": 580, "y": 290, "w": 460, "h": 180, "title": "STRUCTURAL ACCELERATION (G-LOAD)", "unit": "G"},
        {"x": 60, "y": 510, "w": 460, "h": 180, "title": "GUIDANCE ATTITUDE (PITCH LAW &amp; AZIMUTH)", "unit": "deg"},
        {"x": 580, "y": 510, "w": 460, "h": 180, "title": "ORBITAL INSERTION (APOAPSIS &amp; PERIAPSIS)", "unit": "km"},
    ]

    def scale_x(t, p):
        return p["x"] + (t / t_max) * p["w"]

    def scale_y(val, val_max, p):
        clamped = max(0.0, min(float(val), float(val_max)))
        return p["y"] + p["h"] - (clamped / val_max) * p["h"]

    p1, p2, p3, p4, p5, p6 = panels

    p1_path = "M " + " ".join(f"{scale_x(d['t'], p1):.1f},{scale_y(d['alt']/1000, alt_ceil_km, p1):.1f}" for d in sampled)
    p2_srf = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['spd'], vel_ceil, p2):.1f}" for d in sampled)
    p2_orb = "M " + " ".join(f"{scale_x(d['t'], p2):.1f},{scale_y(d['orb_v'], vel_ceil, p2):.1f}" for d in sampled)
    p3_path = "M " + " ".join(f"{scale_x(d['t'], p3):.1f},{scale_y(d['q'], 35, p3):.1f}" for d in sampled)
    p4_path = "M " + " ".join(f"{scale_x(d['t'], p4):.1f},{scale_y(d['g'], 4.0, p4):.1f}" for d in sampled)
    p5_pitch = "M " + " ".join(f"{scale_x(d['t'], p5):.1f},{scale_y(max(0, d['pitch']), 90, p5):.1f}" for d in sampled)

    ap_pts = [f"{scale_x(d['t'], p6):.1f},{scale_y(d['ap']/1000, alt_ceil_km, p6):.1f}" for d in sampled if d["ap"] > 0]
    pe_pts = [f"{scale_x(d['t'], p6):.1f},{scale_y(max(0, d['pe']/1000), alt_ceil_km, p6):.1f}" for d in sampled if d["pe"] > 0]
    p6_ap = ("M " + " ".join(ap_pts)) if ap_pts else f"M {p6['x']},{p6['y']+p6['h']}"
    p6_pe = ("M " + " ".join(pe_pts)) if pe_pts else f"M {p6['x']},{p6['y']+p6['h']}"

    s2 = events["seco2"]
    mq = events["max_q"]
    mg = events["max_g"]
    pk = events["pitch_kick"]
    veh_short = meta["vehicle"].split(" (")[0].upper()
    pay_short = meta["payload"].split(" (")[0].upper()

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
    <text x="25" y="28" fill="#ffffff" font-size="16" font-weight="bold" letter-spacing="1.5">COROLT SPACE AGENCY // FLIGHT OPERATIONS DECK: MISSION {meta['code']}</text>
    <text x="{width-440}" y="28" fill="#93c5fd" font-size="12">VEHICLE: {veh_short} ({pay_short})</text>

    <!-- Panel 1: Altitude -->
    <rect x="{p1['x']}" y="{p1['y']}" width="{p1['w']}" height="{p1['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p1['x']+12}" y="{p1['y']+20}" fill="#38bdf8" font-size="11" font-weight="bold">{p1['title']}</text>
    <text x="{p1['x']+p1['w']-135}" y="{p1['y']+20}" fill="#94a3b8" font-size="10">Final Alt: {s2['alt']/1000:.1f} km</text>
    <line x1="{p1['x']}" y1="{scale_y(70, alt_ceil_km, p1):.1f}" x2="{p1['x']+p1['w']}" y2="{scale_y(70, alt_ceil_km, p1):.1f}" stroke="#f43f5e" stroke-dasharray="3,3" stroke-width="1"/>
    <text x="{p1['x']+15}" y="{scale_y(70, alt_ceil_km, p1)-5:.1f}" fill="#f43f5e" font-size="9">Karman Line (70.0 km)</text>
    <path d="{p1_path}" fill="none" stroke="#38bdf8" stroke-width="2.5" />
    <text x="{p1['x']+15}" y="{p1['y']+p1['h']-12}" fill="#38bdf8" font-size="10">Target Orbit: {meta['target_alt_km']:.1f} km ({pay_short})</text>

    <!-- Panel 2: Velocity -->
    <rect x="{p2['x']}" y="{p2['y']}" width="{p2['w']}" height="{p2['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p2['x']+12}" y="{p2['y']+20}" fill="#f43f5e" font-size="11" font-weight="bold">{p2['title']}</text>
    <text x="{p2['x']+p2['w']-185}" y="{p2['y']+20}" fill="#94a3b8" font-size="10">Orbital Speed: {s2['orb_v']:,.1f} m/s</text>
    <path d="{p2_srf}" fill="none" stroke="#f43f5e" stroke-width="2.0" />
    <path d="{p2_orb}" fill="none" stroke="#38bdf8" stroke-width="2.2"/>
    <text x="{p2['x']+15}" y="{p2['y']+p2['h']-12}" fill="#f43f5e" font-size="10">― Surface Vel</text>
    <text x="{p2['x']+170}" y="{p2['y']+p2['h']-12}" fill="#38bdf8" font-size="10">― Orbital Vel ({meta['target_alt_km']:.0f} km: {s2['orb_v']:,.1f} m/s)</text>

    <!-- Panel 3: Dynamic Pressure -->
    <rect x="{p3['x']}" y="{p3['y']}" width="{p3['w']}" height="{p3['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p3['x']+12}" y="{p3['y']+20}" fill="#fbbf24" font-size="11" font-weight="bold">{p3['title']}</text>
    <text x="{p3['x']+p3['w']-135}" y="{p3['y']+20}" fill="#94a3b8" font-size="10">Max Q: {mq['q']:.2f} kPa</text>
    <line x1="{p3['x']}" y1="{scale_y(32, 35, p3):.1f}" x2="{p3['x']+p3['w']}" y2="{scale_y(32, 35, p3):.1f}" stroke="#ef4444" stroke-dasharray="4,4" stroke-width="1.2"/>
    <text x="{p3['x']+15}" y="{scale_y(32, 35, p3)-5:.1f}" fill="#ef4444" font-size="9">Aero Ceiling (32.0 kPa)</text>
    <path d="{p3_path}" fill="none" stroke="#fbbf24" stroke-width="2.2" />
    <text x="{p3['x']+15}" y="{p3['y']+p3['h']-12}" fill="#fbbf24" font-size="10">Max Q at T+{mq['t']:.1f}s ({mq['alt']/1000:.2f} km)</text>

    <!-- Panel 4: Acceleration -->
    <rect x="{p4['x']}" y="{p4['y']}" width="{p4['w']}" height="{p4['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p4['x']+12}" y="{p4['y']+20}" fill="#ec4899" font-size="11" font-weight="bold">{p4['title']}</text>
    <text x="{p4['x']+p4['w']-130}" y="{p4['y']+20}" fill="#94a3b8" font-size="10">Max G: {mg['g']:.2f} G</text>
    <line x1="{p4['x']}" y1="{scale_y(3.8, 4.0, p4):.1f}" x2="{p4['x']+p4['w']}" y2="{scale_y(3.8, 4.0, p4):.1f}" stroke="#ef4444" stroke-dasharray="4,4" stroke-width="1.2"/>
    <text x="{p4['x']+15}" y="{scale_y(3.8, 4.0, p4)-5:.1f}" fill="#ef4444" font-size="9">Structural Limit (3.80 G)</text>
    <path d="{p4_path}" fill="none" stroke="#ec4899" stroke-width="2.2" />
    <text x="{p4['x']+15}" y="{p4['y']+p4['h']-12}" fill="#ec4899" font-size="10">Peak Load at MECO-1 (T+{mg['t']:.1f}s)</text>

    <!-- Panel 5: Guidance Attitude -->
    <rect x="{p5['x']}" y="{p5['y']}" width="{p5['w']}" height="{p5['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p5['x']+12}" y="{p5['y']+20}" fill="#a855f7" font-size="11" font-weight="bold">{p5['title']}</text>
    <text x="{p5['x']+p5['w']-130}" y="{p5['y']+20}" fill="#94a3b8" font-size="10">Azimuth: 90.0º</text>
    <path d="{p5_pitch}" fill="none" stroke="#a855f7" stroke-width="2.2" />
    <text x="{p5['x']+15}" y="{p5['y']+p5['h']-12}" fill="#a855f7" font-size="10">Gravity Turn: 84º kick at {pk['alt']/1000:.1f} km (T+{pk['t']:.0f}s)</text>

    <!-- Panel 6: Orbital Insertion -->
    <rect x="{p6['x']}" y="{p6['y']}" width="{p6['w']}" height="{p6['h']}" fill="#0b1120" stroke="#334155" stroke-width="1.2" />
    <text x="{p6['x']+12}" y="{p6['y']+20}" fill="#10b981" font-size="11" font-weight="bold">{p6['title']}</text>
    <text x="{p6['x']+p6['w']-175}" y="{p6['y']+20}" fill="#94a3b8" font-size="10">Orbit: {s2['ap']/1000:.1f} x {s2['pe']/1000:.1f} km</text>
    <path d="{p6_ap}" fill="none" stroke="#38bdf8" stroke-width="2.2" />
    <path d="{p6_pe}" fill="none" stroke="#10b981" stroke-width="2.0" />
    <text x="{p6['x']+15}" y="{p6['y']+p6['h']-12}" fill="#38bdf8" font-size="10">― Ap ({s2['ap']/1000:.1f} km)</text>
    <text x="{p6['x']+160}" y="{p6['y']+p6['h']-12}" fill="#10b981" font-size="10">― Pe ({s2['pe']/1000:.1f} km, e={s2['ecc']:.5f})</text>

    <!-- Footer -->
    <text x="25" y="{height-15}" fill="#64748b" font-size="10">COROLT SPACE AGENCY // FLIGHT DYNAMICS DIVISION // MISSION {meta['code']} HIGH-FIDELITY TELEMETRY DECK</text>
</svg>
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg.strip() + "\n")
    print(f"[✓] 6-Panel Dashboard generated: {output_file}")


def generate_dynamic_pressure_plot(data, events, meta, output_file):
    width, height = 900, 500
    t_max = 200.0
    atmo_data = [d for d in data if d["t"] <= t_max]
    if not atmo_data:
        atmo_data = data

    pad_l, pad_r, pad_t, pad_b = 60, 60, 60, 60
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    def sx(t):
        return pad_l + (min(t_max, max(0.0, t)) / t_max) * plot_w

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

    mq = events["max_q"]
    mg = events["max_g"]
    veh_short = meta["vehicle"].split(" (")[0].upper()

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0b1120; font-family:'Courier New', monospace;">
    <rect width="{width}" height="{height}" fill="#0b1120" />
    <rect x="{pad_l}" y="{pad_t}" width="{plot_w}" height="{plot_h}" fill="#0f172a" stroke="#334155" stroke-width="1.2" />

    <!-- Title Banner -->
    <text x="25" y="32" fill="#38bdf8" font-size="16" font-weight="bold">MISSION {meta['code']} // DYNAMIC PRESSURE (Q) &amp; ACCELERATION (G) ENVELOPE</text>
    <text x="{width-330}" y="32" fill="#94a3b8" font-size="11">MAX Q: {mq['q']:.2f} kPa | MAX G: {mg['g']:.2f} G</text>

    <!-- Limit lines -->
    <line x1="{pad_l}" y1="{sy_q(32.0):.1f}" x2="{pad_l+plot_w}" y2="{sy_q(32.0):.1f}" stroke="#ef4444" stroke-dasharray="4,4" stroke-width="1.2"/>
    <text x="{pad_l+10}" y="{sy_q(32.0)-6:.1f}" fill="#ef4444" font-size="10">Max Dynamic Pressure Limit (32.0 kPa)</text>

    <line x1="{pad_l}" y1="{sy_g(3.8):.1f}" x2="{pad_l+plot_w}" y2="{sy_g(3.8):.1f}" stroke="#f43f5e" stroke-dasharray="4,4" stroke-width="1.2"/>
    <text x="{pad_l+plot_w-220}" y="{sy_g(3.8)-6:.1f}" fill="#f43f5e" font-size="10">Max Structural G-Ceiling (3.80 G)</text>

    <!-- Curves -->
    <path d="{q_path}" fill="none" stroke="#fbbf24" stroke-width="2.5" />
    <path d="{g_path}" fill="none" stroke="#ec4899" stroke-width="2.5" />

    <!-- Max Q Marker -->
    <circle cx="{sx(mq['t']):.1f}" cy="{sy_q(mq['q']):.1f}" r="4" fill="#fbbf24" />
    <text x="{sx(mq['t'])+8:.1f}" y="{sy_q(mq['q'])-8:.1f}" fill="#fbbf24" font-size="10" font-weight="bold">Max Q: {mq['q']:.2f} kPa (T+{mq['t']:.1f}s, {mq['alt']/1000:.2f} km)</text>

    <!-- MECO-1 / Max G Marker -->
    <circle cx="{sx(mg['t']):.1f}" cy="{sy_g(mg['g']):.1f}" r="4" fill="#ec4899" />
    <text x="{sx(mg['t'])-160:.1f}" y="{sy_g(mg['g'])-8:.1f}" fill="#ec4899" font-size="10" font-weight="bold">MECO-1: {mg['g']:.2f} G (T+{mg['t']:.1f}s)</text>

    <!-- Legend -->
    <text x="{pad_l+15}" y="{pad_t+plot_h-15}" fill="#fbbf24" font-size="11">― Dynamic Pressure Q (kPa)</text>
    <text x="{pad_l+230}" y="{pad_t+plot_h-15}" fill="#ec4899" font-size="11">― Structural Acceleration (G)</text>

    <!-- Footer -->
    <text x="25" y="{height-15}" fill="#64748b" font-size="10">COROLT SPACE AGENCY // AERODYNAMICS &amp; STRUCTURES DIVISION // VEHICLE {veh_short}</text>
</svg>
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg.strip() + "\n")
    print(f"[✓] Dynamic pressure plot generated: {output_file}")


def generate_attitude_steering_plot(data, events, meta, output_file):
    width, height = 900, 500
    t_max = 200.0
    atmo_data = [d for d in data if d["t"] <= t_max]
    if not atmo_data:
        atmo_data = data

    pad_l, pad_r, pad_t, pad_b = 60, 60, 60, 60
    plot_w = width - pad_l - pad_r
    plot_h = height - pad_t - pad_b

    def sx(t):
        return pad_l + (min(t_max, max(0.0, t)) / t_max) * plot_w

    def sy_deg(deg):
        return pad_t + plot_h - (min(100.0, max(0.0, deg)) / 100.0) * plot_h

    step = max(1, len(atmo_data) // 300)
    sampled = atmo_data[::step]
    if sampled and sampled[-1] != atmo_data[-1]:
        sampled.append(atmo_data[-1])

    pitch_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_deg(d['pitch']):.1f}" for d in sampled)
    hdg_path = "M " + " ".join(f"{sx(d['t']):.1f},{sy_deg(d['hdg']):.1f}" for d in sampled)

    pk = events["pitch_kick"]

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0b1120; font-family:'Courier New', monospace;">
    <rect width="{width}" height="{height}" fill="#0b1120" />
    <rect x="{pad_l}" y="{pad_t}" width="{plot_w}" height="{plot_h}" fill="#0f172a" stroke="#334155" stroke-width="1.2" />

    <!-- Title Banner -->
    <text x="25" y="32" fill="#38bdf8" font-size="16" font-weight="bold">MISSION {meta['code']} // AUTONOMOUS GUIDANCE ATTITUDE &amp; GRAVITY TURN PROFILE</text>
    <text x="{width-320}" y="32" fill="#94a3b8" font-size="11">AZIMUTH: 90.0º DUE EAST | PITCH KICK: 84.0º</text>

    <!-- Pitch Kick marker -->
    <line x1="{sx(pk['t']):.1f}" y1="{pad_t}" x2="{sx(pk['t']):.1f}" y2="{pad_t+plot_h}" stroke="#38bdf8" stroke-dasharray="3,3" stroke-width="1"/>
    <text x="{sx(pk['t'])+6:.1f}" y="{pad_t+25}" fill="#38bdf8" font-size="10">Pitch Kick ({pk['alt']/1000:.1f} km, T+{pk['t']:.0f}s)</text>

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
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg.strip() + "\n")
    print(f"[✓] Attitude steering plot generated: {output_file}")


def generate_kaa_clearance_map(events, meta, output_file):
    width, height = 1000, 640
    lon_min, lon_max = -90.0, 50.0
    lat_min, lat_max = -20.0, 20.0

    def project(lon, lat):
        clon = max(lon_min + 2.0, min(lon_max - 2.0, lon))
        clat = max(lat_min + 2.0, min(lat_max - 2.0, lat))
        x = 60 + ((clon - lon_min) / (lon_max - lon_min)) * (width - 120)
        y = height - 60 - ((clat - lat_min) / (lat_max - lat_min)) * (height - 120)
        return x, y

    ksc = events["liftoff"]
    srb = events["srb_sep"]
    core = events["meco1"]
    s1 = events["seco1"]
    s2 = events["seco2"]
    deorb = events["deorbit"] or s2

    ksc_x, ksc_y = project(ksc["lon"], ksc["lat"])
    srb_x, srb_y = project(srb["lon"], srb["lat"])
    core_x, core_y = project(core["lon"], core["lat"])
    s1_x, s1_y = project(s1["lon"], s1["lat"])
    s2_x, s2_y = project(s2["lon"], s2["lat"])
    deorb_x, deorb_y = project(deorb["lon"], deorb["lat"])

    num_code = meta["code"].replace("CSA-", "")
    veh_short = meta["vehicle"].split(" (")[0].upper()
    pay_short = meta["payload"].split(" (")[0].upper()
    regime_str = "MKO ORBIT ACHIEVED" if meta["target_alt_km"] >= 450 else "LEO ORBIT ACHIEVED"
    deorb_pe_str = f"Stage 2 Deorbit Pe={deorb['pe']/1000:.2f} km" if events["deorbit"] else "Orbital Insertion Verified"

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#090d16; font-family:'Courier New', monospace;">
    <defs>
        <pattern id="hazardHatchRed" width="12" height="12" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="12" stroke="#ef4444" stroke-width="2" opacity="0.7" />
        </pattern>
        <pattern id="hazardHatchAmber" width="10" height="10" patternTransform="rotate(-45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="10" stroke="#f59e0b" stroke-width="2" opacity="0.7" />
        </pattern>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>

    <rect width="{width}" height="{height}" fill="#0b1120" />

    <!-- Header Block -->
    <rect x="0" y="0" width="{width}" height="55" fill="#0f172a" stroke="#334155" stroke-width="1.2" />
    <text x="25" y="32" fill="#38bdf8" font-size="16" font-weight="bold">KERBAL AVIATION ADMINISTRATION (KAA) // SPACE CLEARANCE NOTICE</text>
    <text x="700" y="32" fill="#10b981" font-size="12" font-weight="bold">STATUS: {regime_str}</text>
    <text x="25" y="47" fill="#94a3b8" font-size="10">NOTAM: KAA-CSA{num_code}-2026-{num_code} // MISSION {meta['code']} ({veh_short}) // EQUATORIAL CORRIDOR 090.0º</text>

    <!-- Equator -->
    <line x1="60" y1="{project(0, 0)[1]:.1f}" x2="{width-60}" y2="{project(0, 0)[1]:.1f}" stroke="#475569" stroke-width="1.2" stroke-dasharray="4,4" />
    <text x="65" y="{project(0, 0)[1]-6:.1f}" fill="#64748b" font-size="9">EQUATOR (0.0º LAT)</text>

    <!-- Meridian ticks -->
    <line x1="{project(-60, 0)[0]:.1f}" y1="70" x2="{project(-60, 0)[0]:.1f}" y2="{height-70}" stroke="#1e293b" stroke-width="1" />
    <text x="{project(-60, 0)[0]+4:.1f}" y="85" fill="#475569" font-size="9">60º W</text>
    <line x1="{project(-30, 0)[0]:.1f}" y1="70" x2="{project(-30, 0)[0]:.1f}" y2="{height-70}" stroke="#1e293b" stroke-width="1" />
    <text x="{project(-30, 0)[0]+4:.1f}" y="85" fill="#475569" font-size="9">30º W</text>
    <line x1="{project(0, 0)[0]:.1f}" y1="70" x2="{project(0, 0)[0]:.1f}" y2="{height-70}" stroke="#1e293b" stroke-width="1" />
    <text x="{project(0, 0)[0]+4:.1f}" y="85" fill="#475569" font-size="9">0º PRIME</text>
    <line x1="{project(30, 0)[0]:.1f}" y1="70" x2="{project(30, 0)[0]:.1f}" y2="{height-70}" stroke="#1e293b" stroke-width="1" />
    <text x="{project(30, 0)[0]+4:.1f}" y="85" fill="#475569" font-size="9">30º E</text>

    <!-- Zone 1: SRB Drop Sector -->
    <rect x="{srb_x-25:.1f}" y="{srb_y-30:.1f}" width="50" height="60" fill="url(#hazardHatchAmber)" stroke="#f59e0b" stroke-width="1.5" opacity="0.85" />
    <text x="{srb_x-22:.1f}" y="{srb_y-36:.1f}" fill="#f59e0b" font-size="9" font-weight="bold">ZONE 1: SRB DROP</text>
    <text x="{srb_x-22:.1f}" y="{srb_y+42:.1f}" fill="#94a3b8" font-size="8">T+{srb['t']:.1f}s Maritime Sector</text>

    <!-- Zone 2: Stage 1 Core MECO Impact -->
    <rect x="{core_x-45:.1f}" y="{core_y-40:.1f}" width="90" height="80" fill="url(#hazardHatchRed)" stroke="#ef4444" stroke-width="1.5" opacity="0.85" />
    <text x="{core_x-40:.1f}" y="{core_y-46:.1f}" fill="#ef4444" font-size="9" font-weight="bold">ZONE 2: CORE DISPOSAL</text>
    <text x="{core_x-40:.1f}" y="{core_y+52:.1f}" fill="#94a3b8" font-size="8">Stage 1 MECO Impact Sector</text>

    <!-- Flight Trajectory Ground Track -->
    <path d="M {ksc_x:.1f},{ksc_y:.1f} L {srb_x:.1f},{srb_y:.1f} L {core_x:.1f},{core_y:.1f} L {s1_x:.1f},{s1_y:.1f} L {s2_x:.1f},{s2_y:.1f} L {deorb_x:.1f},{deorb_y:.1f} L {width-60},{deorb_y:.1f}"
          fill="none" stroke="#10b981" stroke-width="3" filter="url(#glow)" />

    <!-- Trajectory Points -->
    <circle cx="{ksc_x:.1f}" cy="{ksc_y:.1f}" r="5" fill="#38bdf8" />
    <text x="{ksc_x-50:.1f}" y="{ksc_y-12:.1f}" fill="#38bdf8" font-size="11" font-weight="bold">KSC PAD (74.6º W)</text>

    <circle cx="{s1_x:.1f}" cy="{s1_y:.1f}" r="4" fill="#a855f7" />
    <text x="{s1_x-25:.1f}" y="{s1_y-14:.1f}" fill="#a855f7" font-size="10">SECO-1 (Ap {s1['ap']/1000:.1f} km)</text>

    <circle cx="{s2_x:.1f}" cy="{s2_y:.1f}" r="5" fill="#10b981" />
    <text x="{s2_x-55:.1f}" y="{s2_y-14:.1f}" fill="#10b981" font-size="11" font-weight="bold">SECO-2 (T+{s2['t']:.0f}s CIRC)</text>

    <circle cx="{deorb_x:.1f}" cy="{deorb_y:.1f}" r="5" fill="#06b6d4" />
    <text x="{deorb_x-65:.1f}" y="{deorb_y+24:.1f}" fill="#06b6d4" font-size="11" font-weight="bold">{pay_short} DEPLOYED</text>
    <text x="{deorb_x-65:.1f}" y="{deorb_y+36:.1f}" fill="#94a3b8" font-size="9">{s2['ap']/1000:.1f} x {s2['pe']/1000:.1f} km // i={s2['inc']:.2f}º // {deorb_pe_str}</text>

    <!-- Telemetry Box -->
    <rect x="60" y="{height-140}" width="480" height="70" fill="#0f172a" stroke="#334155" stroke-width="1" />
    <text x="75" y="{height-120}" fill="#38bdf8" font-size="11" font-weight="bold">MISSION PARAMETERS &amp; KAA COMPLIANCE:</text>
    <text x="75" y="{height-102}" fill="#94a3b8" font-size="10">• Launch Azimuth: 090.0º Due East | Orbital Inclination: {s2['inc']:.2f}º (Equatorial)</text>
    <text x="75" y="{height-86}" fill="#10b981" font-size="10">• Exospheric Insertion: 100% Successful | {deorb_pe_str}</text>

    <!-- Status Badge -->
    <rect x="{width-320}" y="{height-140}" width="260" height="70" fill="#064e3b" stroke="#10b981" stroke-width="1.5" />
    <text x="{width-300}" y="{height-115}" fill="#6ee7b7" font-size="12" font-weight="bold">ORBITAL CORRIDOR SECURED</text>
    <text x="{width-300}" y="{height-95}" fill="#a7f3d0" font-size="10">{meta['payload'][:32]}</text>
    <text x="{width-300}" y="{height-80}" fill="#a7f3d0" font-size="9">KAA Clearance Verified ({events['launch_day']})</text>
</svg>
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(svg.strip() + "\n")
    print(f"[✓] KAA clearance map generated: {output_file}")


def process_mission(mission_code, vehicle=None, payload=None, target_alt=None):
    code = mission_code.upper().replace("_", "-")
    slug = code.lower()
    meta = get_mission_metadata(code, vehicle, payload, target_alt)
    data, events = analyze_mission_telemetry(code)

    assets_dir = os.path.join(REPO_ROOT, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    print(f"\n================================================================================")
    print(f" 🚀 GENERATING TELEMETRY ASSETS FOR {code} ({meta['vehicle']})")
    print(f"    Frames: {len(data)} | Liftoff UT: {events['ut0']:.1f}s ({events['launch_day']})")
    print(f"    Max Q: {events['max_q']['q']:.2f} kPa (T+{events['max_q']['t']:.1f}s) | Max G: {events['max_g']['g']:.2f} G (T+{events['max_g']['t']:.1f}s)")
    print(f"    SECO-1: Ap {events['seco1']['ap']/1000:.2f} km (T+{events['seco1']['t']:.1f}s) | SECO-2: {events['seco2']['ap']/1000:.2f}x{events['seco2']['pe']/1000:.2f} km (T+{events['seco2']['t']:.1f}s)")
    print(f"================================================================================")

    generate_flight_deck_dashboard(data, events, meta, os.path.join(assets_dir, f"{slug}_advanced_dashboard.svg"))
    generate_dynamic_pressure_plot(data, events, meta, os.path.join(assets_dir, f"{slug}_dynamic_pressure_plot.svg"))
    generate_attitude_steering_plot(data, events, meta, os.path.join(assets_dir, f"{slug}_attitude_steering_plot.svg"))
    generate_kaa_clearance_map(events, meta, os.path.join(assets_dir, f"{slug}_kaa_hazard_map.svg"))

    # Also invoke primary telemetry_plot.svg + summary.md via get_plotter_for_mission
    from tools.plotting.rocket_families import get_plotter_for_mission
    plotter = get_plotter_for_mission(code)
    plotter.run()


def main():
    parser = argparse.ArgumentParser(description="CSA Universal Mission Analytics & SVG Asset Suite v4.0")
    parser.add_argument("mission", nargs="?", default=None, help="Mission code (e.g. CSA-16, CSA-17)")
    parser.add_argument("--all", action="store_true", help="Regenerate assets for all orbital missions in manifest")
    parser.add_argument("--vehicle", type=str, default=None, help="Optional vehicle name override")
    parser.add_argument("--payload", type=str, default=None, help="Optional payload name override")
    parser.add_argument("--target-alt", type=float, default=None, help="Optional target altitude in km override")
    args = parser.parse_args()

    if args.all:
        manifest = load_manifest()
        for m_code in manifest.keys():
            csv_p = os.path.join(REPO_ROOT, "missions", f"{m_code}_telemetry.csv")
            if os.path.exists(csv_p):
                process_mission(m_code)
        return

    if args.mission:
        process_mission(args.mission, args.vehicle, args.payload, args.target_alt)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
