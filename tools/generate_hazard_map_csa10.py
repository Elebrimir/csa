#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - KAA Hazard Map Generator for Mission CSA-10
Generates an authentic FAA/KAA-style Commercial Space Transportation / NOTAM Hazard Zone Map
showing the Northbound Coastal Flight Corridor (Heading 005.0º), Stage 1 booster drop zone,
maritime recovery exclusion area, and coastal radar stations.
"""

import math
import os

def generate_faa_hazard_map():
    width = 960
    height = 640

    # Bounds: Central Kerbin eastern sector & Northern coastal waters
    # Lon: -90.0 to -60.0 (30 degrees span)
    # Lat: -5.0 to +55.0 (60 degrees span)
    lon_min, lon_max = -90.0, -60.0
    lat_min, lat_max = -5.0, +55.0

    def project(lon, lat):
        x = 50 + ((lon - lon_min) / (lon_max - lon_min)) * (width - 100)
        y = height - 50 - ((lat - lat_min) / (lat_max - lat_min)) * (height - 100)
        return x, y

    # Key points
    ksc_lon, ksc_lat = -74.557, -0.097
    ksc_x, ksc_y = project(ksc_lon, ksc_lat)

    # Stage 1 (RT-10 Hammer) Burnout & Drop Point (~T+51s, ~12 km alt, ~15 km North)
    s1_drop_lon, s1_drop_lat = -74.54, 1.35
    s1_x, s1_y = project(s1_drop_lon, s1_drop_lat)

    # Apogee Point (~415 km alt over +24º Lat)
    apo_lon, apo_lat = -74.60, 24.50
    apo_x, apo_y = project(apo_lon, apo_lat)

    # Nominal Touchdown Point (+47.57º Lat, -74.65º Lon in Northern Coastal Waters)
    td_lon, td_lat = -74.65, 47.57
    td_x, td_y = project(td_lon, td_lat)

    # Simplified representative Kerbin Eastern Coastline
    coast_pts = [
        (-72.0, -5.0),
        (-73.5, -2.5),
        (-74.557, -0.097), # KSC
        (-74.9, 4.0),
        (-75.5, 9.0),
        (-76.0, 15.0),
        (-76.5, 22.0),
        (-76.2, 30.0),
        (-75.8, 38.0),
        (-75.0, 45.0),
        (-74.2, 52.0),
        (-73.5, 55.0)
    ]
    coast_poly = " ".join(f"{project(p[0], p[1])[0]:.1f},{project(p[0], p[1])[1]:.1f}" for p in coast_pts)
    continent_poly = coast_poly + f" {project(-90.0, 55.0)[0]:.1f},{project(-90.0, 55.0)[1]:.1f} {project(-90.0, -5.0)[0]:.1f},{project(-90.0, -5.0)[1]:.1f}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0a1120; font-family: 'Courier New', Courier, monospace;">
    <defs>
        <!-- Hatched pattern for Hazard Exclusion Zones -->
        <pattern id="hazardHatch" width="12" height="12" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="12" stroke="#ef4444" stroke-width="2.5" opacity="0.8" />
        </pattern>
        <pattern id="boosterHatch" width="10" height="10" patternTransform="rotate(-45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="10" stroke="#f59e0b" stroke-width="2" opacity="0.8" />
        </pattern>
        <!-- Glow filter -->
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>

    <!-- Ocean Background -->
    <rect x="0" y="0" width="{width}" height="{height}" fill="#0b1b2d" />

    <!-- Continental Landmass -->
    <polygon points="{continent_poly}" fill="#162e26" stroke="#22c55e" stroke-width="1.8" />

    <!-- Coordinate Grid -->
    <!-- Latitudes -->
    <g stroke="#1e3a5f" stroke-width="1" stroke-dasharray="3,3" opacity="0.6">
        <line x1="50" y1="{project(0, 0)[1]}" x2="{width-50}" y2="{project(0, 0)[1]}" stroke="#38bdf8" stroke-dasharray="5,5" stroke-width="1.2" />
        <line x1="50" y1="{project(0, 10)[1]}" x2="{width-50}" y2="{project(0, 10)[1]}" />
        <line x1="50" y1="{project(0, 20)[1]}" x2="{width-50}" y2="{project(0, 20)[1]}" />
        <line x1="50" y1="{project(0, 30)[1]}" x2="{width-50}" y2="{project(0, 30)[1]}" />
        <line x1="50" y1="{project(0, 40)[1]}" x2="{width-50}" y2="{project(0, 40)[1]}" />
        <line x1="50" y1="{project(0, 50)[1]}" x2="{width-50}" y2="{project(0, 50)[1]}" />
        
        <!-- Longitudes -->
        <line x1="{project(-85, 0)[0]}" y1="50" x2="{project(-85, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-80, 0)[0]}" y1="50" x2="{project(-80, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-75, 0)[0]}" y1="50" x2="{project(-75, 0)[0]}" y2="{height-50}" stroke="#a855f7" stroke-dasharray="2,4" stroke-width="1" />
        <line x1="{project(-70, 0)[0]}" y1="50" x2="{project(-70, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-65, 0)[0]}" y1="50" x2="{project(-65, 0)[0]}" y2="{height-50}" />
    </g>

    <!-- Labels for Lat/Lon -->
    <text x="55" y="{project(0, 0)[1] - 4}" fill="#38bdf8" font-size="10" font-weight="bold">EQUATOR 0º</text>
    <text x="55" y="{project(0, 20)[1] - 4}" fill="#64748b" font-size="10">+20º LAT</text>
    <text x="55" y="{project(0, 40)[1] - 4}" fill="#64748b" font-size="10">+40º LAT</text>
    <text x="{project(-75, 0)[0] + 5}" y="65" fill="#a855f7" font-size="10">-75º MERIDIAN (COASTLINE AXIS)</text>

    <!-- Geographic Annotations -->
    <text x="{project(-85, 15)[0]}" y="{project(-85, 15)[1]}" fill="#22c55e" font-size="14" font-weight="bold" opacity="0.5">MAINLAND KERBIN</text>
    <text x="{project(-68, 25)[0]}" y="{project(-68, 25)[1]}" fill="#38bdf8" font-size="14" font-weight="bold" opacity="0.5">EASTERN OCEAN</text>

    <!-- 1. HAZARD ZONE 1: Stage 1 Booster Drop Area -->
    <rect x="{s1_x-18}" y="{s1_y-25}" width="36" height="50" rx="8" fill="url(#boosterHatch)" stroke="#f59e0b" stroke-width="1.8" />
    <text x="{s1_x+25}" y="{s1_y}" fill="#f59e0b" font-size="10" font-weight="bold">STAGE 1 DROP ZONE (RT-10)</text>
    <text x="{s1_x+25}" y="{s1_y+13}" fill="#94a3b8" font-size="9">Lat +1.4º, Lon -74.5º | T+51s</text>

    <!-- 2. HAZARD ZONE 2: Northern Maritime Recovery Footprint -->
    <ellipse cx="{td_x}" cy="{td_y}" rx="30" ry="25" fill="url(#hazardHatch)" stroke="#ef4444" stroke-width="2" />
    <text x="{td_x-220}" y="{td_y-12}" fill="#ef4444" font-size="11" font-weight="bold">PRIMARY RECOVERY ZONE (NOTAM)</text>
    <text x="{td_x-220}" y="{td_y+4}" fill="#94a3b8" font-size="10">Target Footprint: +47.6ºN, -74.7ºW</text>
    <text x="{td_x-220}" y="{td_y+18}" fill="#38bdf8" font-size="9">Downrange: 499.2 km (Naval Salvage Zone)</text>

    <!-- FLIGHT CORRIDOR (Heading 005.0º NNE) -->
    <line x1="{ksc_x}" y1="{ksc_y}" x2="{td_x}" y2="{td_y}" stroke="#38bdf8" stroke-width="2.8" stroke-dasharray="6,4" filter="url(#glow)" />

    <!-- Trajectory Waypoint Markers -->
    <!-- Launch Pad KSC -->
    <circle cx="{ksc_x}" cy="{ksc_y}" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="1.5" />
    <text x="{ksc_x+12}" y="{ksc_y+4}" fill="#38bdf8" font-size="11" font-weight="bold">KSC LAUNCH COMPLEX</text>
    <text x="{ksc_x+12}" y="{ksc_y+16}" fill="#94a3b8" font-size="9">Lat -0.10º, Lon -74.56º</text>

    <!-- Apogee Marker -->
    <circle cx="{apo_x}" cy="{apo_y}" r="5" fill="#a855f7" />
    <text x="{apo_x+12}" y="{apo_y+3}" fill="#a855f7" font-size="10" font-weight="bold">APOGEE (415.5 km)</text>
    <text x="{apo_x+12}" y="{apo_y+15}" fill="#94a3b8" font-size="9">Van Allen Radiation Zone</text>

    <!-- Touchdown Marker -->
    <circle cx="{td_x}" cy="{td_y}" r="6" fill="#22c55e" stroke="#ffffff" stroke-width="1.5" />

    <!-- Flight Direction Arrow -->
    <polygon points="{ksc_x},{ksc_y-40} {ksc_x-5},{ksc_y-25} {ksc_x+5},{ksc_y-25}" fill="#38bdf8" />
    <text x="{ksc_x+10}" y="{ksc_y-30}" fill="#38bdf8" font-size="10" font-weight="bold">HEADING 005.0º</text>

    <!-- HEADER BLOCK -->
    <rect x="0" y="0" width="{width}" height="45" fill="#0f172a" />
    <text x="25" y="28" fill="#38bdf8" font-size="14" font-weight="bold">KERBAL AVIATION ADMINISTRATION (KAA) // AIRSPACE HAZARD NOTICE</text>
    <text x="650" y="28" fill="#f59e0b" font-size="12" font-weight="bold">NOTAM: KAA-CSA10-2026-10 (POLAR CORRIDOR)</text>

    <!-- LEGEND BOX -->
    <rect x="{width-240}" y="{height-140}" width="220" height="115" rx="5" fill="#0f172a" stroke="#1e293b" stroke-width="1.2" />
    <text x="{width-225}" y="{height-120}" fill="#f8fafc" font-size="11" font-weight="bold">OPERATIONAL LEGEND</text>
    
    <line x1="{width-225}" y1="{height-100}" x2="{width-195}" y2="{height-100}" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="4,2"/>
    <text x="{width-185}" y="{height-96}" fill="#94a3b8" font-size="10">Active Ascent Track (005º)</text>

    <rect x="{width-225}" y="{height-85}" width="20" height="12" fill="url(#boosterHatch)" stroke="#f59e0b" stroke-width="1"/>
    <text x="{width-185}" y="{height-75}" fill="#94a3b8" font-size="10">Stage 1 Debris Zone</text>

    <rect x="{width-225}" y="{height-60}" width="20" height="12" fill="url(#hazardHatch)" stroke="#ef4444" stroke-width="1"/>
    <text x="{width-185}" y="{height-50}" fill="#94a3b8" font-size="10">Marine Recovery Sector</text>

    <!-- FOOTER STATUS -->
    <rect x="0" y="{height-25}" width="{width}" height="25" fill="#020617" />
    <text x="25" y="{height-8}" fill="#64748b" font-size="10">COROLT SPACE AGENCY // FLIGHT OPERATIONS &amp; SAFETY DIVISION // RESTRICTED MARITIME CORRIDOR</text>
</svg>
"""

    output_path = "assets/csa-10_faa_hazard_map.svg"
    with open(output_path, "w") as f:
        f.write(svg)
    print(f"[✓] KAA Hazard Map generated at: {output_path}")

if __name__ == "__main__":
    generate_faa_hazard_map()
