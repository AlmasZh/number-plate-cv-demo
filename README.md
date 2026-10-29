# Smart Gate Automation - Computer Vision License Plate Reader (Kazakhstan)

**Project:** *Design and Implementation of an IoT-Based Smart Gate Automation System Integrating Computer Vision and GPS Location*  
**Scope:** Accessible smart home gate automation for regular private houses  
**Technical Stack:** Raspberry Pi (Edge Device), Python (Computer Vision / ALPR), Go & Rust (IoT Gate Relay Actuation, GPS Geofencing & IPC)

---

## 1. Overview

This module provides the core **Computer Vision & Automatic License Plate Recognition (ALPR)** engine tailored for **Kazakhstani license plates (GOST format)**. When a vehicle approaches the gate, the camera feed captures the frame, detects and reads the license plate number, resolves the Kazakhstan administrative region, and evaluates access against a homeowner whitelist to trigger the gate relay.

### Key Capabilities
- **Kazakhstan Plate Grammar & Post-Processing:**
  - Modern 2012+ standard format (`123 ABC 02` — 3 digits, 3 letters, 2-digit region code)
  - Modern 2012+ legal entity / corporate format (`123 AB 02`)
  - Two-row / square rear plates (`237 BLM 01`)
  - Pre-2012 standard format (`A 553 ZYM` — 1 region letter, 3 digits, 3 letters)
  - Pre-2012 legal entity format (`A 204 AK`, `Z 313 ZZ`)
  - Special series: Diplomatic (`D 001618`), Foreign resident (`H 783497`), Police (`E 146 KP`), Trailer (`2573 AD`, `8621 MK`), Transit (`110391 AN`), Special AST (`455 AST`)
- **Position-Aware Ambiguity Disambiguation:** Resolves common OCR confusions (`0` vs `O`, `1` vs `I`/`|`, `5` vs `S`, `8` vs `B`) based on strict position rules within the Kazakhstan license plate standard.
- **Smart Gate Access Controller:** Whitelist validation, access grant/deny decision, and relay signal output (`1` = open relay, `0` = locked).
- **Edge-Ready & Lightweight:** Runs entirely on CPU without requiring GPU hardware, suitable for Raspberry Pi 4 / 5.

---

## 2. Dataset of Kazakhstani Number Plates

The repository includes a curated benchmark dataset of **50 real Kazakhstani number plate example images** located in `dataset/images/` with complete ground truth annotations in `dataset/ground_truth.json`:
- **44 Dedicated License Plate Images:** Standard private, corporate, two-row, trailer, transit, and diplomatic plates.
- **6 Street Vehicle Captures:** Real cars photographed on the streets of Almaty and Astana (VW Teramont, VW Polo, Geely Emgrand, Tank 500, Kia K9, Lada Vesta) in authentic outdoor lighting.

---

## 3. Quickstart & Usage

### 3.1. Activate the Virtual Environment

```bash
source /home/almas/Project/university/project_research/.venv/bin/activate
```

### 3.2. Run Full Test Suite (All 50 Images)

Evaluate recognition accuracy and latency across the entire dataset:

```bash
python test_cv_model.py
```

This generates:
- An interactive console table with per-image detection, region name, gate decision, match status, and latency.
- `test_results.json` (Structured JSON benchmark data).
- `test_results.md` (Markdown summary report).

### 3.3. Test Single Vehicle Image (CLI)

```bash
# Whitelisted vehicle test (Triggers OPEN relay)
python run_gate_cv.py --image dataset/images/kz_plate_26.png

# Custom whitelist test
python run_gate_cv.py --image dataset/images/kz_plate_30.jpg --whitelist "429 HUA 12"

# Output JSON payload for Go / Rust IoT integration
python run_gate_cv.py --image dataset/images/kz_plate_26.png --json
```

### 3.4. Test with Your Live Camera

You can test in real time with your laptop webcam, USB camera, or Raspberry Pi camera:

```bash
# Launch interactive live camera feed (default device /dev/video0)
python run_camera_demo.py

# Or via CLI runner with custom whitelist
python run_gate_cv.py --camera 0 --whitelist "143 ABA 12"
```

- **Interactive Controls:**
  - `[SPACE]` : Manually trigger an immediate scan.
  - `[Q]` or `[ESC]` : Exit the live camera window.
  - An on-screen HUD displays target guide, recognized plate, region, and gate status (`ACCESS GRANTED` in green or `ACCESS DENIED` in red).

### 3.5. Batch Processing

```bash
python run_gate_cv.py --batch dataset/images/
```

---

## 4. Architecture & Module Structure

```text
project_research/
├── .venv/                         # Python 3.14 virtual environment
├── smart_gate/                    # Core Python package
│   ├── __init__.py                # Package exports
│   ├── kz_plate_parser.py         # Kazakhstan plate grammar, region lookup & OCR fixes
│   ├── plate_detector.py          # OpenCV morphological plate area detector
│   ├── plate_reader.py            # EasyOCR inference & pipeline coordinator
│   └── gate_access.py             # Whitelist & IoT relay access logic
├── dataset/
│   ├── images/                    # 50 real Kazakhstani plate test images
│   ├── metadata.json              # Image sources, dimensions & URLs
│   └── ground_truth.json          # Verified annotations & plate numbers
├── scripts/
│   ├── download_dataset.py        # Wikimedia Commons dataset fetcher
│   ├── download_street_cars.py    # Street automobile scene fetcher
│   └── build_ground_truth.py      # Ground truth compiler
├── run_gate_cv.py                 # CLI interface for inspection & IoT triggers
├── test_cv_model.py               # Comprehensive 50-image test runner
├── test_results.json              # Automated test output data
├── test_results.md                # Generated test report
└── README.md                      # Documentation
```

---

## 5. IoT Integration with Go / Rust

For the hybrid smart home architecture:
- **Python:** Runs the Computer Vision inference either on demand (when PIR / radar / camera motion triggers) or continuously on keyframes.
- **Go / Rust Microservice:**
  - Can spawn `run_gate_cv.py --image <captured_frame.jpg> --json` via `exec.Command` / `std::process::Command` and parse the JSON stdout.
  - Or receive JSON events over MQTT / Unix Domain Socket.
  - Controls GPIO pin relay (e.g. Raspberry Pi GPIO 17) to actuate the gate motor when `relay_signal == 1`.
  - Integrates with GPS Geofencing (e.g. triggers camera OCR only when homeowner GPS approaches within 50 meters of the house).
# number-plate-cv
