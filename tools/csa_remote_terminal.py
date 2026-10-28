#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Remote kOS Terminal Bridge v3.0 (Local & LAN Laptop Support)
Crash-proof alternative to kOS Telnet on Linux (avoids Mono libKernel32 crash).
Works seamlessly both locally on the KSP host and remotely from a laptop over LAN (--host 192.168.1.50)!

Usage:
  Interactive shell (from Laptop over LAN):
    python3 tools/csa_remote_terminal.py --host 192.168.1.50
  One-shot command + live console tail:
    python3 tools/csa_remote_terminal.py --host 192.168.1.50 -c "go 4292554.6 60"
  Follow live kOS console output only:
    python3 tools/csa_remote_terminal.py --host 192.168.1.50 --tail
"""

import argparse
import json
import os
import readline
import sys
import time
import urllib.request

KOS_SCRIPT_ROOT = "/media/steam_games/SteamLibrary/steamapps/common/Kerbal Space Program/Ships/Script"
CMD_FILE_PATH = os.path.join(KOS_SCRIPT_ROOT, "remote_cmd.ks")
ACK_FILE_PATH = os.path.join(KOS_SCRIPT_ROOT, "remote_ack.txt")
LIVE_LOG_PATH = os.path.join(KOS_SCRIPT_ROOT, "kos_live.log")
OVERRIDE_UT_PATH = os.path.join(KOS_SCRIPT_ROOT, "override_ut.txt")

TARGET_HOST = os.environ.get("CSA_HOST", "127.0.0.1")


def _proxy_base():
    return f"http://{TARGET_HOST}:9105"


def _is_local_fs():
    return TARGET_HOST in ("127.0.0.1", "localhost") and os.path.isdir(KOS_SCRIPT_ROOT)


def get_live_telemetry():
    # 1. Read from Zero-Leak RAM Proxy (:9105/csa_raw) -> 0 TCP/GC load on KSP!
    try:
        req = urllib.request.Request(f"{_proxy_base()}/csa_raw")
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("_live") and "ut" in data:
                return data
            if "_live" in data and not data.get("_live"):
                return None
    except Exception:
        pass
    # 2. Fallback to Telemachus if proxy service is stopped
    try:
        t_url = f"http://{TARGET_HOST}:8085/telemachus/datalink?ut=t.universalTime&met=v.missionTime&alt=v.altitude&ap=o.ApA&pe=o.PeA&ecc=o.eccentricity&period=o.period&th=f.throttle"
        req = urllib.request.Request(t_url)
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if "ut" in data:
                return data
    except Exception:
        pass
    return None


def read_kos_log():
    if _is_local_fs():
        if os.path.exists(LIVE_LOG_PATH):
            with open(LIVE_LOG_PATH, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        return ""
    try:
        req = urllib.request.Request(f"{_proxy_base()}/kos_log")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def read_kos_ack():
    if _is_local_fs():
        if os.path.exists(ACK_FILE_PATH):
            with open(ACK_FILE_PATH, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        return ""
    try:
        req = urllib.request.Request(f"{_proxy_base()}/kos_ack")
        with urllib.request.urlopen(req, timeout=1.0) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    except Exception:
        return ""


def write_kos_file(filename, content):
    if _is_local_fs():
        target = OVERRIDE_UT_PATH if filename == "override_ut.txt" else CMD_FILE_PATH
        with open(target, "w", encoding="utf-8") as f:
            f.write(content)
        return True
    try:
        body = json.dumps({"file": filename, "content": content}).encode("utf-8")
        req = urllib.request.Request(
            f"{_proxy_base()}/kos_cmd",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"⚠️ Error sending command to {TARGET_HOST}:9105/kos_cmd: {e}")
        return False


def format_status_bar(t_data):
    if not t_data:
        return "[Telemachus: OFFLINE]"
    ut = t_data.get("ut", 0.0) or 0.0
    met = t_data.get("met", t_data.get("mtime", 0.0)) or 0.0
    alt = (t_data.get("alt", 0.0) or 0.0) / 1000.0
    ap = (t_data.get("ap", t_data.get("apo", 0.0)) or 0.0) / 1000.0
    pe = (t_data.get("pe", t_data.get("peri", 0.0)) or 0.0) / 1000.0
    ecc = t_data.get("ecc", 0.0) or 0.0
    per = t_data.get("period", 0.0) or 0.0
    th = (t_data.get("th", t_data.get("throttle", 0.0)) or 0.0) * 100.0
    return (
        f"[UT: {ut:9.1f}s | MET: {met:6.1f}s | Alt: {alt:6.2f}km | "
        f"Orbit: {ap:6.2f} x {pe:6.2f}km (e={ecc:.5f}, T={per:.1f}s) | Th: {th:3.0f}%]"
    )


def tail_live_log(initial_lines=20):
    """Streams 0:/kos_live.log + Telemachus status bar in real time to local or laptop terminal."""
    print("================================================================================")
    print(f" 📺 LIVE kOS CONSOLE STREAM ({TARGET_HOST}) — Press Ctrl+C to return to prompt")
    print("================================================================================")
    content = read_kos_log()
    pos = len(content)
    if content:
        for line in content.splitlines()[-initial_lines:]:
            print(f"  {line.rstrip()}")

    last_stat_time = 0.0
    try:
        while True:
            content = read_kos_log()
            cur_len = len(content)
            if cur_len < pos:
                pos = 0
            if cur_len > pos:
                new_chunk = content[pos:]
                for line in new_chunk.splitlines():
                    print(f"  {line.rstrip()}")
                pos = cur_len
            now = time.time()
            if now - last_stat_time >= 5.0:
                t_data = get_live_telemetry()
                if t_data and (t_data.get("met", t_data.get("mtime", 0)) or 0) > 0:
                    print(f"  \033[36m{format_status_bar(t_data)}\033[0m")
                last_stat_time = now
            time.sleep(0.4)
    except KeyboardInterrupt:
        print("\n[Stopped live stream — spacecraft continues running autonomously]")


def send_kos_command(raw_cmd, wait_ack=True, auto_tail=False):
    cmd = raw_cmd.strip()
    if not cmd:
        return

    # Dynamic UT override during Pad Hold
    if cmd.lower().startswith("setut "):
        parts = cmd.split()
        new_ut = float(parts[1])
        write_kos_file("override_ut.txt", f"GLOBAL NEW_TARGET_LAUNCH_UT IS {new_ut:.1f}.\n")
        print(f"✅ Sent live launch window override to 0:/override_ut.txt -> UT {new_ut:.1f} s!")
        return

    # Built-in shortcuts
    if cmd.lower() in ("go18", "launch18", "csa18", "run csa18", "run csa18.", "run go18."):
        cmd = 'RUNPATH("0:/csa/universal_guided_ascent.ks", 600.0, 0, 120.0, "CoroltSat-1F", "CSA-18", "CoroltSat-1H").'
    elif cmd.lower().startswith("go "):
        parts = cmd.split()
        ut_val = float(parts[1]) if len(parts) > 1 else 0
        slot_val = float(parts[2]) if len(parts) > 2 else 120.0
        m_code = parts[3].upper() if len(parts) > 3 else "CSA-19"
        p_name = parts[4] if len(parts) > 4 else "CoroltSat-1I"
        ref_sat = parts[5] if len(parts) > 5 else "CoroltSat-1F"
        alt_km = float(parts[6]) if len(parts) > 6 else 600.0
        cmd = f'RUNPATH("0:/csa/universal_guided_ascent.ks", {alt_km:.1f}, {ut_val:.1f}, {slot_val:.1f}, "{ref_sat}", "{m_code}", "{p_name}").'
    elif cmd.lower().startswith("phase "):
        parts = cmd.split()
        slot_val = float(parts[1]) if len(parts) > 1 else 120.0
        orbits_val = int(parts[2]) if len(parts) > 2 else 3
        ref_sat = parts[3] if len(parts) > 3 else "CoroltSat-1F"
        cmd = f'RUNPATH("0:/csa/constellation_phasing.ks", {slot_val:.1f}, {orbits_val}, "{ref_sat}").'
    elif cmd.upper() == "EXIT_REMOTE":
        cmd = "SET STOP_REMOTE_BRIDGE TO TRUE."
    elif not cmd.endswith(".") and not cmd.endswith("}"):
        cmd += "."

    ack_before = read_kos_ack()
    ack_start_len = len(ack_before)

    file_content = "// Auto-generated by CSA Remote Terminal Bridge\n" + cmd + "\n"
    if not write_kos_file("remote_cmd.ks", file_content):
        return

    print(f"📡 Sent to kOS (0:/remote_cmd.ks on {TARGET_HOST}): {cmd}")

    if not wait_ack:
        return

    print("⏳ Waiting for vessel kOS pickup (ensure `run remote.` is active in KSP)...")
    t0 = time.time()
    started = False
    while time.time() - t0 < 15.0:
        ack_now = read_kos_ack()
        if len(ack_now) > ack_start_len:
            new_lines = ack_now[ack_start_len:].strip().splitlines()
            ack_start_len = len(ack_now)
            for line in new_lines:
                if line.startswith("START|"):
                    started = True
                    print(f"✅ Vessel kOS ACK: Command started on spacecraft ({line})")
                elif line.startswith("DONE|"):
                    print(f"🏁 Vessel kOS DONE: {line}")
                    return
        if started:
            break
        time.sleep(0.3)

    if started:
        print("🚀 Long-running kOS program is now executing on the spacecraft!")
        if auto_tail:
            tail_live_log(initial_lines=10)
    else:
        print("⚠️ Command queued in 0:/remote_cmd.ks (will execute as soon as `run remote.` is running and vessel has CommNet link).")


def interactive_loop():
    print("================================================================================")
    print(f"       COROLT SPACE AGENCY - REMOTE kOS TERMINAL BRIDGE v3.0 ({TARGET_HOST})     ")
    print("       (Live Console Mirroring + Local/LAN HTTP Bridge)                         ")
    print("================================================================================")
    print('1. In KSP kOS window (once), type:  RUNPATH("0:/csa/remote.ks").')
    print("2. Quick commands:")
    print("   • go <UT> <SLOT>       -> Launch mission at exact UT & slot (e.g. `go 4292554.6 60`)")
    print("   • setut <NEW_UT>       -> Change launch window UT live during Pad HOLD!")
    print("   • tail / log           -> Watch live kOS terminal output in real time!")
    print("   • phase <SLOT> [ORBS]  -> Run constellation_phasing.ks (e.g. `phase 60 3`)")
    print("   • status / quit")
    print("--------------------------------------------------------------------------------")

    while True:
        t_data = get_live_telemetry()
        print(format_status_bar(t_data))
        try:
            user_in = input("kOS-LAN> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting CSA Remote Terminal.")
            break

        if not user_in:
            continue
        if user_in.lower() in ("quit", "exit", "q"):
            break
        if user_in.lower() in ("status", "stat", "s"):
            continue
        if user_in.lower() in ("tail", "log", "watch"):
            tail_live_log()
            continue

        is_long = user_in.lower().startswith("go") or user_in.lower().startswith("phase") or "RUNPATH" in user_in.upper()
        send_kos_command(user_in, wait_ack=True, auto_tail=is_long)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CSA Crash-Proof Remote kOS Terminal v3.0 (Local & LAN)")
    parser.add_argument("--host", type=str, default=None, help="KSP host IP on LAN (e.g. 192.168.1.50)")
    parser.add_argument("-c", "--command", type=str, default=None, help="Send a single kOS command or shortcut and stream live output")
    parser.add_argument("-t", "--tail", action="store_true", help="Stream live kOS console output (0:/kos_live.log) in real time")
    args = parser.parse_args()

    if args.host:
        TARGET_HOST = args.host
    elif TARGET_HOST in ("127.0.0.1", "localhost") and not os.path.isdir(KOS_SCRIPT_ROOT):
        TARGET_HOST = "192.168.1.50"

    if args.tail:
        tail_live_log()
    elif args.command:
        send_kos_command(args.command, wait_ack=True, auto_tail=True)
    else:
        interactive_loop()
