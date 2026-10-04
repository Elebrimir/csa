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
import numpy as np
import pandas as pd

# Standard Kerbin atmospheric speed of sound approximation (m/s)
# At SL: ~310 m/s, upper atmo: ~280 m/s
def speed_of_sound_kerbin(altitude):
    if altitude < 10000:
        return 310.0 - (altitude / 10000.0) * 30.0
    elif altitude < 40000:
        return 280.0
    else:
        return 290.0

def calibrate_aerodynamics(csv_path, dry_mass=629.0, wet_mass=5144.0, output_json=None):
    if not os.path.exists(csv_path):
        print(f"Error: No s'ha trobat el fitxer {csv_path}")
        return None

    df = pd.read_csv(csv_path)
    print("=" * 70)
    print(f"🚀 CSA AERODYNAMIC CALIBRATION: {os.path.basename(csv_path)}")
    print("=" * 70)

    # 1. Filter out pre-launch pad idling
    flight = df[df['altitude'] > 80.0].copy()
    if flight.empty:
        print("[!] No s'ha detectat perfil de vol actiu a les dades.")
        return None

    t0 = flight['MET'].min()
    print(f"• Despegue detectat a MET: T+{t0:.1f} s")
    print(f"• Mostres en vol: {len(flight):,}")

    # Standard gravity constant
    g0 = 9.80665

    # Identify coasting in atmosphere (T=0, altitude between 10 km and 68 km, dynamic_pressure > 5 Pa)
    # During unpowered coast, G-meter measures purely aerodynamic drag: F_drag / m = g_force * g0
    # Dynamic pressure Q = dynamic_pressure (in Pa)
    # D = Cd * A * Q => Cd * A = (m * g_force * g0) / Q
    
    # Check if we have ascent coasting or descent coasting
    ap_idx = flight['altitude'].idxmax()
    ascent_coast = flight.loc[:ap_idx]
    ascent_coast = ascent_coast[(ascent_coast['altitude'] >= 15000) & 
                                (ascent_coast['altitude'] <= 68000) & 
                                (ascent_coast['dynamic_pressure'] >= 10.0) &
                                (ascent_coast['g_force'] < 1.0)] # thrust produces > 1.5G, coasting produces < 1.0G

    # Reentry coasting
    reentry = flight.loc[ap_idx:]
    reentry = reentry[(reentry['altitude'] >= 15000) & 
                      (reentry['altitude'] <= 65000) & 
                      (reentry['dynamic_pressure'] >= 50.0) &
                      (reentry['g_force'] < 3.0)]

    samples = []
    
    # Process ascent coast samples (vehicle mass ~ dry_mass + residual payload)
    for _, row in ascent_coast.iterrows():
        q = row['dynamic_pressure']
        g_felt = row['g_force']
        v = row['surface_vel']
        alt = row['altitude']
        mach = v / speed_of_sound_kerbin(alt)
        
        # specific drag force (N / kg)
        f_drag_spec = g_felt * g0
        # Cd * A = (mass * f_drag_spec) / Q
        cda = (dry_mass * f_drag_spec) / q if q > 0 else 0
        if 0.05 < cda < 5.0:
            samples.append({'phase': 'ascent_coast', 'alt': alt, 'mach': mach, 'q': q, 'cda': cda})

    # Process reentry samples
    for _, row in reentry.iterrows():
        q = row['dynamic_pressure']
        g_felt = row['g_force']
        v = row['surface_vel']
        alt = row['altitude']
        mach = v / speed_of_sound_kerbin(alt)
        
        f_drag_spec = g_felt * g0
        cda = (dry_mass * f_drag_spec) / q if q > 0 else 0
        if 0.05 < cda < 5.0:
            samples.append({'phase': 'reentry', 'alt': alt, 'mach': mach, 'q': q, 'cda': cda})

    results_df = pd.DataFrame(samples)
    
    print("\n📊 RESULTATS D'ARROSSEGAMENT EMPÍRIC:")
    if not results_df.empty:
        # Group by Mach buckets
        bins = [0, 0.8, 1.2, 2.5, 4.5, 8.0]
        labels = ['Subsonic (<0.8)', 'Transonic (0.8-1.2)', 'Supersonic (1.2-2.5)', 'High Super (2.5-4.5)', 'Hypersonic (>4.5)']
        results_df['regime'] = pd.cut(results_df['mach'], bins=bins, labels=labels)
        
        summary = results_df.groupby('regime', observed=False)['cda'].agg(['count', 'mean', 'std', 'median']).reset_index()
        print(summary.to_string(index=False))
        
        overall_cda = float(results_df['cda'].median())
        print(f"\n[✓] Valor medià de Cd·A del vehicle: {overall_cda:.3f} m²")
    else:
        # Fallback based on rocket geometry (1.25m diameter cone cylinder with 4 fins)
        print("[i] Dades de planatge insuficients al registre. Utilitzant model geomètric estàndard.")
        overall_cda = 0.45 * (np.pi * (1.25 / 2.0) ** 2) # ~0.55 m2
        print(f"[✓] Valor estimat teòric de Cd·A: {overall_cda:.3f} m²")

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
        print(f"[✓] Perfil de drag desat a: {output_json}")

    return calibration

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Calibrador de Drag Aerodinàmic CSA")
    parser.add_argument("mission", nargs="?", default="CSA-06", help="Codi de missió o ruta al fitxer CSV")
    parser.add_argument("--dry-mass", type=float, default=629.0, help="Massa seca del vehicle en kg (default: 629)")
    parser.add_argument("--wet-mass", type=float, default=5144.0, help="Massa total al llançament en kg (default: 5144)")
    parser.add_argument("--output", type=str, default="vehicles/corolt-3_aero.json", help="Fitxer JSON de sortida")
    args = parser.parse_args()

    csv_file = args.mission if args.mission.endswith('.csv') else f"missions/{args.mission}_telemetry.csv"
    calibrate_aerodynamics(csv_file, dry_mass=args.dry_mass, wet_mass=args.wet_mass, output_json=args.output)
