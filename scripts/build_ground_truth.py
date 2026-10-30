import json
import os

# Verified Ground Truth for all 50 Kazakhstani License Plate Images
GROUND_TRUTH_DATA = {
    1: {"plate": "235 CTO 48", "category": "transit_series", "notes": "Kazakh plate with CTO series"},
    2: {"plate": "D 001618", "category": "diplomatic", "notes": "1992 Diplomatic plate D 001618"},
    3: {"plate": "D 001618", "category": "diplomatic", "notes": "Diplomatic representation plate D 001618"},
    4: {"plate": "H 783497", "category": "foreign_resident", "notes": "Foreign resident yellow plate series H"},
    5: {"plate": "Z 313 ZZ", "category": "legal_entity", "notes": "Non-private vehicle plate series ZZ, Astana"},
    6: {"plate": "2573 AD", "category": "trailer", "notes": "Trailer plate series AD"},
    7: {"plate": "H 1301 10", "category": "foreign_company", "notes": "2012 Foreign company plate, region 10 (Kostanay)"},
    8: {"plate": "42 GHA 10", "category": "trailer", "notes": "2012 Trailer plate, region 10 (Kostanay)"},
    9: {"plate": "237 BLM 01", "category": "standard_two_line", "notes": "2012 Two-row rear plate, region 01 (Astana)"},
    10: {"plate": "A 912 NZ", "category": "pre2012_company", "notes": "Pre-2012 company plate, Almaty (A)"},
    11: {"plate": "237 LM 01", "category": "legal_entity_two_line", "notes": "2012 Company two-row plate, region 01 (Astana)"},
    12: {"plate": "H 0105 02", "category": "foreign_company", "notes": "2012 Foreign company plate, region 02 (Almaty)"},
    13: {"plate": "660 X 02", "category": "trailer", "notes": "Trailer plate series X, region 02"},
    14: {"plate": "D 912 NZM", "category": "pre2012_square", "notes": "1993 private square plate, D (Aktobe)"},
    15: {"plate": "237 LM 01", "category": "legal_entity", "notes": "2012 Public/legal entity plate, region 01"},
    16: {"plate": "4330 AV", "category": "motorcycle", "notes": "1993 Motorcycle plate series AV"},
    17: {"plate": "2401 KB 01", "category": "motorcycle", "notes": "2012 Motorcycle plate, region 01"},
    18: {"plate": "F 0478 01", "category": "non_resident_two_line", "notes": "2012 Non-resident two-row plate, region 01"},
    19: {"plate": "F 0277 02", "category": "non_resident", "notes": "2012 Non-resident plate, region 02 (Almaty)"},
    20: {"plate": "E 419 KLM", "category": "pre2012_standard", "notes": "Pre-2012 plate, E (Atyrau Region)"},
    21: {"plate": "0007 AA", "category": "defense", "notes": "Defense / military plate series AA"},
    22: {"plate": "E 146 KP", "category": "police", "notes": "Police patrol vehicle plate"},
    23: {"plate": "2401 AC 01", "category": "trailer", "notes": "2012 Trailer plate, region 01"},
    24: {"plate": "110391 AN", "category": "transit", "notes": "2012 Transit plate series AN"},
    25: {"plate": "2971 ACE 02", "category": "standard_two_line", "notes": "2012 Two-line plate, region 02 (Almaty)"},
    26: {"plate": "143 ABA 12", "category": "standard_2012", "notes": "2012 Standard plate, region 12 (Mangystau)"},
    27: {"plate": "8621 MK", "category": "trailer", "notes": "Trailer truck plate series MK"},
    28: {"plate": "A 553 ZYM", "category": "pre2012_standard", "notes": "Pre-2012 plate, A (Almaty city)"},
    29: {"plate": "A 553 ZYM", "category": "pre2012_standard", "notes": "Pre-2012 plate graphic, A (Almaty city)"},
    30: {"plate": "429 HUA 12", "category": "standard_2012", "notes": "2012 Standard plate, region 12 (Mangystau)"},
    31: {"plate": "237 BLM 01", "category": "standard_2012", "notes": "2012 Standard plate, region 01 (Astana)"},
    32: {"plate": "A 123 ABC", "category": "pre2012_standard", "notes": "Pre-2012 specimen plate"},
    33: {"plate": "A 001 KAZ", "category": "special", "notes": "Specimen A-001-KAZ"},
    34: {"plate": "H 797 BVM", "category": "pre2012_standard", "notes": "Pre-2012 plate, H (Zhambyl region)"},
    35: {"plate": "M 796 BPN", "category": "pre2012_standard", "notes": "Pre-2012 plate, M (Karaganda region)"},
    36: {"plate": "P 022 SHM", "category": "pre2012_standard", "notes": "Pre-2012 plate, P (North Kazakhstan)"},
    37: {"plate": "A 882 ADP", "category": "pre2012_standard", "notes": "Pre-2012 plate, A (Almaty city)"},
    38: {"plate": "R 575 KMM", "category": "pre2012_standard", "notes": "Pre-2012 plate, R (Mangystau)"},
    39: {"plate": "B 253 YON", "category": "pre2012_standard", "notes": "Pre-2012 plate, B (Almaty Region)"},
    40: {"plate": "N 803 BB", "category": "pre2012_company", "notes": "Pre-2012 corporate plate, N (Kyzylorda)"},
    41: {"plate": "X 763 CD", "category": "pre2012_company", "notes": "Pre-2012 corporate plate, X (South Kazakhstan)"},
    42: {"plate": "Z 313 ZZ", "category": "pre2012_company", "notes": "Pre-2012 corporate plate, Z (Astana)"},
    43: {"plate": "A 204 AK", "category": "pre2012_company", "notes": "Pre-2012 corporate plate, A (Almaty city)"},
    44: {"plate": "455 AST", "category": "special_ast", "notes": "Special AST series plate"},
    45: {"plate": "047 PFA 02", "category": "street_vehicle", "notes": "VW Teramont R-Line, Almaty region 02"},
    46: {"plate": "771 DLA 02", "category": "street_vehicle", "notes": "VW Polo, Almaty region 02"},
    47: {"plate": "342 AOH 01", "category": "street_vehicle", "notes": "Geely Emgrand, Astana region 01"},
    48: {"plate": "848 TTA 01", "category": "street_vehicle", "notes": "Tank 500, Astana region 01"},
    49: {"plate": "107 AES 10", "category": "street_vehicle", "notes": "Kia K9, Kostanay region 10"},
    50: {"plate": "416 AEP 02", "category": "street_vehicle", "notes": "Lada Vesta, Almaty region 02"},
}

def create_ground_truth():
    meta_path = "dataset/metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    annotated = []
    for item in meta:
        iid = item["id"]
        gt = GROUND_TRUTH_DATA.get(iid, {
            "plate": "UNKNOWN",
            "category": "unknown",
            "notes": "No ground truth specified"
        })
        merged = {**item, **gt}
        annotated.append(merged)

    gt_file = "dataset/ground_truth.json"
    with open(gt_file, "w", encoding="utf-8") as f:
        json.dump(annotated, f, indent=2, ensure_ascii=False)

    print(f"Created {gt_file} with {len(annotated)} verified annotations.")

if __name__ == "__main__":
    create_ground_truth()
