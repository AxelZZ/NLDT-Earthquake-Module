#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
NLDT Earthquake Module v5.6 – Japan Trench Focus (Two-Window Edition)
=====================================================================
Non-linear resonance analysis of the Japan Trench with USGS live data
Gold Phase LED, M112 grid (empty circles, size scales with resonance)

Window 1: Interactive (saturation curve, sliders, Axiom G, table)
Window 2: Map (Pacific Ring of Fire, coastlines, borders, USGS earthquakes)

© 2026 Axel Zill-Zheng | Homebase Xiamen NLDT LAB
All rights reserved. Part of the NLDT / RPT Framework.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as mgridspec
from matplotlib.widgets import Slider, Button
import datetime
import json
import csv
import requests

# Try to import cartopy for map outlines (fallback if not available)
try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    CARTOPY_AVAILABLE = True
except ImportError:
    CARTOPY_AVAILABLE = False
    print("⚠ cartopy not installed. Map will show plate boundaries only.")
    print("  Install with: pip install cartopy")

print("=== NLDT Earthquake Module v5.6 – Japan Trench Focus ===\n")
print("© 2026 Axel Zill-Zheng | Homebase Xiamen NLDT LAB\n")
print("Two-window mode: Interactive + Map | M112 grid: empty circles, size scales with resonance\n")

# =====================================================================
# FAULTS (9 Verwerfungen mit Taiwan Fokus)
# =====================================================================
FAULTS = {
    "Japan Trench": {
        "name": "Japan Trench",
        "slip_rate": 0.080,        # m/year (Simons et al. 2011)
        "coupling_ratio": 0.90,
        "locking_depth": 30.0,
        "last_quake": 2011,
        "mag": 9.0,
        "lam": 7.9,
        "color": "#ff4444",
        "lon": 143, "lat": 38,
        "line": [(142, 38), (144, 40), (146, 42)]
    },
    "San Andreas": {
        "name": "San Andreas Fault",
        "slip_rate": 0.022,
        "coupling_ratio": 0.75,
        "locking_depth": 15.0,
        "last_quake": 1906,
        "mag": 7.9,
        "lam": 5.8,
        "color": "#ff5555",
        "lon": -120, "lat": 36,
        "line": [(-122, 36), (-120, 37), (-118, 35)]
    },
    "Cascadia": {
        "name": "Cascadia Subduction",
        "slip_rate": 0.040,
        "coupling_ratio": 0.80,
        "locking_depth": 20.0,
        "last_quake": 1700,
        "mag": 9.0,
        "lam": 7.2,
        "color": "#ffaa00",
        "lon": -125, "lat": 47,
        "line": [(-124, 45), (-124, 47), (-123, 49)]
    },
    "Nankai": {
        "name": "Nankai Trough",
        "slip_rate": 0.035,
        "coupling_ratio": 0.85,
        "locking_depth": 25.0,
        "last_quake": 1946,
        "mag": 8.1,
        "lam": 6.5,
        "color": "#1f77b4",
        "lon": 136, "lat": 33,
        "line": [(135, 33), (136, 34), (137, 33)]
    },
    "Philippine": {
        "name": "Philippine Trench",
        "slip_rate": 0.060,
        "coupling_ratio": 0.65,
        "locking_depth": 20.0,
        "last_quake": 1976,
        "mag": 8.1,
        "lam": 7.1,
        "color": "#ff8800",
        "lon": 126, "lat": 10,
        "line": [(125, 8), (127, 10), (128, 12)]
    },
    "Taiwan Region": {
        "name": "Taiwan / Ryukyu Area",
        "slip_rate": 0.055,
        "coupling_ratio": 0.75,
        "locking_depth": 22.0,
        "last_quake": 1999,
        "mag": 7.6,
        "lam": 7.4,
        "color": "#ffff00",
        "lon": 121, "lat": 24,
        "line": [(119, 22), (121, 25), (123, 28)]
    },
    "Chile": {
        "name": "Chile Trench",
        "slip_rate": 0.065,
        "coupling_ratio": 0.88,
        "locking_depth": 35.0,
        "last_quake": 2010,
        "mag": 8.8,
        "lam": 7.8,
        "color": "#aa44ff",
        "lon": -72, "lat": -35,
        "line": [(-73, -35), (-72, -34), (-71, -33)]
    },
    "Sunda": {
        "name": "Sunda Megathrust",
        "slip_rate": 0.050,
        "coupling_ratio": 0.82,
        "locking_depth": 25.0,
        "last_quake": 2004,
        "mag": 9.1,
        "lam": 7.5,
        "color": "#ff0088",
        "lon": 95, "lat": 5,
        "line": [(95, -5), (100, -2), (105, 0)]
    },
    "Alpine": {
        "name": "Alpine Fault NZ",
        "slip_rate": 0.027,
        "coupling_ratio": 0.70,
        "locking_depth": 18.0,
        "last_quake": 1717,
        "mag": 8.0,
        "lam": 6.1,
        "color": "#00cc88",
        "lon": 171, "lat": -43,
        "line": [(168, -44), (170, -43), (172, -42)]
    }
}

N_FAULTS = len(FAULTS)
THRESHOLD_GOLD = 0.68
PHI_DEFAULT = 2.8  # Elevated stress for Japan Trench
LAM_DEFAULT = 7.9  # Japan Trench λ

# Coupling matrix (for Taiwan focus)
COUPLING = {
    ("Philippine", "Taiwan Region"): 0.32,
    ("Taiwan Region", "Philippine"): 0.28,
    ("Taiwan Region", "Nankai"): 0.18,
    ("Nankai", "Taiwan Region"): 0.15,
    ("Japan Trench", "Nankai"): 0.30,
    ("Nankai", "Japan Trench"): 0.35,
}

def get_coupling(f1, f2):
    return COUPLING.get((f1, f2), COUPLING.get((f2, f1), 0.0))

# Historical earthquakes (for map)
HISTORICAL_QUAKES = {
    "1906 San Francisco": (-122.5, 37.8, 7.9),
    "1700 Cascadia": (-124.0, 48.0, 9.0),
    "1946 Nankai": (136.0, 34.0, 8.1),
    "2011 Tohoku": (143.0, 38.0, 9.0),
    "2004 Sumatra": (95.0, 2.0, 9.1),
    "2010 Chile": (-72.0, -34.0, 8.8),
    "1999 Chi-Chi": (120.8, 23.8, 7.6),
}


# =====================================================================
# MODEL CLASS
# =====================================================================
class NLDTEarthquakeModel:
    def __init__(self):
        self.phi = PHI_DEFAULT
        self.lam = LAM_DEFAULT
        self.base_res = 0.0
        self.grid_state = np.zeros(112)
        self.resonance_state = 0.0

    def nldt_resonance(self, phi, lam):
        return np.tanh(lam * phi / 3.0)

    def axiom_g_transition(self, phi_current, lam):
        resonance_boost = np.tanh(lam * phi_current / 3.0)
        self.grid_state = self.grid_state + resonance_boost * (1 - self.grid_state)
        self.grid_state = np.clip(self.grid_state, 0.0, 1.0)
        self.resonance_state = np.mean(self.grid_state)
        return self.resonance_state

    def get_flip_velocity(self):
        if self.resonance_state >= THRESHOLD_GOLD:
            return float('inf')
        denom = 1.0 - self.resonance_state / THRESHOLD_GOLD
        return (self.resonance_state * self.lam / 0.1) * (1.0 / denom) if denom > 0 else float('inf')

    def get_risk_level(self, phi, lam):
        res = self.nldt_resonance(phi, lam)
        if res >= THRESHOLD_GOLD:
            return "CRITICAL (Gold Phase)"
        elif res >= 0.5:
            return "ELEVATED"
        else:
            return "LOW"

    def full_update(self):
        phi = self.phi
        lam = self.lam
        res = self.nldt_resonance(phi, lam)
        resonance = self.axiom_g_transition(phi, lam)
        flip_vel = self.get_flip_velocity()
        return phi, res, resonance, flip_vel


# =====================================================================
# LIVE USGS DATA
# =====================================================================
def fetch_usgs_recent_earthquakes(days=7, min_mag=4.5):
    """Fetch recent earthquakes from USGS"""
    start = (datetime.datetime.utcnow() - datetime.timedelta(days=days)).strftime('%Y-%m-%d')
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start}&minmagnitude={min_mag}&limit=50"
    try:
        r = requests.get(url, timeout=15)
        data = r.json()
        quakes = []
        for feat in data.get("features", []):
            p = feat["properties"]
            g = feat["geometry"]["coordinates"]
            quakes.append({
                "mag": p["mag"],
                "place": p.get("place", "?"),
                "time": datetime.datetime.utcfromtimestamp(p["time"]/1000),
                "lon": g[0],
                "lat": g[1]
            })
        return quakes
    except:
        return []


# =====================================================================
# MODEL INSTANCE
# =====================================================================
model = NLDTEarthquakeModel()

# =====================================================================
# WINDOW 1: INTERACTIVE (Saturation, Sliders, Axiom G, Table)
# =====================================================================
fig1 = plt.figure(figsize=(16, 12), facecolor='#0d1117')
fig1.suptitle(r'NLDT Earthquake Module v5.6 – Japan Trench Focus (Interactive)',
              fontsize=15, color='white', y=0.97)

# Gold Phase LED
ax_led = fig1.add_axes([0.42, 0.89, 0.16, 0.06])
ax_led.set_facecolor('#0a0e14')
ax_led.axis('off')
led_circle = ax_led.add_patch(plt.Circle((0.5, 0.5), 0.45, color='#4488ff'))
led_text = ax_led.text(0.5, 0.5, 'BLUE PHASE\nSafe', ha='center', va='center', 
                       fontsize=11, fontweight='bold', color='white')

# Saturation Curve
ax_sat = fig1.add_axes([0.08, 0.45, 0.40, 0.40])
ax_sat.set_facecolor('#0a0e14')
ax_sat.set_title('NLDT Resonance: Japan Trench', color='white', fontsize=11)
ax_sat.set_xlabel('Tectonic Stress Φ', color='white')
ax_sat.set_ylabel('Resonance S (Tipping Risk)', color='white')
ax_sat.grid(True, color='#1a2535', lw=0.5, ls='--')

phi_range = np.linspace(0, 5, 500)
sat_line, = ax_sat.plot(phi_range, np.tanh(LAM_DEFAULT * phi_range / 3.0), 
                         color='#ff4444', lw=3.0)
ax_sat.axhline(THRESHOLD_GOLD, color='gold', ls='--', lw=1.5, alpha=0.8, label='Gold Phase')
point, = ax_sat.plot([], [], 'o', color='#ffd700', markersize=14, label='Current Stress')
ax_sat.legend(fontsize=8, facecolor='#0d1117', labelcolor='white')

# Axiom G Panel
ax_axiom = fig1.add_axes([0.55, 0.60, 0.40, 0.25])
ax_axiom.set_facecolor('#0a0e1a')
ax_axiom.axis('off')
ax_axiom.set_title('Axiom G & PLAREK Status', color='#ffd700', fontsize=10)

# Flip Velocity Plot
ax_vel = fig1.add_axes([0.55, 0.45, 0.40, 0.12])
ax_vel.set_facecolor('#0a0e14')
ax_vel.set_title('Flip Velocity v_res (RPT)', color='white', fontsize=9)
vel_line, = ax_vel.plot([], [], color='#ff6688', lw=2)
vel_point, = ax_vel.plot([], [], 'o', color='#ff5555', markersize=8)
ax_vel.set_xlim(0, 5)
ax_vel.set_ylim(0, 6)
ax_vel.tick_params(colors='white')

# Table
ax_table = fig1.add_axes([0.08, 0.08, 0.87, 0.30])
ax_table.axis('off')

# Sliders (with short labels, positioned above)
ax_sl_phi = fig1.add_axes([0.08, 0.04, 0.35, 0.025])
ax_sl_lam = fig1.add_axes([0.55, 0.04, 0.35, 0.025])

slider_phi = Slider(ax_sl_phi, 'Stress Φ', 0.0, 5.0, valinit=PHI_DEFAULT, color='#ff4444')
slider_phi.label.set_position([0.5, 1.2])
slider_phi.label.set_horizontalalignment('center')
slider_phi.label.set_color('white')

slider_lam = Slider(ax_sl_lam, 'λ', 1.0, 15.0, valinit=LAM_DEFAULT, color='#ffd700')
slider_lam.label.set_position([0.5, 1.2])
slider_lam.label.set_horizontalalignment('center')
slider_lam.label.set_color('white')

# Buttons
def _btn(rect, label, bg='#21262d'):
    ax = fig1.add_axes(rect)
    b = Button(ax, label, color=bg, hovercolor='#30363d')
    b.label.set_color('white')
    return b

btn_reset = _btn([0.08, 0.01, 0.10, 0.025], 'Reset')
btn_json = _btn([0.20, 0.01, 0.10, 0.025], 'JSON Export')
btn_csv = _btn([0.32, 0.01, 0.10, 0.025], 'CSV Export')
btn_save = _btn([0.44, 0.01, 0.10, 0.025], 'PNG')


# =====================================================================
# WINDOW 2: MAP (Pacific Ring of Fire + Coastlines + USGS Earthquakes)
# =====================================================================
if CARTOPY_AVAILABLE:
    fig2 = plt.figure(figsize=(15, 10), facecolor='#0d1117')
    ax_map = fig2.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    ax_map.set_facecolor('#0a0e14')
    ax_map.set_global()
    ax_map.set_xlim(-180, 180)
    ax_map.set_ylim(-70, 70)

    # Add geographic features (coastlines, borders)
    ax_map.add_feature(cfeature.LAND, facecolor='#1a1a2e')
    ax_map.add_feature(cfeature.OCEAN, facecolor='#0a0e14')
    ax_map.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='#888888')
    ax_map.add_feature(cfeature.BORDERS, linewidth=0.3, edgecolor='#666666', alpha=0.5)
    ax_map.add_feature(cfeature.LAKES, facecolor='#0a0e14', edgecolor='#333333')
else:
    # Fallback without cartopy
    fig2 = plt.figure(figsize=(15, 10), facecolor='#0d1117')
    ax_map = fig2.add_subplot(1, 1, 1)
    ax_map.set_facecolor('#0a0e14')
    ax_map.set_xlim(-180, 180)
    ax_map.set_ylim(-70, 70)
    ax_map.set_title('Pacific Ring of Fire (coastlines unavailable – install cartopy)', color='white', fontsize=10)

fig2.suptitle('Pacific Ring of Fire – Plate Boundaries, Coastlines & Live Earthquakes',
              fontsize=14, color='white', y=0.97)
ax_map.grid(True, color='#1a2535', lw=0.5, ls='--')

# Draw plate boundaries
for name, f in FAULTS.items():
    lw = 4 if name == "Japan Trench" else 1.5
    alpha = 1.0 if name == "Japan Trench" else 0.6
    if "line" in f:
        lons = [p[0] for p in f["line"]]
        lats = [p[1] for p in f["line"]]
        ax_map.plot(lons, lats, color=f["color"], lw=lw, alpha=alpha)
    ax_map.scatter(f["lon"], f["lat"], c=f["color"], s=100 if name == "Japan Trench" else 50,
                   edgecolors='white', zorder=5)
    ax_map.text(f["lon"]+3, f["lat"]+4, name[:12], color='white', fontsize=7, alpha=0.8)

# Taiwan / Xiamen highlight (yellow line)
ax_map.plot([118, 122, 125], [22, 25, 28], color='#ffff00', lw=3.5, ls='--', alpha=0.9)
ax_map.text(121.5, 26.5, 'TAIWAN / XIAMEN', color='#ffff00', fontsize=11, weight='bold', ha='center')

# Japan Trench focus label
ax_map.text(145, 45, 'JAPAN TRENCH\nFOCUS', color='#ff4444', fontsize=12,
            weight='bold', ha='center', bbox=dict(facecolor='#0a0e14', edgecolor='#ff4444'))

# Historical earthquakes (stars)
for label, (lon, lat, mag) in HISTORICAL_QUAKES.items():
    ax_map.scatter(lon, lat, color='#ffd700', s=120, marker='*', zorder=7)
    ax_map.text(lon+2, lat+1, label, color='#ffd700', fontsize=7, alpha=0.9)

# USGS live earthquakes (size scales with magnitude)
quakes = fetch_usgs_recent_earthquakes()
for q in quakes:
    if abs(q["lon"]) < 180 and abs(q["lat"]) < 70:
        size = max(20, q["mag"] * 10)
        color = '#ff0000' if q["mag"] >= 6.0 else '#ffaa00' if q["mag"] >= 5.0 else '#ffff00'
        ax_map.scatter(q["lon"], q["lat"], color=color, s=size, alpha=0.8,
                       edgecolors='black', linewidth=0.5, zorder=6)

# Legend
ax_map.text(-170, -60, 'LEGEND:', color='white', fontsize=9, weight='bold')
ax_map.text(-170, -63, '★ Historical M7.6-9.1', color='#ffd700', fontsize=7)
ax_map.text(-170, -66, '● USGS live (size=mag)', color='#ffff00', fontsize=7)
ax_map.text(-170, -69, 'Red line: Japan Trench (focus)', color='#ff4444', fontsize=7)


# =====================================================================
# UPDATE FUNCTION (for Window 1)
# =====================================================================
def update(val=None):
    model.phi = slider_phi.val
    model.lam = slider_lam.val

    phi, res, resonance, flip_vel = model.full_update()

    # Gold Phase LED
    if res >= THRESHOLD_GOLD:
        led_circle.set_color('#ffd700')
        led_text.set_text('● GOLD PHASE\nTIPPING IMMINENT')
        led_text.set_color('black')
    else:
        led_circle.set_color('#4488ff')
        led_text.set_text('● BLUE PHASE\nSafe')
        led_text.set_color('white')

    # Saturation curve
    sat_vals = np.tanh(model.lam * phi_range / 3.0)
    sat_line.set_ydata(sat_vals)
    point.set_data([phi], [res])

    # Flip Velocity Plot
    v_range = []
    for p in np.linspace(0, 5, 100):
        r = np.tanh(model.lam * p / 3.0)
        if r >= THRESHOLD_GOLD:
            v_range.append(5.0)
        else:
            denom = 1 - r / THRESHOLD_GOLD
            v = (r * model.lam / 0.1) * (1 / denom) if denom > 0 else 5.0
            v_range.append(min(v, 5.0))
    vel_line.set_data(np.linspace(0, 5, 100), v_range)
    vel_point.set_data([phi], [v_range[int(min(99, phi/5*99))]])

    # Axiom G Panel
    ax_axiom.clear()
    ax_axiom.axis('off')
    ax_axiom.text(0.05, 0.95, 'Axiom G:', transform=ax_axiom.transAxes, color='#ffd700', fontsize=9)
    ax_axiom.text(0.05, 0.88, r'\( G \cdot \Psi_{next} = G \cdot \Psi_{current} \)',
                  transform=ax_axiom.transAxes, color='white', fontsize=9)
    ax_axiom.text(0.05, 0.75, f'Resonance state Ψ: {resonance:.4f}',
                  transform=ax_axiom.transAxes, color='white', fontsize=9)
    ax_axiom.text(0.05, 0.62, f'Flip velocity: {flip_vel:.2f}',
                  transform=ax_axiom.transAxes, color='#ff6688', fontsize=9)

    risk = model.get_risk_level(phi, model.lam)
    ax_axiom.text(0.05, 0.45, f'RISK: {risk}',
                  transform=ax_axiom.transAxes,
                  color='#ff4444' if risk == "CRITICAL (Gold Phase)" else '#ffaa00' if risk == "ELEVATED" else '#44ff88',
                  fontsize=10, weight='bold')

    # M112 Grid (empty circles, size scales with resonance)
    grid_state = model.grid_state
    active = grid_state > 0.05
    if np.any(active):
        sizes = 25 + grid_state[active] * 80
        scatter_syn.set_offsets(np.column_stack((xg[active], yg[active])))
        scatter_syn.set_sizes(sizes)
        scatter_syn.set_facecolors('none')
        scatter_syn.set_edgecolors('#ffd700')
        scatter_syn.set_linewidth(0.8)
        scatter_syn.set_alpha(0.8)
    else:
        scatter_syn.set_offsets(np.empty((0, 2)))

    # Table
    ax_table.clear()
    ax_table.axis('off')
    headers = ["Fault", "Resonance", "Gold Phase", "Risk"]
    rows = []
    for name, f in FAULTS.items():
        r = np.tanh(model.lam * phi / 3.0)
        gold = "YES" if r >= THRESHOLD_GOLD else "NO"
        risk_txt = "CRITICAL" if r >= THRESHOLD_GOLD else ("ELEVATED" if r >= 0.5 else "LOW")
        highlight = "▶ " if name == "Japan Trench" else "  "
        rows.append([highlight + name[:18], f"{r:.3f}", gold, risk_txt])

    tbl = ax_table.table(cellText=rows, colLabels=headers, loc='center', cellLoc='center',
                          colWidths=[0.40, 0.20, 0.20, 0.20])
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9)

    # Highlight Japan Trench row
    for i, name in enumerate(FAULTS.keys()):
        if name == "Japan Trench":
            for j in range(4):
                tbl[(i+1, j)].set_facecolor('#2a0808')
                tbl[(i+1, j)].set_text_props(color='#ff8888', weight='bold')

    fig1.canvas.draw_idle()


# =====================================================================
# M112 Grid Setup (for Window 1)
# =====================================================================
ax_grid = fig1.add_axes([0.55, 0.35, 0.40, 0.08])
ax_grid.set_facecolor('#0a0e14')
ax_grid.set_title('M112 Resonance Grid (Axiom G)', color='white', fontsize=9)
ax_grid.axis('off')

N_SYN = 112
th_sp = np.linspace(0, 12*np.pi, N_SYN)
r_sp = np.linspace(0.3, 3.8, N_SYN)
xg = r_sp * np.cos(th_sp)
yg = r_sp * np.sin(th_sp) * 0.35

# Background grid (gray, fixed)
ax_grid.scatter(xg, yg, s=20, c='#333333', edgecolors='#444', linewidth=0.3, alpha=0.5)

# Active grid (empty circles, will be updated)
scatter_syn = ax_grid.scatter([], [], s=[], facecolors='none', edgecolors='#ffd700', linewidth=0.8, alpha=0.8)


# =====================================================================
# EXPORT FUNCTIONS
# =====================================================================
def export_json(event):
    data = {
        "phi": model.phi,
        "lam": model.lam,
        "resonance": model.nldt_resonance(model.phi, model.lam),
        "resonance_state": model.resonance_state,
        "flip_velocity": model.get_flip_velocity(),
        "timestamp": datetime.datetime.now().isoformat(),
        "model": "NLDT Earthquake v5.6 (Japan Trench Focus)"
    }
    fname = f"nldt_earthquake_v5.6_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(fname, "w", encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    print(f"✅ JSON saved: {fname}")

def export_csv(event):
    fname = f"nldt_earthquake_v5.6_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    phi_sweep = np.linspace(0, 5, 100)
    with open(fname, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["phi", "resonance", "resonance_state", "flip_velocity"])
        for phi in phi_sweep:
            r = np.tanh(model.lam * phi / 3.0)
            res_state = min(r * 1.2, 1.0)
            v = 1e6 if r >= THRESHOLD_GOLD else (r * model.lam / 0.1) * (1 / (1 - r / THRESHOLD_GOLD)) if (1 - r / THRESHOLD_GOLD) > 0 else 1e6
            writer.writerow([round(phi, 3), round(r, 5), round(res_state, 5), round(v, 2) if v < 1e6 else 9999])
    print(f"✅ CSV saved: {fname}")

def save_png(event):
    fname = f"NLDT_Earthquake_v5.6_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    fig1.savefig(fname, dpi=400, bbox_inches='tight', facecolor='#0d1117')
    print(f"✅ PNG saved (Interactive Window): {fname}")

def reset(event):
    slider_phi.set_val(PHI_DEFAULT)
    slider_lam.set_val(LAM_DEFAULT)

# Button connections
btn_reset.on_clicked(reset)
btn_json.on_clicked(export_json)
btn_csv.on_clicked(export_csv)
btn_save.on_clicked(save_png)

# Slider events
slider_phi.on_changed(update)
slider_lam.on_changed(update)

# Start
update()
print("\n✅ Module started. Two windows open:")
print("   • Window 1: Interactive (saturation, sliders, table, M112 grid)")
print("   • Window 2: Map (Ring of Fire, coastlines, USGS live earthquakes)")
plt.show()