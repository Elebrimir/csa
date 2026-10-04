"""
Corolt Space Agency (CSA) - Base Mission Telemetry Plotter
Abstract Base Class defining the pipeline for flight data analysis,
SVG telemetry curve rendering, and official summary reporting.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
import csv
import math
import os

@dataclass
class PlotMarker:
    time: float
    altitude: float
    label: str
    color: str = "#38bdf8"
    anchor: str = "middle"
    dx: float = 0.0
    dy: float = -12.0
    show_circle: bool = True
    circle_color: Optional[str] = None

class BaseMissionPlotter(ABC):
    def __init__(
        self,
        mission_id: str,
        csv_path: Optional[str] = None,
        svg_path: Optional[str] = None,
        summary_path: Optional[str] = None,
        alt_ceil: Optional[float] = None,
        vel_ceil: Optional[float] = None,
        width: int = 880,
        height: int = 420
    ):
        self.mission_id = mission_id.upper()
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        self.csv_path = csv_path or os.path.join(base_dir, "missions", f"{self.mission_id}_telemetry.csv")
        self.svg_path = svg_path or os.path.join(base_dir, "assets", f"{self.mission_id.lower()}_telemetry_plot.svg")
        self.summary_path = summary_path or os.path.join(base_dir, "missions", f"{self.mission_id}_summary.md")
        
        self.alt_ceil = alt_ceil
        self.vel_ceil = vel_ceil
        self.w = width
        self.h = height
        
        self.raw_rows = []
        self.valid_rows = []
        self.times = []
        self.alts = []
        self.vels = []
        self.dyn_press = []
        self.g_forces = []
        
        # Computed statistics
        self.max_alt = 0.0
        self.max_alt_time = 0.0
        self.max_vel = 0.0
        self.max_vel_time = 0.0
        self.max_q = 0.0
        self.max_g = 0.0
        self.time_in_space = 0.0
        self.landing_time = 0.0
        self.landing_alt = 0.0
        self.landing_vel = 0.0

    @abstractmethod
    def get_vehicle_name(self) -> str:
        """Returns the specific launch vehicle configuration (e.g. Corolt-IIIb)."""
        pass

    @abstractmethod
    def get_vehicle_family(self) -> str:
        """Returns the rocket family (e.g. Corolt-I, Corolt-II, Corolt-III)."""
        pass

    @abstractmethod
    def get_mission_objective(self) -> str:
        """Brief flight objective."""
        pass

    @abstractmethod
    def get_mission_outcome(self) -> str:
        """Executive outcome description."""
        pass

    def get_annotated_markers(self) -> List[PlotMarker]:
        """Returns list of points of interest to annotate on the SVG canvas."""
        markers = []
        # Standard Apogee Marker
        unit_str = f"{self.max_alt/1000:.1f} km" if self.max_alt >= 10000 else f"{self.max_alt:,.0f} m"
        markers.append(PlotMarker(
            time=self.max_alt_time,
            altitude=self.max_alt,
            label=f"Apogee: {unit_str} (T+{self.max_alt_time:.0f}s)",
            color="#38bdf8",
            anchor="middle",
            dy=-12.0
        ))
        return markers

    def load_data(self) -> None:
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Telemetry CSV not found: {self.csv_path}")

        with open(self.csv_path, mode="r", encoding="utf-8") as f:
            self.raw_rows = list(csv.DictReader(f))

    def filter_data(self) -> None:
        """Default filter trims pre-launch pad stillness and post-landing data."""
        self.valid_rows = []
        for r in self.raw_rows:
            try:
                met = float(r.get("MET", 0.0))
                alt = float(r.get("altitude", 0.0))
                vel = float(r.get("surface_vel", 0.0))
                self.valid_rows.append(r)
                # Termination condition if vehicle comes to rest after initial climb
                if alt <= 5.0 and met > 300:
                    break
            except (ValueError, TypeError):
                continue

        if not self.valid_rows:
            self.valid_rows = self.raw_rows

    def compute_statistics(self) -> None:
        self.times = [float(r.get("MET", 0.0)) for r in self.valid_rows]
        self.alts = [float(r.get("altitude", 0.0)) for r in self.valid_rows]
        self.vels = [float(r.get("surface_vel", 0.0)) for r in self.valid_rows]
        self.dyn_press = [float(r.get("dynamic_pressure", 0.0)) for r in self.valid_rows]
        self.g_forces = [float(r.get("g_force", 0.0)) for r in self.valid_rows]

        self.max_alt = max(self.alts) if self.alts else 0.0
        max_alt_idx = self.alts.index(self.max_alt) if self.alts else 0
        self.max_alt_time = self.times[max_alt_idx] if self.times else 0.0

        self.max_vel = max(self.vels) if self.vels else 0.0
        max_vel_idx = self.vels.index(self.max_vel) if self.vels else 0
        self.max_vel_time = self.times[max_vel_idx] if self.times else 0.0

        self.max_q = max(self.dyn_press) if self.dyn_press else 0.0
        self.max_g = max(self.g_forces) if self.g_forces else 0.0

        self.landing_time = self.times[-1] if self.times else 0.0
        self.landing_alt = self.alts[-1] if self.alts else 0.0
        self.landing_vel = self.vels[-1] if self.vels else 0.0

        # Space duration (> 70,000 m)
        space_times = [t for t, a in zip(self.times, self.alts) if a >= 70000.0]
        self.time_in_space = (space_times[-1] - space_times[0]) if len(space_times) > 1 else 0.0

        # Auto-compute ceilings if not explicitly provided
        if self.alt_ceil is None:
            if self.max_alt > 200000:
                self.alt_ceil = 260000.0
            elif self.max_alt > 100000:
                self.alt_ceil = 160000.0
            elif self.max_alt > 20000:
                self.alt_ceil = 26000.0
            elif self.max_alt > 10000:
                self.alt_ceil = 16000.0
            elif self.max_alt > 5000:
                self.alt_ceil = 7000.0
            else:
                self.alt_ceil = 4500.0

        if self.vel_ceil is None:
            if self.max_vel > 1500:
                self.vel_ceil = 1800.0
            elif self.max_vel > 1000:
                self.vel_ceil = 1600.0
            elif self.max_vel > 350:
                self.vel_ceil = 450.0
            elif self.max_vel > 200:
                self.vel_ceil = 300.0
            else:
                self.vel_ceil = 200.0

    def generate_svg(self) -> str:
        w = self.w
        h = self.h
        pad_l = 80
        pad_r = 80
        pad_t = 50
        pad_b = 60

        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        max_t = self.times[-1] if (self.times and self.times[-1] > 0) else 1.0
        alt_ceil = self.alt_ceil
        vel_ceil = self.vel_ceil

        # Subsample points for lightweight, clean SVG rendering
        step = max(1, len(self.valid_rows) // 350)
        sub_rows = self.valid_rows[::step]
        if self.valid_rows and self.valid_rows[-1] not in sub_rows:
            sub_rows.append(self.valid_rows[-1])

        pts_alt = []
        pts_vel = []
        for r in sub_rows:
            t = float(r.get("MET", 0.0))
            a = float(r.get("altitude", 0.0))
            v = float(r.get("surface_vel", 0.0))
            x = pad_l + (t / max_t) * plot_w
            y_alt = pad_t + plot_h - (a / alt_ceil) * plot_h
            y_vel = pad_t + plot_h - (v / vel_ceil) * plot_h
            pts_alt.append(f"{x:.1f},{y_alt:.1f}")
            pts_vel.append(f"{x:.1f},{y_vel:.1f}")

        str_alt = " ".join(pts_alt)
        str_vel = " ".join(pts_vel)

        # Horizontal Grid (Altitudes on left, Velocities on right)
        grid_lines = []
        for i in range(6):
            y = pad_t + (i / 5.0) * plot_h
            val_a = (1.0 - i / 5.0) * alt_ceil
            val_v = (1.0 - i / 5.0) * vel_ceil
            a_label = f"{val_a/1000:.0f} km" if alt_ceil >= 10000 else f"{val_a:.0f} m"
            grid_lines.append(f'<line x1="{pad_l}" y1="{y:.1f}" x2="{w - pad_r}" y2="{y:.1f}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
            grid_lines.append(f'<text x="{pad_l - 10}" y="{y + 4:.1f}" font-size="11" fill="#38bdf8" text-anchor="end" font-family="monospace">{a_label}</text>')
            grid_lines.append(f'<text x="{w - pad_r + 10}" y="{y + 4:.1f}" font-size="11" fill="#f43f5e" text-anchor="start" font-family="monospace">{val_v:.0f} m/s</text>')

        # Vertical Grid (Time intervals)
        for i in range(7):
            x = pad_l + (i / 6.0) * plot_w
            val_t = (i / 6.0) * max_t
            grid_lines.append(f'<line x1="{x:.1f}" y1="{pad_t}" x2="{x:.1f}" y2="{h - pad_b}" stroke="#1e293b" stroke-dasharray="3,3" stroke-width="1"/>')
            grid_lines.append(f'<text x="{x:.1f}" y="{h - pad_b + 20}" font-size="11" fill="#94a3b8" text-anchor="middle" font-family="monospace">T+{val_t:.0f}s</text>')

        grid_svg = "\n    ".join(grid_lines)

        # Karman line if altitude ceiling reaches space
        karman_svg = ""
        if alt_ceil >= 70000.0:
            y_70k = pad_t + plot_h - (70000.0 / alt_ceil) * plot_h
            karman_svg = f"""
  <!-- Space boundary 70km -->
  <line x1="{pad_l}" y1="{y_70k:.1f}" x2="{w - pad_r}" y2="{y_70k:.1f}" stroke="#a855f7" stroke-dasharray="6,4" stroke-width="1.5"/>
  <text x="{w - pad_r - 10}" y="{y_70k - 6:.1f}" font-size="11" fill="#a855f7" font-weight="bold" text-anchor="end">Space Boundary (Kármán 70 km)</text>
"""

        # Custom Annotated Markers
        markers_svg = []
        for m in self.get_annotated_markers():
            mx = pad_l + (m.time / max_t) * plot_w
            my = pad_t + plot_h - (m.altitude / alt_ceil) * plot_h
            if m.show_circle:
                c_col = m.circle_color or m.color
                markers_svg.append(f'<circle cx="{mx:.1f}" cy="{my:.1f}" r="4.5" fill="{c_col}" stroke="#ffffff" stroke-width="1.5"/>')
            markers_svg.append(f'<text x="{mx + m.dx:.1f}" y="{my + m.dy:.1f}" font-size="11" font-weight="bold" fill="{m.color}" text-anchor="{m.anchor}">{m.label}</text>')

        annot_svg = "\n  ".join(markers_svg)

        title = f"COROLT SPACE AGENCY  |  FLIGHT TELEMETRY: MISSION {self.mission_id}"
        subtitle = f"{self.get_vehicle_name()} ({self.get_vehicle_family()}) • {self.get_mission_outcome()}"

        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="auto" style="background:#0b0f19; border-radius: 8px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
  <rect width="{w}" height="{h}" fill="#0b0f19" rx="8"/>
  
  <!-- Title & Subtitle -->
  <text x="{w/2}" y="26" font-size="14" font-weight="bold" fill="#f8fafc" text-anchor="middle">{title}</text>
  <text x="{w/2}" y="42" font-size="11" fill="#64748b" text-anchor="middle">{subtitle}</text>

  <!-- Grid & Ticks -->
  {grid_svg}
  {karman_svg}
  <!-- Axes Frame -->
  <line x1="{pad_l}" y1="{pad_t}" x2="{pad_l}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>
  <line x1="{w - pad_r}" y1="{pad_t}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>
  <line x1="{pad_l}" y1="{h - pad_b}" x2="{w - pad_r}" y2="{h - pad_b}" stroke="#475569" stroke-width="1.5"/>

  <!-- Telemetry Curves -->
  <polyline fill="none" stroke="#f43f5e" stroke-width="2" stroke-linecap="round" points="{str_vel}"/>
  <polyline fill="none" stroke="#38bdf8" stroke-width="2.5" stroke-linecap="round" points="{str_alt}"/>

  <!-- Annotated Event Markers -->
  {annot_svg}

  <!-- Axis Titles & Legends -->
  <text x="{w / 2}" y="{h - 15}" font-size="12" fill="#94a3b8" text-anchor="middle">Mission Elapsed Time (MET) in seconds</text>
  <text transform="rotate(-90)" x="{- (pad_t + plot_h/2)}" y="24" font-size="11" fill="#38bdf8" text-anchor="middle">Altitude</text>
  <text transform="rotate(90)" x="{pad_t + plot_h/2}" y="{-w + 24}" font-size="11" fill="#f43f5e" text-anchor="middle">Velocity (m/s)</text>

  <!-- Legend Box -->
  <g transform="translate({pad_l}, {h - 20})">
    <line x1="0" y1="0" x2="20" y2="0" stroke="#38bdf8" stroke-width="2.5"/>
    <text x="25" y="4" font-size="11" fill="#94a3b8">Altitude</text>

    <line x1="100" y1="0" x2="120" y2="0" stroke="#f43f5e" stroke-width="2"/>
    <text x="125" y="4" font-size="11" fill="#94a3b8">Surface Velocity (m/s)</text>
  </g>
</svg>"""
        return svg

    def generate_summary_markdown(self) -> str:
        """Produces official summary document with standard formatting."""
        alt_str = f"{self.max_alt:,.1f} m ({self.max_alt/1000:.2f} km)" if self.max_alt >= 10000 else f"{self.max_alt:,.1f} m"
        lines = [
            f"# Telemetry Summary of Mission {self.mission_id}",
            "",
            f"- **Vehicle**: {self.get_vehicle_name()}",
            f"- **Family**: {self.get_vehicle_family()}",
            f"- **Objective**: {self.get_mission_objective()}",
            f"- **Outcome**: {self.get_mission_outcome()}",
            "",
            "## Critical Recorded Parameters",
            f"- **Maximum Altitude (Apoapsis)**: {alt_str} at T+{self.max_alt_time:.1f}s",
            f"- **Maximum Surface Speed**: {self.max_vel:,.1f} m/s ({self.max_vel*3.6:,.1f} km/h) at T+{self.max_vel_time:.1f}s",
            f"- **Maximum Dynamic Pressure (Max Q)**: {self.max_q:,.1f} Pa ({self.max_q/1000:.2f} kPa)",
            f"- **Maximum Acceleration**: {self.max_g:.2f} G",
        ]
        if self.time_in_space > 0:
            lines.append(f"- **Time in Outer Space (>70 km)**: {self.time_in_space:.1f} seconds ({self.time_in_space/60:.1f} minutes)")
        lines.append(f"- **Total Flight Time**: {self.landing_time:.1f} seconds ({self.landing_time/60:.2f} minutes)")
        lines.append(f"- **Terminal Velocity**: {self.landing_vel:.2f} m/s at elevation {self.landing_alt:.1f} m")
        lines.append("")
        return "\n".join(lines)

    def run(self) -> None:
        self.load_data()
        self.filter_data()
        self.compute_statistics()
        
        svg_content = self.generate_svg()
        os.makedirs(os.path.dirname(self.svg_path), exist_ok=True)
        with open(self.svg_path, "w", encoding="utf-8") as f:
            f.write(svg_content)
        print(f"[✓] SVG plot generated: {self.svg_path}")

        summary_md = self.generate_summary_markdown()
        os.makedirs(os.path.dirname(self.summary_path), exist_ok=True)
        with open(self.summary_path, "w", encoding="utf-8") as f:
            f.write(summary_md)
        print(f"[✓] Summary saved: {self.summary_path}")
