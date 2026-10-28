#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Live Telemetry Recorder v3.0 (Zero-Leak Proxy & Laptop Edition)
Connects to the CSA Zero-Leak Memory Proxy (:9105/csa_raw) or Telemachus (:8085) via persistent
HTTP Keep-Alive sockets. Can run locally on the host tower (127.0.0.1) or remotely on a laptop
(192.168.1.50 / Tailscale 100.71.29.22) with zero additional memory pressure on KSP/Mono.
"""

import urllib.request
import urllib.parse
import http.client
import json
import time
import sys
import os
import csv
import argparse
import signal

try:
    from mqtt_bridge import SimpleMQTTClient, publish_discovery, format_telemetry_payload, STATE_TOPIC
    HAS_MQTT_BRIDGE = True
except Exception:
    HAS_MQTT_BRIDGE = False


def _handle_sigterm(signum, frame):
    raise KeyboardInterrupt


signal.signal(signal.SIGTERM, _handle_sigterm)

DEFAULT_LAN_HOST = os.environ.get("CSA_HOST", "192.168.1.50")

# Strictly verified Telemachus.dll API keys (Zero UnknownAPIException in C#/Mono)
QUERY_PARAMS = {
    "ut": "t.universalTime",
    "mtime": "v.missionTime",
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
    "res_ec": "r.resource[ElectricCharge]",
    "fuel_lf": "r.resource[LiquidFuel]",
    "fuel_ox": "r.resource[Oxidizer]",
    "fuel_sf": "r.resource[SolidFuel]",
    "temp_sensor": "s.sensor.temp",
}

QUERY_API = "/telemachus/datalink?" + "&".join(f"{k}={urllib.parse.quote(v)}" for k, v in QUERY_PARAMS.items())


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


class PersistentTelemetryClient:
    """Zero-leak telemetry fetcher: prefers the in-memory proxy (:9105/csa_raw) and reuses TCP Keep-Alive sockets."""

    def __init__(self, host=None):
        self.host = self._resolve_host(host)
        self.proxy_conn = None
        self.direct_conn = None
        self.using_proxy = False

    def _resolve_host(self, requested_host):
        if requested_host and requested_host != "auto":
            return requested_host
        # Check if local proxy (:9105) or local Telemachus (:8085) is listening
        for port in (9105, 8085):
            try:
                with socket.create_connection(("127.0.0.1", port), timeout=0.4):
                    return "127.0.0.1"
            except Exception:
                pass
        return DEFAULT_LAN_HOST

    def fetch(self, fast=True):
        # 1. Try Zero-Load RAM Proxy on port 9105 first (0 requests to KSP.x86_64!)
        path = "/csa_raw?fast=1" if fast else "/csa_raw"
        for _ in range(2):
            try:
                if self.proxy_conn is None:
                    self.proxy_conn = http.client.HTTPConnection(self.host, 9105, timeout=1.2)
                self.proxy_conn.request(
                    "GET", path, headers={"User-Agent": "CSA-Recorder/3.0", "Connection": "keep-alive"}
                )
                resp = self.proxy_conn.getresponse()
                raw = resp.read()
                if resp.status == 200 and raw:
                    data = json.loads(raw.decode("utf-8", errors="ignore"))
                    if data.get("_live") and data.get("alt") is not None:
                        self.using_proxy = True
                        return data
                    elif "_live" in data and not data.get("_live"):
                        self.using_proxy = True
                        return None
            except Exception:
                if self.proxy_conn is not None:
                    try:
                        self.proxy_conn.close()
                    except Exception:
                        pass
                    self.proxy_conn = None

        # 2. Fallback: Persistent HTTP Keep-Alive directly to Telemachus (:8085)
        for _ in range(2):
            try:
                if self.direct_conn is None:
                    self.direct_conn = http.client.HTTPConnection(self.host, 8085, timeout=1.5)
                self.direct_conn.request(
                    "GET", QUERY_API, headers={"User-Agent": "CSA-Recorder/3.0", "Connection": "keep-alive"}
                )
                resp = self.direct_conn.getresponse()
                raw = resp.read()
                if resp.status == 200 and raw:
                    data = json.loads(raw.decode("utf-8", errors="ignore"))
                    if data.get("alt") is not None and "errors" not in data:
                        self.using_proxy = False
                        return data
            except Exception:
                if self.direct_conn is not None:
                    try:
                        self.direct_conn.close()
                    except Exception:
                        pass
                    self.direct_conn = None
        return None


def record_flight(mission_name="CSA-07", interval=0.5, mock_mode=False, host="auto", record_pad=False):
    print(f"\n================================================================================")
    print(f"   COROLT SPACE AGENCY (CSA) - ZERO-LEAK TELEMETRY RECORDER v3.0 (PROXY/LAN)   ")
    print(f"================================================================================")

    initial_ut = 0.0
    kerbin_date = "Year 1, Day 1 (00h 00m 00s)"
    client = None

    if not mock_mode:
        client = PersistentTelemetryClient(host=host)
        print(f"[*] Target Telemetry Host: {client.host} (Proxy :9105 / Telemachus :8085)...")
        data = client.fetch(fast=False)
        if data is None:
            print(f"[!] Waiting for vessel to be loaded on launchpad...")
            while data is None:
                time.sleep(1.5)
                data = client.fetch(fast=False)
        mode_str = "ZERO-LOAD RAM PROXY (:9105)" if client.using_proxy else "DIRECT KEEP-ALIVE (:8085)"
        print(f"[✓] Telemetry link established via {mode_str}!")
        initial_ut = safe_float(data.get("ut", 0.0))
        kerbin_date = ut_to_kerbin_date(initial_ut)
        print(f"[📅] Official Kerbin Date: {kerbin_date} (UT: {initial_ut:,.1f}s)")
    else:
        print(f"[🔬] MOCK MODE ACTIVE: Generating synthetic verification data...")

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    missions_dir = os.path.join(repo_root, "missions")
    os.makedirs(missions_dir, exist_ok=True)
    csv_file = os.path.join(missions_dir, f"{mission_name}_telemetry.csv")

    fieldnames = [
        "timestamp", "UT", "MET",
        "altitude", "radar_alt", "vert_speed", "orbital_vel", "surface_vel",
        "pitch", "heading", "roll", "angle_prograde",
        "dynamic_pressure", "atmospheric_density", "atmospheric_pressure_pa", "g_force",
        "apoapsis", "periapsis", "semi_major_axis", "eccentricity", "inclination", "period",
        "latitude", "longitude",
        "throttle", "stage",
        "solid_fuel", "liquid_fuel", "oxidizer", "electric_charge", "electric_charge_max",
        "temp_ambient", "temp_core", "temp_skin", "temp_sensor"
    ]

    start_time = None
    max_alt = 0.0
    max_vel = 0.0
    max_g = 0.0
    max_q = 0.0
    min_pitch = 90.0
    max_skin_temp = 0.0
    written_rows = 0
    flight_active = record_pad or mock_mode
    last_pad_sample_ts = 0.0

    with open(csv_file, mode="w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        print(f"[*] Recording telemetry to: {csv_file}")
        mqtt_client = None
        # Only open a secondary MQTT connection if we are NOT using the torre_ksp_agent proxy (which already publishes MQTT)
        if HAS_MQTT_BRIDGE and not mock_mode and (client is None or not client.using_proxy):
            try:
                mqtt_client = SimpleMQTTClient()
                mqtt_client.connect()
                publish_discovery(mqtt_client)
                print(f"[📡] Direct MQTT Telemetry Uplink ACTIVE -> 192.168.1.14:1883 ({STATE_TOPIC})")
            except Exception as e:
                print(f"[!] MQTT Uplink unavailable ({e}), continuing local recording...")
                mqtt_client = None
        elif not mock_mode and client and client.using_proxy:
            print(f"[🛡️] Proxy MQTT deduplication active (torre-ksp-agent handles MQTT & Prometheus)")

        print(f"    (Press Ctrl+C to stop recording and generate mission summary)\n")
        print(f"{'MET (s)':>7} | {'Alt (m)':>9} | {'Spd (m/s)':>9} | {'Pitch':>6} | {'Apo (km)':>8} | {'Q (kPa)':>7} | {'EC':>6} | {'Skin T (K)':>10}")
        print("-" * 85)

        try:
            sample_count = 0
            while True:
                if not mock_mode:
                    data = client.fetch(fast=flight_active)
                    if not data:
                        time.sleep(max(1.0, interval))
                        continue
                else:
                    sample_count += 1
                    t_mock = sample_count * interval
                    data = {
                        "ut": 100000.0 + t_mock,
                        "mtime": t_mock,
                        "alt": 75.0 + 0.5 * 25.0 * (t_mock ** 2),
                        "rad_alt": 5.0 + 0.5 * 25.0 * (t_mock ** 2),
                        "v_spd": 25.0 * t_mock,
                        "orb_vel": 175.0 + 25.0 * t_mock,
                        "surf_vel": 25.0 * t_mock,
                        "pitch": max(30.0, 90.0 - 0.8 * t_mock),
                        "heading": 270.0,
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
                        "res_ec": max(0.0, 800.0 - 2.5 * t_mock),
                        "res_ec_max": 800.0,
                        "temp_atmo": 288.15 - min(70.0, 1.5 * t_mock),
                        "temp_core": 290.0,
                        "temp_skin": 290.0 + 2.0 * t_mock,
                        "temp_sensor": 288.0
                    }
                    if sample_count >= 10:
                        raise KeyboardInterrupt

                now = time.time()
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

                res_sf = safe_float(data.get("res_sf"), safe_float(data.get("fuel_sf"), -1.0))
                res_lf = safe_float(data.get("res_lf"), safe_float(data.get("fuel_lf"), -1.0))
                res_ox = safe_float(data.get("res_ox"), safe_float(data.get("fuel_ox"), -1.0))
                res_ec = safe_float(data.get("res_ec"), -1.0)
                if res_ec < 0:
                    res_ec = safe_float(data.get("res_ec_alt"), -1.0)
                res_ec_max = safe_float(data.get("res_ec_max"), -1.0)

                temp_atmo = safe_float(data.get("temp_atmo"), 0.0)
                temp_core = safe_float(data.get("temp_core"), 0.0)
                temp_skin = safe_float(data.get("temp_skin"), 0.0)
                raw_tsensor = data.get("temp_sensor")
                if isinstance(raw_tsensor, list) and len(raw_tsensor) >= 2 and isinstance(raw_tsensor[1], list) and raw_tsensor[1]:
                    temp_sensor = safe_float(raw_tsensor[1][0], temp_skin)
                else:
                    temp_sensor = safe_float(raw_tsensor, temp_skin)

                # Native in-game MET when available, otherwise wall-clock from liftoff/activation
                ingame_met = safe_float(data.get("met", data.get("mtime")), -1.0)
                if not flight_active and (ingame_met > 0.1 or throttle > 0.01 or alt > 115.0 or v_spd > 1.5):
                    flight_active = True
                    start_time = now - max(0.0, ingame_met)

                if start_time is None:
                    start_time = now
                met = round(ingame_met, 1) if ingame_met > 0.0 else round(now - start_time, 1)

                max_alt = max(max_alt, alt)
                max_vel = max(max_vel, max(orb_vel, surf_vel))
                max_g = max(max_g, g_force)
                max_q = max(max_q, q)
                max_skin_temp = max(max_skin_temp, temp_skin)
                if alt > 500:
                    min_pitch = min(min_pitch, pitch)

                row_dict = {
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
                    "electric_charge": round(res_ec, 1),
                    "electric_charge_max": round(res_ec_max, 1),
                    "temp_ambient": round(temp_atmo, 1),
                    "temp_core": round(temp_core, 1),
                    "temp_skin": round(temp_skin, 1),
                    "temp_sensor": round(temp_sensor, 1)
                }

                # Pad Hold Smart Gate: while sitting idle on the pad (MET=0, throttle=0), write only 1 baseline row every 15s
                if flight_active or (now - last_pad_sample_ts >= 15.0):
                    writer.writerow(row_dict)
                    f.flush()
                    written_rows += 1
                    last_pad_sample_ts = now

                if mqtt_client is not None:
                    try:
                        mqtt_payload = format_telemetry_payload(mission_name, "IN FLIGHT (LIVE)", row_dict)
                        mqtt_client.publish(STATE_TOPIC, mqtt_payload, retain=True)
                    except Exception:
                        pass

                ec_str = f"{res_ec:.0f}" if res_ec >= 0 else "N/A"
                pad_tag = "" if flight_active else " [PAD-HOLD ECO]"
                print(
                    f"{met:>7.1f} | {alt:>9.1f} | {surf_vel:>9.1f} | {pitch:>5.1f}º | {apo/1000:>8.1f} | {q:>7.2f} | {ec_str:>6} | {temp_skin:>10.1f}{pad_tag}   ",
                    end="\r",
                    flush=True
                )
                time.sleep(interval if flight_active else max(1.5, interval))

        except KeyboardInterrupt:
            print("\n\n" + "=" * 75)
            print(f"      RECORDING COMPLETE - MISSION SUMMARY: {mission_name}")
            print("=" * 75)
            summary = f"""# 📊 Official Telemetry - Mission {mission_name}
* **Flight Date (Kerbin Calendar)**: {kerbin_date}
* **Recorded Samples**: {written_rows}

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
            with open(os.path.join(missions_dir, f"{mission_name}_summary.md"), "w") as sf:
                sf.write(summary)
            print(f"[✓] Official summary saved to: missions/{mission_name}_summary.md")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corolt Space Agency Telemetry Recorder v3.0 (Zero-Leak Proxy & Laptop Edition)")
    parser.add_argument("mission", nargs="?", default="CSA-07", help="Mission code (e.g., CSA-19)")
    parser.add_argument("--interval", type=float, default=0.5, help="Sampling interval in seconds (default: 0.5)")
    parser.add_argument("--host", type=str, default="auto", help="Telemetry host IP (default: auto -> 127.0.0.1 or 192.168.1.50)")
    parser.add_argument("--record-pad", action="store_true", help="Record 0.5s frames even while stationary on launchpad")
    parser.add_argument("--mock", action="store_true", help="Run in synthetic mock test mode without Telemachus")
    args = parser.parse_args()

    record_flight(
        mission_name=args.mission,
        interval=args.interval,
        mock_mode=args.mock,
        host=args.host,
        record_pad=args.record_pad
    )
