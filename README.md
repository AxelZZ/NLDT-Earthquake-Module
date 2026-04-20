<img width="5869" height="4688" alt="NLDT_Earthquake_v5 6_20260420_214234" src="https://github.com/user-attachments/assets/d7f6de8d-3647-4620-9781-cb82cf210134" />
<img width="1224" height="808" alt="image" src="https://github.com/user-attachments/assets/ac24c1d8-8b2d-4434-a4cf-feed56c2aad0" />

# NLDT Earthquake Module v5.6 – Japan Trench Focus

**Non-linear resonance analysis of the Japan Trench with USGS live data**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## © Copyright & License

Copyright (c) 2026 Axel Zill-Zheng

MIT License

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## ⚠️ LEGAL DISCLAIMER

> **IMPORTANT:** This is an **independent research project** developed by Axel Zill-Zheng.
>
> **This software is NOT affiliated with, endorsed by, or connected to any government agency, space agency, or company.**
>
> **The code is provided for RESEARCH, EDUCATIONAL, and EXPLORATORY purposes ONLY.**
>
> **This is NOT a certified earthquake forecasting system.**
>
> **DO NOT use this tool for real evacuation or safety decisions.**
>
> **The author assumes NO LIABILITY for any decisions made based on this simulation.**

---

## ✍️ AUTHOR & ATTRIBUTION

| | |
|---|---|
| **Author** | Axel Zill-Zheng |
| **Location** | Homebase Xiamen, China |
| **Framework** | NLDT / RPT (Non-Linear Dimensions Theory / Relativistic Phase Transition) |
| **Contact** | GitHub Issues (preferred) |
| **Copyright** | © 2026 Axel Zill-Zheng. All rights reserved. |

---

## 🌟 OVERVIEW

This interactive earthquake module analyzes tectonic stress and resonance at the **Japan Trench** using the NLDT resonance function:

S(Φ) = tanh(λ · Φ / 3.0)

The module features:

- **Japan Trench focus** – prominent red line, focus label
- **Taiwan / Xiamen highlight** – yellow line (Philippine Trench, Ryukyu Arc)
- **USGS live earthquake data** – recent earthquakes (7 days, M≥4.5)
- **Gold Phase LED** – immediate visual warning when resonance ≥ 0.68
- **Flip velocity v_res (RPT)** – shows how close the system is to tipping
- **Axiom G & PLAREK status** – grid-based resonance state
- **M112 resonance grid** – 112 nodes, empty circles scale with resonance
- **JSON / CSV / PNG export** – for documentation and analysis

---

## 🖥️ INSTALLATION & EXECUTION

Install the required packages:

pip install numpy matplotlib requests

Optional (for map coastlines):

pip install cartopy

Run the simulator:

python NLDT_Earthquake_v5.6.py

Two windows will open:
- Window 1 (Interactive) – saturation curve, sliders, table, M112 grid
- Window 2 (Map) – Pacific Ring of Fire, plate boundaries, USGS earthquakes

---

## 🎮 INTERACTIVE CONTROLS

Sliders:

| Slider | Function | Range | Default |
|--------|----------|-------|---------|
| Stress Φ | Tectonic stress level | 0.0 – 5.0 | 2.8 |
| λ | Resonance strength | 1.0 – 15.0 | 7.9 |

Buttons:

| Button | Action |
|--------|--------|
| Reset | Resets all sliders to default |
| JSON Export | Saves current simulation state |
| CSV Export | Exports parameter sweep (0–5 Φ) |
| PNG | Saves screenshot of interactive window |

---

## 📊 VISUALIZATIONS

| Panel | Description |
|-------|-------------|
| Saturation Curve | NLDT resonance S(Φ) with Gold Phase threshold (0.68) |
| Gold Phase LED | BLUE = safe, GOLD = tipping imminent |
| Flip Velocity | RPT velocity v_res – diverges at Gold Phase |
| M112 Grid | 112 nodes, empty circles – size scales with resonance |
| Risk Table | All 9 faults with resonance, Gold Phase status, risk level |
| Map | Pacific Ring of Fire, plate boundaries, USGS live earthquakes, historical markers |

---

## 🗺️ MAP FEATURES

- Plate boundaries – 9 major faults with individual colors
- Japan Trench – red line (focus)
- Taiwan / Xiamen – yellow dashed line
- USGS live earthquakes – yellow/orange/red dots (size = magnitude)
- Historical earthquakes – gold stars (1906, 1946, 2011, 2004, etc.)

---

## 📸 SCREENSHOT

![NLDT Earthquake Module v5.6](screenshot.png)

---

## 📤 EXPORT FORMATS

JSON Export – Complete simulation state (Φ, λ, resonance, flip velocity)

CSV Export – Parameter sweep over Φ (0–5) with resonance, resonance state, flip velocity

PNG – Screenshot of interactive window

---

## 🔬 SCIENTIFIC BASIS

The model uses the NLDT resonance function with parameters derived from published sources:

| Parameter | Value | Source |
|-----------|-------|--------|
| Japan Trench slip rate | 80 mm/year | Simons et al. (2011) |
| Coupling ratio | 0.90 | Loveless & Meade (2010) |
| Locking depth | 30 km | – |
| λ (resonance strength) | 7.9 | NLDT framework |

Gold Phase threshold: S ≥ 0.68 (empirical from NLDT simulations)

Flip velocity (RPT): v_res = (Φ · λ / Δt) / (1 - Φ / Θ_gold)

---

## ⚠️ DISCLAIMER (Short Version)

This is a research and educational simulation only. NOT a certified earthquake forecasting system. Do not use for real evacuation or safety decisions.

---

## 📌 VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| v5.6 | 2026-04-20 | Two-window layout, Japan Trench focus, M112 grid (empty circles, size scales), cartopy support |
| v5.5 | 2026-04-20 | Gold Phase LED, flip velocity, Axiom G panel |
| v5.1 | 2026-04-03 | Original Taiwan/Xiamen focus |

---

## 📞 CONTACT & SUPPORT

| | |
|---|---|
| Author | Axel Zill-Zheng |
| GitHub | github.com/AxelZZ |
| Issues | Please open an issue on GitHub |

---

© 2026 Axel Zill-Zheng | Homebase Xiamen NLDT LAB
Part of the NLDT / RPT Framework

All rights reserved.

END OF README
