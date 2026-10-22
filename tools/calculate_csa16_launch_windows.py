#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Constellation Launch Window Calculator v3.1 (CSA-16)
Calculates exact sidereal launch windows from Kerbin Space Center (KSC) to insert
CoroltSat-1F into Slot 4 (+160.0 deg ahead of CorolSat-1B / +40.0 deg ahead of CoroltSat-1C),
extending the 5-satellite continuous mesh backbone:
  1B (0 deg) <-> 1D (+40 deg) <-> 1E (+80 deg) <-> 1C (+120 deg) <-> 1F (+160 deg).

CALIBRATION UPGRADES IN v3.1 (Post-CSA-15 Telemetry Feedback Loop):
1. Exact FLIGHTSTATE UT Extraction + Live Telemachus UT Query:
   - Parses UT specifically from the FLIGHTSTATE block in persistent.sfs (fixing the
     first-match regex issue) and optionally queries live UT from Telemachus HTTP API.
2. Ground-Truth CSA-15 Ascent Calibration (Effective Launch UT to SECO-2 + 3s Audit):
   - dt_ascent        = 743.10 s (from T-0 ignition at UT 4,022,750.80s to SECO-2+3s at 4,023,493.90s)
   - surface_arc      = 66.1061 deg (from KSC -74.55767 deg to SECO-2 audit -8.45154 deg)
   - inertial_arc     = 78.5202 deg
   - CSA-15 Backtest  = Predicted +37.325 deg vs kOS Actual +37.320 deg (Error: +0.0046 deg!)
"""

import argparse
import json
import math
import os
import re
import urllib.request

SAVEFILE_PATH = "/media/steam_games/SteamLibrary/steamapps/common/Kerbal Space Program/saves/Corolt Space Agency/persistent.sfs"
TELEMACHUS_URL = "http://127.0.0.1:8085/telemachus/datalink?ut=t.universalTime"

# Exact KSP Astrodynamics Constants for Kerbin
KERBIN_MU = 3.5316000e12
KERBIN_SIDEREAL_PERIOD = 21549.4251830898  # Exact sidereal rotation period (s)
KERBIN_SOLAR_DAY = 21600.0                 # Calendar day length (6h) for Y1-Dxxx clock display
KERBIN_THETA0_DEG = 90.0000                # Kerbin initial rotation angle at UT = 0 (deg)
KSC_LON_DEG = -74.55767                    # LaunchPad surface longitude (deg)

# Ground-Truth CSA-15 Empirical Ascent Calibration (T-0 Ignition to SECO-2 + 3s Phase Audit)
DT_ASCENT_SEC = 743.10                     # T-0 Ignition to SECO-2 phase audit (s)
ASCENT_SURFACE_ARC_DEG = 66.1061           # Eastward surface longitude traversed during ascent (deg)
ASCENT_INERTIAL_ARC_DEG = ASCENT_SURFACE_ARC_DEG + (360.0 / KERBIN_SIDEREAL_PERIOD) * DT_ASCENT_SEC  # 78.5202 deg


def get_live_telemachus_ut():
    try:
        req = urllib.request.Request(TELEMACHUS_URL, headers={'User-Agent': 'CSA-FlightDynamics/3.1'})
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if 'ut' in data and isinstance(data['ut'], (int, float)) and data['ut'] > 0:
                return float(data['ut'])
    except Exception:
        pass
    return None


def load_constellation_state():
    if not os.path.exists(SAVEFILE_PATH):
        raise FileNotFoundError(f"Savefile not found: {SAVEFILE_PATH}")

    with open(SAVEFILE_PATH, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    # Extract UT specifically from FLIGHTSTATE block
    fs_idx = text.find('FLIGHTSTATE')
    if fs_idx != -1:
        m_ut = re.search(r'UT = (\d+\.\d+)', text[fs_idx:fs_idx + 400])
        ut_save = float(m_ut.group(1)) if m_ut else 4040352.6
    else:
        m_ut = re.search(r'UT = (\d+\.\d+)', text)
        ut_save = float(m_ut.group(1)) if m_ut else 4040352.6

    ut_live = get_live_telemachus_ut()
    ut = max(ut_save, ut_live) if ut_live is not None else ut_save
    ut_source = "Telemachus Live API" if (ut_live is not None and ut_live >= ut_save) else "persistent.sfs (FLIGHTSTATE)"

    def parse_orbit(vname):
        idx = text.find(f'name = {vname}\n')
        if idx == -1:
            idx = text.find(f'name = {vname}')
        if idx == -1:
            return None
        sub = text[idx:idx + 2500]
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
    node2 = parse_orbit('CoroltSat-1E')
    node3 = parse_orbit('CoroltSat-1C')

    return {
        'ut': ut,
        'ut_source': ut_source,
        'anchor': anchor,
        'node1': node1,
        'node2': node2,
        'node3': node3,
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
    ut_source = state['ut_source']
    anchor = state['anchor']
    node1 = state['node1']
    node2 = state['node2']
    node3 = state['node3']

    omega_sid_rad = 2.0 * math.pi / KERBIN_SIDEREAL_PERIOD

    ref_sat = anchor
    if ref_name:
        rn = ref_name.lower()
        if node1 and '1d' in rn:
            ref_sat = node1
        elif node2 and '1e' in rn:
            ref_sat = node2
        elif node3 and '1c' in rn:
            ref_sat = node3

    sma = ref_sat['sma']
    period = 2.0 * math.pi * math.sqrt(sma**3 / KERBIN_MU)
    n = 2.0 * math.pi / period
    synodic_period = 2.0 * math.pi / (n - omega_sid_rad)

    t_start = ut_now if start_ut is None else max(ut_now, start_ut)

    # Historical verification on CSA-15 actual launch (T-0 ignition UT = 4,022,750.80 s)
    csa15_liftoff = 4022750.80
    csa15_t_ins = csa15_liftoff + DT_ASCENT_SEC
    csa15_l_ins = get_ship_insertion_longitude_deg(csa15_liftoff)
    csa15_l_1d = get_sat_longitude_deg(node1, csa15_t_ins)
    csa15_pred_phase = (csa15_l_ins - csa15_l_1d) % 360.0

    print("==============================================================================================")
    print("  COROLT SPACE AGENCY - CSA-16 SIDEREAL LAUNCH WINDOW CALCULATOR v3.1 (SLOT 4 EXPANSION)      ")
    print("==============================================================================================")
    print(f"Current Game UT:             {ut_now:.1f} s ({format_kerbin_time(ut_now)}) [{ut_source}]")
    print(f"Kerbin Sidereal Period:      {KERBIN_SIDEREAL_PERIOD:.6f} s (theta_0 = {KERBIN_THETA0_DEG:.3f} deg at UT=0)")
    print(f"CSA-15 Backtest Check:       Predicted +{csa15_pred_phase:.3f} deg vs kOS Actual +37.320 deg (Err: {csa15_pred_phase-37.320:+.4f} deg!)")
    print(f"Slot 0 Anchor (0.0 deg):     {anchor['name']} (SMA: {anchor['sma']:.1f} m, T: {period:.2f} s)")
    if node1:
        p_1d = 2.0 * math.pi * math.sqrt(node1['sma']**3 / KERBIN_MU)
        print(f"Slot 1 Node (+40.0 deg):     {node1['name']} (SMA: {node1['sma']:.1f} m, T: {p_1d:.2f} s)")
    if node2:
        p_1e = 2.0 * math.pi * math.sqrt(node2['sma']**3 / KERBIN_MU)
        print(f"Slot 2 Node (+80.0 deg):     {node2['name']} (SMA: {node2['sma']:.1f} m, T: {p_1e:.2f} s)")
    if node3:
        p_1c = 2.0 * math.pi * math.sqrt(node3['sma']**3 / KERBIN_MU)
        print(f"Slot 3 Node (+120.0 deg):    {node3['name']} (SMA: {node3['sma']:.1f} m, T: {p_1c:.2f} s)")
    print(f"Ascent Duration (to Audit):  {DT_ASCENT_SEC:.2f} s ({DT_ASCENT_SEC/60:.2f} min)")
    print(f"Ascent Surface / Inert Arc:  {ASCENT_SURFACE_ARC_DEG:.4f} deg surface / {ASCENT_INERTIAL_ARC_DEG:.4f} deg inertial")
    print(f"Synodic Launch Cycle:        {synodic_period:.2f} s ({synodic_period/60:.2f} min)")
    print("----------------------------------------------------------------------------------------------")

    targets = []
    if target_slot is not None:
        targets.append((f"{target_slot:+.1f} deg relative to {ref_sat['name']}", ref_sat, target_slot % 360.0))
    else:
        targets.append(("Slot 4 (+160.0 deg ahead of CorolSat-1B | Nominal Constellation Grid)", anchor, 160.0))
        if node3:
            targets.append(("Slot 4 (+40.0 deg ahead of CoroltSat-1C | Exact +40 deg Mesh Link < 650 km)", node3, 40.0))

    for label, sat_obj, target_deg in targets:
        sat_sma = sat_obj['sma']
        sat_period = 2.0 * math.pi * math.sqrt(sat_sma**3 / KERBIN_MU)
        sat_n_deg = 360.0 / sat_period
        omega_sid_deg = 360.0 / KERBIN_SIDEREAL_PERIOD
        rate_deg_per_s = omega_sid_deg - sat_n_deg
        sat_synodic = 360.0 / abs(rate_deg_per_s)

        print(f"\n🚀 EXACT SIDEREAL LAUNCH WINDOWS FOR {label.upper()}:")
        print(f"{'#':<3} | {'KERBIN TIME':<18} | {'LIFTOFF UT (s)':<14} | {'COUNTDOWN FROM NOW':<20} | {'VS 1B':<9} | {'VS 1C':<9} | {'VS 1D'}")
        print("-" * 94)

        t = t_start
        found = 0

        while found < num_windows:
            t_sol = t
            for _ in range(12):
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
                ph_1c = to_signed_deg(l_ins - get_sat_longitude_deg(node3, t_ins)) if node3 else 0.0
                ph_1d = (l_ins - get_sat_longitude_deg(node1, t_ins)) % 360.0 if node1 else 0.0

                print(f"{found+1:<3} | {format_kerbin_time(t_sol):<18} | {t_sol:<14.1f} | {cd_str:<20} | +{ph_1b:06.2f}º | {ph_1c:+06.2f}º | +{ph_1d:06.2f}º")
                found += 1

            t = t_sol + sat_synodic * 0.90

    print("\n==============================================================================================")
    print("OPERATIONAL INSTRUCTIONS (CSA-16 / CoroltSat-1F):")
    print("1. Remember: csa16_guided_ascent.ks takes ~125s for pad fueling before entering HOLD.")
    print("   Always choose a window at least 3-4 minutes (> 200 s) ahead of current UT!")
    print("2. Execute on the pad (Option A: +160.0 deg vs CorolSat-1B, or Option B: +40.0 deg vs CoroltSat-1C):")
    print("   RUNPATH(\"0:/csa/csa16_guided_ascent.ks\", <LIFTOFF_UT>, 160.0, \"CorolSat-1B\").")
    print("   -- OR for exact +40.0 deg link ahead of CoroltSat-1C:")
    print("   RUNPATH(\"0:/csa/csa16_guided_ascent.ks\", <LIFTOFF_UT>, 40.0, \"CoroltSat-1C\").")
    print("3. If residual phase deviation > 6.0 deg at SECO-2, execute universal phasing:")
    print("   RUNPATH(\"0:/csa/constellation_phasing.ks\", 160, 3, \"CorolSat-1B\").")
    print("==============================================================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate exact sidereal CSA-16 launch windows for CoroltSat-1F")
    parser.add_argument("--slot", type=float, default=None, help="Specific target slot in degrees (default: 160 vs 1B and 40 vs 1C)")
    parser.add_argument("--ref", type=str, default="CorolSat-1B", help="Reference satellite name (CorolSat-1B, CoroltSat-1C, CoroltSat-1D, CoroltSat-1E)")
    parser.add_argument("--day", type=int, default=None, help="Kerbin calendar day to search from")
    parser.add_argument("--ut", type=float, default=None, help="Exact starting UT in seconds")
    parser.add_argument("--count", type=int, default=6, help="Number of windows to generate")
    args = parser.parse_args()

    start_ut_val = args.ut
    if args.day is not None:
        start_ut_val = (args.day - 1) * KERBIN_SOLAR_DAY

    calculate_windows(start_ut=start_ut_val, num_windows=args.count, target_slot=args.slot, ref_name=args.ref)
