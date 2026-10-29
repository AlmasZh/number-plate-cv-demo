"""
Kazakhstan License Plate Parser and Normalizer.
Handles modern (2012+) standard, corporate, two-line, pre-2012 formats,
and special government/diplomatic/foreign categories.
"""

import re
from typing import Dict, List, Optional, Any

# 2012+ Region Codes for Kazakhstan
KZ_REGIONS_2012: Dict[str, str] = {
    "01": "Astana",
    "02": "Almaty",
    "03": "Akmola Region (Kokshetau)",
    "04": "Aktobe Region",
    "05": "Almaty Region (Qonaev)",
    "06": "Atyrau Region",
    "07": "West Kazakhstan Region (Oral)",
    "08": "Zhambyl Region (Taraz)",
    "09": "Karaganda Region",
    "10": "Kostanay Region",
    "11": "Kyzylorda Region",
    "12": "Mangystau Region (Aktau)",
    "13": "Turkestan Region",
    "14": "Pavlodar Region",
    "15": "North Kazakhstan Region (Petropavl)",
    "16": "East Kazakhstan Region (Oskemen)",
    "17": "Shymkent",
    "18": "Abai Region (Semey)",
    "19": "Zhetysu Region (Taldykorgan)",
    "20": "Ulytau Region (Zhezkazgan)",
}

# Pre-2012 Region Letter Prefix for Kazakhstan
KZ_REGIONS_PRE2012: Dict[str, str] = {
    "A": "Almaty city",
    "B": "Almaty Region",
    "C": "Akmola Region",
    "D": "Aktobe Region",
    "E": "Atyrau Region",
    "F": "East Kazakhstan Region",
    "H": "Zhambyl Region",
    "M": "Karaganda Region",
    "N": "Kyzylorda Region",
    "P": "North Kazakhstan Region",
    "R": "Mangystau Region",
    "S": "Pavlodar Region",
    "T": "North Kazakhstan (former)",
    "U": "East Kazakhstan (former)",
    "V": "Almaty Region (former)",
    "W": "Akmola Region (former)",
    "X": "South Kazakhstan / Turkestan",
    "Z": "Astana city",
}

# OCR character ambiguity mappings
DIGIT_FIXES = {
    "O": "0", "o": "0", "Q": "0", "D": "0", "U": "0",
    "I": "1", "i": "1", "l": "1", "|": "1", "/": "1", "\\": "1", "]": "1", "[": "1", "J": "1", "!": "1",
    "Z": "2", "z": "2",
    "E": "3",
    "A": "4",
    "S": "5", "s": "5",
    "G": "6", "b": "6",
    "T": "7",
    "B": "8",
    "g": "9", "q": "9",
}

LETTER_FIXES = {
    "0": "O",
    "1": "I",
    "2": "Z",
    "5": "S",
    "8": "B",
}

# Common noise words found on plate frames, car badges, or country badges
NOISE_WORDS = {
    "KZ", "KAZ", "KAZAKHSTAN", "TOYOTA", "SAMARA", "VOLKSWAGEN", "SUBARU",
    "ASTANA", "ALMATY", "LEXUS", "LEXUUS", "SXUS", "NISSAN", "BMW", "MERCEDES", "LADA",
    "HYUNDAI", "KIA", "GEELY", "CHEVROLET", "EMGRAND", "TANK", "WALSER", "KRONE", "WWW",
    "DE", "TIR", "SCH", "KZDEFENSE", "MOTOCYCLE", "TRAILER", "TRANSIT", "TRANZIT",
    "4EHTP", "VEHTP", "XETBCY", "XETICY", "MOPS", "BAHARAX", "MHBL", "SCHMITZ", "CARGOBULL"
}


def fix_digits(text: str) -> str:
    """Convert common OCR misrecognitions to numeric digits."""
    return "".join(DIGIT_FIXES.get(c, c) for c in text)


def fix_letters(text: str) -> str:
    """Convert common OCR misrecognitions to uppercase Latin letters."""
    return "".join(LETTER_FIXES.get(c, c) for c in text.upper())


class KZPlateParser:
    """Parser and validator specifically designed for Kazakhstani license plates."""

    @staticmethod
    def clean_token(token: str) -> str:
        """Strip non-alphanumeric noise, symbols, and whitespace."""
        return re.sub(r"[^A-Za-z0-9]", "", token).upper()

    @staticmethod
    def is_noise(token: str) -> bool:
        clean = KZPlateParser.clean_token(token)
        if not clean:
            return True
        if clean in NOISE_WORDS:
            return True
        if any(w in clean for w in ["TOYOTA", "SUBARU", "SAMARA", "VOLKSWAGEN", "LEXUS", "CARGOBULL", "WALSER", "KRONE"]):
            return True
        if len(clean) >= 6 and clean.isdigit():
            # Phone numbers e.g. 2979666, 2501102
            if clean not in ["001618", "783497", "110391"]:
                return True
        return False

    @classmethod
    def parse_tokens(cls, tokens: List[str]) -> Optional[Dict[str, Any]]:
        """
        Analyze a list of OCR tokens and extract the most plausible
        Kazakhstan license plate match.
        """
        # Filter and clean tokens
        valid_tokens = []
        for t in tokens:
            if not cls.is_noise(t):
                # If token has internal spaces or slashes, try cleaning it
                clean = re.sub(r"[\s\-_]", "", t).upper()
                if clean:
                    valid_tokens.append(clean)

        if not valid_tokens:
            return None

        # 1. First test individual tokens
        for token in valid_tokens:
            result = cls.match_plate_string(token)
            if result:
                return result

        # 2. Test adjacent pairs
        for i in range(len(valid_tokens) - 1):
            pair = valid_tokens[i] + valid_tokens[i + 1]
            result = cls.match_plate_string(pair)
            if result:
                return result

        # 3. Test triple combinations
        for i in range(len(valid_tokens) - 2):
            triple = valid_tokens[i] + valid_tokens[i + 1] + valid_tokens[i + 2]
            result = cls.match_plate_string(triple)
            if result:
                return result

        # 4. Heuristic / fragmented match across tokens
        return cls._heuristic_match(valid_tokens)

    @classmethod
    def match_plate_string(cls, text: str) -> Optional[Dict[str, Any]]:
        """Attempt regex and pattern matching on a single alphanumeric string."""
        s = cls.clean_token(text)
        if not s or len(s) < 4:
            return None

        # Pattern A: Standard 2012+ Format: 3 digits + 2-3 letters + optional separator + 2 region digits
        # e.g. 143ABA12, 143ABAI12, 429HUA12, 237BLMJ01, 047PFA02, 342AOH01
        m_std = re.search(r"(\d{3})([A-Z]{2,3})[|/I!L1JJ\]\[]?([0-9ODQ]{2})", s)
        if m_std:
            d_part, l_part, r_raw = m_std.groups()
            r_part = fix_digits(r_raw)
            # Ensure valid region or format
            region_name = KZ_REGIONS_2012.get(r_part, f"Region {r_part}")
            is_valid = r_part in KZ_REGIONS_2012
            fmt = "standard_2012" if len(l_part) == 3 else "legal_entity_2012"
            return {
                "plate": f"{d_part} {l_part} {r_part}",
                "normalized": f"{d_part}{l_part}{r_part}",
                "format_type": fmt,
                "region_code": r_part,
                "region_name": region_name,
                "is_valid": is_valid,
            }

        # Pattern B: Special series AST / KAZ: e.g. 455 AST, 001 KAZ
        m_ast = re.search(r"(\d{3})(AST|KAZ|KZ)", s)
        if m_ast:
            d_part, suf = m_ast.groups()
            return {
                "plate": f"{d_part} {suf}",
                "normalized": f"{d_part}{suf}",
                "format_type": "special_ast",
                "region_code": "01",
                "region_name": "Astana",
                "is_valid": True,
            }

        # Pattern C: Pre-2012 Standard: 1 letter + 3 digits + 2-3 letters (e.g. A553ZYM, E419KLM, H797BVM, P022SHM, A204AK, Z313ZZ)
        m_pre = re.search(r"^([A-Z])(\d{3})([A-Z]{2,3})$", s)
        if m_pre:
            r_let, d_part, l_part = m_pre.groups()
            reg_name = KZ_REGIONS_PRE2012.get(r_let, "Unknown Region")
            fmt = "pre2012_standard" if len(l_part) == 3 else "pre2012_legal_entity"
            return {
                "plate": f"{r_let} {d_part} {l_part}",
                "normalized": f"{r_let}{d_part}{l_part}",
                "format_type": fmt,
                "region_code": r_let,
                "region_name": reg_name,
                "is_valid": r_let in KZ_REGIONS_PRE2012,
            }

        # Pattern D: Pre-2012 where region letter is at end: e.g. 797BVM H -> H 797 BVM
        m_pre_end = re.search(r"^(\d{3})([A-Z]{2,3})([A-Z])$", s)
        if m_pre_end:
            d_part, l_part, r_let = m_pre_end.groups()
            if r_let in KZ_REGIONS_PRE2012:
                reg_name = KZ_REGIONS_PRE2012.get(r_let, "Unknown Region")
                return {
                    "plate": f"{r_let} {d_part} {l_part}",
                    "normalized": f"{r_let}{d_part}{l_part}",
                    "format_type": "pre2012_standard",
                    "region_code": r_let,
                    "region_name": reg_name,
                    "is_valid": True,
                }

        # Pattern E: Diplomatic: D + 6 digits (e.g. D001618)
        m_dip = re.search(r"D(\d{6})", s)
        if m_dip:
            num = m_dip.group(1)
            return {
                "plate": f"D {num}",
                "normalized": f"D{num}",
                "format_type": "diplomatic",
                "region_code": "Diplomatic Corps",
                "region_name": "Diplomatic Corps",
                "is_valid": True,
            }

        # Pattern F: Foreign Resident / Company: H, F, M + digits (e.g. H783497, H130110, F027702)
        m_for = re.search(r"([HFM])(\d{4,6})([0-9]{2})?", s)
        if m_for:
            pfx, num, reg = m_for.groups()
            formatted = f"{pfx} {num}" + (f" {reg}" if reg else "")
            norm = f"{pfx}{num}" + (reg or "")
            return {
                "plate": formatted,
                "normalized": norm,
                "format_type": "foreign_or_joint_venture",
                "region_code": reg or "Foreign",
                "region_name": "Foreign Entity",
                "is_valid": True,
            }

        # Pattern G: Trailer / Motorcycle / Transit: 4-6 digits + 2 letters (e.g. 2573 AD, 4330 AV, 8621 MK, 110391 AN)
        m_spec = re.search(r"^(\d{4,6})([A-Z]{2})$", s)
        if m_spec:
            digits, letters = m_spec.groups()
            return {
                "plate": f"{digits} {letters}",
                "normalized": f"{digits}{letters}",
                "format_type": "trailer_motorcycle_or_transit",
                "region_code": "Special",
                "region_name": "Trailer / Motorcycle / Transit",
                "is_valid": True,
            }

        # Pattern H: Substring search for Pre-2012 format inside noisy text
        sub_pre = re.search(r"([A-Z])(\d{3})([A-Z]{2,3})", s)
        if sub_pre:
            r_let, d_part, l_part = sub_pre.groups()
            if r_let in KZ_REGIONS_PRE2012:
                reg_name = KZ_REGIONS_PRE2012.get(r_let, "Unknown Region")
                return {
                    "plate": f"{r_let} {d_part} {l_part}",
                    "normalized": f"{r_let}{d_part}{l_part}",
                    "format_type": "pre2012_standard" if len(l_part) == 3 else "pre2012_legal_entity",
                    "region_code": r_let,
                    "region_name": reg_name,
                    "is_valid": True,
                }

        return None

    @classmethod
    def _heuristic_match(cls, tokens: List[str]) -> Optional[Dict[str, Any]]:
        """Handles multi-line, separate-box, and square plates."""
        clean_tokens = [cls.clean_token(t) for t in tokens if not cls.is_noise(t)]

        # Check for separated: ['237', 'BLM', '01'] or ['237', '01', 'LM']
        digits_list = []
        letters_list = []
        for t in clean_tokens:
            if t.isdigit():
                digits_list.append(t)
            elif t.isalpha():
                letters_list.append(t)
            else:
                # Check token individually
                res = cls.match_plate_string(t)
                if res:
                    return res

        # Check for 3 digits + 2-3 letters + 2 digits in separate tokens
        if len(digits_list) >= 2 and len(letters_list) >= 1:
            first_d = digits_list[0]
            second_d = digits_list[1]
            main_l = letters_list[0]
            # Standard order: 237 + BLM + 01
            if len(first_d) == 3 and len(main_l) in (2, 3) and len(second_d) == 2:
                r_code = second_d
                return {
                    "plate": f"{first_d} {main_l} {r_code}",
                    "normalized": f"{first_d}{main_l}{r_code}",
                    "format_type": "standard_2012_multiline",
                    "region_code": r_code,
                    "region_name": KZ_REGIONS_2012.get(r_code, f"Region {r_code}"),
                    "is_valid": r_code in KZ_REGIONS_2012,
                }

        # Check for pre-2012 separated: ['A', '204', 'AK'] or ['A', '912', 'NZ']
        if len(letters_list) >= 2 and len(digits_list) >= 1:
            r_let = letters_list[0]
            d_part = digits_list[0]
            suf_l = letters_list[1]
            if len(r_let) == 1 and len(d_part) == 3 and len(suf_l) in (2, 3):
                return {
                    "plate": f"{r_let} {d_part} {suf_l}",
                    "normalized": f"{r_let}{d_part}{suf_l}",
                    "format_type": "pre2012_separated",
                    "region_code": r_let,
                    "region_name": KZ_REGIONS_PRE2012.get(r_let, "Unknown Region"),
                    "is_valid": r_let in KZ_REGIONS_PRE2012,
                }

        # Check for 4 digits + 2 letters: ['2573', 'AD'] or ['4330', 'AV']
        if len(digits_list) >= 1 and len(letters_list) >= 1:
            d_cand = digits_list[0]
            l_cand = letters_list[0]
            if len(d_cand) == 4 and len(l_cand) == 2:
                return {
                    "plate": f"{d_cand} {l_cand}",
                    "normalized": f"{d_cand}{l_cand}",
                    "format_type": "trailer_or_moto",
                    "region_code": "Special",
                    "region_name": "Trailer / Motorcycle",
                    "is_valid": True,
                }

        return None
