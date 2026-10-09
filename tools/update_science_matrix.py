#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Science Matrix Generator
Parses KSP persistent.sfs to extract Kerbalism / R&D science progress.
Generates:
1. VitePress web dashboard (science/index.md) with visual progress bars and mission planning targets.
2. Excel-compatible CSV matrix (science/kerbin_science_matrix.csv) for offline spreadsheet planning.
"""

import os
import re
import csv
import argparse

SAVE_PATH = "/media/steam_games/SteamLibrary/steamapps/common/Kerbal Space Program/saves/Corolt Space Agency/persistent.sfs"
DOCS_DIR = "/home/pablo-cortes/Documents/Corolt_Space_Agency"

EXPERIMENT_LABELS = {
    "barometerScan": "Registración de la Presión Atmosférica (Barómetro PresMat)",
    "temperatureScan": "Exploración de temperatura (Termómetro 2HOT)",
    "SRExperiment01": "Meteorological Experiments (Meteorological Survey Package)",
    "SRExperiment02": "Aeronomical Experiments (Aeronomy Sensor Array)",
    "SRExperiment03": "Estudio de Materiales (Materials Study Mini-Lab)",
    "SRExperiment04": "Engineering Experiments (Engineering Payload)",
    "kerbalism_TELEMETRY": "Informe de telemetría (Avionics Package)",
    "geigerCounter": "Escaneo de radiación (Contador Geiger)",
    "mysteryGoo": "Misterio Goo (Mystery Goo)",
    "mobileMaterialsLab": "Bahía de Materiales (Science Jr.)",
    "crewReport": "Informe de tripulación (Crew Report)",
    "evaReport": "Informe de AEV (EVA Report)",
    "recovery": "Recuperación de la nave (Vessel Recovery)"
}

BIOMES = [
    ("Shores", "Shores"),
    ("Grasslands", "Grasslands"),
    ("Highlands", "Highlands"),
    ("Mountains", "Mountains"),
    ("Water", "Water (Ocean)"),
    ("Deserts", "Deserts"),
    ("Badlands", "Badlands"),
    ("Tundra", "Tundra"),
    ("IceCaps", "Ice Caps")
]

SITUATIONS = [
    ("SrfLanded", "Surface (Landed)"),
    ("SrfSplashed", "Surface (Splashed / Ocean)"),
    ("FlyingLow", "Low Atmosphere (0 - 18 km)"),
    ("FlyingHigh", "Upper Atmosphere (18 - 70 km)"),
    ("InSpaceLow", "Low Space (70 - 250 km)"),
    ("InSpaceHigh", "High Space (> 250 km / Van Allen)")
]

def parse_science_from_save(sfs_file=SAVE_PATH):
    if not os.path.exists(sfs_file):
        print(f"Error: Save file not found at {sfs_file}")
        return {}

    with open(sfs_file, 'r', errors='ignore') as f:
        text = f.read()

    rd_idx = text.find('name = ResearchAndDevelopment\n')
    if rd_idx == -1:
        return {}
    rd_end = text.find('SCENARIO\n\t{', rd_idx + 1)
    if rd_end == -1:
        rd_end = len(text)
    rd_block = text[rd_idx:rd_end]

    science_data = {}
    for m in re.finditer(r'Science\s*\{([^}]+)\}', rd_block):
        block = m.group(1)
        id_m = re.search(r'id = ([^\n\r]+)', block)
        sci_m = re.search(r'sci = ([^\n\r]+)', block)
        cap_m = re.search(r'cap = ([^\n\r]+)', block)
        title_m = re.search(r'title = ([^\n\r]+)', block)

        if id_m and sci_m and cap_m:
            sid = id_m.group(1).strip()
            sci = float(sci_m.group(1).strip())
            cap = float(cap_m.group(1).strip())
            title = title_m.group(1).strip() if title_m else sid
            science_data[sid] = {
                "sci": sci,
                "cap": cap,
                "pct": (sci / cap * 100.0) if cap > 0 else 0.0,
                "title": title
            }
    return science_data

def build_matrix(science_data):
    rows = []
    
    # 1. Registered subjects in save
    for sid, d in sorted(science_data.items()):
        if not sid.startswith("recovery@"):
            parts = sid.split('@Kerbin')
            exp_key = parts[0]
            context = parts[1] if len(parts) > 1 else ""
        else:
            exp_key = "recovery"
            context = sid.replace("recovery@Kerbin", "")

        exp_name = EXPERIMENT_LABELS.get(exp_key, exp_key)

        # Detect situation & biome
        sit_found = "Other"
        for s_code, s_name in SITUATIONS:
            if s_code in context:
                sit_found = s_name
                context = context.replace(s_code, "")
                break

        biome_found = "Global"
        for b_code, b_name in BIOMES:
            if b_code in context:
                biome_found = b_name
                break

        pct = d["pct"]
        rem = max(0.0, d["cap"] - d["sci"])
        
        status = "Completed (100%)" if pct >= 99.5 else (f"In Progress ({pct:.1f}%)" if pct > 0 else "Pending (0%)")

        rows.append({
            "id": sid,
            "experiment": exp_name,
            "situation": sit_found,
            "biome": biome_found,
            "points_earned": round(d["sci"], 2),
            "points_cap": round(d["cap"], 2),
            "points_remaining": round(rem, 2),
            "percentage": round(pct, 1),
            "status": status
        })

    # 2. Add high-priority unstarted opportunities for Kerbin
    unstarted_keys = [
        # Water biome targets (high priority for ocean splashdown)
        ("barometerScan@KerbinSrfSplashedWater", "Atmospheric Pressure (PresMat)", "Surface (Splashed / Ocean)", "Water (Ocean)", 1.62),
        ("temperatureScan@KerbinSrfSplashedWater", "Temperature (2HOT)", "Surface (Splashed / Ocean)", "Water (Ocean)", 0.54),
        ("SRExperiment01@KerbinSrfSplashedWater", "Meteorology (SR.Payload.01)", "Surface (Splashed / Ocean)", "Water (Ocean)", 0.72),
        ("SRExperiment02@KerbinSrfSplashedWater", "Aeronomy (SR.Payload.02)", "Surface (Splashed / Ocean)", "Water (Ocean)", 0.72),
        ("barometerScan@KerbinFlyingLowWater", "Atmospheric Pressure (PresMat)", "Low Atmosphere (0 - 18 km)", "Water (Ocean)", 3.78),
        ("temperatureScan@KerbinFlyingLowWater", "Temperature (2HOT)", "Low Atmosphere (0 - 18 km)", "Water (Ocean)", 1.26),
        ("SRExperiment01@KerbinFlyingLowWater", "Meteorology (SR.Payload.01)", "Low Atmosphere (0 - 18 km)", "Water (Ocean)", 1.68),
        # Space targets (Corolt-III targets)
        ("barometerScan@KerbinInSpaceLow", "Atmospheric Pressure (PresMat)", "Low Space (70 - 250 km)", "Global", 5.40),
        ("geigerCounter@KerbinFlyingLow", "Radiation & Geiger (Kerbalism)", "Low Atmosphere (0 - 18 km)", "Global", 2.50),
        ("geigerCounter@KerbinFlyingHigh", "Radiation & Geiger (Kerbalism)", "Upper Atmosphere (18 - 70 km)", "Global", 3.20),
        ("geigerCounter@KerbinInSpaceLow", "Radiation & Geiger (Kerbalism)", "Low Space (70 - 250 km)", "Global", 4.50),
        ("geigerCounter@KerbinInSpaceHigh", "Radiation & Geiger (Kerbalism)", "High Space (> 250 km / Van Allen)", "Global", 6.00),
    ]

    existing_ids = {r["id"] for r in rows}
    for sid, exp_name, sit, biome, cap in unstarted_keys:
        if sid not in existing_ids:
            rows.append({
                "id": sid,
                "experiment": exp_name,
                "situation": sit,
                "biome": biome,
                "points_earned": 0.0,
                "points_cap": cap,
                "points_remaining": cap,
                "percentage": 0.0,
                "status": "Pending (0%)"
            })

    return rows

def generate_csv(rows, csv_path):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    fieldnames = [
        "experiment", "situation", "biome",
        "points_earned", "points_cap", "points_remaining",
        "percentage", "status", "id"
    ]
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    print(f"[✓] CSV spreadsheet saved to: {csv_path}")

def generate_markdown(rows, md_path):
    os.makedirs(os.path.dirname(md_path), exist_ok=True)

    total_pts = sum(r["points_earned"] for r in rows)
    total_cap = sum(r["points_cap"] for r in rows)
    total_rem = sum(r["points_remaining"] for r in rows)
    global_pct = (total_pts / total_cap * 100.0) if total_cap > 0 else 0.0

    completed_count = sum(1 for r in rows if r["percentage"] >= 99.5)
    in_progress_count = sum(1 for r in rows if 0.0 < r["percentage"] < 99.5)
    unstarted_count = sum(1 for r in rows if r["percentage"] == 0.0)

    # Sort rows by remaining points descending
    sorted_rows = sorted(rows, key=lambda x: x["points_remaining"], reverse=True)

    lines = [
        "# 🔬 Kerbin Science Matrix & Research Status",
        "",
        "> *«Ad Astra Per Scientiam» — Mission planning and experiment tracking console for the Corolt Space Agency (CSA).* ",
        "",
        f"*Data automatically synchronized from official career save (`saves/Corolt Space Agency/persistent.sfs`).*",
        "",
        "---",
        "",
        "## 📊 Global Science Indicators",
        "",
        f"| Key Metric | Value Achieved | Details |",
        f"| :--- | :--- | :--- |",
        f"| **Science Points Earned** | **`{total_pts:.2f} pts`** | Science transmitted or recovered at KSC |",
        f"| **Identified Science Potential** | **`{total_cap:.2f} pts`** | Cumulative Kerbin ceiling |",
        f"| **Points Available to Yield** | **`{total_rem:.2f} pts`** | Immediate reachable opportunities |",
        f"| **Overall Kerbin Progress** | **`{global_pct:.1f}%`** | Sampling completion rate |",
        f"| **Experiment Status** | ✅ {completed_count} completed | ⏳ {in_progress_count} in progress &#124; ❌ {unstarted_count} pending |",
        "",
        "```text",
        f"OVERALL PROGRESS: [{'=' * int(global_pct // 5)}{' ' * (20 - int(global_pct // 5))}] {global_pct:.1f}% ({total_pts:.1f}/{total_cap:.1f} pts)",
        "```",
        "",
        "---",
        "",
        "## 🎯 High-Yield Scientific Objectives (For Upcoming Missions)",
        "",
        "Priority pending experiments that maximize scientific return for the CSA fleet:",
        "",
        "| Experiment | Situation | Biome | Remaining Points | Current Status |",
        "| :--- | :--- | :--- | :---: | :---: |"
    ]

    for r in sorted_rows[:12]:
        badge = "🟩 100%" if r["percentage"] >= 99.5 else (f"🟨 {r['percentage']:.1f}%" if r["percentage"] > 0 else "⬜ 0%")
        lines.append(f"| **{r['experiment']}** | {r['situation']} | `{r['biome']}` | **+{r['points_remaining']:.2f} pts** | {badge} |")

    lines.extend([
        "",
        "---",
        "",
        "## 📋 Complete Experiment Matrix",
        "",
        "Download the full dataset in CSV format for **Excel or LibreOffice Calc**: [`kerbin_science_matrix.csv`](./kerbin_science_matrix.csv).",
        "",
        "| Experiment | Situation | Biome | Points (Earned / Cap) | Status & Progress |",
        "| :--- | :--- | :--- | :---: | :---: |"
    ])

    for r in sorted_rows:
        badge = "🟩 Completed" if r["percentage"] >= 99.5 else (f"🟨 {r['percentage']:.1f}%" if r["percentage"] > 0 else "⬜ Pending")
        lines.append(f"| **{r['experiment']}** | {r['situation']} | `{r['biome']}` | **{r['points_earned']:.2f}** / {r['points_cap']:.2f} | {badge} |")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")

    print(f"[✓] VitePress Markdown saved to: {md_path}")

def main():
    parser = argparse.ArgumentParser(description="Corolt Space Agency Science Matrix Updater")
    parser.add_argument("--save", default=SAVE_PATH, help="Path to persistent.sfs save file")
    args = parser.parse_args()

    print("================================================================================")
    print("       COROLT SPACE AGENCY (CSA) - SCIENCE TRACKING MATRIX                     ")
    print("================================================================================")
    
    data = parse_science_from_save(args.save)
    rows = build_matrix(data)
    
    csv_file = os.path.join(DOCS_DIR, "science", "kerbin_science_matrix.csv")
    md_file = os.path.join(DOCS_DIR, "science", "index.md")

    generate_csv(rows, csv_file)
    generate_markdown(rows, md_file)
    print("================================================================================")

if __name__ == "__main__":
    main()
