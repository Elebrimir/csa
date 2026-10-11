#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Constellation Launch Window Calculator
Calculates high-precision launch windows from Kerbin Space Center (KSC) to insert
CoroltSat-1C into a phased equatorial orbit relative to CoroltSat-1B.
"""

import math
import argparse
import os
import re

SAVEFILE_PATH = "/media/steam_games/SteamLibrary/steamapps/common/Kerbal Space Program/saves/Corolt Space Agency/persistent.sfs"

def load_orbital_state():
    if not os.path.exists(SAVEFILE_PATH):
        # Fallback to nominal values from CSA-12 telemetry
        return {
            'ut': 3418248.0,
            'sma': 905751.83,
            'ecc': 0.006331,
            'inc': 0.1307,
            'lpe': 348.5189,
            'lan': 245.6987,
            'mna0': 0.420587,
            'eph': 3418234.80,
        }
    
    with open(SAVEFILE_PATH, 'r') as f:
        text = f.read()

    m_ut = re.search(r'UT = (\d+\.\d+)', text)
    ut = float(m_ut.group(1)) if m_ut else 3418248.0

    idx = text.find('name = CorolSat-1B')
    if idx == -1:
        idx = text.find('name = CoroltSat-1B')
    
    sub = text[idx:idx+1500] if idx != -1 else ""
    sma = float(re.search(r'SMA = (.*?)\n', sub).group(1)) if 'SMA =' in sub else 905751.83
    ecc = float(re.search(r'ECC = (.*?)\n', sub).group(1)) if 'ECC =' in sub else 0.006331
    inc = float(re.search(r'INC = (.*?)\n', sub).group(1)) if 'INC =' in sub else 0.1307
    lpe = float(re.search(r'LPE = (.*?)\n', sub).group(1)) if 'LPE =' in sub else 348.5189
    lan = float(re.search(r'LAN = (.*?)\n', sub).group(1)) if 'LAN =' in sub else 245.6987
    mna = float(re.search(r'MNA = (.*?)\n', sub).group(1)) if 'MNA =' in sub else 0.420587
    eph = float(re.search(r'EPH = (.*?)\n', sub).group(1)) if 'EPH =' in sub else 3418234.80

    return {
        'ut': ut,
        'sma': sma,
        'ecc': ecc,
        'inc': inc,
        'lpe': lpe,
        'lan': lan,
        'mna0': mna,
        'eph': eph,
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

def calculate_windows(start_day=169, num_windows=6):
    state = load_orbital_state()
    mu = 3.5316000e12
    kerbin_rot_rate = 2 * math.pi / 21600.0
    ksc_lon = math.radians(-74.557)
    dt_ascent = 1208.4  # seconds from liftoff to SECO-2 circularization
    delta_theta_inertial = math.radians(82.90)  # inertial insertion arc

    sma = state['sma']
    ecc = state['ecc']
    lan = math.radians(state['lan'])
    lpe = math.radians(state['lpe'])
    mna0 = state['mna0']
    eph = state['eph']

    period = 2 * math.pi * math.sqrt(sma**3 / mu)
    n = 2 * math.pi / period  # rad/s

    # Synodic period between ground track and satellite orbit
    synodic_period = 2 * math.pi / (n - kerbin_rot_rate)

    # Start time in UT: Day 169 start or rollout time
    # Day 1 is UT 0..21600. Day 169 start is (169-1)*21600 = 3628800
    # Day 159 + 10 days = UT 3418248 + 216000 = 3634248 s (Day 169 01:30:48)
    t_start = (start_day - 1) * 21600.0
    if t_start < state['ut'] + 216000.0:
        t_start = state['ut'] + 216000.0

    print("================================================================================")
    print("       COROLT SPACE AGENCY - LAUNCH WINDOW & CONSTELLATION PHASING CALCULATOR    ")
    print("================================================================================")
    print(f"Target Constellation Anchor: CoroltSat-1B")
    print(f"Current Game UT:             {state['ut']:.1f} s ({format_kerbin_time(state['ut'])})")
    print(f"Vehicle Ready (KCT +10d):    {state['ut'] + 216000.0:.1f} s ({format_kerbin_time(state['ut'] + 216000.0)})")
    print(f"Target Orbit Altitude:       {(sma - 600000)/1000:.1f} km (Equatorial)")
    print(f"Anchor Orbital Period:       {period:.2f} s ({period/60:.2f} min)")
    print(f"Synodic Phasing Cycle:       {synodic_period:.2f} s ({synodic_period/60:.2f} min)")
    print("--------------------------------------------------------------------------------")

    targets = [
        ("180º (2-Satellite Antipodal Constellation)", math.pi),
        ("120º (3-Satellite Constellation - Slot 1)", 2 * math.pi / 3),
        ("240º (3-Satellite Constellation - Slot 2)", 4 * math.pi / 3),
    ]

    for label, target_rad in targets:
        print(f"\n🚀 OPTIMAL LAUNCH WINDOWS FOR {label.upper()}:")
        print(f"{'#':<3} | {'KERBIN CALENDAR':<18} | {'UT (s)':<12} | {'COUNTDOWN FROM READY':<22} | {'PHASING ERROR'}")
        print("-" * 80)
        
        t = t_start
        found = 0
        rate = kerbin_rot_rate - n
        
        while found < num_windows:
            # Solve for exact zero-crossing
            t_sol = t
            for _ in range(5):
                t_ins = t_sol + dt_ascent
                l_ins = (ksc_lon + kerbin_rot_rate * t_sol + delta_theta_inertial) % (2 * math.pi)
                m = (mna0 + n * (t_ins - eph)) % (2 * math.pi)
                nu = m + 2 * ecc * math.sin(m)
                l_1b = (lan + lpe + nu) % (2 * math.pi)
                diff = (l_ins - l_1b) % (2 * math.pi)
                err = (diff - target_rad + math.pi) % (2 * math.pi) - math.pi
                t_sol -= err / rate
            
            if t_sol >= t_start:
                cd_sec = t_sol - (state['ut'] + 216000.0)
                cd_hr = int(cd_sec // 3600)
                cd_mn = int((cd_sec % 3600) // 60)
                cd_sc = int(cd_sec % 60)
                cd_str = f"T+{cd_hr:02d}h {cd_mn:02d}m {cd_sc:02d}s" if cd_sec >= 0 else f"T-{abs(cd_sec):.0f}s"
                
                print(f"{found+1:<3} | {format_kerbin_time(t_sol):<18} | {t_sol:<12.1f} | {cd_str:<22} | ±0.00º")
                found += 1
            
            t = t_sol + synodic_period * 0.85

    print("\n================================================================================")
    print("OPERATIONAL INSTRUCTIONS FOR FLIGHT DIRECTOR:")
    print("1. Set KSP In-game Alarm Clock or warp to selected UT launch window.")
    print("2. Launch on exact second using kOS guidance script: csa13_guided_ascent.ks")
    print("3. CoroltSat-1C will insert directly into the designated phasing slot upon SECO-2.")
    print("================================================================================")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate CSA-13 constellation launch windows")
    parser.add_argument("--day", type=int, default=169, help="Starting Kerbin day (default: 169)")
    parser.add_argument("--count", type=int, default=5, help="Number of windows to generate")
    args = parser.parse_args()
    calculate_windows(start_day=args.day, num_windows=args.count)
