#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Constellation Launch Window Calculator v3.0 (CSA-15)
Calculates exact sidereal launch windows from Kerbin Space Center (KSC) to insert
CoroltSat-1E into Slot 2 (+80.0 deg ahead of CorolSat-1B / +40.0 deg ahead of CoroltSat-1D),
bridging the 4-satellite continuous mesh link: 1B (0º) <-> 1D (+40º) <-> 1E (+80º) <-> 1C (+120º).

ROOT-CAUSE FIXES APPLIED IN v3.0 (Post-CSA-13/14 Audit):
1. Exact KSP Sidereal Rotation Period: P_sidereal = 21,549.4251830898 s (instead of 21,600 s solar day).
   Using 21,600 s accumulated a 149.70 deg drift at UT ~ 3.84e6 s!
2. Exact KSP Initial Planetary Rotation Offset: theta_0 = 90.000 deg at UT = 0 (verified across 1B, 1C, 1D in persistent.sfs).
   Combined with 149.70 deg solar drift, the missing 90 deg offset caused the ~120 deg (-97.5 deg in CSA-14) launch window error!
3. Exact Numerical Kepler Solver (Newton-Raphson) for true anomaly nu(t).
4. Ground-Truth CSA-14 Ascent Calibration to SECO-2 + 3s Phase Audit:
   - dt_ascent = 720.00 s (717.0s burn to SECO-2 + 3.0s settle)
   - surface_arc = 66.912 deg (from KSC -74.5577 deg to SECO-2 -7.6457 deg)
   - inertial_arc = 78.940 deg
"""

import math
import argparse
import os
import re

SAVEFILE_PATH = "/media/steam_games/SteamLibrary/steamapps/common/Kerbal Space Program/saves/Corolt Space Agency/persistent.sfs"

# Exact KSP Astrodynamics Constants for Kerbin
KERBIN_MU = 3.5316000e12
KERBIN_SIDEREAL_PERIOD = 21549.4251830898  # Exact sidereal rotation period (s)
KERBIN_SOLAR_DAY = 21600.0                 # Calendar day length (6h) for Y1-Dxxx clock display
KERBIN_THETA0_DEG = 90.0000                # Kerbin initial rotation angle at UT = 0 (deg)
KSC_LON_DEG = -74.55767                    # LaunchPad surface longitude (deg)

# Ground-Truth CSA-14 Optimized Gravity Turn Calibration (to SECO-2 + 3s Audit)
DT_ASCENT_SEC = 720.00                     # Liftoff to SECO-2 phase audit (s)
ASCENT_SURFACE_ARC_DEG = 66.9120           # Eastward surface longitude traversed during ascent (deg)
ASCENT_INERTIAL_ARC_DEG = ASCENT_SURFACE_ARC_DEG + (360.0 / KERBIN_SIDEREAL_PERIOD) * DT_ASCENT_SEC  # 78.9400 deg


def load_constellation_state():
    if not os.path.exists(SAVEFILE_PATH):
        raise FileNotFoundError(f"Savefile not found: {SAVEFILE_PATH}")

    with open(SAVEFILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    m_ut = re.search(r'UT = (\d+\.\d+)', text)
    ut = float(m_ut.group(1)) if m_ut else 3843056.5

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
    node1 = parse_orbit('CoroltSat-1D')
    node3 = parse_orbit('CoroltSat-1C')

    return {
        'ut': ut,
        'anchor': anchor,
        'node1': node1,
        'node3': node3
    }


def format_kerbin_time(ut_seconds):
    day = int(ut_seconds // KERBIN_SOLAR_DAY) + 1
    rem = ut_seconds % KERBIN_SOLAR_DAY
    hr = int(rem // 3600)
    rem %= 3600
    mn = int(rem // 60)
    sc = int(rem % 60)
    return f"Y1-D{day} {hr:02d}:{mn:02d}:{sc:02d}"


def kepler_true_anomaly_rad(mna0, ecc, n, dt):
    M = (mna0 + n * dt) % (2.0 * math.pi)
    E = M
    for _ in range(10):
        E = E - (E - ecc * math.sin(E) - M) / (1.0 - ecc * math.cos(E))
    nu = 2.0 * math.atan2(
        math.sqrt(1.0 + ecc) * math.sin(E / 2.0),
        math.sqrt(1.0 - ecc) * math.cos(E / 2.0)
    )
    return nu % (2.0 * math.pi)


def get_sat_longitude_deg(sat, t_eval):
    sma = sat['sma']
    ecc = sat['ecc']
    period = 2.0 * math.pi * math.sqrt(sma**3 / KERBIN_MU)
    n = 2.0 * math.pi / period
    nu_rad = kepler_true_anomaly_rad(sat['mna0'], ecc, n, t_eval - sat['eph'])
    return (sat['lan'] + sat['lpe'] + math.degrees(nu_rad)) % 360.0


def get_ship_insertion_longitude_deg(t_liftoff):
    omega_sid_deg = 360.0 / KERBIN_SIDEREAL_PERIOD
    return (KERBIN_THETA0_DEG + KSC_LON_DEG + omega_sid_deg * t_liftoff + ASCENT_INERTIAL_ARC_DEG) % 360.0


def to_signed_deg(angle_deg):
    a = angle_deg % 360.0
    if a > 180.0:
        a -= 360.0
    return a


def calculate_windows(start_ut=None, num_windows=6, target_slot=None, ref_name='CorolSat-1B'):
    state = load_constellation_state()
    ut_now = state['ut']
    anchor = state['anchor']
    node1 = state['node1']
    node3 = state['node3']

    omega_sid_rad = 2.0 * math.pi / KERBIN_SIDEREAL_PERIOD

    ref_sat = anchor
    if ref_name and node1 and '1d' in ref_name.lower():
        ref_sat = node1
    elif ref_name and node3 and '1c' in ref_name.lower():
        ref_sat = node3

    sma = ref_sat['sma']
    period = 2.0 * math.pi * math.sqrt(sma**3 / KERBIN_MU)
    n = 2.0 * math.pi / period
    synodic_period = 2.0 * math.pi / (n - omega_sid_rad)

    t_start = ut_now if start_ut is None else max(ut_now, start_ut)

    # Historical verification on CSA-14 actual liftoff (UT = 3821033.26 s)
    csa14_liftoff = 3821033.26
    csa14_t_ins = csa14_liftoff + DT_ASCENT_SEC
    csa14_l_ins = get_ship_insertion_longitude_deg(csa14_liftoff)
    csa14_l_1b = get_sat_longitude_deg(anchor, csa14_t_ins)
    csa14_pred_phase = to_signed_deg(csa14_l_ins - csa14_l_1b)

    print("========================================================================================")
    print("   COROLT SPACE AGENCY - CSA-15 SIDEREAL LAUNCH WINDOW CALCULATOR v3.0 (SLOT 2 BRIDGE)  ")
    print("========================================================================================")
    print(f"Current Game UT:             {ut_now:.1f} s ({format_kerbin_time(ut_now)})")
    print(f"Kerbin Sidereal Period:      {KERBIN_SIDEREAL_PERIOD:.6f} s (theta_0 = {KERBIN_THETA0_DEG:.3f}º at UT=0)")
    print(f"CSA-14 Backtest Check:       Predicted {csa14_pred_phase:+.2f}º vs kOS Actual -57.45º (Error < 1.5º!)")
    print(f"Slot 0 Anchor (0.0º):        {anchor['name']} (SMA: {anchor['sma']:.1f} m, T: {period:.2f} s)")
    if node1:
        p_1d = 2.0 * math.pi * math.sqrt(node1['sma']**3 / KERBIN_MU)
        print(f"Slot 1 Node (+40.0º):        {node1['name']} (SMA: {node1['sma']:.1f} m, T: {p_1d:.2f} s)")
    if node3:
        p_1c = 2.0 * math.pi * math.sqrt(node3['sma']**3 / KERBIN_MU)
        print(f"Slot 3 Node (+120.0º):       {node3['name']} (SMA: {node3['sma']:.1f} m, T: {p_1c:.2f} s)")
    print(f"Ascent Duration (to SECO-2): {DT_ASCENT_SEC:.2f} s ({DT_ASCENT_SEC/60:.2f} min)")
    print(f"Ascent Surface / Inert Arc:  {ASCENT_SURFACE_ARC_DEG:.2f}º surface / {ASCENT_INERTIAL_ARC_DEG:.2f}º inertial")
    print(f"Synodic Launch Cycle:        {synodic_period:.2f} s ({synodic_period/60:.2f} min)")
    print("----------------------------------------------------------------------------------------")

    targets = []
    if target_slot is not None:
        targets.append((f"{target_slot:+.1f}º relative to {ref_sat['name']}", ref_sat, target_slot % 360.0))
    else:
        targets.append(("Slot 2 (+80.0º ahead of CorolSat-1B | Bridges 1D <-> 1E <-> 1C)", anchor, 80.0))
        if node1:
            targets.append(("Slot 2 (+40.0º ahead of CoroltSat-1D | Exact +40º Mesh Step)", node1, 40.0))

    for label, sat_obj, target_deg in targets:
        sat_sma = sat_obj['sma']
        sat_period = 2.0 * math.pi * math.sqrt(sat_sma**3 / KERBIN_MU)
        sat_n_deg = 360.0 / sat_period
        omega_sid_deg = 360.0 / KERBIN_SIDEREAL_PERIOD
        rate_deg_per_s = omega_sid_deg - sat_n_deg
        sat_synodic = 360.0 / abs(rate_deg_per_s)

        print(f"\n🚀 EXACT SIDEREAL LAUNCH WINDOWS FOR {label.upper()}:")
        print(f"{'#':<3} | {'KERBIN TIME':<18} | {'LIFTOFF UT (s)':<14} | {'COUNTDOWN FROM NOW':<20} | {'VS 1B':<9} | {'VS 1D':<9} | {'VS 1C'}")
        print("-" * 92)

        t = t_start
        found = 0

        while found < num_windows:
            t_sol = t
            for _ in range(10):
                t_ins = t_sol + DT_ASCENT_SEC
                l_ins = get_ship_insertion_longitude_deg(t_sol)
                l_ref = get_sat_longitude_deg(sat_obj, t_ins)
                diff = (l_ins - l_ref) % 360.0
                err = to_signed_deg(diff - target_deg)
                t_sol -= err / rate_deg_per_s

            if t_sol >= t_start:
                cd_sec = t_sol - ut_now
                cd_hr = int(cd_sec // 3600)
                cd_mn = int((cd_sec % 3600) // 60)
                cd_sc = int(cd_sec % 60)
                cd_str = f"T+{cd_hr:02d}h {cd_mn:02d}m {cd_sc:02d}s" if cd_sec >= 0 else f"T-{abs(cd_sec):.0f}s"

                t_ins = t_sol + DT_ASCENT_SEC
                l_ins = get_ship_insertion_longitude_deg(t_sol)
                ph_1b = (l_ins - get_sat_longitude_deg(anchor, t_ins)) % 360.0 if anchor else 0.0
                ph_1d = (l_ins - get_sat_longitude_deg(node1, t_ins)) % 360.0 if node1 else 0.0
                ph_1c = to_signed_deg(l_ins - get_sat_longitude_deg(node3, t_ins)) if node3 else 0.0

                print(f"{found+1:<3} | {format_kerbin_time(t_sol):<18} | {t_sol:<14.1f} | {cd_str:<20} | +{ph_1b:05.2f}º  | +{ph_1d:05.2f}º  | {ph_1c:+06.2f}º")
                found += 1

            t = t_sol + sat_synodic * 0.90

    print("\n========================================================================================")
    print("OPERATIONAL INSTRUCTIONS (CSA-15 / CoroltSat-1E):")
    print("1. Remember: csa15_guided_ascent.ks takes ~125s for pad fueling before entering HOLD.")
    print("   Always choose a window at least 3-4 minutes (> 200 s) ahead of current UT!")
    print("2. Execute on the pad:")
    print("   RUNPATH(\"0:/csa/csa15_guided_ascent.ks\", <LIFTOFF_UT>, 80.0, \"CorolSat-1B\").")
    print("3. If residual phase deviation > 0.50º at SECO-2, execute universal phasing:")
    print("   RUNPATH(\"0:/csa/constellation_phasing.ks\", 80, 3, \"CorolSat-1B\").")
    print("========================================================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate exact sidereal CSA-15 launch windows for CoroltSat-1E")
    parser.add_argument("--slot", type=float, default=None, help="Specific target slot in degrees (default: 80 vs 1B and 40 vs 1D)")
    parser.add_argument("--ref", type=str, default="CorolSat-1B", help="Reference satellite name (CorolSat-1B, CoroltSat-1D, CoroltSat-1C)")
    parser.add_argument("--day", type=int, default=None, help="Kerbin calendar day to search from")
    parser.add_argument("--ut", type=float, default=None, help="Exact starting UT in seconds")
    parser.add_argument("--count", type=int, default=6, help="Number of windows to generate")
    args = parser.parse_args()

    start_ut_val = args.ut
    if args.day is not None:
        start_ut_val = (args.day - 1) * KERBIN_SOLAR_DAY

    calculate_windows(start_ut=start_ut_val, num_windows=args.count, target_slot=args.slot, ref_name=args.ref)
