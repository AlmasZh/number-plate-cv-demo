import json
import os
import cv2
import easyocr

def inspect():
    reader = easyocr.Reader(["en"], gpu=False)

    with open("dataset/metadata.json", "r", encoding="utf-8") as f:
        meta = json.load(f)

    print(f"Total downloaded files: {len(meta)}\n")
    for item in meta:
        fpath = item["filepath"]
        img = cv2.imread(fpath)
        if img is None:
            print(f"Failed to read image {fpath}")
            continue
        h, w, c = img.shape
        # OCR
        results = reader.readtext(fpath, detail=1)
        texts = [text for (bbox, text, conf) in results if conf > 0.15]
        print(f"[{item['id']:02d}] {item['filename']} ({w}x{h}) | OCR: {texts} | Title: {item['title'][:40]}")

if __name__ == "__main__":
    inspect()
