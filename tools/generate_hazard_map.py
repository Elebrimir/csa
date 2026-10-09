#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - KAA (Kerbal Aviation Administration) Hazard Map Generator
Generates an authentic FAA-style Commercial Space Transportation / NOTAM Hazard Zone Map
showing Kerbin regional geography, flight corridors, stage drop zones, and maritime exclusion areas.
"""

import math
import os

def generate_faa_hazard_map():
    width = 960
    height = 640
    
    # Geographic bounds:
    # Lon: -115.0 to -65.0 (50 degrees span)
    # Lat: -12.0 to +28.0 (40 degrees span)
    lon_min, lon_max = -115.0, -65.0
    lat_min, lat_max = -12.0, +28.0
    
    def project(lon, lat):
        x = 50 + ((lon - lon_min) / (lon_max - lon_min)) * (width - 100)
        y = height - 50 - ((lat - lat_min) / (lat_max - lat_min)) * (height - 100)
        return x, y

    # Key points
    ksc_lon, ksc_lat = -74.557, -0.097
    ksc_x, ksc_y = project(ksc_lon, ksc_lat)
    
    # CSA-08 actual trajectory points
    s1_drop_lon, s1_drop_lat = -77.2, 2.5
    s1_x, s1_y = project(s1_drop_lon, s1_drop_lat)
    
    apogee_lon, apogee_lat = -85.5, 9.8
    apo_x, apo_y = project(apogee_lon, apogee_lat)
    
    impact_lon, impact_lat = -95.68, 18.25
    imp_x, imp_y = project(impact_lon, impact_lat)

    # Simplified representative Kerbin coastlines in this sector:
    # Equatorial coast runs roughly from lat -10, lon -73 to lat 5, lon -75
    # Then curves around Booster Bay: lat 5, lon -75 -> lat 8, lon -80 -> lat 12, lon -83 -> lat 15, lon -105 (Northern Gulf)
    coast_pts = [
        (-72.0, -12.0),
        (-73.5, -5.0),
        (-74.55, -0.097), # KSC
        (-75.2, 4.0),
        (-77.0, 7.5),
        (-80.0, 9.0),
        (-84.0, 10.5),
        (-89.0, 12.0),
        (-93.0, 14.5),
        (-98.0, 17.0),
        (-105.0, 19.5),
        (-115.0, 22.0)
    ]
    coast_poly = " ".join(f"{project(p[0], p[1])[0]:.1f},{project(p[0], p[1])[1]:.1f}" for p in coast_pts)
    # Complete continent polygon to the west
    continent_poly = coast_poly + f" {project(-115.0, -12.0)[0]:.1f},{project(-115.0, -12.0)[1]:.1f} {project(-72.0, -12.0)[0]:.1f},{project(-72.0, -12.0)[1]:.1f}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0a1120; font-family: 'Courier New', Courier, monospace;">
    <defs>
        <!-- Hatched pattern for Hazard Exclusion Zones -->
        <pattern id="hazardHatch" width="12" height="12" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="12" stroke="#ef4444" stroke-width="2.5" opacity="0.8" />
        </pattern>
        <pattern id="boosterHatch" width="10" height="10" patternTransform="rotate(-45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="10" stroke="#f59e0b" stroke-width="2" opacity="0.8" />
        </pattern>
        <!-- Radar Grid Glow -->
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>

    <!-- Ocean Background -->
    <rect x="0" y="0" width="{width}" height="{height}" fill="#0b1b2d" />

    <!-- Continental Landmass (Mainland Kerbin) -->
    <polygon points="{continent_poly}" fill="#162e26" stroke="#22c55e" stroke-width="1.8" />

    <!-- Coordinate Grid (Latitude & Longitude) -->
    <!-- Latitudes -->
    <g stroke="#1e3a5f" stroke-width="1" stroke-dasharray="3,3" opacity="0.6">
        <line x1="50" y1="{project(0, -10)[1]}" x2="{width-50}" y2="{project(0, -10)[1]}" />
        <line x1="50" y1="{project(0, 0)[1]}" x2="{width-50}" y2="{project(0, 0)[1]}" stroke="#38bdf8" stroke-dasharray="5,5" stroke-width="1.2" /> <!-- Equator -->
        <line x1="50" y1="{project(0, 10)[1]}" x2="{width-50}" y2="{project(0, 10)[1]}" />
        <line x1="50" y1="{project(0, 20)[1]}" x2="{width-50}" y2="{project(0, 20)[1]}" />
        
        <!-- Longitudes -->
        <line x1="{project(-110, 0)[0]}" y1="50" x2="{project(-110, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-100, 0)[0]}" y1="50" x2="{project(-100, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-90, 0)[0]}" y1="50" x2="{project(-90, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-80, 0)[0]}" y1="50" x2="{project(-80, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-70, 0)[0]}" y1="50" x2="{project(-70, 0)[0]}" y2="{height-50}" />
    </g>

    <!-- Grid Coordinate Labels -->
    <text x="55" y="{project(0, 0)[1] - 4}" fill="#38bdf8" font-size="10" font-weight="bold">EQUATOR 0º</text>
    <text x="55" y="{project(0, 10)[1] - 4}" fill="#64748b" font-size="10">10º N</text>
    <text x="55" y="{project(0, 20)[1] - 4}" fill="#64748b" font-size="10">20º N</text>
    <text x="{project(-100, 0)[0] + 4}" y="{height-55}" fill="#64748b" font-size="10">-100º W</text>
    <text x="{project(-90, 0)[0] + 4}" y="{height-55}" fill="#64748b" font-size="10">-90º W</text>
    <text x="{project(-80, 0)[0] + 4}" y="{height-55}" fill="#64748b" font-size="10">-80º W</text>

    <!-- Region Annotations -->
    <text x="{ksc_x - 120}" y="{ksc_y + 60}" fill="#22c55e" font-size="12" opacity="0.7" font-weight="bold">GRASSLANDS CONTINENT</text>
    <text x="{ksc_x + 30}" y="{ksc_y + 100}" fill="#38bdf8" font-size="12" opacity="0.7">EASTERN OCEAN</text>
    <text x="{imp_x - 30}" y="{imp_y - 30}" fill="#38bdf8" font-size="12" opacity="0.7" font-weight="bold">NORTHERN GULF (WATER)</text>

    <!-- ==================== EXCLUSION ZONES (NOTAM) ==================== -->
    
    <!-- Hazard Zone 1: Stage 1 Booster Drop Area (RT-10) -->
    <ellipse cx="{s1_x}" cy="{s1_y}" rx="32" ry="20" fill="url(#boosterHatch)" stroke="#f59e0b" stroke-width="2" transform="rotate(-35 {s1_x} {s1_y})" />
    <text x="{s1_x + 35}" y="{s1_y - 10}" fill="#f59e0b" font-size="10" font-weight="bold">HAZARD ZONE 1: BOOSTER IMPACT</text>
    <text x="{s1_x + 35}" y="{s1_y + 4}" fill="#94a3b8" font-size="9">RT-10 Spent Casing (T+52s)</text>

    <!-- Hazard Zone 2: Payload Reentry Impact Footprint (CSA-08 Anomaly) -->
    <ellipse cx="{imp_x}" cy="{imp_y}" rx="55" ry="35" fill="url(#hazardHatch)" stroke="#ef4444" stroke-width="2.5" transform="rotate(-38 {imp_x} {imp_y})" />
    <text x="{imp_x + 45}" y="{imp_y - 20}" fill="#ef4444" font-size="11" font-weight="bold">HAZARD ZONE 2: PRIMARY IMPACT FOOTPRINT</text>
    <text x="{imp_x + 45}" y="{imp_y - 5}" fill="#fca5a5" font-size="9">Unpowered Suborbital Reentry (T+850s)</text>
    <text x="{imp_x + 45}" y="{imp_y + 8}" fill="#fca5a5" font-size="9">Lat 18.25º N, Lon 95.68º W (Ocean Bay)</text>

    <!-- ==================== TRAJECTORY PATH ==================== -->
    <!-- Flight Corridor Guideline -->
    <line x1="{ksc_x}" y1="{ksc_y}" x2="{imp_x}" y2="{imp_y}" stroke="#38bdf8" stroke-width="2.5" stroke-dasharray="6,4" />
    
    <!-- KSC Launchpad Marker -->
    <circle cx="{ksc_x}" cy="{ksc_y}" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="2" filter="url(#glow)" />
    <text x="{ksc_x + 12}" y="{ksc_y + 4}" fill="#ffffff" font-size="12" font-weight="bold">KSC PAD 01 (LAUNCH)</text>
    <text x="{ksc_x + 12}" y="{ksc_y + 17}" fill="#94a3b8" font-size="9">Lat 0.10º S, Lon 74.56º W</text>

    <!-- Stage 2 Burnout Marker -->
    <circle cx="{(ksc_x + apo_x)/2}" cy="{(ksc_y + apo_y)/2}" r="4" fill="#fbbf24" stroke="#ffffff" stroke-width="1.5" />
    <text x="{(ksc_x + apo_x)/2 + 10}" y="{(ksc_y + apo_y)/2 - 5}" fill="#fbbf24" font-size="9" font-weight="bold">MECO-2 (T+99s)</text>

    <!-- Apogee Marker -->
    <circle cx="{apo_x}" cy="{apo_y}" r="5" fill="#a855f7" stroke="#ffffff" stroke-width="1.5" />
    <text x="{apo_x + 10}" y="{apo_y - 5}" fill="#c084fc" font-size="10" font-weight="bold">APOGEE (179.4 km)</text>
    <text x="{apo_x + 10}" y="{apo_y + 8}" fill="#cbd5e1" font-size="9">Inland Overflight (T+420s)</text>

    <!-- Final Impact Splashdown Marker -->
    <polygon points="{imp_x},{imp_y-9} {imp_x+8},{imp_y+7} {imp_x-8},{imp_y+7}" fill="#ef4444" stroke="#ffffff" stroke-width="1.5" />
    <circle cx="{imp_x}" cy="{imp_y}" r="12" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-dasharray="3,3" />

    <!-- Azimuth Heading Arrow -->
    <g transform="translate({ksc_x - 30}, {ksc_y - 30}) rotate(-45)">
        <line x1="0" y1="0" x2="25" y2="0" stroke="#38bdf8" stroke-width="2" />
        <polyline points="18,-4 25,0 18,4" fill="none" stroke="#38bdf8" stroke-width="2" />
        <text x="5" y="-6" fill="#38bdf8" font-size="9" font-weight="bold">HDG 315º</text>
    </g>

    <!-- ==================== OFFICIAL KAA / FAA HEADER BLOCK ==================== -->
    <rect x="50" y="30" width="{width-100}" height="70" fill="#0f172a" stroke="#334155" stroke-width="1.5" rx="4" />
    
    <!-- Agency Seal / Emblem Representation -->
    <circle cx="85" cy="65" r="22" fill="#1e293b" stroke="#38bdf8" stroke-width="2" />
    <text x="85" y="62" fill="#38bdf8" font-size="11" font-weight="bold" text-anchor="middle">KAA</text>
    <text x="85" y="74" fill="#94a3b8" font-size="7" text-anchor="middle">OFFICIAL</text>

    <text x="120" y="52" fill="#f8fafc" font-size="14" font-weight="bold">KERBAL AVIATION ADMINISTRATION (KAA) — AIRSPACE &amp; MARITIME HAZARD NOTICE</text>
    <text x="120" y="70" fill="#38bdf8" font-size="11">MISSION: CSA-08 COMMERCIAL SPACE LAUNCH REENTRY CORRIDOR</text>
    <text x="120" y="85" fill="#94a3b8" font-size="9">NOTAM ID: KAA-CSA08-2026-09 | EFFECTIVE LAUNCH WINDOW: Y1-D90 (T+00h to T+04h)</text>

    <!-- Warning Stamp -->
    <rect x="{width-220}" y="42" width="155" height="46" fill="#7f1d1d" stroke="#ef4444" stroke-width="1.5" rx="3" />
    <text x="{width-142}" y="60" fill="#fef2f2" font-size="10" font-weight="bold" text-anchor="middle">RESTRICTED AIRSPACE</text>
    <text x="{width-142}" y="76" fill="#fca5a5" font-size="8" text-anchor="middle">ACTIVE DEBRIS CORRIDOR</text>

    <!-- Legend & Warnings Card at Bottom -->
    <rect x="50" y="{height-115}" width="380" height="55" fill="#0f172a" stroke="#334155" stroke-width="1" rx="4" opacity="0.95" />
    <text x="60" y="{height-98}" fill="#e2e8f0" font-size="10" font-weight="bold">SPECIAL OPERATING PROCEDURES (SOP):</text>
    <text x="60" y="{height-83}" fill="#94a3b8" font-size="8">• Aircraft &amp; seafaring vessels maintain minimum 25 NM clearance from Hazard Zones.</text>
    <text x="60" y="{height-70}" fill="#94a3b8" font-size="8">• High-energy suborbital trajectory. Ballistic impact probability: 99.4% in Sector 2.</text>

    <rect x="{width-350}" y="{height-115}" width="300" height="55" fill="#0f172a" stroke="#334155" stroke-width="1" rx="4" opacity="0.95" />
    <text x="{width-340}" y="{height-98}" fill="#e2e8f0" font-size="10" font-weight="bold">CORIOLIS DRIFT INVESTIGATION:</text>
    <text x="{width-340}" y="{height-83}" fill="#cbd5e1" font-size="8">• Inertial trajectory aimed at inland Highlands.</text>
    <text x="{width-340}" y="{height-70}" fill="#f87171" font-size="8">• 174.5 m/s Eastward Kerbin spin rotated gulf water under flight path.</text>
</svg>
"""
    
    os.makedirs("assets", exist_ok=True)
    out_file = "assets/csa-08_faa_hazard_map.svg"
    with open(out_file, "w") as f:
        f.write(svg)
    print(f"[✓] Official KAA/FAA Hazard Map generated at: {out_file}")

if __name__ == "__main__":
    generate_faa_hazard_map()
