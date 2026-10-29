#!/usr/bin/env python3
"""
CLI entry point for Smart Gate Computer Vision License Plate Reader.
Integrates with IoT Gate automation backend (Python, Go, Rust, Raspberry Pi).
"""

import argparse
import glob
import json
import os
import sys

from smart_gate.plate_reader import PlateReader
from smart_gate.gate_access import SmartGateController


def main():
    parser = argparse.ArgumentParser(
        description="Smart Gate IoT - Kazakhstan License Plate Reader (CV Module)"
    )
    parser.add_argument(
        "--image",
        type=str,
        help="Path to vehicle or plate image file to analyze."
    )
    parser.add_argument(
        "--batch",
        type=str,
        help="Directory path containing images to process in batch."
    )
    parser.add_argument(
        "--whitelist",
        type=str,
        help="Comma-separated list of authorized plate numbers (e.g. '143 ABA 12,237 BLM 01')."
    )
    parser.add_argument(
        "--whitelist-file",
        type=str,
        help="Path to JSON file containing authorized plates."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON event payload (for Go / Rust / IPC integration)."
    )
    parser.add_argument(
        "--camera",
        nargs="?",
        const=0,
        type=int,
        help="Run live camera inspection stream (default device index: 0)."
    )

    args = parser.parse_args()

    if args.camera is not None:
        from run_camera_demo import run_camera
        run_camera(device_index=args.camera, whitelist=args.whitelist)
        return

    if not args.image and not args.batch:
        parser.print_help()
        print("\nExample usage:")
        print("  python run_gate_cv.py --image dataset/images/kz_plate_26.png")
        print("  python run_gate_cv.py --camera 0")
        print("  python run_gate_cv.py --image dataset/images/kz_plate_26.png --whitelist '143 ABA 12'")
        print("  python run_gate_cv.py --batch dataset/images/ --json")
        sys.exit(1)

    # Initialize gate controller
    gate = SmartGateController(config_path=args.whitelist_file)
    if args.whitelist:
        for p in args.whitelist.split(","):
            p_strip = p.strip()
            if p_strip:
                gate.add_authorized_plate(p_strip, owner="CLI Whitelisted Vehicle", role="resident")

    # Initialize CV reader
    reader = PlateReader(languages=["en"], use_gpu=False)

    # Process single image
    if args.image:
        if not os.path.exists(args.image):
            print(f"Error: Image file not found: {args.image}", file=sys.stderr)
            sys.exit(1)

        plate_result = reader.read_plate(args.image)
        decision = gate.evaluate_access(plate_result)

        if args.json:
            combined = {
                "cv_result": plate_result,
                "gate_decision": decision
            }
            print(json.dumps(combined, indent=2, ensure_ascii=False))
        else:
            print("\n" + "=" * 60)
            print("  SMART GATE CV - VEHICLE INSPECTION RESULT")
            print("=" * 60)
            print(f"Image File:          {args.image}")
            print(f"Plate Recognized:    {plate_result.get('plate') or '[No plate detected]'}")
            print(f"Format Category:     {plate_result.get('format_type') or '-'}")
            print(f"Region:              {plate_result.get('region_name') or '-'}")
            print(f"Confidence:          {plate_result.get('confidence', 0.0) * 100:.1f}%")
            print(f"Inference Latency:   {plate_result.get('processing_time_ms', 0.0):.1f} ms")
            print("-" * 60)
            print(f"Gate Access Status:  {decision.get('status')}")
            print(f"Relay Control Action:{decision.get('action')} (Signal: {decision.get('relay_signal')})")
            print(f"Vehicle Owner:       {decision.get('owner')}")
            print(f"System Message:      {decision.get('message')}")
            print("=" * 60 + "\n")

    # Process batch
    elif args.batch:
        if not os.path.isdir(args.batch):
            print(f"Error: Directory not found: {args.batch}", file=sys.stderr)
            sys.exit(1)

        patterns = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.PNG"]
        files = []
        for pat in patterns:
            files.extend(glob.glob(os.path.join(args.batch, pat)))
        files = sorted(list(set(files)))

        batch_results = []
        for f in files:
            p_res = reader.read_plate(f)
            dec = gate.evaluate_access(p_res)
            batch_results.append({
                "file": os.path.basename(f),
                "plate": p_res.get("plate"),
                "format": p_res.get("format_type"),
                "status": dec.get("status"),
                "time_ms": p_res.get("processing_time_ms")
            })

        if args.json:
            print(json.dumps(batch_results, indent=2, ensure_ascii=False))
        else:
            print(f"\nProcessed {len(batch_results)} images in {args.batch}:")
            for r in batch_results:
                print(f"  {r['file']:<16} -> {str(r['plate']):<14} | Gate: {r['status']:<14} ({r['time_ms']:.1f} ms)")


if __name__ == "__main__":
    main()
