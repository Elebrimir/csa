#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - KAA Airspace Hazard & Trajectory Clearance Map for Mission CSA-11
Generates an authentic FAA/KAA-style Commercial Space Transportation / NOTAM Hazard Zone Map
showing the Due East Equatorial Corridor (Heading 90.0º), SRB booster drop zone, Stage 1 Core impact sector,
and downrange re-entry corridor to the +28.76º E impact site.
"""

import math
import os

def generate_kaa_hazard_map():
    width = 1000
    height = 640

    # Bounds: Equatorial Kerbin belt
    # Lon: -90.0 to +40.0 (130 degrees span)
    # Lat: -20.0 to +20.0 (40 degrees span)
    lon_min, lon_max = -90.0, 40.0
    lat_min, lat_max = -20.0, 20.0

    def project(lon, lat):
        x = 60 + ((lon - lon_min) / (lon_max - lon_min)) * (width - 120)
        y = height - 60 - ((lat - lat_min) / (lat_max - lat_min)) * (height - 120)
        return x, y

    # Key Points
    ksc_lon, ksc_lat = -74.557, -0.097
    ksc_x, ksc_y = project(ksc_lon, ksc_lat)

    srb_lon, srb_lat = -73.5, 0.0
    srb_x, srb_y = project(srb_lon, srb_lat)

    core_lon, core_lat = -58.0, 0.05
    core_x, core_y = project(core_lon, core_lat)

    apo_lon, apo_lat = -20.0, 0.15
    apo_x, apo_y = project(apo_lon, apo_lat)

    reentry_lon, reentry_lat = 15.0, 0.22
    reentry_x, reentry_y = project(reentry_lon, reentry_lat)

    impact_lon, impact_lat = 28.76, 0.28
    impact_x, impact_y = project(impact_lon, impact_lat)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#090d16; font-family:'Courier New', monospace;">
    <defs>
        <!-- Patterns for Hazard Exclusion Zones -->
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

    <!-- Ocean Background -->
    <rect x="0" y="0" width="{width}" height="{height}" fill="#08101e" />

    <!-- Lat / Lon Coordinate Grid -->
    <!-- Latitudes -->
    <line x1="60" y1="{project(-90, 10)[1]:.1f}" x2="{width-60}" y2="{project(-90, 10)[1]:.1f}" stroke="#1e293b" stroke-dasharray="4,4" stroke-width="1"/>
    <text x="35" y="{project(-90, 10)[1]+4:.1f}" fill="#64748b" font-size="10">+10ºN</text>

    <!-- Equator -->
    <line x1="60" y1="{project(-90, 0)[1]:.1f}" x2="{width-60}" y2="{project(-90, 0)[1]:.1f}" stroke="#334155" stroke-width="1.5"/>
    <text x="25" y="{project(-90, 0)[1]+4:.1f}" fill="#38bdf8" font-size="11" font-weight="bold">EQUATOR</text>

    <line x1="60" y1="{project(-90, -10)[1]:.1f}" x2="{width-60}" y2="{project(-90, -10)[1]:.1f}" stroke="#1e293b" stroke-dasharray="4,4" stroke-width="1"/>
    <text x="35" y="{project(-90, -10)[1]+4:.1f}" fill="#64748b" font-size="10">-10ºS</text>

    <!-- Longitudes -->
    <line x1="{project(-80, 0)[0]:.1f}" y1="60" x2="{project(-80, 0)[0]:.1f}" y2="{height-60}" stroke="#1e293b" stroke-dasharray="4,4" stroke-width="1"/>
    <text x="{project(-80, 0)[0]:.1f}" y="{height-40}" fill="#64748b" font-size="10" text-anchor="middle">80ºW</text>

    <line x1="{project(-60, 0)[0]:.1f}" y1="60" x2="{project(-60, 0)[0]:.1f}" y2="{height-60}" stroke="#1e293b" stroke-dasharray="4,4" stroke-width="1"/>
    <text x="{project(-60, 0)[0]:.1f}" y="{height-40}" fill="#64748b" font-size="10" text-anchor="middle">60ºW</text>

    <line x1="{project(-30, 0)[0]:.1f}" y1="60" x2="{project(-30, 0)[0]:.1f}" y2="{height-60}" stroke="#1e293b" stroke-dasharray="4,4" stroke-width="1"/>
    <text x="{project(-30, 0)[0]:.1f}" y="{height-40}" fill="#64748b" font-size="10" text-anchor="middle">30ºW</text>

    <line x1="{project(0, 0)[0]:.1f}" y1="60" x2="{project(0, 0)[0]:.1f}" y2="{height-60}" stroke="#334155" stroke-width="1.5"/>
    <text x="{project(0, 0)[0]:.1f}" y="{height-40}" fill="#38bdf8" font-size="10" text-anchor="middle" font-weight="bold">0º PRIME</text>

    <line x1="{project(30, 0)[0]:.1f}" y1="60" x2="{project(30, 0)[0]:.1f}" y2="{height-60}" stroke="#1e293b" stroke-dasharray="4,4" stroke-width="1"/>
    <text x="{project(30, 0)[0]:.1f}" y="{height-40}" fill="#64748b" font-size="10" text-anchor="middle">30ºE</text>

    <!-- Representative Landmasses (KSC continent & Eastern continent) -->
    <!-- KSC Peninsula -->
    <path d="M {project(-90, 15)[0]:.1f},{project(-90, 15)[1]:.1f} L {project(-75, 12)[0]:.1f},{project(-75, 12)[1]:.1f} L {project(-74.5, 0)[0]:.1f},{project(-74.5, 0)[1]:.1f} L {project(-76, -15)[0]:.1f},{project(-76, -15)[1]:.1f} L {project(-90, -15)[0]:.1f},{project(-90, -15)[1]:.1f} Z" fill="#132338" stroke="#1e3a5f" stroke-width="1.5" />
    <text x="{project(-82, 5)[0]:.1f}" y="{project(-82, 5)[1]:.1f}" fill="#334155" font-size="11" font-weight="bold">WEST CONTINENT</text>

    <!-- Eastern Impact Continent -->
    <path d="M {project(20, 15)[0]:.1f},{project(20, 15)[1]:.1f} L {project(38, 12)[0]:.1f},{project(38, 12)[1]:.1f} L {project(40, -15)[0]:.1f},{project(40, -15)[1]:.1f} L {project(22, -15)[0]:.1f},{project(22, -15)[1]:.1f} L {project(18, 0)[0]:.1f},{project(18, 0)[1]:.1f} Z" fill="#132338" stroke="#1e3a5f" stroke-width="1.5" />
    <text x="{project(26, -5)[0]:.1f}" y="{project(26, -5)[1]:.1f}" fill="#334155" font-size="11" font-weight="bold">EAST CONTINENT</text>

    <!-- Trajectory Flight Corridor (Equatorial East - Heading 90º) -->
    <path d="M {ksc_x:.1f},{ksc_y:.1f} L {srb_x:.1f},{srb_y:.1f} L {core_x:.1f},{core_y:.1f} L {apo_x:.1f},{apo_y:.1f} L {reentry_x:.1f},{reentry_y:.1f} L {impact_x:.1f},{impact_y:.1f}" fill="none" stroke="#38bdf8" stroke-width="3" filter="url(#glow)"/>

    <!-- Hazard Zone 1: SRB Booster Drop Footprint (Offshore KSC) -->
    <ellipse cx="{srb_x:.1f}" cy="{srb_y:.1f}" rx="22" ry="16" fill="url(#hazardHatchAmber)" stroke="#f59e0b" stroke-width="1.5"/>
    <text x="{srb_x:.1f}" y="{srb_y-22:.1f}" fill="#f59e0b" font-size="9" text-anchor="middle" font-weight="bold">ZONE 1: SRB DROP (T+12s)</text>

    <!-- Hazard Zone 2: Stage 1 Core Drop Footprint (Ocean) -->
    <ellipse cx="{core_x:.1f}" cy="{core_y:.1f}" rx="45" ry="25" fill="url(#hazardHatchRed)" stroke="#ef4444" stroke-width="1.5"/>
    <text x="{core_x:.1f}" y="{core_y-32:.1f}" fill="#ef4444" font-size="9" text-anchor="middle" font-weight="bold">ZONE 2: CORE MECO DROP (T+125s)</text>

    <!-- Apogee Point (In Space) -->
    <circle cx="{apo_x:.1f}" cy="{apo_y:.1f}" r="5" fill="#a855f7"/>
    <text x="{apo_x:.1f}" y="{apo_y-14:.1f}" fill="#a855f7" font-size="10" text-anchor="middle" font-weight="bold">APOGEE 269.1 KM (T+828s)</text>
    <text x="{apo_x:.1f}" y="{apo_y+18:.1f}" fill="#94a3b8" font-size="9" text-anchor="middle">Exospheric Microgravity Arc</text>

    <!-- Atmospheric Re-entry Point -->
    <circle cx="{reentry_x:.1f}" cy="{reentry_y:.1f}" r="4" fill="#f97316"/>
    <text x="{reentry_x:.1f}" y="{reentry_y-12:.1f}" fill="#f97316" font-size="9" text-anchor="middle" font-weight="bold">RE-ENTRY 70 KM (T+1252s)</text>

    <!-- Hazard Zone 3: Spacecraft Impact Site (East Continent) -->
    <ellipse cx="{impact_x:.1f}" cy="{impact_y:.1f}" rx="32" ry="20" fill="url(#hazardHatchRed)" stroke="#ef4444" stroke-width="2"/>
    <circle cx="{impact_x:.1f}" cy="{impact_y:.1f}" r="4" fill="#ef4444"/>
    <text x="{impact_x:.1f}" y="{impact_y-26:.1f}" fill="#ef4444" font-size="10" text-anchor="middle" font-weight="bold">ZONE 3: GROUND IMPACT (T+1380s)</text>
    <text x="{impact_x:.1f}" y="{impact_y+28:.1f}" fill="#fca5a5" font-size="9" text-anchor="middle">Lon +28.76º E, Lat +0.28º N (832m ASL)</text>

    <!-- KSC Marker -->
    <circle cx="{ksc_x:.1f}" cy="{ksc_y:.1f}" r="6" fill="#22c55e" stroke="#fff" stroke-width="1.5"/>
    <text x="{ksc_x-10:.1f}" y="{ksc_y-12:.1f}" fill="#22c55e" font-size="11" font-weight="bold" text-anchor="end">KSC PAD (LAT -0.1º, LON -74.6º)</text>

    <!-- Header Box / NOTAM Document Title -->
    <rect x="0" y="0" width="{width}" height="55" fill="#0f172a" stroke="#1e293b" stroke-width="1"/>
    <text x="25" y="24" fill="#ef4444" font-size="14" font-weight="bold">KERBIN AVIATION ADMINISTRATION (KAA) // COMMERCIAL SPACE TRANSPORTATION</text>
    <text x="25" y="44" fill="#94a3b8" font-size="11">NOTAM NOTICE REF: KAA-CSA11-2026-11 | MISSION: CSA-11 (COROLT-IV B) | AZIMUTH: 090.0º EQUATORIAL</text>
    <rect x="{width-240}" y="10" width="220" height="35" fill="#1e293b" rx="4"/>
    <text x="{width-130}" y="32" fill="#ef4444" font-size="11" font-weight="bold" text-anchor="middle">RESTRICTED AIRSPACE</text>

    <!-- Footer Summary Box -->
    <rect x="50" y="{height-50}" width="{width-100}" height="35" fill="#0b1324" stroke="#1e293b" stroke-width="1" rx="4"/>
    <text x="65" y="{height-28}" fill="#94a3b8" font-size="10">LAUNCH CORRIDOR: Heading 090.0º East | TOTAL DOWNRANGE: 1,082 km | AIRSPACE STATUS: ALL COMMERCIAL CORRIDORS DIVERTED</text>
</svg>"""

    output_file = "/home/pablo-cortes/Documents/Corolt_Space_Agency/assets/csa-11_kaa_hazard_map.svg"
    with open(output_file, 'w') as f:
        f.write(svg)
    print(f"[✓] Generated: {output_file}")

if __name__ == "__main__":
    generate_kaa_hazard_map()
