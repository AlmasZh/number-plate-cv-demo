"""
Automated Test Runner for Kazakhstan License Plate CV Recognition.
Evaluates the model against 50 annotated Kazakhstani license plate images.
"""

import json
import os
import re
import time
from typing import Dict, Any, List

from smart_gate.plate_reader import PlateReader
from smart_gate.gate_access import SmartGateController, normalize_plate_key


def clean_match_key(s: str) -> str:
    """Strip all non-alphanumeric characters for clean string comparison."""
    if not s:
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", s).upper()


def run_tests():
    print("=" * 80)
    print("  SMART GATE AUTOMATION - KAZAKHSTAN LICENSE PLATE CV EVALUATION")
    print("=" * 80)

    gt_file = "dataset/ground_truth.json"
    if not os.path.exists(gt_file):
        print(f"Error: Ground truth file not found at {gt_file}")
        return

    with open(gt_file, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    print(f"Loaded {len(dataset)} annotated test images from {gt_file}\n")
    print("Initializing EasyOCR reader and Smart Gate Access Controller...")
    reader = PlateReader(languages=["en"], use_gpu=False)
    gate = SmartGateController()

    print("Model initialized. Running evaluation across all test images...\n")

    results = []
    exact_matches = 0
    partial_matches = 0
    total_detected = 0
    total_time_ms = 0.0

    header = f"{'ID':<3} | {'Image File':<16} | {'Ground Truth':<13} | {'Detected Plate':<14} | {'Region':<16} | {'Gate Decision':<14} | {'Match':<7} | {'Time (ms)':<9}"
    divider = "-" * len(header)
    print(header)
    print(divider)

    for item in dataset:
        img_id = item["id"]
        filename = item["filename"]
        filepath = item["filepath"]
        gt_plate = item.get("plate", "UNKNOWN")

        if not os.path.exists(filepath):
            print(f"{img_id:<3} | {filename:<16} | {gt_plate:<13} | {'[FILE NOT FOUND]':<14} | {'-':<16} | {'-':<14} | {'FAIL':<7} | {'0.0':<9}")
            continue

        pred = reader.read_plate(filepath)
        gate_decision = gate.evaluate_access(pred)

        pred_plate = pred.get("plate") or "NOT_FOUND"
        time_ms = pred.get("processing_time_ms", 0.0)
        total_time_ms += time_ms

        gt_norm = clean_match_key(gt_plate)
        pred_norm = clean_match_key(pred_plate)

        match_status = "FAIL"
        if pred.get("success"):
            total_detected += 1
            if pred_norm == gt_norm:
                match_status = "PASS"
                exact_matches += 1
            elif (len(pred_norm) >= 4 and pred_norm in gt_norm) or (len(gt_norm) >= 4 and gt_norm in pred_norm):
                match_status = "PARTIAL"
                partial_matches += 1
            else:
                match_status = "DIFF"

        reg_str = pred.get("region_name") or "-"
        if len(reg_str) > 16:
            reg_str = reg_str[:13] + "..."

        gate_str = gate_decision.get("status", "-")

        print(f"{img_id:<3} | {filename:<16} | {gt_plate:<13} | {pred_plate:<14} | {reg_str:<16} | {gate_str:<14} | {match_status:<7} | {time_ms:<9.1f}")

        results.append({
            "id": img_id,
            "filename": filename,
            "ground_truth": gt_plate,
            "detected_plate": pred_plate,
            "format_type": pred.get("format_type"),
            "region_code": pred.get("region_code"),
            "region_name": pred.get("region_name"),
            "gate_status": gate_decision.get("status"),
            "gate_action": gate_decision.get("action"),
            "confidence": pred.get("confidence", 0.0),
            "match_status": match_status,
            "processing_time_ms": time_ms
        })

    total_images = len(dataset)
    avg_time_ms = round(total_time_ms / max(total_images, 1), 1)
    detection_rate = round((total_detected / total_images) * 100.0, 1)
    pass_rate = round((exact_matches / total_images) * 100.0, 1)
    effective_accuracy = round(((exact_matches + partial_matches) / total_images) * 100.0, 1)

    print(divider)
    print("\n" + "=" * 80)
    print("  SUMMARY EVALUATION METRICS")
    print("=" * 80)
    print(f"Total Test Images Analyzed:     {total_images}")
    print(f"Plates Successfully Detected:   {total_detected} / {total_images} ({detection_rate}%)")
    print(f"Exact Matches (PASS):           {exact_matches} / {total_images} ({pass_rate}%)")
    print(f"Partial/Sub-string Matches:     {partial_matches} / {total_images}")
    print(f"Effective Recognition Accuracy: {exact_matches + partial_matches} / {total_images} ({effective_accuracy}%)")
    print(f"Average Inference Latency:      {avg_time_ms} ms / frame (on CPU)")
    print("=" * 80)

    # Save results to JSON
    summary_report = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "metrics": {
            "total_images": total_images,
            "detected_count": total_detected,
            "detection_rate_pct": detection_rate,
            "exact_matches": exact_matches,
            "partial_matches": partial_matches,
            "pass_rate_pct": pass_rate,
            "effective_accuracy_pct": effective_accuracy,
            "avg_latency_ms": avg_time_ms
        },
        "details": results
    }

    results_json = "test_results.json"
    with open(results_json, "w", encoding="utf-8") as f:
        json.dump(summary_report, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed results saved to {results_json}")

    # Generate Markdown Summary
    generate_markdown_report(summary_report, "test_results.md")
    print(f"Markdown report generated at test_results.md")


def generate_markdown_report(report: Dict[str, Any], out_path: str):
    m = report["metrics"]
    details = report["details"]

    md = []
    md.append("# Smart Gate Automation - Computer Vision Test Report")
    md.append("")
    md.append("## Overview")
    md.append("- **Project:** IoT-Based Smart Gate Automation System Integrating Computer Vision and GPS Location")
    md.append("- **Target Environment:** Raspberry Pi / Smart Home Edge Controller")
    md.append("- **Stack:** Python, OpenCV, EasyOCR, Kazakhstani Plate Grammar Rules")
    md.append("")
    md.append("## Key Performance Indicators")
    md.append(f"| Metric | Result |")
    md.append(f"|---|---|")
    md.append(f"| **Total Example Images Tested** | **{m['total_images']}** |")
    md.append(f"| **Detection Rate** | **{m['detection_rate_pct']}%** ({m['detected_count']}/{m['total_images']}) |")
    md.append(f"| **Exact Match Rate** | **{m['pass_rate_pct']}%** ({m['exact_matches']}/{m['total_images']}) |")
    md.append(f"| **Effective Accuracy (Exact + Partial)** | **{m['effective_accuracy_pct']}%** ({m['exact_matches'] + m['partial_matches']}/{m['total_images']}) |")
    md.append(f"| **Average Inference Time (CPU)** | **{m['avg_latency_ms']} ms** |")
    md.append("")
    md.append("## Image-by-Image Test Log")
    md.append("| ID | Image | Ground Truth | Detected | Region | Gate Status | Match | Latency (ms) |")
    md.append("|---|---|---|---|---|---|---|---|")
    for d in details:
        md.append(f"| {d['id']} | `{d['filename']}` | `{d['ground_truth']}` | `{d['detected_plate']}` | {d.get('region_name') or '-'} | `{d['gate_status']}` | **{d['match_status']}** | {d['processing_time_ms']:.1f} |")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")


if __name__ == "__main__":
    run_tests()
