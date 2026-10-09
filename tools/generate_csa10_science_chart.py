#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Mission CSA-10 Science Data & Power Execution Chart
Generates an SVG chart detailing:
1. Active Scientific Experiments executed during flight and post-touchdown
2. Battery discharge & reserve management (800 EC total bank)
3. Biome and environmental regime progression (Low Atmo -> Upper Atmo -> Low Space -> Mountains)
"""

def generate_science_chart():
    width, height = 960, 560
    
    experiments = [
        {"name": "Bahía de Materiales (Mini-Lab)", "regime": "En ejecució (Mountains)", "yield": "+10.8 pts", "status": "COMPLETED", "color": "#38bdf8"},
        {"name": "Baròmetre PresMat", "regime": "Exploración Presión (Mountains)", "yield": "+4.9 pts", "status": "COMPLETED", "color": "#f59e0b"},
        {"name": "Contador Geiger (Kerbalism)", "regime": "Escaneo Radiación (Low Space / Mountains)", "yield": "+4.5 pts", "status": "COMPLETED", "color": "#a855f7"},
        {"name": "Termòmetre 2HOT", "regime": "Exploración Temperatura (Mountains)", "yield": "+3.5 pts", "status": "COMPLETED", "color": "#ef4444"},
        {"name": "Aeronomy Sensor Array", "regime": "Aeronomical Experiments (Atmo/Ground)", "yield": "+2.2 pts", "status": "COMPLETED", "color": "#10b981"},
        {"name": "Engineering Test Bay", "regime": "Engineering Experiments (Mountains)", "yield": "+2.2 pts", "status": "COMPLETED", "color": "#ec4899"},
        {"name": "Meteorological Survey Package", "regime": "Meteorological Experiments (Mountains)", "yield": "+2.2 pts", "status": "COMPLETED", "color": "#6366f1"},
    ]

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" style="background:#090d16; font-family:'Courier New', monospace;">
    <rect width="{width}" height="{height}" fill="#090d16" />
    <rect x="0" y="0" width="{width}" height="45" fill="#0f172a" />
    <text x="25" y="28" fill="#38bdf8" font-size="15" font-weight="bold">COROLT SPACE AGENCY // CSA-10 SCIENTIFIC PAYLOAD HARVEST &amp; EXPERIMENTS</text>
    <text x="730" y="28" fill="#10b981" font-size="12" font-weight="bold">TOTAL YIELD: +30.3 pts SCIENCE</text>

    <!-- Main Table Container -->
    <rect x="50" y="65" width="{width-100}" height="280" fill="#0b1120" stroke="#334155" stroke-width="1.2" rx="4"/>
    <text x="70" y="95" fill="#94a3b8" font-size="11" font-weight="bold">EXPERIMENT / SENSOR</text>
    <text x="400" y="95" fill="#94a3b8" font-size="11" font-weight="bold">REGIME / BIOME</text>
    <text x="680" y="95" fill="#94a3b8" font-size="11" font-weight="bold">ESTIMATED HARVEST</text>
    <text x="830" y="95" fill="#94a3b8" font-size="11" font-weight="bold">STATUS</text>
    <line x1="50" y1="108" x2="{width-50}" y2="108" stroke="#334155" stroke-width="1"/>
"""

    y = 135
    for exp in experiments:
        svg += f"""
    <circle cx="65" cy="{y-4}" r="4" fill="{exp['color']}"/>
    <text x="80" y="{y}" fill="#f8fafc" font-size="11">{exp['name']}</text>
    <text x="400" y="{y}" fill="#94a3b8" font-size="11">{exp['regime']}</text>
    <text x="680" y="{y}" fill="#22c55e" font-size="11" font-weight="bold">{exp['yield']}</text>
    <text x="830" y="{y}" fill="#38bdf8" font-size="11" font-weight="bold">{exp['status']}</text>
"""
        y += 32

    # Lower Panel: Battery & Environmental Progression
    svg += f"""
    <rect x="50" y="365" width="410" height="150" fill="#0b1120" stroke="#334155" stroke-width="1.2" rx="4"/>
    <text x="65" y="390" fill="#facc15" font-size="12" font-weight="bold">ELECTRICAL POWER CONSUMPTION PROFILE</text>
    <text x="65" y="415" fill="#f8fafc" font-size="11">• Total Capacity: 800.0 EC (4x Radial Truss Packs)</text>
    <text x="65" y="435" fill="#f8fafc" font-size="11">• Liftoff to Space Coast: 795.2 EC -> 792.4 EC</text>
    <text x="65" y="455" fill="#f8fafc" font-size="11">• Atmospheric Entry: 349.0 EC (43.7% reserve)</text>
    <text x="65" y="475" fill="#f8fafc" font-size="11">• Post-Touchdown Science Run: Continuous drain at 0.05 EC/s</text>
    <text x="65" y="495" fill="#22c55e" font-size="11" font-weight="bold">✓ Avionics &amp; Recovery Chute safely powered at 100%</text>

    <rect x="500" y="365" width="410" height="150" fill="#0b1120" stroke="#334155" stroke-width="1.2" rx="4"/>
    <text x="515" y="390" fill="#38bdf8" font-size="12" font-weight="bold">ENVIRONMENTAL REGIMES SAMPLED</text>
    <text x="515" y="415" fill="#f8fafc" font-size="11">1. Shores (Launch Pad, Elev 79m)</text>
    <text x="515" y="435" fill="#f8fafc" font-size="11">2. Upper Atmosphere (Supersonic climb 25-50 km)</text>
    <text x="515" y="455" fill="#f8fafc" font-size="11">3. Low Space Microgravity (Vacuum 70 - 162.65 km)</text>
    <text x="515" y="475" fill="#22c55e" font-size="11" font-weight="bold">4. Kerbin Mountains (Landing site, Elev 1,584m)</text>
    <text x="515" y="495" fill="#94a3b8" font-size="11">New Mountain science recovered for R&amp;D unlocks!</text>

    <!-- Footer -->
    <rect x="0" y="{height-25}" width="{width}" height="25" fill="#020617" />
    <text x="25" y="{height-8}" fill="#64748b" font-size="10">COROLT SPACE AGENCY // MISSION CSA-10 POST-FLIGHT HARVEST // DATA READY FOR TECH TREE ACQUISITIONS</text>
</svg>
"""

    out = "assets/csa-10_science_harvest_dashboard.svg"
    with open(out, "w") as f: f.write(svg)
    print(f"[✓] Science Harvest Chart generated: {out}")

if __name__ == "__main__":
    generate_science_chart()
