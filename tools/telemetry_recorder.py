#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Live Telemetry Recorder v2.0
Connects to Telemachus in Kerbal Space Program (http://127.0.0.1:8085).
Records real-time flight data to CSV and generates a comprehensive mission report.
Captures attitude (pitch, heading, roll, AoA), atmospheric density, orbital elements,
and stage resource consumption for aerodynamic calibration and ascent simulation.
"""

import urllib.request
import urllib.parse
import json
import time
import sys
import os
import csv
import argparse
import signal
from datetime import datetime

def _handle_sigterm(signum, frame):
    raise KeyboardInterrupt

signal.signal(signal.SIGTERM, _handle_sigterm)

TELEMACHUS_URL = "http://127.0.0.1:8085/telemachus/datalink"

# Telemachus API Query String - Complete Mission Package
QUERY_PARAMS = {
    "ut": "t.universalTime",
    "alt": "v.altitude",
    "rad_alt": "v.heightFromTerrain",
    "v_spd": "v.verticalSpeed",
    "orb_vel": "v.orbitalVelocity",
    "surf_vel": "v.surfaceVelocity",
    "pitch": "n.pitch",
    "heading": "n.heading",
    "roll": "n.roll",
    "aoa": "v.angleToPrograde",
    "density": "v.atmosphericDensity",
    "atmo_pa": "v.atmosphericPressurePa",
    "dyn_pres": "v.dynamicPressure",
    "g_force": "v.geeForce",
    "apo": "o.ApA",
    "peri": "o.PeA",
    "sma": "o.sma",
    "ecc": "o.eccentricity",
    "inc": "o.inclination",
    "period": "o.period",
    "lat": "v.lat",
    "lon": "v.long",
    "throttle": "f.throttle",
    "stage": "s.stage",
    "res_sf": "r.resourceCurrent[SolidFuel]",
    "res_lf": "r.resourceCurrent[LiquidFuel]",
    "res_ox": "r.resourceCurrent[Oxidizer]",
    "res_ec": "r.resourceCurrent[ElectricCharge]",
}

QUERY_API = "?" + "&".join(f"{k}={urllib.parse.quote(v)}" for k, v in QUERY_PARAMS.items())

def ut_to_kerbin_date(ut):
    """Converts KSP Universal Time in seconds to Kerbin calendar date."""
    SECONDS_IN_HOUR = 3600
    HOURS_IN_DAY = 6
    SECONDS_IN_DAY = SECONDS_IN_HOUR * HOURS_IN_DAY
    DAYS_IN_YEAR = 426
    SECONDS_IN_YEAR = SECONDS_IN_DAY * DAYS_IN_YEAR

    year = int(ut // SECONDS_IN_YEAR) + 1
    rem_year = ut % SECONDS_IN_YEAR
    day = int(rem_year // SECONDS_IN_DAY) + 1
    rem_day = rem_year % SECONDS_IN_DAY
    hour = int(rem_day // SECONDS_IN_HOUR)
    rem_hour = rem_day % SECONDS_IN_HOUR
    minute = int(rem_hour // 60)
    second = int(rem_hour % 60)

    return f"Year {year}, Day {day} ({hour:02d}h {minute:02d}m {second:02d}s)"

def check_connection(url=TELEMACHUS_URL):
    try:
        req = urllib.request.Request(f"{url}?test=v.altitude", headers={'User-Agent': 'CSA-Telemetry'})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            data = json.loads(resp.read().decode())
            return "errors" not in data
    except Exception:
        return False

def safe_float(val, default=0.0):
    """Converts string/none/int to float safely."""
    try:
        if val is None or val == "nan" or val == "NaN":
            return default
        return float(val)
    except (ValueError, TypeError):
        return default

def safe_int(val, default=0):
    try:
        if val is None:
            return default
        return int(float(val))
    except (ValueError, TypeError):
        return default

def record_flight(mission_name="CSA-07", interval=0.5, mock_mode=False):
    print(f"\n================================================================================")
    print(f"       COROLT SPACE AGENCY (CSA) - ADVANCED TELEMETRY RECORDER v2.0            ")
    print(f"================================================================================")
    
    initial_ut = 0.0
    kerbin_date = "Year 1, Day 1 (00h 00m 00s)"

    if not mock_mode:
        print(f"[*] Checking link with Telemachus (127.0.0.1:8085)...")
        if not check_connection():
            print(f"[!] Waiting for vessel to be loaded on launchpad...")
            while not check_connection():
                time.sleep(1.0)
        print(f"[✓] Telemetry link established! Fetching official Kerbin date...")
        
        try:
            req = urllib.request.Request(f"{TELEMACHUS_URL}?ut=t.universalTime", headers={'User-Agent': 'CSA-Telemetry'})
            with urllib.request.urlopen(req, timeout=2.0) as resp:
                data = json.loads(resp.read().decode())
                initial_ut = safe_float(data.get("ut", 0.0))
                kerbin_date = ut_to_kerbin_date(initial_ut)
                print(f"[📅] Official Kerbin Date: {kerbin_date} (UT: {initial_ut:,.1f}s)")
        except Exception:
            pass
    else:
        print(f"[🔬] MOCK MODE ACTIVE: Generating synthetic verification data...")

    os.makedirs("missions", exist_ok=True)
    csv_file = f"missions/{mission_name}_telemetry.csv"
    
    fieldnames = [
        "timestamp", "UT", "MET",
        "altitude", "radar_alt", "vert_speed", "orbital_vel", "surface_vel",
        "pitch", "heading", "roll", "angle_prograde",
        "dynamic_pressure", "atmospheric_density", "atmospheric_pressure_pa", "g_force",
        "apoapsis", "periapsis", "semi_major_axis", "eccentricity", "inclination", "period",
        "latitude", "longitude",
        "throttle", "stage",
        "solid_fuel", "liquid_fuel", "oxidizer", "electric_charge"
    ]
    
    start_time = None
    max_alt = 0.0
    max_vel = 0.0
    max_g = 0.0
    max_q = 0.0
    min_pitch = 90.0

    with open(csv_file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print(f"[*] Recording telemetry to: {csv_file}")
        print(f"    (Press Ctrl+C to stop recording and generate mission summary)\n")
        print(f"{'MET (s)':>7} | {'Alt (m)':>9} | {'Spd (m/s)':>9} | {'Pitch':>6} | {'AoA':>5} | {'Apo (km)':>8} | {'Q (kPa)':>7} | {'G':>5}")
        print("-" * 75)

        try:
            sample_count = 0
            while True:
                if not mock_mode:
                    req = urllib.request.Request(f"{TELEMACHUS_URL}{QUERY_API}", headers={'User-Agent': 'CSA-Telemetry'})
                    try:
                        with urllib.request.urlopen(req, timeout=2.5) as resp:
                            data = json.loads(resp.read().decode())
                    except Exception:
                        time.sleep(interval)
                        continue
                else:
                    sample_count += 1
                    t_mock = sample_count * interval
                    data = {
                        "ut": 100000.0 + t_mock,
                        "alt": 75.0 + 0.5 * 25.0 * (t_mock ** 2),
                        "rad_alt": 5.0 + 0.5 * 25.0 * (t_mock ** 2),
                        "v_spd": 25.0 * t_mock,
                        "orb_vel": 175.0 + 25.0 * t_mock,
                        "surf_vel": 25.0 * t_mock,
                        "pitch": max(30.0, 90.0 - 0.8 * t_mock),
                        "heading": 90.0,
                        "roll": 0.0,
                        "aoa": 1.2,
                        "density": 1.225 * max(0.0, 1.0 - t_mock / 50.0),
                        "atmo_pa": 101325.0 * max(0.0, 1.0 - t_mock / 50.0),
                        "dyn_pres": 0.5 * 1.225 * (25.0 * t_mock) ** 2 / 1000.0,
                        "g_force": 2.5,
                        "apo": 150000.0,
                        "peri": -500000.0,
                        "sma": 325000.0,
                        "ecc": 0.95,
                        "inc": 0.05,
                        "period": 1800.0,
                        "lat": -0.097,
                        "lon": -74.55,
                        "throttle": 1.0,
                        "stage": 1,
                        "res_sf": max(0.0, 400.0 - 8.0 * t_mock),
                        "res_lf": 0.0,
                        "res_ox": 0.0,
                        "res_ec": 150.0
                    }
                    if sample_count >= 10:
                        raise KeyboardInterrupt

                now = time.time()
                if start_time is None:
                    start_time = now
                met = round(now - start_time, 1)

                ut = safe_float(data.get("ut"), initial_ut)
                alt = safe_float(data.get("alt"))
                rad_alt = safe_float(data.get("rad_alt"))
                v_spd = safe_float(data.get("v_spd"))
                orb_vel = safe_float(data.get("orb_vel"))
                surf_vel = safe_float(data.get("surf_vel"))
                pitch = safe_float(data.get("pitch"), 90.0)
                heading = safe_float(data.get("heading"), 90.0)
                roll = safe_float(data.get("roll"))
                aoa = safe_float(data.get("aoa"))
                density = safe_float(data.get("density"))
                atmo_pa = safe_float(data.get("atmo_pa"))
                q = safe_float(data.get("dyn_pres"))
                g_force = safe_float(data.get("g_force"))
                apo = safe_float(data.get("apo"))
                peri = safe_float(data.get("peri"))
                sma = safe_float(data.get("sma"))
                ecc = safe_float(data.get("ecc"))
                inc = safe_float(data.get("inc"))
                period = safe_float(data.get("period"))
                lat = safe_float(data.get("lat"))
                lon = safe_float(data.get("lon"))
                throttle = safe_float(data.get("throttle"))
                stage = safe_int(data.get("stage"))
                res_sf = safe_float(data.get("res_sf"))
                res_lf = safe_float(data.get("res_lf"))
                res_ox = safe_float(data.get("res_ox"))
                res_ec = safe_float(data.get("res_ec"))

                max_alt = max(max_alt, alt)
                max_vel = max(max_vel, max(orb_vel, surf_vel))
                max_g = max(max_g, g_force)
                max_q = max(max_q, q)
                if alt > 500:
                    min_pitch = min(min_pitch, pitch)

                writer.writerow({
                    "timestamp": round(now, 2),
                    "UT": round(ut, 1),
                    "MET": met,
                    "altitude": round(alt, 1),
                    "radar_alt": round(rad_alt, 1),
                    "vert_speed": round(v_spd, 1),
                    "orbital_vel": round(orb_vel, 1),
                    "surface_vel": round(surf_vel, 1),
                    "pitch": round(pitch, 2),
                    "heading": round(heading, 2),
                    "roll": round(roll, 2),
                    "angle_prograde": round(aoa, 2),
                    "dynamic_pressure": round(q, 2),
                    "atmospheric_density": round(density, 6),
                    "atmospheric_pressure_pa": round(atmo_pa, 1),
                    "g_force": round(g_force, 2),
                    "apoapsis": round(apo, 1),
                    "periapsis": round(peri, 1),
                    "semi_major_axis": round(sma, 1),
                    "eccentricity": round(ecc, 4),
                    "inclination": round(inc, 3),
                    "period": round(period, 1),
                    "latitude": round(lat, 5),
                    "longitude": round(lon, 5),
                    "throttle": round(throttle, 2),
                    "stage": stage,
                    "solid_fuel": round(res_sf, 1),
                    "liquid_fuel": round(res_lf, 1),
                    "oxidizer": round(res_ox, 1),
                    "electric_charge": round(res_ec, 1)
                })
                f.flush()

                print(f"{met:>7.1f} | {alt:>9.1f} | {surf_vel:>9.1f} | {pitch:>5.1f}º | {aoa:>4.1f}º | {apo/1000:>8.1f} | {q:>7.2f} | {g_force:>4.1f}G", end="\r")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\n\n" + "=" * 75)
            print(f"      RECORDING COMPLETE - MISSION SUMMARY: {mission_name}")
            print("=" * 75)
            summary = f"""# 📊 Official Telemetry - Mission {mission_name}
* **Flight Date (Kerbin Calendar)**: {kerbin_date}
* **Recorded Samples**: {met / interval:.0f}

| Flight Metric | Recorded Value |
| :--- | :--- |
| **Flight Duration (MET)** | {met:.1f} s |
| **Maximum Altitude Achieved** | {max_alt:,.1f} m ({(max_alt/1000):.2f} km) |
| **Maximum Speed** | {max_vel:,.1f} m/s (Mach ~{max_vel/310:.2f}) |
| **Maximum Dynamic Pressure (Max Q)** | {max_q:.2f} kPa |
| **Maximum Acceleration** | {max_g:.2f} G |
| **Minimum Pitch Achieved** | {min_pitch:.1f}º |

*High-fidelity telemetry saved in `{csv_file}`.*
"""
            print(summary)
            with open(f"missions/{mission_name}_summary.md", "w") as sf:
                sf.write(summary)
            print(f"[✓] Official summary saved to: missions/{mission_name}_summary.md")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corolt Space Agency Telemetry Recorder v2.0")
    parser.add_argument("mission", nargs="?", default="CSA-07", help="Mission code (e.g., CSA-07)")
    parser.add_argument("--interval", type=float, default=0.5, help="Sampling interval in seconds (default: 0.5)")
    parser.add_argument("--mock", action="store_true", help="Run in synthetic mock test mode without Telemachus")
    args = parser.parse_args()

    record_flight(mission_name=args.mission, interval=args.interval, mock_mode=args.mock)
