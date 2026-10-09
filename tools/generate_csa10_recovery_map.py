#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Mission CSA-10 Actual Recovery & Flight Path Map
Generates an SVG map comparing the launch site (KSC) to the actual touchdown point
in the Mountains of northern Kerbin (Lat +19.42º N, Lon -77.97º W), 211 km downrange.
"""

import math
import os

def generate_recovery_map():
    width = 960
    height = 640

    lon_min, lon_max = -90.0, -70.0
    lat_min, lat_max = -5.0, 30.0

    def project(lon, lat):
        x = 50 + ((lon - lon_min) / (lon_max - lon_min)) * (width - 100)
        y = height - 50 - ((lat - lat_min) / (lat_max - lat_min)) * (height - 100)
        return x, y

    ksc_lon, ksc_lat = -74.557, -0.097
    ksc_x, ksc_y = project(ksc_lon, ksc_lat)

    td_lon, td_lat = -77.965, 19.419
    td_x, td_y = project(td_lon, td_lat)

    # Simplified coastline
    coast_pts = [
        (-70.0, -5.0),
        (-74.557, -0.097), # KSC
        (-74.9, 5.0),
        (-75.2, 10.0),
        (-75.8, 15.0),
        (-76.2, 20.0),
        (-76.0, 25.0),
        (-75.5, 30.0),
    ]
    coast_poly = " ".join(f"{project(p[0], p[1])[0]:.1f},{project(p[0], p[1])[1]:.1f}" for p in coast_pts)
    continent_poly = coast_poly + f" {project(-90.0, 30.0)[0]:.1f},{project(-90.0, 30.0)[1]:.1f} {project(-90.0, -5.0)[0]:.1f},{project(-90.0, -5.0)[1]:.1f}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0a1120; font-family: 'Courier New', Courier, monospace;">
    <defs>
        <pattern id="mountainsHatch" width="12" height="12" patternTransform="rotate(30 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="12" stroke="#854d0e" stroke-width="2.5" opacity="0.6" />
        </pattern>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>

    <rect x="0" y="0" width="{width}" height="{height}" fill="#0b1b2d" />

    <!-- Mainland -->
    <polygon points="{continent_poly}" fill="#162e26" stroke="#22c55e" stroke-width="1.8" />

    <!-- Mountain Zone Polygon -->
    <polygon points="{project(-82, 15)[0]},{project(-82, 15)[1]} {project(-76.5, 17)[0]},{project(-76.5, 17)[1]} {project(-76.8, 23)[0]},{project(-76.8, 23)[1]} {project(-82, 22)[0]},{project(-82, 22)[1]}" fill="url(#mountainsHatch)" stroke="#ca8a04" stroke-width="1.5" />
    <text x="{project(-81.5, 18)[0]}" y="{project(-81.5, 18)[1]}" fill="#facc15" font-size="12" font-weight="bold">KERBIN MOUNTAINS RANGE (ELEV > 1,500m)</text>

    <!-- Flight track line -->
    <line x1="{ksc_x}" y1="{ksc_y}" x2="{td_x}" y2="{td_y}" stroke="#38bdf8" stroke-width="3" filter="url(#glow)"/>

    <!-- KSC -->
    <circle cx="{ksc_x}" cy="{ksc_y}" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5"/>
    <text x="{ksc_x+12}" y="{ksc_y+4}" fill="#38bdf8" font-size="11" font-weight="bold">KSC LAUNCH PAD</text>
    <text x="{ksc_x+12}" y="{ksc_y+16}" fill="#94a3b8" font-size="9">Lat -0.10º, Lon -74.56º</text>

    <!-- Touchdown -->
    <circle cx="{td_x}" cy="{td_y}" r="7" fill="#22c55e" stroke="#ffffff" stroke-width="2"/>
    <text x="{td_x-230}" y="{td_y-15}" fill="#22c55e" font-size="12" font-weight="bold">CSA-10 TOUCHDOWN: MOUNTAINS BIOME</text>
    <text x="{td_x-230}" y="{td_y+2}" fill="#f8fafc" font-size="10">Lat +19.42ºN, Lon -77.97ºW | Alt: 1,584m</text>
    <text x="{td_x-230}" y="{td_y+16}" fill="#38bdf8" font-size="9">Downrange: 211 km | 100% SOLID DRY LAND</text>

    <!-- Header Block -->
    <rect x="0" y="0" width="{width}" height="45" fill="#0f172a" />
    <text x="25" y="28" fill="#38bdf8" font-size="14" font-weight="bold">COROLT SPACE AGENCY // CSA-10 ACTUAL RECOVERY &amp; TOPOGRAPHIC MAP</text>
    <text x="680" y="28" fill="#22c55e" font-size="12" font-weight="bold">PRIMARY RECOVERY: SOLID GROUND</text>

    <!-- Footer -->
    <rect x="0" y="{height-25}" width="{width}" height="25" fill="#020617" />
    <text x="25" y="{height-8}" fill="#64748b" font-size="10">CSA EXPEDITIONARY RECOVERY TEAM // MOUNTAIN RECOVERY SUCCESSFUL // WATER HAZARDS COMPLETELY ELIMINATED</text>
</svg>
"""

    out = "assets/csa-10_actual_recovery_map.svg"
    with open(out, "w") as f: f.write(svg)
    print(f"[✓] Actual Recovery Map generated: {out}")

if __name__ == "__main__":
    generate_recovery_map()
