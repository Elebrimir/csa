#!/usr/bin/env python3
"""
Corolt Space Agency (CSA) - Unified Mission Telemetry Plotting & Reporting Tool
Generates high-resolution SVG telemetry plots and Markdown summaries using
the object-oriented rocket family architecture.

Usage:
    python3 tools/plot_mission.py CSA-07
    python3 tools/plot_mission.py --all
    python3 tools/plot_mission.py --family corolt-3
    python3 tools/plot_mission.py --list
"""

import sys
import os
import argparse

# Add repo root to Python path
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.plotting.rocket_families import MISSION_REGISTRY, get_plotter_for_mission

def list_missions():
    print("\n================================================================================")
    print("       COROLT SPACE AGENCY (CSA) - REGISTERED MISSION FLEET                     ")
    print("================================================================================")
    print(f"{'Mission':<10} | {'Family':<18} | {'Vehicle':<35} | {'CSV Available'}")
    print("-" * 80)
    for code, plotter_cls in MISSION_REGISTRY.items():
        try:
            plotter = plotter_cls()
            exists = "✓ Yes" if os.path.exists(plotter.csv_path) else "✗ Missing"
            print(f"{code:<10} | {plotter.get_vehicle_family():<18} | {plotter.get_vehicle_name():<35} | {exists}")
        except Exception as e:
            print(f"{code:<10} | Error instantiating: {e}")
    print("-" * 80 + "\n")

def run_mission(code):
    try:
        plotter = get_plotter_for_mission(code)
        print(f"\n🚀 Processing Mission: {plotter.mission_id} [{plotter.get_vehicle_family()}]")
        print(f"• Vehicle: {plotter.get_vehicle_name()}")
        plotter.run()
        # For orbital missions (CSA-09 onwards), also generate the 4 multi-charts & KAA map
        try:
            num_part = int("".join(ch for ch in plotter.mission_id if ch.isdigit()))
            if num_part >= 9:
                from tools.generate_mission_assets import (
                    analyze_mission_telemetry,
                    get_mission_metadata,
                    generate_flight_deck_dashboard,
                    generate_dynamic_pressure_plot,
                    generate_attitude_steering_plot,
                    generate_kaa_clearance_map,
                )
                slug = plotter.mission_id.lower()
                assets_dir = os.path.join(REPO_ROOT, "assets")
                meta = get_mission_metadata(plotter.mission_id)
                data, events = analyze_mission_telemetry(plotter.mission_id)
                generate_flight_deck_dashboard(data, events, meta, os.path.join(assets_dir, f"{slug}_advanced_dashboard.svg"))
                generate_dynamic_pressure_plot(data, events, meta, os.path.join(assets_dir, f"{slug}_dynamic_pressure_plot.svg"))
                generate_attitude_steering_plot(data, events, meta, os.path.join(assets_dir, f"{slug}_attitude_steering_plot.svg"))
                generate_kaa_clearance_map(events, meta, os.path.join(assets_dir, f"{slug}_kaa_hazard_map.svg"))
        except Exception as sub_e:
            print(f"[!] Note: Extended orbital assets skipped for {code}: {sub_e}")
        return True
    except FileNotFoundError as e:
        print(f"[!] Warning for {code}: {e}")
        return False
    except Exception as e:
        print(f"[✗] Error processing {code}: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Corolt Space Agency Mission Plotting & Telemetry Reporting Suite")
    parser.add_argument("mission", nargs="?", default=None, help="Mission code (e.g. CSA-01, CSA-16, CSA-17)")
    parser.add_argument("--all", action="store_true", help="Generate SVG plots and summaries for all registered missions")
    parser.add_argument("--family", choices=["corolt-1", "corolt-2", "corolt-3", "corolt-4"], help="Process only a specific rocket family")
    parser.add_argument("--list", action="store_true", help="List all registered missions and rocket families")

    args = parser.parse_args()

    if args.list:
        list_missions()
        return

    if args.all:
        print(f"\n🌌 Regenerating Telemetry Plots and Summaries for ALL registered CSA missions...")
        success = 0
        total = len(MISSION_REGISTRY)
        for code in MISSION_REGISTRY.keys():
            if run_mission(code):
                success += 1
        print(f"\n[✓] Completed: {success}/{total} missions plotted successfully.\n")
        return

    if args.family:
        family_keyword = args.family.replace("-", " ").title()
        print(f"\n🚀 Processing missions belonging to family: {family_keyword}...")
        for code, plotter_cls in MISSION_REGISTRY.items():
            plotter = plotter_cls()
            if family_keyword.lower() in plotter.get_vehicle_family().lower():
                run_mission(code)
        return

    if args.mission:
        run_mission(args.mission)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

