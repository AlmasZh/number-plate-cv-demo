#!/usr/bin/env python3
"""
Helper utility to add a user's custom image to the dataset and ground truth.
Usage:
  python scripts/add_image.py --file path/to/my_photo.jpg --plate "777 AAA 02" --notes "My car"
"""

import argparse
import json
import os
import shutil
import sys

def main():
    parser = argparse.ArgumentParser(description="Add custom image to dataset and ground truth benchmark.")
    parser.add_argument("--file", required=True, type=str, help="Path to your image file (.jpg, .png, etc.)")
    parser.add_argument("--plate", required=True, type=str, help="Expected license plate number (e.g. '777 AAA 02')")
    parser.add_argument("--category", default="user_custom", type=str, help="Category (default: user_custom)")
    parser.add_argument("--notes", default="User custom test image", type=str, help="Description/notes")
    args = parser.parse_args()

    src_file = os.path.abspath(args.file)
    if not os.path.exists(src_file):
        print(f"Error: File not found: {src_file}", file=sys.stderr)
        sys.exit(1)

    gt_path = "dataset/ground_truth.json"
    if not os.path.exists(gt_path):
        print(f"Error: {gt_path} not found.", file=sys.stderr)
        sys.exit(1)

    with open(gt_path, "r", encoding="utf-8") as f:
        gt_data = json.load(f)

    # Determine new ID and filename
    new_id = len(gt_data) + 1
    ext = os.path.splitext(src_file)[1].lower() or ".jpg"
    dest_filename = f"kz_plate_{new_id:02d}{ext}"
    dest_path = os.path.join("dataset/images", dest_filename)

    # Copy image
    shutil.copy2(src_file, dest_path)
    file_size = os.path.getsize(dest_path)

    # Append record
    entry = {
        "id": new_id,
        "filename": dest_filename,
        "filepath": dest_path,
        "title": f"Custom: {os.path.basename(src_file)}",
        "url": "local",
        "size_bytes": file_size,
        "plate": args.plate,
        "category": args.category,
        "notes": args.notes
    }
    gt_data.append(entry)

    with open(gt_path, "w", encoding="utf-8") as f:
        json.dump(gt_data, f, indent=2, ensure_ascii=False)

    print(f"Successfully added image:")
    print(f"  ID:         {new_id}")
    print(f"  Saved to:   {dest_path}")
    print(f"  Ground Truth: {args.plate}")
    print(f"  Total images in dataset: {len(gt_data)}")
    print(f"\nYou can now test it via:")
    print(f"  python run_gate_cv.py --image {dest_path}")
    print(f"  python test_cv_model.py")

if __name__ == "__main__":
    main()
