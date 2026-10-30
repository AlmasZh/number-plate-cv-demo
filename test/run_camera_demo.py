#!/usr/bin/env python3
"""
Live Camera Demonstration for Smart Gate Automation System.
Captures live frames from a USB webcam, Raspberry Pi Camera, or laptop camera (/dev/video0),
runs the Kazakhstan license plate recognition pipeline, and visualizes gate access decisions.
"""

import argparse
import sys
import time
import cv2
import numpy as np

from smart_gate.plate_reader import PlateReader
from smart_gate.gate_access import SmartGateController


def run_camera(
    device_index: int = 0,
    scan_interval: float = 1.0,
    whitelist: str = None
):
    print("=" * 65)
    print("  SMART GATE AUTOMATION - LIVE CAMERA DEMONSTRATION")
    print("=" * 65)
    print(f"Opening camera device index: {device_index} (/dev/video{device_index})...")

    cap = cv2.VideoCapture(device_index)
    if not cap.isOpened():
        print(f"\n[ERROR] Could not open camera at index {device_index}.", file=sys.stderr)
        print("Please check if your camera is connected and you have permission.", file=sys.stderr)
        print("Common devices: 0 (/dev/video0) or 1 (/dev/video1).", file=sys.stderr)
        return

    # Set camera resolution to standard 720p or 480p for smooth edge processing
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera opened successfully: {actual_w}x{actual_h} resolution.")
    print("\nInitializing EasyOCR and Smart Gate Controller...")

    reader = PlateReader(languages=["en"], use_gpu=False)
    gate = SmartGateController()

    if whitelist:
        for p in whitelist.split(","):
            p_clean = p.strip()
            if p_clean:
                gate.add_authorized_plate(p_clean, owner="Custom Whitelisted", role="resident")

    print("\nControls:")
    print("  [SPACE] - Scan plate immediately")
    print("  [Q / ESC] - Exit camera demo")
    print(f"\nAuto-scan runs every {scan_interval:.1f} seconds. Point camera at a Kazakh license plate.\n")

    last_scan_time = 0.0
    last_decision = {
        "status": "WAITING_FOR_VEHICLE",
        "action": "KEEP_CLOSED",
        "plate": None,
        "region": None,
        "message": "Point camera at a license plate or press SPACE to scan.",
        "confidence": 0.0
    }
    last_bbox = None

    window_name = "Smart Gate Automation - Live Camera Feed (KZ ALPR)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

    try:
        while True:
            ret, frame = cap.read()
            if not ret or frame is None:
                print("[WARNING] Failed to grab frame from camera.", file=sys.stderr)
                time.sleep(0.1)
                continue

            current_time = time.time()
            trigger_scan = (current_time - last_scan_time) >= scan_interval

            key = cv2.waitKey(1) & 0xFF
            if key == 27 or key == ord('q') or key == ord('Q'):
                print("Exiting camera feed.")
                break
            elif key == 32:  # SPACE key
                trigger_scan = True

            # Perform license plate scan
            if trigger_scan:
                last_scan_time = current_time
                cv_result = reader.read_plate(frame)
                decision = gate.evaluate_access(cv_result)

                if cv_result.get("success"):
                    last_decision = decision
                    last_bbox = cv_result.get("bbox")
                    print(f"[{time.strftime('%H:%M:%S')}] Detected: {cv_result.get('plate')} | Region: {cv_result.get('region_name')} | Status: {decision.get('status')} (Signal: {decision.get('relay_signal')})")
                else:
                    if last_decision.get("status") != "WAITING_FOR_VEHICLE":
                        # Expire previous scan after a short while
                        if current_time - last_scan_time > 3.0:
                            last_decision = {
                                "status": "SCANNING",
                                "action": "KEEP_CLOSED",
                                "plate": None,
                                "region": None,
                                "message": "Searching for license plate...",
                                "confidence": 0.0
                            }
                            last_bbox = None

            # --- HUD Overlay ---
            display_frame = frame.copy()
            fh, fw = display_frame.shape[:2]

            # Draw central target guide box (guides where to position plate)
            box_w, box_h = int(fw * 0.45), int(fh * 0.22)
            bx1, by1 = (fw - box_w) // 2, (fh - box_h) // 2
            bx2, by2 = bx1 + box_w, by1 + box_h
            cv2.rectangle(display_frame, (bx1, by1), (bx2, by2), (200, 200, 200), 1, cv2.LINE_AA)

            # Draw detected plate bbox if available
            if last_bbox and last_decision.get("plate"):
                x, y, w, h = last_bbox
                color = (0, 220, 0) if last_decision.get("status") == "ACCESS_GRANTED" else (0, 0, 240)
                cv2.rectangle(display_frame, (x, y), (x + w, y + h), color, 3)

            # Top HUD Bar
            status = last_decision.get("status", "SCANNING")
            if status == "ACCESS_GRANTED":
                bar_color = (30, 160, 40)      # Green
                title_text = "ACCESS GRANTED - GATE OPENING"
            elif status == "ACCESS_DENIED":
                bar_color = (30, 30, 200)      # Red
                title_text = "ACCESS DENIED - UNAUTHORIZED"
            else:
                bar_color = (60, 60, 60)       # Dark gray
                title_text = "SMART GATE - MONITORING APPROACH"

            # Top bar background
            cv2.rectangle(display_frame, (0, 0), (fw, 75), bar_color, -1)
            cv2.putText(display_frame, title_text, (20, 35), cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 255, 255), 2, cv2.LINE_AA)

            sub_info = f"Relay: {last_decision.get('action', 'KEEP_CLOSED')} | SPACE: Scan Now | Q: Exit"
            cv2.putText(display_frame, sub_info, (20, 62), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (230, 230, 230), 1, cv2.LINE_AA)

            # Bottom Info Card
            cv2.rectangle(display_frame, (0, fh - 80), (fw, fh), (20, 20, 20), -1)
            plate_display = last_decision.get("plate") or "[No Plate]"
            region_display = last_decision.get("region") or "-"
            owner_display = last_decision.get("owner") or "Unregistered"

            cv2.putText(display_frame, f"Plate: {plate_display}", (20, fh - 48), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(display_frame, f"Region: {region_display}", (20, fh - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)
            cv2.putText(display_frame, f"Owner: {owner_display}", (fw // 2, fh - 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1, cv2.LINE_AA)

            cv2.imshow(window_name, display_frame)

    except KeyboardInterrupt:
        print("\nInterrupted by user.")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        print("Camera released. Demo finished.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Live camera test for Smart Gate Kazakh Plate Recognition.")
    parser.add_argument("--device", type=int, default=0, help="Camera device index (default: 0 for /dev/video0)")
    parser.add_argument("--interval", type=float, default=1.0, help="Auto-scan interval in seconds (default: 1.0)")
    parser.add_argument("--whitelist", type=str, help="Comma-separated authorized plates")
    args = parser.parse_args()

    run_camera(
        device_index=args.device,
        scan_interval=args.interval,
        whitelist=args.whitelist
    )
