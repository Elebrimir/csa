#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - KAA Spaceflight Clearance & Orbital Insertion Map for Mission CSA-16
Generates an official FAA/KAA-style Commercial Space Transportation Clearance Notice
showing the Equatorial Launch Corridor, SRB Drop Sector, Stage 1 Core Disposal Zone,
and the successful Orbital Insertion Arc into the 600x600 km MKO Constellation Plane (Node 0 Foundation Anchor).
"""

def generate_kaa_clearance_map():
    width = 1000
    height = 640

    lon_min, lon_max = -90.0, 50.0
    lat_min, lat_max = -20.0, 20.0

    def project(lon, lat):
        x = 60 + ((lon - lon_min) / (lon_max - lon_min)) * (width - 120)
        y = height - 60 - ((lat - lat_min) / (lat_max - lat_min)) * (height - 120)
        return x, y

    # Key Points from CSA-16 Ascent Ground Track
    ksc_lon, ksc_lat = -74.558, -0.097
    ksc_x, ksc_y = project(ksc_lon, ksc_lat)

    srb_lon, srb_lat = -74.491, -0.099
    srb_x, srb_y = project(srb_lon, srb_lat)

    core_lon, core_lat = -71.437, -0.099
    core_x, core_y = project(core_lon, core_lat)

    seco1_lon, seco1_lat = -54.666, -0.085
    seco1_x, seco1_y = project(seco1_lon, seco1_lat)

    seco2_lon, seco2_lat = 18.299, 0.079
    seco2_x, seco2_y = project(seco2_lon, seco2_lat)

    deorbit_lon, deorbit_lat = 23.904, 0.093
    deorbit_x, deorbit_y = project(deorbit_lon, deorbit_lat)

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

    <!-- Grid lines -->
    <rect width="{width}" height="{height}" fill="#0b1120" />

    <!-- Header Block -->
    <rect x="0" y="0" width="{width}" height="55" fill="#0f172a" stroke="#334155" stroke-width="1.2" />
    <text x="25" y="32" fill="#38bdf8" font-size="16" font-weight="bold">KERBAL AVIATION ADMINISTRATION (KAA) // SPACE CLEARANCE NOTICE</text>
    <text x="700" y="32" fill="#10b981" font-size="12" font-weight="bold">STATUS: MKO ORBIT ACHIEVED</text>

    <!-- Subheader -->
    <text x="25" y="47" fill="#94a3b8" font-size="10">NOTAM: KAA-CSA16-2026-16 // MISSION CSA-16 (COROLT-IV B #6) // EQUATORIAL CORRIDOR 090.0º</text>

    <!-- Map Grid -->
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
    <text x="{srb_x-22:.1f}" y="{srb_y+42:.1f}" fill="#94a3b8" font-size="8">T+46.7s Maritime Sector</text>

    <!-- Zone 2: Stage 1 Core MECO Impact -->
    <rect x="{core_x-45:.1f}" y="{core_y-40:.1f}" width="90" height="80" fill="url(#hazardHatchRed)" stroke="#ef4444" stroke-width="1.5" opacity="0.85" />
    <text x="{core_x-40:.1f}" y="{core_y-46:.1f}" fill="#ef4444" font-size="9" font-weight="bold">ZONE 2: CORE DISPOSAL</text>
    <text x="{core_x-40:.1f}" y="{core_y+52:.1f}" fill="#94a3b8" font-size="8">Etoh-140-TU Impact Sector</text>

    <!-- Flight Trajectory Ground Track -->
    <path d="M {ksc_x:.1f},{ksc_y:.1f} L {srb_x:.1f},{srb_y:.1f} L {core_x:.1f},{core_y:.1f} L {seco1_x:.1f},{seco1_y:.1f} L {seco2_x:.1f},{seco2_y:.1f} L {deorbit_x:.1f},{deorbit_y:.1f} L {width-60},{deorbit_y:.1f}"
          fill="none" stroke="#10b981" stroke-width="3" filter="url(#glow)" />

    <!-- Trajectory Points -->
    <!-- KSC -->
    <circle cx="{ksc_x:.1f}" cy="{ksc_y:.1f}" r="5" fill="#38bdf8" />
    <text x="{ksc_x-50:.1f}" y="{ksc_y-12:.1f}" fill="#38bdf8" font-size="11" font-weight="bold">KSC PAD (74.6º W)</text>

    <!-- SECO-1 -->
    <circle cx="{seco1_x:.1f}" cy="{seco1_y:.1f}" r="4" fill="#a855f7" />
    <text x="{seco1_x-25:.1f}" y="{seco1_y-14:.1f}" fill="#a855f7" font-size="10">SECO-1 (Ap 600.1 km)</text>

    <!-- SECO-2 -->
    <circle cx="{seco2_x:.1f}" cy="{seco2_y:.1f}" r="5" fill="#10b981" />
    <text x="{seco2_x-55:.1f}" y="{seco2_y-14:.1f}" fill="#10b981" font-size="11" font-weight="bold">SECO-2 (T+1367s CIRC)</text>

    <!-- Deployment Zone -->
    <circle cx="{deorbit_x:.1f}" cy="{deorbit_y:.1f}" r="5" fill="#06b6d4" />
    <text x="{deorbit_x-65:.1f}" y="{deorbit_y+24:.1f}" fill="#06b6d4" font-size="11" font-weight="bold">COROLTSAT-1F NODE 0 LOCK</text>
    <text x="{deorbit_x-65:.1f}" y="{deorbit_y+36:.1f}" fill="#94a3b8" font-size="9">601.1 x 598.9 km // i=0.08º // Stage 2 Deorbit Pe=-1.75 km</text>

    <!-- Telemetry Box / Compliance Legend -->
    <rect x="60" y="{height-140}" width="480" height="70" fill="#0f172a" stroke="#334155" stroke-width="1" />
    <text x="75" y="{height-120}" fill="#38bdf8" font-size="11" font-weight="bold">MISSION PARAMETERS &amp; KAA COMPLIANCE:</text>
    <text x="75" y="{height-102}" fill="#94a3b8" font-size="10">• Launch Azimuth: 090.0º Due East | Orbital Inclination: 0.08º (Equatorial)</text>
    <text x="75" y="{height-86}" fill="#10b981" font-size="10">• Exospheric Insertion: 100% Successful | Stage 2 Deorbited (Pe = -1.75 km)</text>

    <!-- Status Badge -->
    <rect x="{width-320}" y="{height-140}" width="260" height="70" fill="#064e3b" stroke="#10b981" stroke-width="1.5" />
    <text x="{width-300}" y="{height-115}" fill="#6ee7b7" font-size="12" font-weight="bold">ORBITAL CORRIDOR SECURED</text>
    <text x="{width-300}" y="{height-95}" fill="#a7f3d0" font-size="10">CoroltSat-1F (Node 0 MKO-600)</text>
    <text x="{width-300}" y="{height-80}" fill="#a7f3d0" font-size="9">KAA Clearance Verified (Y1-D196)</text>
</svg>
"""

    output_path = "/home/pablo-cortes/Documents/Corolt_Space_Agency/assets/csa-16_kaa_hazard_map.svg"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[✓] KAA clearance map generated: {output_path}")

if __name__ == "__main__":
    generate_kaa_clearance_map()
