"""
Corolt Space Agency (CSA) - Rocket Families & Mission Plotters
Organizes mission telemetry visualization by vehicle architectures:
- Corolt-I Family (Atmospheric Suborbital Sounding)
- Corolt-II Family (Multistage & Radial Booster Rockets)
- Corolt-III Family (Space Suborbital & Guided Heavy Trans-Atmospheric)
"""

from typing import List, Dict, Type
import os
from .base_plotter import BaseMissionPlotter, PlotMarker

# ==============================================================================
# FAMÍLIA COROLT-I (Atmospheric Low-Altitude Sounding)
# ==============================================================================
class CoroltIFamilyPlotter(BaseMissionPlotter):
    def get_vehicle_family(self) -> str:
        return "Corolt-I Family"

class CSA01Plotter(CoroltIFamilyPlotter):
    def __init__(self, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_file = os.path.join(base_dir, "missions", "Corolt-I_telemetry.csv")
        super().__init__(mission_id="CSA-01", csv_path=csv_file, alt_ceil=7000.0, vel_ceil=300.0, **kwargs)

    def get_vehicle_name(self) -> str:
        return "Corolt-I (Baseline)"

    def get_mission_objective(self) -> str:
        return "First agency sounding rocket launch and ascent telemetry test"

    def get_mission_outcome(self) -> str:
        return "🟢 Historical Success | Apogee 6.4 km | Parachute landing"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        # Add parachute descent phase note
        if self.times:
            markers.append(PlotMarker(
                time=self.times[-1] * 0.85,
                altitude=self.max_alt * 0.5,
                label="Parachute Phase: -12.8 m/s",
                color="#94a3b8",
                anchor="end",
                show_circle=False
            ))
        return markers

class CSA02Plotter(CoroltIFamilyPlotter):
    def __init__(self, **kwargs):
        super().__init__(mission_id="CSA-02", alt_ceil=4500.0, vel_ceil=200.0, **kwargs)

    def get_vehicle_name(self) -> str:
        return "Corolt-Ib (Scientific Variant)"

    def get_mission_objective(self) -> str:
        return "Scientific sensor bay flight (2HOT & PresMat) and controlled touchdown"

    def get_mission_outcome(self) -> str:
        return "🟢 Complete Flight & Touchdown (4.1 km) | 100% Recovery"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        # Max velocity burnout marker
        markers.append(PlotMarker(
            time=self.max_vel_time,
            altitude=self.alts[self.vels.index(self.max_vel)],
            label=f"Vmax: {self.max_vel:.0f} m/s (T+{self.max_vel_time:.0f}s)",
            color="#f43f5e",
            anchor="start",
            dx=10,
            dy=-6
        ))
        # Parachute deployment marker (~2000m on descent)
        for i in range(self.alts.index(self.max_alt), len(self.alts)):
            if self.alts[i] < 2000.0:
                markers.append(PlotMarker(
                    time=self.times[i],
                    altitude=self.alts[i],
                    label=f"Parachutes ({self.alts[i]:.0f}m)",
                    color="#10b981",
                    anchor="start",
                    dx=8,
                    dy=16
                ))
                break
        return markers

# ==============================================================================
# FAMÍLIA COROLT-II (Multistage & Radial Boosters)
# ==============================================================================
class CoroltIIFamilyPlotter(BaseMissionPlotter):
    def get_vehicle_family(self) -> str:
        return "Corolt-II Family"

class CSA03Plotter(CoroltIIFamilyPlotter):
    def __init__(self, **kwargs):
        super().__init__(mission_id="CSA-03", alt_ceil=26000.0, vel_ceil=450.0, **kwargs)

    def get_vehicle_name(self) -> str:
        return "Corolt-II (Tandem 2-Stage)"

    def get_mission_objective(self) -> str:
        return "First multistage stratospheric ascent and high-altitude separation"

    def get_mission_outcome(self) -> str:
        return "🟢 Total Success | Apogee 24.0 km | High Stratospheric Data"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        # Stage 1 separation at ~10.6 km
        markers.append(PlotMarker(
            time=58.0,
            altitude=10600.0,
            label="Stage 1 Sep (10.6 km)",
            color="#fbbf24",
            anchor="end",
            dx=-8,
            dy=-8
        ))
        # Vmax marker
        markers.append(PlotMarker(
            time=self.max_vel_time,
            altitude=self.alts[self.vels.index(self.max_vel)],
            label=f"Vmax: {self.max_vel:.0f} m/s",
            color="#f43f5e",
            anchor="end",
            dx=-8,
            dy=-10
        ))
        # Parachutes
        markers.append(PlotMarker(
            time=228.0,
            altitude=2528.0,
            label="Parachutes (2,528m)",
            color="#10b981",
            anchor="start",
            dx=8,
            dy=14
        ))
        return markers

class CSA04Plotter(CoroltIIFamilyPlotter):
    def __init__(self, **kwargs):
        super().__init__(mission_id="CSA-04", alt_ceil=1000.0, vel_ceil=250.0, **kwargs)

    def get_vehicle_name(self) -> str:
        return "Corolt-IIb (Radial Quad-Booster)"

    def get_mission_objective(self) -> str:
        return "Radial booster configuration maiden flight and maximum aerodynamic test"

    def get_mission_outcome(self) -> str:
        return "🟡 Aerodynamic Loss of Control at Max Q (460m) | Capsule Recovered Intact"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        markers.append(PlotMarker(
            time=12.0,
            altitude=669.7,
            label="Loss of Control / Max Q (20.3 kPa)",
            color="#fbbf24",
            anchor="middle",
            dy=-14
        ))
        markers.append(PlotMarker(
            time=35.0,
            altitude=150.0,
            label="Emergency Chutes (13.6 G)",
            color="#22c55e",
            anchor="start",
            dx=10,
            dy=0
        ))
        return markers

class CSA04bPlotter(CoroltIIFamilyPlotter):
    def __init__(self, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_file = os.path.join(base_dir, "missions", "CSA-04b_telemetry.csv")
        sum_file = os.path.join(base_dir, "missions", "CSA-04b_summary.md")
        super().__init__(mission_id="CSA-04b", csv_path=csv_file, summary_path=sum_file, alt_ceil=16000.0, vel_ceil=350.0, **kwargs)

    def get_vehicle_name(self) -> str:
        return "Corolt-IIb (Aerodynamic Redesign)"

    def get_mission_objective(self) -> str:
        return "Centrifugal booster staging test and high-altitude stability"

    def get_mission_outcome(self) -> str:
        return "🟢 Total Success | Apogee 14.49 km | Controlled Radial Separation"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        markers.append(PlotMarker(
            time=175.0,
            altitude=1666.3,
            label="Parachute Deployment (19.4 G)",
            color="#10b981",
            anchor="start",
            dx=8,
            dy=14
        ))
        return markers

class CSA05Plotter(CoroltIIFamilyPlotter):
    def __init__(self, **kwargs):
        super().__init__(mission_id="CSA-05", alt_ceil=24000.0, vel_ceil=500.0, **kwargs)

    def get_vehicle_name(self) -> str:
        return "Corolt-IIb (Suborbital Multistage)"

    def get_mission_objective(self) -> str:
        return "Stratospheric payload sounding and parachute braking qualification"

    def get_mission_outcome(self) -> str:
        return "🟢 Total Success | Apogee 20.43 km | 100% Payload Recovery"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        markers.append(PlotMarker(
            time=self.max_vel_time,
            altitude=self.alts[self.vels.index(self.max_vel)],
            label=f"Vmax: {self.max_vel:.0f} m/s",
            color="#f43f5e",
            anchor="end",
            dx=-10,
            dy=-10
        ))
        return markers

# ==============================================================================
# FAMÍLIA COROLT-III (Outer Space Suborbital & Guided Flight)
# ==============================================================================
class CoroltIIIFamilyPlotter(BaseMissionPlotter):
    def get_vehicle_family(self) -> str:
        return "Corolt-III Family"

class CSA05bPlotter(CoroltIIIFamilyPlotter):
    def __init__(self, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_file = os.path.join(base_dir, "missions", "CSA-05b_telemetry.csv")
        sum_file = os.path.join(base_dir, "missions", "CSA-05b_summary.md")
        super().__init__(mission_id="CSA-05b", csv_path=csv_file, summary_path=sum_file, alt_ceil=260000.0, vel_ceil=1800.0, **kwargs)

    def filter_data(self) -> None:
        self.valid_rows = []
        for r in self.raw_rows:
            try:
                met = float(r.get("MET", 0.0))
                if met > 1012.0:
                    break
                self.valid_rows.append(r)
            except (ValueError, TypeError):
                continue
        if not self.valid_rows:
            self.valid_rows = self.raw_rows

    def get_vehicle_name(self) -> str:
        return "Corolt-III (Unit 02 - Tandem)"

    def get_mission_objective(self) -> str:
        return "Atmospheric / Suborbital space crossing and heavy payload capacity test"

    def get_mission_outcome(self) -> str:
        return "Space Propulsion Success (240 km) | Loss on Reentry due to Impact"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        markers.append(PlotMarker(
            time=self.landing_time,
            altitude=self.landing_alt,
            label=f"Ground Impact: {self.landing_vel:.0f} m/s",
            color="#ef4444",
            circle_color="#ef4444",
            anchor="end",
            dx=-10,
            dy=-15
        ))
        return markers

class CSA06Plotter(CoroltIIIFamilyPlotter):
    def __init__(self, **kwargs):
        super().__init__(mission_id="CSA-06", alt_ceil=260000.0, vel_ceil=1800.0, **kwargs)

    def filter_data(self) -> None:
        self.valid_rows = []
        for r in self.raw_rows:
            try:
                met = float(r.get("MET", 0.0))
                if met > 1705.0:
                    break
                self.valid_rows.append(r)
            except (ValueError, TypeError):
                continue
        if not self.valid_rows:
            self.valid_rows = self.raw_rows

    def get_vehicle_name(self) -> str:
        return "Corolt-III (Unit 03 - Guided kOS)"

    def get_mission_objective(self) -> str:
        return "High-altitude suborbital flight and full autonomous recovery"

    def get_mission_outcome(self) -> str:
        return "🟢 Total Success | Apogee 245.0 km | Soft Autonomous Recovery"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        markers.append(PlotMarker(
            time=self.landing_time,
            altitude=self.landing_alt,
            label=f"Soft Touchdown: T+{self.landing_time:.0f}s ({self.landing_time/60:.1f} min)",
            color="#22c55e",
            circle_color="#22c55e",
            anchor="end",
            dx=-10,
            dy=-15
        ))
        return markers

class CSA07Plotter(CoroltIIIFamilyPlotter):
    def __init__(self, **kwargs):
        super().__init__(mission_id="CSA-07", alt_ceil=160000.0, vel_ceil=1600.0, **kwargs)

    def filter_data(self) -> None:
        self.valid_rows = []
        for r in self.raw_rows:
            try:
                met = float(r.get("MET", 0.0))
                alt = float(r.get("altitude", 0.0))
                self.valid_rows.append(r)
                if alt <= 0.0 and met > 500:
                    break
            except (ValueError, TypeError):
                continue
        if not self.valid_rows:
            self.valid_rows = self.raw_rows

    def get_vehicle_name(self) -> str:
        return "Corolt-IIIb (Movable Control Surfaces)"

    def get_mission_objective(self) -> str:
        return "Aerodynamic actuation validation, eastward inclined trajectory and ocean recovery"

    def get_mission_outcome(self) -> str:
        return "🟢 Total Success | Apogee 138.6 km | Full Ocean Recovery"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        markers.append(PlotMarker(
            time=self.landing_time,
            altitude=self.landing_alt,
            label="Water Touchdown / Splashdown (0.1 m/s)",
            color="#22c55e",
            circle_color="#22c55e",
            anchor="end",
            dx=-10,
            dy=-15
        ))
        return markers

class CSA08Plotter(CoroltIIIFamilyPlotter):
    def __init__(self, **kwargs):
        super().__init__(mission_id="CSA-08", alt_ceil=200000.0, vel_ceil=1800.0, **kwargs)

    def filter_data(self) -> None:
        self.valid_rows = []
        for r in self.raw_rows:
            try:
                met = float(r.get("MET", 0.0))
                alt = float(r.get("altitude", 0.0))
                self.valid_rows.append(r)
                if alt <= 0.0 and met > 500:
                    break
            except (ValueError, TypeError):
                continue
        if not self.valid_rows:
            self.valid_rows = self.raw_rows

    def get_vehicle_name(self) -> str:
        return "Corolt-IIIb (Deep Space Inland Sounding)"

    def get_mission_objective(self) -> str:
        return "Inland ascent steering (Heading 315º), Van Allen boundary testing & autonomous science"

    def get_mission_outcome(self) -> str:
        return "🟡 Partial Success / Loss of Vessel | Apogee 179.4 km | Battery Depleted | Water Impact"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        markers.append(PlotMarker(
            time=113.6,
            altitude=70500.0,
            label="Battery Depletion (0 EC) - kOS Abort",
            color="#ef4444",
            circle_color="#ef4444",
            anchor="start",
            dx=10,
            dy=-15
        ))
        markers.append(PlotMarker(
            time=self.landing_time,
            altitude=self.landing_alt,
            label="Water Impact (Uncontrolled Descent)",
            color="#ef4444",
            circle_color="#ef4444",
            anchor="end",
            dx=-10,
            dy=-15
        ))
        return markers

class CSA09Plotter(CoroltIIIFamilyPlotter):
    def __init__(self, **kwargs):
        super().__init__(mission_id="CSA-09", alt_ceil=180000.0, vel_ceil=1600.0, **kwargs)

    def filter_data(self) -> None:
        self.valid_rows = []
        for r in self.raw_rows:
            try:
                met = float(r.get("MET", 0.0))
                alt = float(r.get("altitude", 0.0))
                self.valid_rows.append(r)
                if alt <= 0.0 and met > 1200:
                    break
            except (ValueError, TypeError):
                continue
        if not self.valid_rows:
            self.valid_rows = self.raw_rows

    def get_vehicle_name(self) -> str:
        return "Corolt-IIIb (Deep Space Sounding - Flight 2)"

    def get_mission_objective(self) -> str:
        return "Deep space apogee, power-managed science architecture & safe aerodynamic parachute recovery"

    def get_mission_outcome(self) -> str:
        return "🟢 Recovery Success (85.5% Value) | Apogee 162.6 km | Full Vessel & Payload Intact"

    def get_annotated_markers(self) -> List[PlotMarker]:
        markers = super().get_annotated_markers()
        markers.append(PlotMarker(
            time=923.9,
            altitude=162558.3,
            label="Apogee 162.6 km (Low Space)",
            color="#38bdf8",
            circle_color="#38bdf8",
            anchor="middle",
            dx=0,
            dy=-18
        ))
        markers.append(PlotMarker(
            time=self.landing_time,
            altitude=self.landing_alt,
            label="Safe Splashdown (85.5% Recov)",
            color="#22c55e",
            circle_color="#22c55e",
            anchor="end",
            dx=-10,
            dy=-15
        ))
        return markers

# ==============================================================================
# MISSION REGISTRY & FACTORY
# ==============================================================================
MISSION_REGISTRY: Dict[str, Type[BaseMissionPlotter]] = {
    "CSA-01": CSA01Plotter,
    "CSA-02": CSA02Plotter,
    "CSA-03": CSA03Plotter,
    "CSA-04": CSA04Plotter,
    "CSA-04B": CSA04bPlotter,
    "CSA-05": CSA05Plotter,
    "CSA-05B": CSA05bPlotter,
    "CSA-06": CSA06Plotter,
    "CSA-07": CSA07Plotter,
    "CSA-08": CSA08Plotter,
    "CSA-09": CSA09Plotter,
}

def get_plotter_for_mission(mission_code: str, **kwargs) -> BaseMissionPlotter:
    code = mission_code.upper().replace("_", "-")
    if code in MISSION_REGISTRY:
        return MISSION_REGISTRY[code](**kwargs)
    raise KeyError(f"Mission '{mission_code}' not found in CSA registry. Available: {list(MISSION_REGISTRY.keys())}")
