#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Universal Sidereal Launch Window Calculator v4.0
Mission-agnostic, orbit-agnostic sidereal launch window calculator with automatic
empirical ascent calibration from historical mission telemetry CSVs.

Usage Examples:
    # Default (CSA-17: +60 deg and -60 deg relative to CoroltSat-1F at 600 km MKO, calibrated from CSA-16)
    python3 tools/calculate_launch_windows.py

    # Custom mission, reference satellite, slots, and telemetry calibration source
    python3 tools/calculate_launch_windows.py --mission CSA-17 --ref CoroltSat-1F --slot 60 -60 --calibrate-from CSA-16

    # Legacy 300 km LEO ring check against CoroltSat-1B calibrated from CSA-15
    python3 tools/calculate_launch_windows.py --mission CSA-16 --ref CoroltSat-1B --slot 160 --calibrate-from CSA-15
"""

import argparse
import csv
import json
import math
import os
import re
import urllib.request

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAVEFILE_PATH = "/media/steam_games/SteamLibrary/steamapps/common/Kerbal Space Program/saves/Corolt Space Agency/persistent.sfs"
TELEMACHUS_URL = "http://127.0.0.1:8085/telemachus/datalink?ut=t.universalTime"
MANIFEST_PATH = os.path.join(REPO_ROOT, "missions", "missions_manifest.json")

# Exact KSP Astrodynamics Constants for Kerbin
KERBIN_MU = 3.5316000e12
KERBIN_RADIUS = 600000.0
KERBIN_SIDEREAL_PERIOD = 21549.4251830898  # Exact sidereal rotation period (s)
KERBIN_SOLAR_DAY = 21600.0                 # Calendar day length (6h) for Y1-Dxxx clock display
KERBIN_THETA0_DEG = 90.0000                # Kerbin initial rotation angle at UT = 0 (deg)
KSC_LON_DEG = -74.55767                    # LaunchPad surface longitude (deg)

# Fallback Ascent Calibration Profiles by Orbital Regime (if CSV not found)
DEFAULT_PROFILES = {
    300: {"dt_ascent": 743.10, "surface_arc_deg": 66.1061, "source": "CSA-15 Empirical Baseline (300 km LEO)"},
    600: {"dt_ascent": 1269.00, "surface_arc_deg": 91.8423, "source": "CSA-16 Empirical Baseline (600 km MKO)"},
}


def get_live_telemachus_ut():
    try:
        req = urllib.request.Request(TELEMACHUS_URL, headers={"User-Agent": "CSA-FlightDynamics/4.0"})
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "ut" in data and isinstance(data["ut"], (int, float)) and data["ut"] > 0:
                return float(data["ut"])
    except Exception:
        pass
    return None


def calibrate_ascent_from_csv(mission_code):
    """
    Automatically extracts empirical ascent duration (T-0 liftoff to SECO-2 + 3s phase audit)
    and surface/inertial longitude arc traversed from a recorded mission telemetry CSV.
    """
    code_clean = mission_code.upper().replace("_", "-")
    csv_path = os.path.join(REPO_ROOT, "missions", f"{code_clean}_telemetry.csv")
    if not os.path.exists(csv_path):
        return None

    with open(csv_path, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        return None

    liftoff_idx = None
    for i, r in enumerate(rows):
        try:
            alt = float(r.get("altitude", 0) or 0)
            vspd = float(r.get("vert_speed", 0) or 0)
            if vspd > 2.0 or alt > 95.0:
                liftoff_idx = max(0, i - 1)
                break
        except (ValueError, TypeError):
            continue

    if liftoff_idx is None:
        return None

    liftoff_row = rows[liftoff_idx]
    ut0 = float(liftoff_row["UT"])
    lon0 = float(liftoff_row["longitude"])

    best_ecc = 999.0
    seco2_row = None
    for r in rows[liftoff_idx:]:
        try:
            ut = float(r["UT"])
            if ut < ut0 + 400.0:
                continue
            ecc = float(r.get("eccentricity", 1.0) or 1.0)
            th = float(r.get("throttle", 0.0) or 0.0)
            if ecc < best_ecc:
                best_ecc = ecc
                seco2_row = r
            if best_ecc < 0.003 and th == 0.0 and seco2_row is not None and ut >= float(seco2_row["UT"]) + 3.0:
                seco2_row = r
                break
        except (ValueError, TypeError):
            continue

    if seco2_row is None:
        return None

    ut_s2 = float(seco2_row["UT"])
    dt_ascent = ut_s2 - ut0
    lon_s2 = float(seco2_row["longitude"])
    srf_arc = (lon_s2 - lon0) % 360.0
    inert_arc = (srf_arc + (360.0 / KERBIN_SIDEREAL_PERIOD) * dt_ascent) % 360.0
    ap_km = float(seco2_row.get("apoapsis", 0) or 0) / 1000.0
    pe_km = float(seco2_row.get("periapsis", 0) or 0) / 1000.0

    return {
        "mission": code_clean,
        "ut0": ut0,
        "ut_seco2": ut_s2,
        "dt_ascent": dt_ascent,
        "surface_arc_deg": srf_arc,
        "inertial_arc_deg": inert_arc,
        "orbit_str": f"{ap_km:.2f} x {pe_km:.2f} km (e={best_ecc:.5f})",
        "source": f"Auto-calibrated from {code_clean}_telemetry.csv",
    }


def load_constellation_state():
    if not os.path.exists(SAVEFILE_PATH):
        raise FileNotFoundError(f"Savefile not found: {SAVEFILE_PATH}")

    with open(SAVEFILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()

    fs_idx = text.find("FLIGHTSTATE")
    if fs_idx != -1:
        m_ut = re.search(r"UT = (\d+\.\d+)", text[fs_idx : fs_idx + 400])
        ut_save = float(m_ut.group(1)) if m_ut else 0.0
    else:
        m_ut = re.search(r"UT = (\d+\.\d+)", text)
        ut_save = float(m_ut.group(1)) if m_ut else 0.0

    ut_live = get_live_telemachus_ut()
    ut = max(ut_save, ut_live) if ut_live is not None else ut_save
    ut_source = (
        "Telemachus Live API"
        if (ut_live is not None and ut_live >= ut_save)
        else "persistent.sfs (FLIGHTSTATE)"
    )

    satellites = {}
    for p in text.split("VESSEL")[1:]:
        header = p[:2500]
        name_m = re.search(r"^\s*name\s*=\s*(.+)", header, re.M)
        vtype_m = re.search(r"^\s*type\s*=\s*(.+)", header, re.M)
        sit_m = re.search(r"^\s*sit\s*=\s*(.+)", header, re.M)
        if not (name_m and vtype_m and sit_m):
            continue
        vname = name_m.group(1).strip()
        vtype = vtype_m.group(1).strip()
        vsit = sit_m.group(1).strip()
        if vsit != "ORBITING" or vtype in ("Debris", "SpaceObject", "Flag"):
            continue
        try:
            sma = float(re.search(r"^\s*SMA\s*=\s*([0-9.E+-]+)", header, re.M).group(1))
            ecc = float(re.search(r"^\s*ECC\s*=\s*([0-9.E+-]+)", header, re.M).group(1))
            inc = float(re.search(r"^\s*INC\s*=\s*([0-9.E+-]+)", header, re.M).group(1))
            lpe = float(re.search(r"^\s*LPE\s*=\s*([0-9.E+-]+)", header, re.M).group(1))
            lan = float(re.search(r"^\s*LAN\s*=\s*([0-9.E+-]+)", header, re.M).group(1))
            mna = float(re.search(r"^\s*MNA\s*=\s*([0-9.E+-]+)", header, re.M).group(1))
            eph = float(re.search(r"^\s*EPH\s*=\s*([0-9.E+-]+)", header, re.M).group(1))
            alt_avg_km = (sma - KERBIN_RADIUS) / 1000.0
            period = 2.0 * math.pi * math.sqrt(sma**3 / KERBIN_MU)
            satellites[vname] = {
                "name": vname,
                "type": vtype,
                "sma": sma,
                "ecc": ecc,
                "inc": inc,
                "lpe": lpe,
                "lan": lan,
                "mna0": mna,
                "eph": eph,
                "alt_km": alt_avg_km,
                "period": period,
            }
        except Exception:
            continue

    return {
        "ut": ut,
        "ut_source": ut_source,
        "satellites": satellites,
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
    for _ in range(12):
        E = E - (E - ecc * math.sin(E) - M) / (1.0 - ecc * math.cos(E))
    nu = 2.0 * math.atan2(
        math.sqrt(1.0 + ecc) * math.sin(E / 2.0),
        math.sqrt(1.0 - ecc) * math.cos(E / 2.0),
    )
    return nu % (2.0 * math.pi)


def get_sat_longitude_deg(sat, t_eval):
    sma = sat["sma"]
    ecc = sat["ecc"]
    period = sat["period"]
    n = 2.0 * math.pi / period
    nu_rad = kepler_true_anomaly_rad(sat["mna0"], ecc, n, t_eval - sat["eph"])
    return (sat["lan"] + sat["lpe"] + math.degrees(nu_rad)) % 360.0


def to_signed_deg(angle_deg):
    a = angle_deg % 360.0
    if a > 180.0:
        a -= 360.0
    return a


def resolve_satellite(satellites, query_name):
    if not query_name:
        return None
    if query_name in satellites:
        return satellites[query_name]
    ql = query_name.lower()
    for name, s in satellites.items():
        if ql in name.lower():
            return s
    return None


def calculate_windows(
    mission_code="CSA-17",
    ref_name="CoroltSat-1F",
    slots=None,
    calibrate_from="CSA-16",
    start_ut=None,
    num_windows=6,
    fueling_lead_sec=485.0,
):
    state = load_constellation_state()
    ut_now = state["ut"]
    ut_source = state["ut_source"]
    satellites = state["satellites"]

    ref_sat = resolve_satellite(satellites, ref_name)
    if not ref_sat:
        avail = ", ".join(satellites.keys())
        raise ValueError(f"Reference satellite '{ref_name}' not found in orbit. Available: {avail}")

    # Calibrate ascent profile from historical CSV or fallback
    cal = calibrate_ascent_from_csv(calibrate_from)
    if cal is None:
        regime_key = 600 if ref_sat["alt_km"] > 450 else 300
        fb = DEFAULT_PROFILES[regime_key]
        dt_ascent = fb["dt_ascent"]
        srf_arc = fb["surface_arc_deg"]
        inert_arc = (srf_arc + (360.0 / KERBIN_SIDEREAL_PERIOD) * dt_ascent) % 360.0
        cal_source = fb["source"]
        cal_orbit_str = f"~{regime_key} km"
    else:
        dt_ascent = cal["dt_ascent"]
        srf_arc = cal["surface_arc_deg"]
        inert_arc = cal["inertial_arc_deg"]
        cal_source = cal["source"]
        cal_orbit_str = cal["orbit_str"]

    def get_ship_insertion_longitude_deg(t_liftoff):
        omega_sid_deg = 360.0 / KERBIN_SIDEREAL_PERIOD
        return (KERBIN_THETA0_DEG + KSC_LON_DEG + omega_sid_deg * t_liftoff + inert_arc) % 360.0

    # Find all co-orbital satellites in the same altitude ring (+/- 50 km)
    ring_sats = [
        s for s in satellites.values() if abs(s["alt_km"] - ref_sat["alt_km"]) < 50.0
    ]
    ring_sats.sort(key=lambda s: s["name"])

    omega_sid_rad = 2.0 * math.pi / KERBIN_SIDEREAL_PERIOD
    n_ref = 2.0 * math.pi / ref_sat["period"]
    synodic_period = 2.0 * math.pi / abs(omega_sid_rad - n_ref)

    if not slots:
        slots = [60.0, -60.0] if ref_sat["alt_km"] > 450 else [40.0, -40.0]

    t_start = ut_now if start_ut is None else max(ut_now, start_ut)

    # Load payload name from manifest if available
    payload_name = "Payload"
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as mf:
                manifest = json.load(mf)
                m_info = manifest.get(mission_code.upper(), {})
                payload_name = m_info.get("payload", payload_name).split(" (")[0]
        except Exception:
            pass

    print("======================================================================================================")
    print(f"  COROLT SPACE AGENCY - UNIVERSAL SIDEREAL LAUNCH WINDOW CALCULATOR v4.0 ({mission_code.upper()}) ")
    print("======================================================================================================")
    print(f"Current Game UT:             {ut_now:.1f} s ({format_kerbin_time(ut_now)}) [{ut_source}]")
    print(f"Kerbin Sidereal Period:      {KERBIN_SIDEREAL_PERIOD:.6f} s (theta_0 = {KERBIN_THETA0_DEG:.3f} deg at UT=0)")
    print(f"Reference Anchor Satellite:  {ref_sat['name']} (Alt: {ref_sat['alt_km']:.2f} km, SMA: {ref_sat['sma']:.1f} m, T: {ref_sat['period']:.2f} s)")
    print(f"Co-Orbital Ring Nodes:       {', '.join(s['name'] for s in ring_sats)}")
    print(f"Ascent Calibration Source:   {cal_source} [{cal_orbit_str}]")
    print(f"Ascent Duration (T-0->Audit):{dt_ascent:.2f} s ({dt_ascent/60:.2f} min)")
    print(f"Ascent Surface / Inert Arc:  {srf_arc:.4f} deg surface / {inert_arc:.4f} deg inertial")
    print(f"Synodic Launch Cycle:        {synodic_period:.2f} s ({synodic_period/60:.2f} min)")
    print(f"Pad Fueling + Countdown:     ~{fueling_lead_sec:.0f} s ({fueling_lead_sec/60:.1f} min) required before T-0 Liftoff")
    print("------------------------------------------------------------------------------------------------------")

    sat_n_deg = 360.0 / ref_sat["period"]
    omega_sid_deg = 360.0 / KERBIN_SIDEREAL_PERIOD
    rate_deg_per_s = omega_sid_deg - sat_n_deg
    sat_synodic = 360.0 / abs(rate_deg_per_s)

    for slot_deg in slots:
        target_deg = slot_deg % 360.0
        signed_target = to_signed_deg(target_deg)
        print(f"\n🚀 EXACT SIDEREAL LAUNCH WINDOWS FOR SLOT {signed_target:+.1f} DEG RELATIVE TO {ref_sat['name'].upper()}:")
        print(f"{'#':<3} | {'KERBIN TIME (T-0)':<18} | {'LIFTOFF UT (s)':<14} | {'START SCRIPT BY':<16} | {'WAIT FROM NOW':<16} | {'PHASE AT SECO-2'}")
        print("-" * 102)

        t = t_start
        found = 0

        while found < num_windows:
            t_sol = t
            for _ in range(14):
                t_ins = t_sol + dt_ascent
                l_ins = get_ship_insertion_longitude_deg(t_sol)
                l_ref = get_sat_longitude_deg(ref_sat, t_ins)
                diff = (l_ins - l_ref) % 360.0
                err = to_signed_deg(diff - target_deg)
                t_sol -= err / rate_deg_per_s

            if t_sol >= t_start:
                cd_sec = t_sol - ut_now
                cd_hr = int(cd_sec // 3600)
                cd_mn = int((cd_sec % 3600) // 60)
                cd_sc = int(cd_sec % 60)
                status_tag = "🟢 GO" if cd_sec >= fueling_lead_sec else "🟡 TIGHT (<8m)"
                cd_str = f"T+{cd_hr:02d}h {cd_mn:02d}m {cd_sc:02d}s"

                t_script_max = t_sol - fueling_lead_sec
                script_str = f"UT {t_script_max:.0f} ({status_tag})"

                t_ins = t_sol + dt_ascent
                l_ins = get_ship_insertion_longitude_deg(t_sol)
                ph_ref = to_signed_deg(l_ins - get_sat_longitude_deg(ref_sat, t_ins))

                print(
                    f"{found+1:<3} | {format_kerbin_time(t_sol):<18} | {t_sol:<14.1f} | {script_str:<16} | {cd_str:<16} | {ph_ref:+06.2f}º vs {ref_sat['name']}"
                )
                found += 1

            t = t_sol + sat_synodic * 0.90

    first_slot = to_signed_deg(slots[0])
    target_alt_km = round(ref_sat["alt_km"] / 10.0) * 10.0
    print("\n======================================================================================================")
    print(f"OPERATIONAL INSTRUCTIONS ({mission_code.upper()} / {payload_name}):")
    print(f"1. Quarter-rate pad fueling (25% duty cycle) + countdown requires ~{fueling_lead_sec:.0f}s (~8.1 min).")
    print("   Always choose a window marked 🟢 GO (at least 9-10 minutes ahead of current UT)!")
    print("2. Execute universal guided ascent on the pad:")
    print(
        f'   RUNPATH("0:/csa/universal_guided_ascent.ks", {target_alt_km:.1f}, <LIFTOFF_UT>, {first_slot:.1f}, "{ref_sat["name"]}", "{mission_code.upper()}", "{payload_name}").'
    )
    print("3. If post-SECO-2 orbital phasing is required (> 0.50 deg deviation), execute:")
    print(f'   RUNPATH("0:/csa/constellation_phasing.ks", {first_slot:.1f}, 3, "{ref_sat["name"]}").')
    print("======================================================================================================")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CSA Universal Sidereal Launch Window Calculator v4.0"
    )
    parser.add_argument("--mission", type=str, default="CSA-17", help="Mission code (default: CSA-17)")
    parser.add_argument("--ref", type=str, default="CoroltSat-1F", help="Reference anchor satellite name (default: CoroltSat-1F)")
    parser.add_argument("--slot", type=float, nargs="+", default=None, help="Target phase angle slot(s) in deg (e.g. 60 -60)")
    parser.add_argument("--calibrate-from", type=str, default="CSA-16", help="Mission code to auto-calibrate ascent profile from (default: CSA-16)")
    parser.add_argument("--day", type=int, default=None, help="Kerbin calendar day to search from")
    parser.add_argument("--ut", type=float, default=None, help="Exact starting UT in seconds")
    parser.add_argument("--count", type=int, default=6, help="Number of windows per slot to generate")
    args = parser.parse_args()

    start_ut_val = args.ut
    if args.day is not None:
        start_ut_val = (args.day - 1) * KERBIN_SOLAR_DAY

    calculate_windows(
        mission_code=args.mission,
        ref_name=args.ref,
        slots=args.slot,
        calibrate_from=args.calibrate_from,
        start_ut=start_ut_val,
        num_windows=args.count,
    )
