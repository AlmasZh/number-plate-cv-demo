"""
Kazakhstan License Plate Reader Pipeline.
Combines PlateDetector, EasyOCR, and KZPlateParser.
"""

import time
from typing import Dict, Any, Optional, Union, List
import cv2
import numpy as np
import easyocr

from .plate_detector import PlateDetector
from .kz_plate_parser import KZPlateParser


class PlateReader:
    """Full-pipeline license plate recognition engine for smart gate automation."""

    def __init__(self, languages: Optional[List[str]] = None, use_gpu: bool = False):
        if languages is None:
            languages = ["en"]
        self.reader = easyocr.Reader(languages, gpu=use_gpu)
        self.detector = PlateDetector(max_dimension=1024)

    def read_plate(self, image_input: Union[str, np.ndarray]) -> Dict[str, Any]:
        """
        Process an image file path or numpy array and recognize Kazakhstani license plate.
        """
        start_time = time.perf_counter()

        # Load image if file path
        if isinstance(image_input, str):
            image = cv2.imread(image_input)
            if image is None:
                return {
                    "success": False,
                    "error": f"Failed to load image from {image_input}",
                    "plate": None,
                    "processing_time_ms": 0.0,
                }
        else:
            image = image_input

        # Step 1: Detect candidate regions + full image
        candidates = self.detector.extract_candidates(image)

        best_result: Optional[Dict[str, Any]] = None
        all_raw_tokens: List[str] = []
        max_confidence = 0.0

        # Step 2: Run OCR on candidates (crops first, then full image)
        for crop, bbox in candidates:
            # Run EasyOCR
            ocr_results = self.reader.readtext(crop, detail=1)
            tokens = []
            confidences = []

            for _, text, conf in ocr_results:
                if conf >= 0.15:
                    tokens.append(text)
                    confidences.append(conf)
                    all_raw_tokens.append(text)

            if not tokens:
                continue

            # Parse with KZ rules
            parsed = KZPlateParser.parse_tokens(tokens)
            if parsed:
                avg_conf = float(np.mean(confidences)) if confidences else 0.5
                if avg_conf > max_confidence or best_result is None:
                    max_confidence = avg_conf
                    best_result = {
                        **parsed,
                        "confidence": round(avg_conf, 3),
                        "bbox": bbox,
                        "matched_tokens": tokens,
                    }
                    # If high confidence standard plate matched, we can return early
                    if avg_conf >= 0.65 and parsed.get("is_valid", False):
                        break

        # If candidates didn't yield a match, attempt direct scaled read
        if best_result is None:
            img_scaled, _ = self.detector.resize_for_inference(image)
            ocr_results = self.reader.readtext(img_scaled, detail=1)
            tokens = [text for (_, text, conf) in ocr_results if conf >= 0.15]
            parsed = KZPlateParser.parse_tokens(tokens)
            if parsed:
                best_result = {
                    **parsed,
                    "confidence": 0.5,
                    "bbox": (0, 0, img_scaled.shape[1], img_scaled.shape[0]),
                    "matched_tokens": tokens,
                }

        elapsed_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        if best_result:
            return {
                "success": True,
                "plate": best_result["plate"],
                "normalized": best_result["normalized"],
                "format_type": best_result["format_type"],
                "region_code": best_result.get("region_code"),
                "region_name": best_result.get("region_name"),
                "is_valid_format": best_result.get("is_valid", False),
                "confidence": best_result.get("confidence", 0.5),
                "bbox": best_result.get("bbox"),
                "raw_tokens": all_raw_tokens,
                "processing_time_ms": elapsed_ms,
            }

        return {
            "success": False,
            "plate": None,
            "normalized": None,
            "format_type": None,
            "region_code": None,
            "region_name": None,
            "is_valid_format": False,
            "confidence": 0.0,
            "bbox": None,
            "raw_tokens": all_raw_tokens,
            "processing_time_ms": elapsed_ms,
        }
