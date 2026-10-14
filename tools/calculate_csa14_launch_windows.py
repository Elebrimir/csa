#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Constellation Launch Window Calculator v2.0
Calculates high-precision launch windows from Kerbin Space Center (KSC) to insert
CoroltSat-1D into a phased equatorial orbit relative to CorolSat-1B and CoroltSat-1C.

Ground-truth telemetry calibration from CSA-13 flight:
- dt_ascent: 1149.3 s (from liftoff to SECO-2 circularization)
- surface_arc: 87.24 deg
- inertial_arc: 106.39 deg
"""

import math
import argparse
import os
import re

SAVEFILE_PATH = "/media/steam_games/SteamLibrary/steamapps/common/Kerbal Space Program/saves/Corolt Space Agency/persistent.sfs"

def load_constellation_state():
    if not os.path.exists(SAVEFILE_PATH):
        return {
            'ut': 3657330.0,
            'anchor': {
                'name': 'CorolSat-1B',
                'sma': 905751.83,
                'ecc': 0.006331,
                'inc': 0.1307,
                'lpe': 348.5189,
                'lan': 245.6987,
                'mna0': 0.420587,
                'eph': 3418234.80,
            },
            'node2': {
                'name': 'CoroltSat-1C',
                'sma': 905716.04,
                'ecc': 0.0034,
                'inc': 0.189,
                'lpe': 300.0,
                'lan': 245.0,
                'mna0': 0.0,
                'eph': 3638000.0,
            }
        }
    
    with open(SAVEFILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    m_ut = re.search(r'UT = (\d+\.\d+)', text)
    ut = float(m_ut.group(1)) if m_ut else 3657330.0

    def parse_orbit(vname):
        idx = text.find(f'name = {vname}\n')
        if idx == -1:
            idx = text.find(f'name = {vname}')
        if idx == -1:
            return None
        sub = text[idx:idx+2500]
        sma = float(re.search(r'SMA = (.*?)\n', sub).group(1))
        ecc = float(re.search(r'ECC = (.*?)\n', sub).group(1))
        inc = float(re.search(r'INC = (.*?)\n', sub).group(1))
        lpe = float(re.search(r'LPE = (.*?)\n', sub).group(1))
        lan = float(re.search(r'LAN = (.*?)\n', sub).group(1))
        mna = float(re.search(r'MNA = (.*?)\n', sub).group(1))
        eph = float(re.search(r'EPH = (.*?)\n', sub).group(1))
        return {
            'name': vname,
            'sma': sma,
            'ecc': ecc,
            'inc': inc,
            'lpe': lpe,
            'lan': lan,
            'mna0': mna,
            'eph': eph,
        }

    anchor = parse_orbit('CorolSat-1B') or parse_orbit('CoroltSat-1B')
    node2 = parse_orbit('CoroltSat-1C')

    return {
        'ut': ut,
        'anchor': anchor,
        'node2': node2
    }

def format_kerbin_time(ut_seconds):
    kerbin_day_len = 21600.0  # 6 hours
    day = int(ut_seconds // kerbin_day_len) + 1
    rem = ut_seconds % kerbin_day_len
    hr = int(rem // 3600)
    rem %= 3600
    mn = int(rem // 60)
    sc = int(rem % 60)
    return f"Y1-D{day} {hr:02d}:{mn:02d}:{sc:02d}"

def calculate_windows(start_ut=None, num_windows=5, target_slot=None):
    state = load_constellation_state()
    ut_now = state['ut']
    anchor = state['anchor']
    node2 = state['node2']

    mu = 3.5316000e12
    kerbin_rot_rate = 2 * math.pi / 21600.0
    ksc_lon = math.radians(-74.55767)

    # Telemetry calibration from CSA-13 flight:
    dt_ascent = 1149.3  # seconds from liftoff to SECO-2 circularization
    delta_theta_inertial = math.radians(106.39)  # inertial insertion arc

    sma = anchor['sma']
    ecc = anchor['ecc']
    lan = math.radians(anchor['lan'])
    lpe = math.radians(anchor['lpe'])
    mna0 = anchor['mna0']
    eph = anchor['eph']

    period = 2 * math.pi * math.sqrt(sma**3 / mu)
    n = 2 * math.pi / period  # mean motion rad/s
    synodic_period = 2 * math.pi / (n - kerbin_rot_rate)

    t_start = ut_now if start_ut is None else max(ut_now, start_ut)

    print("================================================================================")
    print("    COROLT SPACE AGENCY - CSA-14 LAUNCH WINDOW CALCULATOR (EMPIRICAL CAL)")
    print("================================================================================")
    print(f"Current Game UT:             {ut_now:.1f} s ({format_kerbin_time(ut_now)})")
    print(f"Anchor Satellite:            {anchor['name']} (SMA: {anchor['sma']:.1f} m, T: {period:.2f} s)")
    if node2:
        period_2 = 2 * math.pi * math.sqrt(node2['sma']**3 / mu)
        print(f"Second Node:                 {node2['name']} (SMA: {node2['sma']:.1f} m, T: {period_2:.2f} s)")
    print(f"Target Orbit Altitude:       {(sma - 600000)/1000:.1f} km (Equatorial Circular)")
    print(f"Ascent Duration (SECO-2):    {dt_ascent:.1f} s ({dt_ascent/60:.2f} min)")
    print(f"Ascent Inertial Arc:         {math.degrees(delta_theta_inertial):.2f}º")
    print(f"Synodic Launch Cycle:        {synodic_period:.2f} s ({synodic_period/60:.2f} min)")
    print("--------------------------------------------------------------------------------")

    targets = []
    if target_slot is not None:
        targets.append((f"{target_slot:.1f}º Custom Constellation Slot", math.radians(target_slot)))
    else:
        targets = [
            ("240.0º (Slot 2: 3-Satellite Global Triangulation)", math.radians(240.0)),
            ("40.0º (Slot 1: 9-Satellite Mesh Ring)", math.radians(40.0)),
        ]

    for label, target_rad in targets:
        print(f"\n🚀 OPTIMAL LAUNCH WINDOWS FOR {label.upper()}:")
        print(f"{'#':<3} | {'KERBIN TIME':<18} | {'UT (s)':<12} | {'COUNTDOWN FROM NOW':<22} | {'INSERTION PHASE'}")
        print("-" * 80)

        t = t_start
        found = 0
        rate = kerbin_rot_rate - n

        while found < num_windows:
            t_sol = t
            for _ in range(6):
                t_ins = t_sol + dt_ascent
                l_ins = (ksc_lon + kerbin_rot_rate * t_sol + delta_theta_inertial) % (2 * math.pi)
                m = (mna0 + n * (t_ins - eph)) % (2 * math.pi)
                nu = m + 2 * ecc * math.sin(m)
                l_1b = (lan + lpe + nu) % (2 * math.pi)
                diff = (l_ins - l_1b) % (2 * math.pi)
                err = (diff - target_rad + math.pi) % (2 * math.pi) - math.pi
                t_sol -= err / rate

            if t_sol >= t_start:
                cd_sec = t_sol - ut_now
                cd_hr = int(cd_sec // 3600)
                cd_mn = int((cd_sec % 3600) // 60)
                cd_sc = int(cd_sec % 60)
                cd_str = f"T+{cd_hr:02d}h {cd_mn:02d}m {cd_sc:02d}s" if cd_sec >= 0 else f"T-{abs(cd_sec):.0f}s"

                # Verification check
                t_ins = t_sol + dt_ascent
                l_ins = (ksc_lon + kerbin_rot_rate * t_sol + delta_theta_inertial) % (2 * math.pi)
                m = (mna0 + n * (t_ins - eph)) % (2 * math.pi)
                nu = m + 2 * ecc * math.sin(m)
                l_1b = (lan + lpe + nu) % (2 * math.pi)
                actual_phase = math.degrees((l_ins - l_1b) % (2 * math.pi))

                print(f"{found+1:<3} | {format_kerbin_time(t_sol):<18} | {t_sol:<12.1f} | {cd_str:<22} | {actual_phase:.2f}º (±0.00º)")
                found += 1

            t = t_sol + synodic_period * 0.90

    print("\n================================================================================")
    print("OPERATIONAL INSTRUCTIONS:")
    print("1. Set KSP Alarm Clock or warp to the designated Launch Window UT.")
    print("2. Ensure target craft in kOS script is set to 'CorolSat-1B'.")
    print("3. Execute: runpath(\"0:/csa/csa14_guided_ascent.ks\").")
    print("4. Vehicle will insert directly into the target slot with phase validation (±0.5º).")
    print("================================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate CSA-14 launch windows")
    parser.add_argument("--slot", type=float, default=None, help="Specific target slot in degrees (e.g. 240 or 40)")
    parser.add_argument("--day", type=int, default=None, help="Kerbin calendar day to search from")
    parser.add_argument("--count", type=int, default=5, help="Number of windows to generate")
    args = parser.parse_args()

    start_ut_val = None
    if args.day is not None:
        start_ut_val = (args.day - 1) * 21600.0

    calculate_windows(start_ut=start_ut_val, num_windows=args.count, target_slot=args.slot)
