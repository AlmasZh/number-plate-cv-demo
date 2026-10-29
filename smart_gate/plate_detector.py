"""
License Plate Detector and Preprocessor using OpenCV.
Optimized for Raspberry Pi and edge compute environments.
Extracts candidate license plate regions using morphological operations.
"""

from typing import List, Tuple, Optional
import cv2
import numpy as np


class PlateDetector:
    """Detects and extracts candidate license plate bounding boxes and crops."""

    def __init__(self, max_dimension: int = 1024):
        self.max_dimension = max_dimension

    def resize_for_inference(self, image: np.ndarray) -> Tuple[np.ndarray, float]:
        """Resize image so max dimension does not exceed max_dimension, preserving aspect ratio."""
        h, w = image.shape[:2]
        if max(h, w) <= self.max_dimension:
            return image, 1.0

        scale = self.max_dimension / float(max(h, w))
        new_w = int(w * scale)
        new_h = int(h * scale)
        resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_AREA)
        return resized, scale

    def extract_candidates(self, image: np.ndarray) -> List[Tuple[np.ndarray, Tuple[int, int, int, int]]]:
        """
        Locate potential license plate bounding boxes in the image.
        Returns a list of tuples: (cropped_image, (x, y, w, h)).
        """
        img_scaled, scale = self.resize_for_inference(image)
        h, w = img_scaled.shape[:2]

        # Convert to grayscale
        if len(img_scaled.shape) == 3:
            gray = cv2.cvtColor(img_scaled, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_scaled

        # Enhance contrast with CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        contrast_enhanced = clahe.apply(gray)

        # Bilateral filter to smooth noise while keeping edges sharp
        blurred = cv2.bilateralFilter(contrast_enhanced, 11, 17, 17)

        # Sobel gradient along X axis (detects vertical character strokes)
        grad_x = cv2.Sobel(blurred, cv2.CV_32F, 1, 0, ksize=-1)
        grad_x = np.absolute(grad_x)
        min_val, max_val = np.min(grad_x), np.max(grad_x)
        if max_val > min_val:
            grad_x = (255 * ((grad_x - min_val) / (max_val - min_val))).astype("uint8")
        else:
            grad_x = np.zeros_like(blurred)

        # Blur the gradient
        grad_x = cv2.GaussianBlur(grad_x, (5, 5), 0)

        # Otsu thresholding
        _, thresh = cv2.threshold(grad_x, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

        # Morphological close: rectangular horizontal kernel to fuse characters together
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (21, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

        # Morphological open to clear small noise specks
        kernel_clean = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        closed = cv2.morphologyEx(closed, cv2.MORPH_OPEN, kernel_clean)

        # Find contours
        contours, _ = cv2.findContours(closed.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        candidates = []
        img_area = float(w * h)

        for cnt in contours:
            x_box, y_box, w_box, h_box = cv2.boundingRect(cnt)
            area = w_box * h_box
            aspect_ratio = float(w_box) / max(h_box, 1)

            # Kazakh plate aspect ratios:
            # - Rectangular plates: ~3.0 - 5.5
            # - Two-row square plates: ~1.2 - 2.5
            if (1.2 <= aspect_ratio <= 6.0) and (area >= 500) and (area <= 0.45 * img_area):
                # Add small margin
                pad_x = int(w_box * 0.08)
                pad_y = int(h_box * 0.15)
                x1 = max(0, x_box - pad_x)
                y1 = max(0, y_box - pad_y)
                x2 = min(w, x_box + w_box + pad_x)
                y2 = min(h, y_box + h_box + pad_y)

                crop = img_scaled[y1:y2, x1:x2]
                if crop.size > 0:
                    candidates.append((crop, (x1, y1, x2 - x1, y2 - y1)))

        # Sort candidates by area descending (largest/most prominent plate first)
        candidates.sort(key=lambda item: item[1][2] * item[1][3], reverse=True)

        # Limit to top 5 candidates + always include full scaled image as fallback
        top_candidates = candidates[:5]
        top_candidates.append((img_scaled, (0, 0, w, h)))

        return top_candidates
