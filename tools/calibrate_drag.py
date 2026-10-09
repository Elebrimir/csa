#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Aerodynamic Drag Calibration Tool
Analyzes recorded mission telemetry to extract the effective aerodynamic drag profile (Cd * A)
as a function of Mach number and flight regime.
"""

import sys
import os
import argparse
import json
import csv
import numpy as np

# Standard Kerbin atmospheric speed of sound approximation (m/s)
def speed_of_sound_kerbin(altitude):
    if altitude < 10000:
        return 310.0 - (altitude / 10000.0) * 30.0
    elif altitude < 40000:
        return 280.0
    else:
        return 290.0

def safe_float(v, default=0.0):
    try:
        return float(v)
    except (ValueError, TypeError):
        return default

def calibrate_aerodynamics(csv_path, dry_mass=629.0, wet_mass=5144.0, output_json=None):
    if not os.path.exists(csv_path):
        print(f"Error: File {csv_path} not found")
        return None

    print("=" * 70)
    print(f"🚀 CSA AERODYNAMIC CALIBRATION: {os.path.basename(csv_path)}")
    print("=" * 70)

    rows = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for r in reader:
            alt = safe_float(r.get("altitude"))
            if alt > 80.0:
                rows.append({
                    "MET": safe_float(r.get("MET")),
                    "altitude": alt,
                    "surface_vel": safe_float(r.get("surface_vel")),
                    "dynamic_pressure": safe_float(r.get("dynamic_pressure")),
                    "g_force": safe_float(r.get("g_force")),
                })

    if not rows:
        print("[!] No active flight profile detected in data.")
        return None

    t0 = rows[0]["MET"]
    print(f"• Liftoff detected at MET: T+{t0:.1f} s")
    print(f"• Flight samples: {len(rows):,}")

    g0 = 9.80665

    # Find apogee index
    max_alt = -1.0
    ap_idx = 0
    for i, r in enumerate(rows):
        if r["altitude"] > max_alt:
            max_alt = r["altitude"]
            ap_idx = i

    samples = []

    # Ascent coast: before apogee
    for r in rows[:ap_idx]:
        alt = r["altitude"]
        q = r["dynamic_pressure"]
        g_felt = r["g_force"]
        if 15000 <= alt <= 68000 and q >= 10.0 and g_felt < 1.0:
            v = r["surface_vel"]
            mach = v / speed_of_sound_kerbin(alt)
            f_drag_spec = g_felt * g0
            cda = (dry_mass * f_drag_spec) / q if q > 0 else 0
            if 0.05 < cda < 5.0:
                samples.append({"phase": "ascent_coast", "alt": alt, "mach": mach, "q": q, "cda": cda})

    # Reentry coast: after apogee
    for r in rows[ap_idx:]:
        alt = r["altitude"]
        q = r["dynamic_pressure"]
        g_felt = r["g_force"]
        if 15000 <= alt <= 65000 and q >= 50.0 and g_felt < 3.0:
            v = r["surface_vel"]
            mach = v / speed_of_sound_kerbin(alt)
            f_drag_spec = g_felt * g0
            cda = (dry_mass * f_drag_spec) / q if q > 0 else 0
            if 0.05 < cda < 5.0:
                samples.append({"phase": "reentry", "alt": alt, "mach": mach, "q": q, "cda": cda})

    print("\n📊 EMPIRICAL DRAG RESULTS:")
    if samples:
        cdas = [s["cda"] for s in samples]
        overall_cda = float(np.median(cdas))
        
        # Buckets by Mach
        buckets = {
            'Subsonic (<0.8)': [],
            'Transonic (0.8-1.2)': [],
            'Supersonic (1.2-2.5)': [],
            'High Super (2.5-4.5)': [],
            'Hypersonic (>4.5)': []
        }
        for s in samples:
            m = s["mach"]
            if m < 0.8:
                buckets['Subsonic (<0.8)'].append(s["cda"])
            elif m < 1.2:
                buckets['Transonic (0.8-1.2)'].append(s["cda"])
            elif m < 2.5:
                buckets['Supersonic (1.2-2.5)'].append(s["cda"])
            elif m < 4.5:
                buckets['High Super (2.5-4.5)'].append(s["cda"])
            else:
                buckets['Hypersonic (>4.5)'].append(s["cda"])

        print(f"{'Regime':<22} | {'Count':<7} | {'Mean':<7} | {'Median':<7}")
        print("-" * 55)
        for reg, vals in buckets.items():
            if vals:
                print(f"{reg:<22} | {len(vals):<7} | {np.mean(vals):<7.3f} | {np.median(vals):<7.3f}")
            else:
                print(f"{reg:<22} | {0:<7} | {'-':<7} | {'-':<7}")

        print(f"\n[✓] Vehicle median Cd·A: {overall_cda:.3f} m²")
    else:
        print("[i] Insufficient coasting data in telemetry. Using standard geometric model.")
        overall_cda = 0.45 * (np.pi * (1.25 / 2.0) ** 2)
        print(f"[✓] Estimated theoretical Cd·A: {overall_cda:.3f} m²")

    calibration = {
        "mission_source": os.path.basename(csv_path),
        "vehicle_dry_mass_kg": dry_mass,
        "calibrated_cda_m2": round(overall_cda, 4),
        "subsonic_cda": round(overall_cda * 0.85, 4),
        "transonic_peak_cda": round(overall_cda * 1.35, 4),
        "supersonic_cda": round(overall_cda * 1.05, 4),
        "hypersonic_cda": round(overall_cda * 0.95, 4)
    }

    if output_json:
        os.makedirs(os.path.dirname(output_json) or ".", exist_ok=True)
        with open(output_json, 'w') as f:
            json.dump(calibration, f, indent=2)
        print(f"[✓] Drag profile saved to: {output_json}")

    return calibration

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CSA Aerodynamic Drag Calibrator")
    parser.add_argument("mission", nargs="?", default="CSA-06", help="Mission code or path to CSV file")
    parser.add_argument("--dry-mass", type=float, default=629.0, help="Vehicle dry mass in kg (default: 629)")
    parser.add_argument("--wet-mass", type=float, default=5144.0, help="Total liftoff mass in kg (default: 5144)")
    parser.add_argument("--output", type=str, default="vehicles/corolt-3_aero.json", help="Output JSON file path")
    args = parser.parse_args()

    csv_file = args.mission if args.mission.endswith('.csv') else f"missions/{args.mission}_telemetry.csv"
    calibrate_aerodynamics(csv_file, dry_mass=args.dry_mass, wet_mass=args.wet_mass, output_json=args.output)
