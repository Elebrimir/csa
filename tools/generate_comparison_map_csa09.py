#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Comparative Flight Map Generator for CSA-09
Plots the planned trajectory corridor vs actual flown trajectory,
touchdown location, and historical CSA-08 reference on Kerbin's map.
"""

import csv
import math
import os

def generate_comparison_map():
    width = 960
    height = 640

    # Bounds: Equatorial continent & western waters
    lon_min, lon_max = -160.0, -60.0
    lat_min, lat_max = -20.0, +20.0

    def project(lon, lat):
        x = 50 + ((lon - lon_min) / (lon_max - lon_min)) * (width - 100)
        y = height - 50 - ((lat - lat_min) / (lat_max - lat_min)) * (height - 100)
        return x, y

    # Extract actual trajectory from CSV
    csv_path = "missions/CSA-09_telemetry.csv"
    with open(csv_path) as f:
        rows = list(csv.DictReader(f))

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

    actual_points = []
    step = max(1, (td_idx - l_idx) // 120)
    for i in range(l_idx, td_idx + 1, step):
        r = rows[i]
        lon = float(r['longitude'])
        lat = float(r['latitude'])
        alt = float(r['altitude'])
        if lon != 0.0 or lat != 0.0:
            actual_points.append((lon, lat, alt))
    
    # Ensure exact touchdown is added
    actual_points.append((float(rows[td_idx]['longitude']), float(rows[td_idx]['latitude']), float(rows[td_idx]['altitude'])))

    # Projected coordinates
    ksc_lon, ksc_lat = -74.557, -0.097
    ksc_x, ksc_y = project(ksc_lon, ksc_lat)

    sim_td_lon, sim_td_lat = -144.5, -0.1
    sim_td_x, sim_td_y = project(sim_td_lon, sim_td_lat)

    act_td_lon, act_td_lat = -100.223, -0.089
    act_td_x, act_td_y = project(act_td_lon, act_td_lat)

    csa08_lon, csa08_lat = -95.63, 18.27
    csa08_x, csa08_y = project(csa08_lon, csa08_lat)

    # Actual path string
    actual_path_d = []
    for idx, pt in enumerate(actual_points):
        px, py = project(pt[0], pt[1])
        cmd = "M" if idx == 0 else "L"
        actual_path_d.append(f"{cmd} {px:.1f} {py:.1f}")
    actual_path_str = " ".join(actual_path_d)

    # Simulated path (arc to -144.5)
    sim_path_str = f"M {ksc_x:.1f} {ksc_y:.1f} L {sim_td_x:.1f} {sim_td_y:.1f}"

    # Continent boundary (Equatorial continent + Northern land)
    continent_pts = [
        (-74.55, -20.0),
        (-74.55, -0.097), # KSC
        (-76.0, 10.0),
        (-80.0, 15.0),
        (-100.0, 18.0),
        (-160.0, 20.0),
        (-160.0, -20.0),
    ]
    continent_poly = " ".join(f"{project(p[0], p[1])[0]:.1f},{project(p[0], p[1])[1]:.1f}" for p in continent_pts)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0a1120; font-family: 'Courier New', Courier, monospace;">
    <defs>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
        <pattern id="gridPattern" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="#172554" stroke-width="0.7" opacity="0.4"/>
        </pattern>
    </defs>

    <!-- Deep Ocean Background -->
    <rect x="0" y="0" width="{width}" height="{height}" fill="#0b1b2d" />
    <rect x="0" y="0" width="{width}" height="{height}" fill="url(#gridPattern)" />

    <!-- Equatorial Continent Landmass -->
    <polygon points="{continent_poly}" fill="#142c23" stroke="#22c55e" stroke-width="1.6" opacity="0.9" />

    <!-- Lat/Lon Coordinate Grid -->
    <g stroke="#1e3a5f" stroke-width="1" stroke-dasharray="3,3" opacity="0.6">
        <line x1="50" y1="{project(0, -10)[1]}" x2="{width-50}" y2="{project(0, -10)[1]}" />
        <line x1="50" y1="{project(0, 0)[1]}" x2="{width-50}" y2="{project(0, 0)[1]}" stroke="#38bdf8" stroke-dasharray="6,4" stroke-width="1.4" />
        <line x1="50" y1="{project(0, 10)[1]}" x2="{width-50}" y2="{project(0, 10)[1]}" />
        
        <line x1="{project(-150, 0)[0]}" y1="50" x2="{project(-150, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-130, 0)[0]}" y1="50" x2="{project(-130, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-110, 0)[0]}" y1="50" x2="{project(-110, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-90, 0)[0]}" y1="50" x2="{project(-90, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-70, 0)[0]}" y1="50" x2="{project(-70, 0)[0]}" y2="{height-50}" />
    </g>

    <!-- Labels -->
    <text x="55" y="{project(0, 0)[1] - 6}" fill="#38bdf8" font-size="10" font-weight="bold">EQUATOR 0º (FLIGHT VECTOR 270º)</text>
    <text x="55" y="{project(0, 10)[1] - 4}" fill="#64748b" font-size="10">10º N</text>
    <text x="55" y="{project(0, -10)[1] - 4}" fill="#64748b" font-size="10">10º S</text>
    <text x="{project(-70, 0)[0] - 25}" y="{height - 35}" fill="#64748b" font-size="10">70º W</text>
    <text x="{project(-90, 0)[0] - 25}" y="{height - 35}" fill="#64748b" font-size="10">90º W</text>
    <text x="{project(-110, 0)[0] - 30}" y="{height - 35}" fill="#64748b" font-size="10">110º W</text>
    <text x="{project(-130, 0)[0] - 30}" y="{height - 35}" fill="#64748b" font-size="10">130º W</text>
    <text x="{project(-150, 0)[0] - 30}" y="{height - 35}" fill="#64748b" font-size="10">150º W</text>

    <!-- Planned Trajectory Corridor (Dashed Cyan) -->
    <path d="{sim_path_str}" stroke="#06b6d4" stroke-width="3" stroke-dasharray="8,6" opacity="0.6" />

    <!-- Actual Flown Trajectory (Solid Magenta/Violet with Glow) -->
    <path d="{actual_path_str}" stroke="#e879f9" stroke-width="3.5" filter="url(#glow)" />
    <path d="{actual_path_str}" stroke="#ffffff" stroke-width="1.2" opacity="0.9" />

    <!-- CSA-08 Historical Reference -->
    <g transform="translate({csa08_x:.1f}, {csa08_y:.1f})">
        <circle r="7" fill="#ef4444" opacity="0.3" />
        <circle r="4" fill="#ef4444" />
        <text x="12" y="4" fill="#f87171" font-size="11" font-weight="bold">CSA-08 Impact (Lon -95.6º, Lat +18.3º)</text>
        <text x="12" y="16" fill="#94a3b8" font-size="9">Battery failure at T+113s | Lost at Sea</text>
    </g>

    <!-- Simulated Target Footprint -->
    <g transform="translate({sim_td_x:.1f}, {sim_td_y:.1f})">
        <circle r="18" fill="none" stroke="#06b6d4" stroke-width="1.5" stroke-dasharray="4,4" />
        <circle r="5" fill="#06b6d4" />
        <text x="-15" y="-24" fill="#38bdf8" font-size="11" font-weight="bold" text-anchor="middle">Planned Target (Lon -144.5º)</text>
        <text x="-15" y="-12" fill="#94a3b8" font-size="9" text-anchor="middle">Inland Highlands (733 km West)</text>
    </g>

    <!-- Actual CSA-09 Recovery Splashdown -->
    <g transform="translate({act_td_x:.1f}, {act_td_y:.1f})">
        <circle r="22" fill="#22c55e" opacity="0.25" filter="url(#glow)" />
        <circle r="9" fill="#22c55e" stroke="#ffffff" stroke-width="2" />
        <!-- Custom Recovery Icon -->
        <text x="0" y="4" fill="#000000" font-size="10" font-weight="bold" text-anchor="middle">✓</text>
        
        <text x="-15" y="28" fill="#4ade80" font-size="12" font-weight="bold">CSA-09 Touchdown (Lon -100.2º, Lat -0.09º)</text>
        <text x="-15" y="42" fill="#cbd5e1" font-size="10">🟢 100% RECOVERED INTACT (85.5% Value)</text>
        <text x="-15" y="55" fill="#94a3b8" font-size="9">Distance from KSC: 268.0 km West | Apogee: 162.6 km</text>
    </g>

    <!-- KSC Launch Site Marker -->
    <g transform="translate({ksc_x:.1f}, {ksc_y:.1f})">
        <circle r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="2" />
        <text x="14" y="4" fill="#38bdf8" font-size="12" font-weight="bold">KSC Launch Pad 09</text>
        <text x="14" y="16" fill="#94a3b8" font-size="9">Lon -74.56º, Lat -0.10º</text>
    </g>

    <!-- Header & Mission Comparison Info Card -->
    <rect x="50" y="25" width="560" height="78" rx="8" fill="#030712" stroke="#334155" stroke-width="1.5" opacity="0.95" />
    <text x="65" y="48" fill="#38bdf8" font-size="14" font-weight="bold">MISSION CSA-09: FLIGHT PROFILE COMPARISON</text>
    <text x="65" y="68" fill="#e2e8f0" font-size="10">Planned: Due West Corridor (733 km West, Apogee 277 km) | Model: Corolt-IIIb (800 EC)</text>
    <text x="65" y="85" fill="#4ade80" font-size="10" font-weight="bold">Actual: 268 km West | Apogee 162.6 km | 100% Vessel Salvaged (85.5% Recovery Funds)</text>

    <!-- Legend -->
    <rect x="{width - 290}" y="25" width="240" height="120" rx="6" fill="#030712" stroke="#334155" stroke-width="1.2" opacity="0.9" />
    <text x="{width - 275}" y="45" fill="#94a3b8" font-size="10" font-weight="bold">MISSION LEGEND</text>
    
    <line x1="{width - 275}" y1="62" x2="{width - 245}" y2="62" stroke="#06b6d4" stroke-width="2.5" stroke-dasharray="6,4" />
    <text x="{width - 235}" y="66" fill="#e2e8f0" font-size="10">Planned Flight (Simulated)</text>
    
    <line x1="{width - 275}" y1="82" x2="{width - 245}" y2="82" stroke="#e879f9" stroke-width="3" />
    <text x="{width - 235}" y="86" fill="#e2e8f0" font-size="10">Actual Flown Trajectory</text>
    
    <circle cx="{width - 260}" cy="102" r="4.5" fill="#22c55e" />
    <text x="{width - 235}" y="106" fill="#4ade80" font-size="10">Safe Recovery Touchdown</text>

    <circle cx="{width - 260}" cy="122" r="4.5" fill="#ef4444" />
    <text x="{width - 235}" y="126" fill="#f87171" font-size="10">CSA-08 Impact Site (Water)</text>

    <!-- Water/Land biome context notes -->
    <text x="65" y="{height - 75}" fill="#64748b" font-size="10">Note: CSA-09 was recovered in coastal waters at Lon -100.2º (268 km from KSC).</text>
    <text x="65" y="{height - 60}" fill="#64748b" font-size="10">The entire payload &amp; avionics remained powered and structurally intact throughout splashdown.</text>
</svg>
"""

    out_file = "assets/csa-09_comparison_map.svg"
    with open(out_file, "w") as f:
        f.write(svg)
    print(f"[✓] Generated comparison map: {out_file}")

if __name__ == "__main__":
    generate_comparison_map()
