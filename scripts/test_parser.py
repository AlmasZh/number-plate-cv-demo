import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import easyocr
from smart_gate.kz_plate_parser import KZPlateParser

def test():
    reader = easyocr.Reader(["en"], gpu=False)
    with open("dataset/ground_truth.json", "r", encoding="utf-8") as f:
        gt = json.load(f)

    for item in gt[:20]:
        fpath = item["filepath"]
        res = reader.readtext(fpath, detail=0)
        parsed = KZPlateParser.parse_tokens(res)
        expected = item.get("plate", "")
        detected = parsed.get("plate") if parsed else "None"
        print(f"[{item['id']:02d}] {item['filename']} | Raw: {res} | Expected: {expected} | Parsed: {detected}")

if __name__ == "__main__":
    test()
