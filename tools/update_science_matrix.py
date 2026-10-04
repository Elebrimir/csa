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
    "barometerScan": "Pressió Atmosfèrica (PresMat)",
    "temperatureScan": "Temperatura (2HOT)",
    "SRExperiment01": "Meteorologia (SR.Payload.01)",
    "SRExperiment02": "Aeronomia (SR.Payload.02)",
    "SRExperiment03": "Sondeig Avançat (SR.Payload.03)",
    "SRExperiment04": "Enginyeria i Estrès (SR.Payload.04)",
    "kerbalism_TELEMETRY": "Telemetria de Nau (Kerbalism)",
    "geigerCounter": "Radiació i Geiger (Kerbalism)",
    "mysteryGoo": "Misteriós Goo",
    "mobileMaterialsLab": "Badia de Materials (Science Jr.)",
    "crewReport": "Informe de Tripulació",
    "evaReport": "Informe EVA",
    "recovery": "Recuperació de Nau"
}

BIOMES = [
    ("Shores", "Costas"),
    ("Grasslands", "Praderas"),
    ("Highlands", "Montes"),
    ("Mountains", "Montañas"),
    ("Water", "Agua (Oceà)"),
    ("Deserts", "Desiertos"),
    ("Badlands", "Páramo"),
    ("Tundra", "Tundra"),
    ("IceCaps", "Capas de Hielo")
]

SITUATIONS = [
    ("SrfLanded", "Superfície (Terra)"),
    ("SrfSplashed", "Superfície (Oceà / Aigua)"),
    ("FlyingLow", "Vol Baix (0 - 18 km)"),
    ("FlyingHigh", "Vol Alt (18 - 70 km)"),
    ("InSpaceLow", "Espai Baix (70 - 250 km)"),
    ("InSpaceHigh", "Espai Alt (> 250 km / Van Allen)")
]

def parse_science_from_save(sfs_file=SAVE_PATH):
    if not os.path.exists(sfs_file):
        print(f"Error: No s'ha trobat el fitxer {sfs_file}")
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
        sit_found = "Altres"
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
        
        status = "Completat (100%)" if pct >= 99.5 else (f"En Progrés ({pct:.1f}%)" if pct > 0 else "Pendent (0%)")

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
        # Water biome targets (super high priority for ocean splashdown)
        ("barometerScan@KerbinSrfSplashedWater", "Pressió Atmosfèrica (PresMat)", "Superfície (Oceà / Aigua)", "Agua (Oceà)", 1.62),
        ("temperatureScan@KerbinSrfSplashedWater", "Temperatura (2HOT)", "Superfície (Oceà / Aigua)", "Agua (Oceà)", 0.54),
        ("SRExperiment01@KerbinSrfSplashedWater", "Meteorologia (SR.Payload.01)", "Superfície (Oceà / Aigua)", "Agua (Oceà)", 0.72),
        ("SRExperiment02@KerbinSrfSplashedWater", "Aeronomia (SR.Payload.02)", "Superfície (Oceà / Aigua)", "Agua (Oceà)", 0.72),
        ("barometerScan@KerbinFlyingLowWater", "Pressió Atmosfèrica (PresMat)", "Vol Baix (0 - 18 km)", "Agua (Oceà)", 3.78),
        ("temperatureScan@KerbinFlyingLowWater", "Temperatura (2HOT)", "Vol Baix (0 - 18 km)", "Agua (Oceà)", 1.26),
        ("SRExperiment01@KerbinFlyingLowWater", "Meteorologia (SR.Payload.01)", "Vol Baix (0 - 18 km)", "Agua (Oceà)", 1.68),
        # Space targets (Corolt-III targets)
        ("barometerScan@KerbinInSpaceLow", "Pressió Atmosfèrica (PresMat)", "Espai Baix (70 - 250 km)", "Global", 5.40),
        ("geigerCounter@KerbinFlyingLow", "Radiació i Geiger (Kerbalism)", "Vol Baix (0 - 18 km)", "Global", 2.50),
        ("geigerCounter@KerbinFlyingHigh", "Radiació i Geiger (Kerbalism)", "Vol Alt (18 - 70 km)", "Global", 3.20),
        ("geigerCounter@KerbinInSpaceLow", "Radiació i Geiger (Kerbalism)", "Espai Baix (70 - 250 km)", "Global", 4.50),
        ("geigerCounter@KerbinInSpaceHigh", "Radiació i Geiger (Kerbalism)", "Espai Alt (> 250 km / Van Allen)", "Global", 6.00),
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
                "status": "Pendent (0%)"
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
    print(f"[✓] Full de càlcul CSV desat a: {csv_path}")

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
        "# 🔬 Matriu Científica i Estat de Recerca (Kerbin)",
        "",
        "> *«Ad Astra Per Scientiam» — Panell operatiu de seguiment d'experiments i planificació de missions de la Corolt Space Agency (CSA).*",
        "",
        f"*Dades sincronitzades automàticament des de la partida oficial (`saves/Corolt Space Agency/persistent.sfs`).*",
        "",
        "---",
        "",
        "## 📊 Indicadors Globals de Ciència",
        "",
        f"| Mètrica Clau | Valor Assolit | Detall |",
        f"| :--- | :--- | :--- |",
        f"| **Punts de Ciència Obtinguts** | **`{total_pts:.2f} pts`** | Ciència transmesa o recuperada a KSC |",
        f"| **Potencial de Ciència Identificat** | **`{total_cap:.2f} pts`** | Suma del sostre màxim de Kerbin |",
        f"| **Punts Disponibles per Guanyar** | **`{total_rem:.2f} pts`** | Punts pendents a l'abast immediat |",
        f"| **Progrés Global de Kerbin** | **`{global_pct:.1f}%`** | Grau de mostreig completat |",
        f"| **Estat d'Experiments** | ✅ {completed_count} completats | ⏳ {in_progress_count} en progrés &#124; ❌ {unstarted_count} pendents |",
        "",
        "```text",
        f"PROGRÉS GLOBAL: [{'=' * int(global_pct // 5)}{' ' * (20 - int(global_pct // 5))}] {global_pct:.1f}% ({total_pts:.1f}/{total_cap:.1f} pts)",
        "```",
        "",
        "---",
        "",
        "## 🎯 Objectius de Màxim Retorn Científic (Per a Noves Missions)",
        "",
        "Aquests són els experiments pendents que aporten el major nombre de punts per a la flota CSA:",
        "",
        "| Experiment | Situació | Bioma | Punts Restants | Estat Actual |",
        "| :--- | :--- | :--- | :---: | :---: |"
    ]

    for r in sorted_rows[:12]:
        badge = "🟩 100%" if r["percentage"] >= 99.5 else (f"🟨 {r['percentage']:.1f}%" if r["percentage"] > 0 else "⬜ 0%")
        lines.append(f"| **{r['experiment']}** | {r['situation']} | `{r['biome']}` | **+{r['points_remaining']:.2f} pts** | {badge} |")

    lines.extend([
        "",
        "---",
        "",
        "## 📋 Matriu Completa d'Experiments",
        "",
        "Pots descarregar el full complet en format CSV per obrir-lo a **Excel o LibreOffice Calc**: [`kerbin_science_matrix.csv`](./kerbin_science_matrix.csv).",
        "",
        "| Experiment | Situació | Bioma | Punts (Assolits / Sostre) | Estat & Progrés |",
        "| :--- | :--- | :--- | :---: | :---: |"
    ])

    for r in sorted_rows:
        badge = "🟩 Completat" if r["percentage"] >= 99.5 else (f"🟨 {r['percentage']:.1f}%" if r["percentage"] > 0 else "⬜ Pendent")
        lines.append(f"| **{r['experiment']}** | {r['situation']} | `{r['biome']}` | **{r['points_earned']:.2f}** / {r['points_cap']:.2f} | {badge} |")

    with open(md_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines) + "\n")

    print(f"[✓] Documentació VitePress Markdown desada a: {md_path}")

def main():
    parser = argparse.ArgumentParser(description="Actualitzador de la Matriu Científica CSA")
    parser.add_argument("--save", default=SAVE_PATH, help="Ruta al fitxer persistent.sfs")
    args = parser.parse_args()

    print("================================================================================")
    print("       COROLT SPACE AGENCY (CSA) - MATRIU DE SEGUIMENT CIENTÍFIC               ")
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
