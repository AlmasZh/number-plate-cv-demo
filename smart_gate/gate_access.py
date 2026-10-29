"""
IoT Smart Gate Access Control Logic for Private Houses.
Evaluates recognized vehicle license plates against an authorized whitelist
and produces access decision events for Raspberry Pi GPIO relay / Go / Rust services.
"""

from datetime import datetime
import json
import os
import re
from typing import Dict, Any, List, Optional


def normalize_plate_key(plate_str: Optional[str]) -> str:
    """Normalize plate text for exact comparison: uppercase alphanumeric only."""
    if not plate_str:
        return ""
    return re.sub(r"[^A-Za-z0-9]", "", plate_str).upper()


class SmartGateController:
    """Smart Home Gate Access Controller."""

    def __init__(self, config_path: Optional[str] = None):
        self.whitelist: Dict[str, Dict[str, Any]] = {}
        if config_path and os.path.exists(config_path):
            self.load_whitelist(config_path)
        else:
            # Default sample whitelist for private house demonstration
            self._init_default_whitelist()

    def _init_default_whitelist(self):
        default_vehicles = [
            {"plate": "143 ABA 12", "owner": "Homeowner Primary (Toyota Land Cruiser)", "role": "resident"},
            {"plate": "237 BLM 01", "owner": "Homeowner Secondary (Hyundai Elantra)", "role": "resident"},
            {"plate": "123 ABC 01", "owner": "Family Member (Kia Sportage)", "role": "resident"},
            {"plate": "A 553 ZYM", "owner": "Frequent Visitor (Subaru Outback)", "role": "guest"},
            {"plate": "E 419 KLM", "owner": "Maintenance Service", "role": "service"},
            {"plate": "771 DLA 02", "owner": "Tenant (VW Polo)", "role": "resident"},
            {"plate": "205 LFA 02", "owner": "Homeowner (VW Teramont)", "role": "resident"},
        ]
        for v in default_vehicles:
            self.add_authorized_plate(v["plate"], v["owner"], v["role"])

    def add_authorized_plate(self, plate: str, owner: str = "Authorized Vehicle", role: str = "resident") -> None:
        key = normalize_plate_key(plate)
        if key:
            self.whitelist[key] = {
                "display_plate": plate,
                "owner": owner,
                "role": role,
                "added_at": datetime.now().isoformat()
            }

    def remove_authorized_plate(self, plate: str) -> bool:
        key = normalize_plate_key(plate)
        return self.whitelist.pop(key, None) is not None

    def load_whitelist(self, filepath: str) -> None:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            for item in data:
                self.add_authorized_plate(
                    item.get("plate", ""),
                    item.get("owner", "Authorized Vehicle"),
                    item.get("role", "resident")
                )

    def save_whitelist(self, filepath: str) -> None:
        data = list(self.whitelist.values())
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def evaluate_access(self, plate_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate recognition result and generate an IoT Gate Decision Event.
        """
        timestamp = datetime.now().isoformat()
        detected_plate = plate_result.get("plate")
        normalized = normalize_plate_key(detected_plate or plate_result.get("normalized"))
        confidence = plate_result.get("confidence", 0.0)
        processing_time_ms = plate_result.get("processing_time_ms", 0.0)

        # Case 1: No plate recognized
        if not plate_result.get("success") or not normalized:
            return {
                "timestamp": timestamp,
                "status": "NO_PLATE_DETECTED",
                "action": "KEEP_CLOSED",
                "relay_signal": 0,
                "plate": None,
                "confidence": confidence,
                "message": "No valid license plate detected in camera frame.",
                "processing_time_ms": processing_time_ms
            }

        # Case 2: Plate recognized, check whitelist
        if normalized in self.whitelist:
            vehicle_info = self.whitelist[normalized]
            return {
                "timestamp": timestamp,
                "status": "ACCESS_GRANTED",
                "action": "TRIGGER_RELAY_OPEN",
                "relay_signal": 1,
                "plate": detected_plate,
                "confidence": confidence,
                "owner": vehicle_info["owner"],
                "role": vehicle_info["role"],
                "region": plate_result.get("region_name"),
                "message": f"Welcome! Access granted for {vehicle_info['owner']} ({detected_plate}). Gate opening.",
                "processing_time_ms": processing_time_ms
            }

        # Case 3: Plate recognized, but unauthorized
        return {
            "timestamp": timestamp,
            "status": "ACCESS_DENIED",
            "action": "KEEP_CLOSED",
            "relay_signal": 0,
            "plate": detected_plate,
            "confidence": confidence,
            "owner": "Unknown / Unregistered",
            "role": "unauthorized",
            "region": plate_result.get("region_name"),
            "message": f"Access denied for plate {detected_plate}. Vehicle is not in the authorized whitelist.",
            "processing_time_ms": processing_time_ms
        }
