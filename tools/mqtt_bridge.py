#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - MQTT Bridge for Home Assistant
Publishes MQTT Auto-Discovery configs and streams live or latest mission telemetry
to the Mosquitto MQTT broker (192.168.1.14:1883) using zero external dependencies (raw TCP socket).
"""

import argparse
import csv
import glob
import json
import os
import socket
import struct
import time

MQTT_HOST = "192.168.1.14"
MQTT_PORT = 1883
STATE_TOPIC = "csa/telemetry/state"

DEVICE_INFO = {
    "identifiers": ["csa_mission_control_telemetry"],
    "name": "CSA Flight Telemetry Computer",
    "manufacturer": "Corolt Space Agency (CSA)",
    "model": "Telemachus / kOS Avionics Bridge v2.0",
    "sw_version": "CSA Telemetry OS 2.4"
}

SENSORS = [
    {"id": "mission_name", "name": "Active Mission Code", "icon": "mdi:rocket-launch"},
    {"id": "flight_status", "name": "Flight Status", "icon": "mdi:satellite-uplink"},
    {"id": "met", "name": "Mission Elapsed Time (MET)", "unit": "s", "device_class": "duration", "icon": "mdi:timer-outline", "state_class": "measurement"},
    {"id": "altitude_km", "name": "Altitude (ASL)", "unit": "km", "device_class": "distance", "icon": "mdi:altimeter", "state_class": "measurement"},
    {"id": "apoapsis_km", "name": "Apoapsis (ApA)", "unit": "km", "device_class": "distance", "icon": "mdi:orbit", "state_class": "measurement"},
    {"id": "periapsis_km", "name": "Periapsis (PeA)", "unit": "km", "device_class": "distance", "icon": "mdi:orbit", "state_class": "measurement"},
    {"id": "surface_vel", "name": "Surface Velocity", "unit": "m/s", "device_class": "speed", "icon": "mdi:speedometer", "state_class": "measurement"},
    {"id": "orbital_vel", "name": "Orbital Velocity", "unit": "m/s", "device_class": "speed", "icon": "mdi:speedometer-medium", "state_class": "measurement"},
    {"id": "vert_speed", "name": "Vertical Speed", "unit": "m/s", "device_class": "speed", "icon": "mdi:arrow-up-bold-circle-outline", "state_class": "measurement"},
    {"id": "g_force", "name": "G-Force Load", "unit": "G", "icon": "mdi:Axis-arrow", "state_class": "measurement"},
    {"id": "dynamic_pressure", "name": "Dynamic Pressure (Q)", "unit": "kPa", "device_class": "pressure", "icon": "mdi:weather-windy", "state_class": "measurement"},
    {"id": "pitch", "name": "Pitch Attitude", "unit": "°", "icon": "mdi:compass-rose", "state_class": "measurement"},
    {"id": "heading", "name": "Heading", "unit": "°", "icon": "mdi:compass", "state_class": "measurement"},
    {"id": "roll", "name": "Roll Angle", "unit": "°", "icon": "mdi:rotate-right", "state_class": "measurement"},
    {"id": "throttle_pct", "name": "Main Throttle", "unit": "%", "icon": "mdi:fire", "state_class": "measurement"},
    {"id": "stage", "name": "Active Stage", "icon": "mdi:layers-triple", "state_class": "measurement"},
    {"id": "electric_charge", "name": "Electric Charge", "unit": "EC", "icon": "mdi:battery-charging-high", "state_class": "measurement"},
    {"id": "temp_skin", "name": "Hull Skin Temperature", "unit": "K", "device_class": "temperature", "icon": "mdi:thermometer-alert", "state_class": "measurement"},
    {"id": "inclination", "name": "Orbital Inclination", "unit": "°", "icon": "mdi:angle-acute", "state_class": "measurement"},
    {"id": "eccentricity", "name": "Orbital Eccentricity", "icon": "mdi:vector-circle-variant", "state_class": "measurement"},
]


def _encode_varlen(length):
    out = bytearray()
    while True:
        byte = length % 128
        length //= 128
        if length > 0:
            byte |= 128
        out.append(byte)
        if length == 0:
            break
    return bytes(out)


def _encode_str(s):
    b = s.encode("utf-8")
    return struct.pack("!H", len(b)) + b


class SimpleMQTTClient:
    """Minimal zero-dependency MQTT v3.1.1 publisher over standard TCP sockets."""

    def __init__(self, host=MQTT_HOST, port=MQTT_PORT, client_id="csa_telemetry_bridge"):
        self.host = host
        self.port = port
        self.client_id = client_id
        self.sock = None

    def connect(self):
        self.sock = socket.create_connection((self.host, self.port), timeout=3.0)
        var_header = _encode_str("MQTT") + bytes([4, 2]) + struct.pack("!H", 60)
        payload = _encode_str(self.client_id)
        packet = bytes([0x10]) + _encode_varlen(len(var_header) + len(payload)) + var_header + payload
        self.sock.sendall(packet)
        resp = self.sock.recv(4)
        if len(resp) < 4 or resp[0] != 0x20 or resp[3] != 0x00:
            raise ConnectionError(f"MQTT CONNACK failed: {resp}")

    def publish(self, topic, payload_obj, retain=False):
        if self.sock is None:
            self.connect()
        t_bytes = _encode_str(topic)
        if isinstance(payload_obj, (dict, list)):
            p_bytes = json.dumps(payload_obj).encode("utf-8")
        else:
            p_bytes = str(payload_obj).encode("utf-8")
        header_byte = 0x31 if retain else 0x30
        rem_len = len(t_bytes) + len(p_bytes)
        packet = bytes([header_byte]) + _encode_varlen(rem_len) + t_bytes + p_bytes
        try:
            self.sock.sendall(packet)
        except Exception:
            self.connect()
            self.sock.sendall(packet)

    def close(self):
        if self.sock:
            try:
                self.sock.sendall(bytes([0xE0, 0x00]))
                self.sock.close()
            except Exception:
                pass
            self.sock = None


def publish_discovery(client):
    for s in SENSORS:
        uid = f"csa_ksp_{s['id']}"
        cfg_topic = f"homeassistant/sensor/csa_ksp/{s['id']}/config"
        payload = {
            "name": s["name"],
            "unique_id": uid,
            "default_entity_id": f"sensor.csa_ksp_{s['id']}",
            "state_topic": STATE_TOPIC,
            "value_template": f"{{{{ value_json.{s['id']} }}}}",
            "icon": s["icon"],
            "device": DEVICE_INFO,
        }
        if "unit" in s:
            payload["unit_of_measurement"] = s["unit"]
        if "device_class" in s:
            payload["device_class"] = s["device_class"]
        if "state_class" in s:
            payload["state_class"] = s["state_class"]
        client.publish(cfg_topic, payload, retain=True)


def format_telemetry_payload(mission_name, status, row):
    def fval(k, default=0.0):
        try:
            return float(row.get(k, default))
        except Exception:
            return default

    alt_m = fval("altitude")
    apo_m = fval("apoapsis")
    peri_m = fval("periapsis")
    throttle = fval("throttle")
    ec = fval("electric_charge")

    return {
        "mission_name": mission_name,
        "flight_status": status,
        "met": round(fval("MET"), 1),
        "altitude_km": round(alt_m / 1000.0, 2),
        "apoapsis_km": round(apo_m / 1000.0, 2),
        "periapsis_km": round(peri_m / 1000.0, 2),
        "surface_vel": round(fval("surface_vel"), 1),
        "orbital_vel": round(fval("orbital_vel"), 1),
        "vert_speed": round(fval("vert_speed"), 1),
        "g_force": round(fval("g_force"), 2),
        "dynamic_pressure": round(fval("dynamic_pressure") / 1000.0 if fval("dynamic_pressure") > 500 else fval("dynamic_pressure"), 2),
        "pitch": round(fval("pitch", 90.0), 1),
        "heading": round(fval("heading", 90.0), 1),
        "roll": round(fval("roll", 0.0), 1),
        "throttle_pct": round(throttle * 100.0 if throttle <= 1.0 else throttle, 0),
        "stage": int(fval("stage", 0)),
        "electric_charge": round(max(0.0, ec), 1),
        "temp_skin": round(fval("temp_skin", 288.0), 1),
        "inclination": round(fval("inclination", 0.0), 2),
        "eccentricity": round(fval("eccentricity", 0.0), 4),
    }


def replay_csv_to_mqtt(csv_path, mission_name=None, speed_factor=10.0):
    if not mission_name:
        base = os.path.basename(csv_path)
        mission_name = base.replace("_telemetry.csv", "")

    client = SimpleMQTTClient()
    client.connect()
    publish_discovery(client)

    with open(csv_path, "r") as f:
        rows = list(csv.DictReader(f))

    if not rows:
        print("Empty CSV file.")
        return

    print(f"[*] Replaying {len(rows)} frames from {mission_name} to Home Assistant MQTT...")
    step = max(1, len(rows) // 45)
    sampled = rows[::step]
    if rows[-1] not in sampled:
        sampled.append(rows[-1])

    for i, r in enumerate(sampled):
        status = "IN FLIGHT (REPLAY)" if i < len(sampled) - 1 else "MISSION COMPLETED"
        payload = format_telemetry_payload(mission_name, status, r)
        client.publish(STATE_TOPIC, payload, retain=True)
        time.sleep(0.15)

    # Finally set peak summary state so gauges show peak flight metrics when idle
    max_alt = max(float(r.get("altitude", 0)) for r in rows)
    max_apo = max(float(r.get("apoapsis", 0)) for r in rows)
    max_peri = max(float(r.get("periapsis", -600000)) for r in rows)
    max_svel = max(float(r.get("surface_vel", 0)) for r in rows)
    max_ovel = max(float(r.get("orbital_vel", 0)) for r in rows)
    max_g = max(float(r.get("g_force", 0)) for r in rows)
    max_q = max(float(r.get("dynamic_pressure", 0)) for r in rows)
    max_temp = max(float(r.get("temp_skin", 288)) for r in rows)
    last_r = dict(rows[-1])
    last_r["altitude"] = max_alt
    last_r["apoapsis"] = max_apo
    last_r["periapsis"] = max_peri
    last_r["surface_vel"] = max_svel
    last_r["orbital_vel"] = max_ovel
    last_r["g_force"] = max_g
    last_r["dynamic_pressure"] = max_q / 1000.0 if max_q > 500 else max_q
    last_r["temp_skin"] = max_temp

    final_payload = format_telemetry_payload(mission_name, "STANDBY (LAST PEAK)", last_r)
    client.publish(STATE_TOPIC, final_payload, retain=True)
    client.close()
    print(f"[✓] Replay complete! {mission_name} telemetry published to Home Assistant.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSA MQTT Telemetry Bridge for Home Assistant")
    parser.add_argument("--replay", help="Path to a mission CSV to replay to MQTT", default=None)
    args = parser.parse_args()

    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if args.replay:
        csv_file = args.replay
    else:
        csv_files = sorted(glob.glob(os.path.join(repo_dir, "missions", "*_telemetry.csv")))
        csv_file = csv_files[-1] if csv_files else None

    if csv_file and os.path.exists(csv_file):
        replay_csv_to_mqtt(csv_file)
    else:
        print("No telemetry CSV found to replay.")
