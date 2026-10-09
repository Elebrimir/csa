#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - KAA (Kerbal Aviation Administration) Hazard Map Generator for CSA-09
Generates an official FAA/KAA Launch Hazard Corridor & Terrestrial Exclusion Zone Map
for Mission CSA-09: Heading 270º (Due West), equatorial continental corridor.
"""

import math
import os

def generate_faa_hazard_map_csa09():
    width = 960
    height = 640
    
    # Geographic bounds centered on equatorial continental corridor:
    # Lon: -160.0 to -60.0 (100 degrees span)
    # Lat: -20.0 to +20.0 (40 degrees span)
    lon_min, lon_max = -160.0, -60.0
    lat_min, lat_max = -20.0, +20.0
    
    def project(lon, lat):
        x = 50 + ((lon - lon_min) / (lon_max - lon_min)) * (width - 100)
        y = height - 50 - ((lat - lat_min) / (lat_max - lat_min)) * (height - 100)
        return x, y

    # Key points for CSA-09
    ksc_lon, ksc_lat = -74.557, -0.097
    ksc_x, ksc_y = project(ksc_lon, ksc_lat)
    
    # Stage 1 drop zone (RT-10 Hammer, ~25 km downrange West)
    s1_drop_lon, s1_drop_lat = -77.5, -0.1
    s1_x, s1_y = project(s1_drop_lon, s1_drop_lat)
    
    # Stage 2 burnout (SRM-XL, ~80 km downrange West)
    s2_bo_lon, s2_bo_lat = -85.0, -0.1
    s2_x, s2_y = project(s2_bo_lon, s2_bo_lat)

    # Predicted Apogee (~277 km, ~580 km inertial downrange, ~Lon -105º)
    apo_lon, apo_lat = -105.0, -0.1
    apo_x, apo_y = project(apo_lon, apo_lat)
    
    # Predicted Touchdown after Coriolis shift (Lon -144.5º, Lat -0.1º)
    imp_lon, imp_lat = -144.5, -0.1
    imp_x, imp_y = project(imp_lon, imp_lat)

    # Continental landmass representation:
    # Equatorial continent stretches from Lon -74.5 (KSC shore) westward across the entire map
    continent_pts = [
        (-74.55, -20.0),
        (-74.55, -0.097), # KSC on eastern shoreline
        (-76.0, 10.0),
        (-80.0, 15.0),
        (-100.0, 18.0),
        (-160.0, 20.0),
        (-160.0, -20.0),
    ]
    continent_poly = " ".join(f"{project(p[0], p[1])[0]:.1f},{project(p[0], p[1])[1]:.1f}" for p in continent_pts)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#0a1120; font-family: 'Courier New', Courier, monospace;">
    <defs>
        <!-- Hatched pattern for Hazard Exclusion Zones -->
        <pattern id="hazardHatch" width="12" height="12" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="12" stroke="#ef4444" stroke-width="2.5" opacity="0.8" />
        </pattern>
        <pattern id="boosterHatch" width="10" height="10" patternTransform="rotate(-45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="10" stroke="#f59e0b" stroke-width="2" opacity="0.8" />
        </pattern>
        <pattern id="recoveryHatch" width="10" height="10" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="10" stroke="#22c55e" stroke-width="2" opacity="0.7" />
        </pattern>
        <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="3" result="blur" />
            <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
    </defs>

    <!-- Ocean Background (Eastern Ocean) -->
    <rect x="0" y="0" width="{width}" height="{height}" fill="#0b1b2d" />

    <!-- Continental Landmass (Equatorial Mainland: Grasslands, Highlands, Mountains) -->
    <polygon points="{continent_poly}" fill="#162e26" stroke="#22c55e" stroke-width="1.8" />

    <!-- Coordinate Grid (Latitude & Longitude) -->
    <g stroke="#1e3a5f" stroke-width="1" stroke-dasharray="3,3" opacity="0.6">
        <line x1="50" y1="{project(0, -10)[1]}" x2="{width-50}" y2="{project(0, -10)[1]}" />
        <line x1="50" y1="{project(0, 0)[1]}" x2="{width-50}" y2="{project(0, 0)[1]}" stroke="#38bdf8" stroke-dasharray="6,4" stroke-width="1.5" /> <!-- Equator -->
        <line x1="50" y1="{project(0, 10)[1]}" x2="{width-50}" y2="{project(0, 10)[1]}" />
        
        <!-- Longitudes -->
        <line x1="{project(-150, 0)[0]}" y1="50" x2="{project(-150, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-130, 0)[0]}" y1="50" x2="{project(-130, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-110, 0)[0]}" y1="50" x2="{project(-110, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-90, 0)[0]}" y1="50" x2="{project(-90, 0)[0]}" y2="{height-50}" />
        <line x1="{project(-70, 0)[0]}" y1="50" x2="{project(-70, 0)[0]}" y2="{height-50}" />
    </g>

    <!-- Grid Coordinate Labels -->
    <text x="55" y="{project(0, 0)[1] - 5}" fill="#38bdf8" font-size="10" font-weight="bold">EQUATOR 0º (FLIGHT VECTOR)</text>
    <text x="55" y="{project(0, 10)[1] - 4}" fill="#64748b" font-size="10">10º N</text>
    <text x="55" y="{project(0, -10)[1] - 4}" fill="#64748b" font-size="10">10º S</text>
    <text x="{project(-150, 0)[0] + 4}" y="{height-55}" fill="#64748b" font-size="10">-150º W</text>
    <text x="{project(-130, 0)[0] + 4}" y="{height-55}" fill="#64748b" font-size="10">-130º W</text>
    <text x="{project(-110, 0)[0] + 4}" y="{height-55}" fill="#64748b" font-size="10">-110º W</text>
    <text x="{project(-90, 0)[0] + 4}" y="{height-55}" fill="#64748b" font-size="10">-90º W</text>
    <text x="{project(-70, 0)[0] + 4}" y="{height-55}" fill="#64748b" font-size="10">-70º W</text>

    <!-- Biome Annotations -->
    <text x="{project(-82, -5)[0]}" y="{project(-82, -5)[1]}" fill="#22c55e" font-size="11" opacity="0.8" font-weight="bold">GRASSLANDS PLATEAU</text>
    <text x="{project(-115, -6)[0]}" y="{project(-115, -6)[1]}" fill="#86efac" font-size="11" opacity="0.8" font-weight="bold">HIGHLANDS CONTINENTAL RANGE</text>
    <text x="{project(-68, 5)[0]}" y="{project(-68, 5)[1]}" fill="#38bdf8" font-size="11" opacity="0.8">EASTERN OCEAN</text>

    <!-- ==================== EXCLUSION ZONES (NOTAM) ==================== -->
    
    <!-- Hazard Zone 1: Stage 1 Booster Drop Area (RT-10) -->
    <ellipse cx="{s1_x}" cy="{s1_y}" rx="28" ry="16" fill="url(#boosterHatch)" stroke="#f59e0b" stroke-width="2" />
    <text x="{s1_x}" y="{s1_y - 22}" fill="#f59e0b" font-size="10" font-weight="bold" text-anchor="middle">HAZARD ZONE 1: BOOSTER DROP</text>
    <text x="{s1_x}" y="{s1_y + 26}" fill="#cbd5e1" font-size="8" text-anchor="middle">RT-10 Spent Casing (T+51s, -77.5º W)</text>

    <!-- Planned Recovery Zone (Payload Touchdown Area under Parachute) -->
    <ellipse cx="{imp_x}" cy="{imp_y}" rx="48" ry="24" fill="url(#recoveryHatch)" stroke="#22c55e" stroke-width="2.5" />
    <text x="{imp_x}" y="{imp_y - 30}" fill="#22c55e" font-size="11" font-weight="bold" text-anchor="middle">PRIMARY RECOVERY ZONE (TERRESTRIAL)</text>
    <text x="{imp_x}" y="{imp_y + 35}" fill="#86efac" font-size="9" text-anchor="middle">Nominal Parachute Touchdown: Lon -144.5º W, Lat -0.1º S</text>
    <text x="{imp_x}" y="{imp_y + 47}" fill="#94a3b8" font-size="8" text-anchor="middle">Highlands Inland Biome (100% Solid Ground)</text>

    <!-- ==================== FLIGHT CORRIDOR ==================== -->
    <!-- Flight Corridor Path (Due West along Equator) -->
    <line x1="{ksc_x}" y1="{ksc_y}" x2="{imp_x}" y2="{imp_y}" stroke="#38bdf8" stroke-width="3" stroke-dasharray="6,4" />
    
    <!-- KSC Launchpad Marker -->
    <circle cx="{ksc_x}" cy="{ksc_y}" r="6" fill="#38bdf8" stroke="#ffffff" stroke-width="2" filter="url(#glow)" />
    <text x="{ksc_x + 10}" y="{ksc_y - 10}" fill="#ffffff" font-size="11" font-weight="bold">KSC PAD 01 (LAUNCH)</text>
    <text x="{ksc_x + 10}" y="{ksc_y + 5}" fill="#94a3b8" font-size="8">Lat 0.10º S, Lon 74.56º W</text>

    <!-- Stage 2 Burnout Marker -->
    <circle cx="{s2_x}" cy="{s2_y}" r="4" fill="#fbbf24" stroke="#ffffff" stroke-width="1.5" />
    <text x="{s2_x}" y="{s2_y - 10}" fill="#fbbf24" font-size="8" font-weight="bold" text-anchor="middle">MECO-2 (T+110s)</text>

    <!-- Apogee Marker -->
    <circle cx="{apo_x}" cy="{apo_y}" r="5" fill="#a855f7" stroke="#ffffff" stroke-width="1.5" />
    <text x="{apo_x}" y="{apo_y - 12}" fill="#c084fc" font-size="9" font-weight="bold" text-anchor="middle">APOGEE (277.6 km)</text>
    <text x="{apo_x}" y="{apo_y + 18}" fill="#cbd5e1" font-size="8" text-anchor="middle">Van Allen Penetration (T+430s)</text>

    <!-- Touchdown Crosshair -->
    <circle cx="{imp_x}" cy="{imp_y}" r="8" fill="none" stroke="#22c55e" stroke-width="2" />
    <line x1="{imp_x - 12}" y1="{imp_y}" x2="{imp_x + 12}" y2="{imp_y}" stroke="#22c55e" stroke-width="1.5" />
    <line x1="{imp_x}" y1="{imp_y - 12}" x2="{imp_x}" y2="{imp_y + 12}" stroke="#22c55e" stroke-width="1.5" />

    <!-- Azimuth Heading Arrow (Due West 270º) -->
    <g transform="translate({ksc_x - 30}, {ksc_y})">
        <line x1="25" y1="0" x2="0" y2="0" stroke="#38bdf8" stroke-width="2.5" />
        <polyline points="8,-4 0,0 8,4" fill="none" stroke="#38bdf8" stroke-width="2.5" />
        <text x="12" y="-8" fill="#38bdf8" font-size="9" font-weight="bold" text-anchor="middle">HDG 270º (WEST)</text>
    </g>

    <!-- ==================== OFFICIAL KAA HEADER BLOCK ==================== -->
    <rect x="50" y="25" width="{width-100}" height="70" fill="#0f172a" stroke="#334155" stroke-width="1.5" rx="4" />
    
    <circle cx="85" cy="60" r="22" fill="#1e293b" stroke="#38bdf8" stroke-width="2" />
    <text x="85" y="57" fill="#38bdf8" font-size="11" font-weight="bold" text-anchor="middle">KAA</text>
    <text x="85" y="69" fill="#94a3b8" font-size="7" text-anchor="middle">OFFICIAL</text>

    <text x="120" y="48" fill="#f8fafc" font-size="13" font-weight="bold">KERBAL AVIATION ADMINISTRATION (KAA) — AIRSPACE &amp; SURFACE HAZARD NOTAM</text>
    <text x="120" y="65" fill="#38bdf8" font-size="11">MISSION: CSA-09 EQUATORIAL CONTINENTAL FLIGHT CORRIDOR</text>
    <text x="120" y="80" fill="#94a3b8" font-size="9">NOTAM ID: KAA-CSA09-2026-10 | LAUNCH WINDOW: Y1-D91 | CORRIDOR: DUE WEST (270º AZIMUTH)</text>

    <!-- Status Stamp -->
    <rect x="{width-220}" y="37" width="155" height="46" fill="#14532d" stroke="#22c55e" stroke-width="1.5" rx="3" />
    <text x="{width-142}" y="55" fill="#f0fdf4" font-size="10" font-weight="bold" text-anchor="middle">ACTIVE FLIGHT NOTAM</text>
    <text x="{width-142}" y="71" fill="#86efac" font-size="8" text-anchor="middle">INLAND RECOVERY APPROVED</text>

    <!-- Bottom Notice Cards -->
    <rect x="50" y="{height-110}" width="420" height="52" fill="#0f172a" stroke="#334155" stroke-width="1" rx="4" opacity="0.95" />
    <text x="60" y="{height-94}" fill="#e2e8f0" font-size="9" font-weight="bold">EQUATORIAL CORRIDOR SAFETY DIRECTIVE:</text>
    <text x="60" y="{height-80}" fill="#94a3b8" font-size="8">• Aircraft in sector 0º Equator (Lon -75º to -145º) clear altitude FL200+ during T+0 to T+15m.</text>
    <text x="60" y="{height-68}" fill="#94a3b8" font-size="8">• All debris and payload impacts restricted to 100% uninhabited continental wilderness.</text>

    <rect x="{width-390}" y="{height-110}" width="340" height="52" fill="#0f172a" stroke="#334155" stroke-width="1" rx="4" opacity="0.95" />
    <text x="{width-380}" y="{height-94}" fill="#e2e8f0" font-size="9" font-weight="bold">CORIOLIS EXPLOITATION STRATEGY:</text>
    <text x="{width-380}" y="{height-80}" fill="#cbd5e1" font-size="8">• Kerbin's 174.5 m/s Eastward spin offsets ground track 149 km deeper inland.</text>
    <text x="{width-380}" y="{height-68}" fill="#86efac" font-size="8">• Guarantees zero maritime water exposure for soft parachute recovery.</text>
</svg>
"""
    
    os.makedirs("assets", exist_ok=True)
    out_file = "assets/csa-09_faa_hazard_map.svg"
    with open(out_file, "w") as f:
        f.write(svg)
    print(f"[✓] Official KAA Hazard Map for CSA-09 generated at: {out_file}")

if __name__ == "__main__":
    generate_faa_hazard_map_csa09()
