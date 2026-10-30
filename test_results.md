# Smart Gate Automation - Computer Vision Test Report

## Overview
- **Project:** IoT-Based Smart Gate Automation System Integrating Computer Vision and GPS Location
- **Target Environment:** Raspberry Pi / Smart Home Edge Controller
- **Stack:** Python, OpenCV, EasyOCR, Kazakhstani Plate Grammar Rules

## Key Performance Indicators
| Metric | Result |
|---|---|
| **Total Example Images Tested** | **50** |
| **Detection Rate** | **76.0%** (38/50) |
| **Exact Match Rate** | **54.0%** (27/50) |
| **Effective Accuracy (Exact + Partial)** | **60.0%** (30/50) |
| **Average Inference Time (CPU)** | **822.8 ms** |

## Image-by-Image Test Log
| ID | Image | Ground Truth | Detected | Region | Gate Status | Match | Latency (ms) |
|---|---|---|---|---|---|---|---|
| 1 | `kz_plate_01.jpg` | `235 CTO 48` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 274.4 |
| 2 | `kz_plate_02.jpg` | `D 001618` | `D 001618` | Diplomatic Corps | `ACCESS_DENIED` | **PASS** | 664.8 |
| 3 | `kz_plate_03.jpg` | `D 001618` | `D 001618` | Diplomatic Corps | `ACCESS_DENIED` | **PASS** | 1953.7 |
| 4 | `kz_plate_04.jpg` | `H 783497` | `H 783497` | Foreign Entity | `ACCESS_DENIED` | **PASS** | 656.0 |
| 5 | `kz_plate_05.png` | `Z 313 ZZ` | `2313 ZZ` | Trailer / Motorcycle / Transit | `ACCESS_DENIED` | **DIFF** | 163.6 |
| 6 | `kz_plate_06.png` | `2573 AD` | `2573 AD` | Trailer / Motorcycle / Transit | `ACCESS_DENIED` | **PASS** | 52.5 |
| 7 | `kz_plate_07.jpg` | `H 1301 10` | `H 1301` | Foreign Entity | `ACCESS_DENIED` | **PARTIAL** | 643.9 |
| 8 | `kz_plate_08.jpg` | `42 GHA 10` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 1051.6 |
| 9 | `kz_plate_09.jpg` | `237 BLM 01` | `237 BLM 01` | Astana | `ACCESS_GRANTED` | **PASS** | 93.4 |
| 10 | `kz_plate_10.png` | `A 912 NZ` | `A 912 NZ` | Almaty city | `ACCESS_DENIED` | **PASS** | 111.9 |
| 11 | `kz_plate_11.png` | `237 LM 01` | `23701 LM` | Trailer / Motorcycle / Transit | `ACCESS_DENIED` | **DIFF** | 108.0 |
| 12 | `kz_plate_12.png` | `H 0105 02` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 106.9 |
| 13 | `kz_plate_13.jpg` | `660 X 02` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 1110.1 |
| 14 | `kz_plate_14.jpg` | `D 912 NZM` | `D 912 NZM` | Aktobe Region | `ACCESS_DENIED` | **PASS** | 118.1 |
| 15 | `kz_plate_15.jpg` | `237 LM 01` | `237 LM 01` | Astana | `ACCESS_DENIED` | **PASS** | 162.4 |
| 16 | `kz_plate_16.jpg` | `4330 AV` | `4330 AV` | Trailer / Motorcycle / Transit | `ACCESS_DENIED` | **PASS** | 56.3 |
| 17 | `kz_plate_17.png` | `2401 KB 01` | `2401 KB` | Trailer / Motorcycle / Transit | `ACCESS_DENIED` | **PARTIAL** | 83.0 |
| 18 | `kz_plate_18.png` | `F 0478 01` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 112.4 |
| 19 | `kz_plate_19.png` | `F 0277 02` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 258.6 |
| 20 | `kz_plate_20.jpg` | `E 419 KLM` | `E 419 KLM` | Atyrau Region | `ACCESS_GRANTED` | **PASS** | 570.0 |
| 21 | `kz_plate_21.jpg` | `0007 AA` | `0007 AA` | Trailer / Motorcycle / Transit | `ACCESS_DENIED` | **PASS** | 593.1 |
| 22 | `kz_plate_22.jpg` | `E 146 KP` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 168.4 |
| 23 | `kz_plate_23.png` | `2401 AC 01` | `M 0124` | Foreign Entity | `ACCESS_DENIED` | **DIFF** | 64.4 |
| 24 | `kz_plate_24.png` | `110391 AN` | `11039 AN` | Trailer / Motorcycle / Transit | `ACCESS_DENIED` | **DIFF** | 77.8 |
| 25 | `kz_plate_25.png` | `2971 ACE 02` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 96.5 |
| 26 | `kz_plate_26.png` | `143 ABA 12` | `143 ABA 12` | Mangystau Region (Aktau) | `ACCESS_GRANTED` | **PASS** | 126.8 |
| 27 | `kz_plate_27.jpg` | `8621 MK` | `8621 MK` | Trailer / Motorcycle / Transit | `ACCESS_DENIED` | **PASS** | 149.7 |
| 28 | `kz_plate_28.jpg` | `A 553 ZYM` | `A 553 ZYM` | Almaty city | `ACCESS_GRANTED` | **PASS** | 723.0 |
| 29 | `kz_plate_29.png` | `A 553 ZYM` | `A 553 ZYM` | Almaty city | `ACCESS_GRANTED` | **PASS** | 203.2 |
| 30 | `kz_plate_30.jpg` | `429 HUA 12` | `429 HUA 12` | Mangystau Region (Aktau) | `ACCESS_DENIED` | **PASS** | 591.7 |
| 31 | `kz_plate_31.jpg` | `237 BLM 01` | `237 BLM 01` | Astana | `ACCESS_GRANTED` | **PASS** | 85.2 |
| 32 | `kz_plate_32.jpg` | `A 123 ABC` | `C 123 AB` | Akmola Region | `ACCESS_DENIED` | **DIFF** | 309.1 |
| 33 | `kz_plate_33.jpg` | `A 001 KAZ` | `001 KAZ` | Astana | `ACCESS_DENIED` | **PARTIAL** | 106.4 |
| 34 | `kz_plate_34.jpg` | `H 797 BVM` | `H 797 BVM` | Zhambyl Region | `ACCESS_DENIED` | **PASS** | 574.3 |
| 35 | `kz_plate_35.jpg` | `M 796 BPN` | `M 796 BPN` | Karaganda Region | `ACCESS_DENIED` | **PASS** | 875.5 |
| 36 | `kz_plate_36.jpg` | `P 022 SHM` | `P 022 SHM` | North Kazakhstan Region | `ACCESS_DENIED` | **PASS** | 942.8 |
| 37 | `kz_plate_37.jpg` | `A 882 ADP` | `A 882 ADP` | Almaty city | `ACCESS_DENIED` | **PASS** | 603.5 |
| 38 | `kz_plate_38.jpg` | `R 575 KMM` | `R 575 KMM` | Mangystau Region | `ACCESS_DENIED` | **PASS** | 974.7 |
| 39 | `kz_plate_39.jpg` | `B 253 YON` | `B 253 YON` | Almaty Region | `ACCESS_DENIED` | **PASS** | 1073.1 |
| 40 | `kz_plate_40.jpg` | `N 803 BB` | `N 803 BB` | Kyzylorda Region | `ACCESS_DENIED` | **PASS** | 869.4 |
| 41 | `kz_plate_41.jpg` | `X 763 CD` | `X 763 CD` | South Kazakhstan / Turkestan | `ACCESS_DENIED` | **PASS** | 601.9 |
| 42 | `kz_plate_42.jpg` | `Z 313 ZZ` | `2313 ZZ` | Trailer / Motorcycle / Transit | `ACCESS_DENIED` | **DIFF** | 657.2 |
| 43 | `kz_plate_43.jpg` | `A 204 AK` | `A 204 AK` | Almaty city | `ACCESS_DENIED` | **PASS** | 990.1 |
| 44 | `kz_plate_44.jpg` | `455 AST` | `455 AST` | Astana | `ACCESS_DENIED` | **PASS** | 773.5 |
| 45 | `kz_plate_45.jpg` | `047 PFA 02` | `R 414 HE` | Mangystau Region | `ACCESS_DENIED` | **DIFF** | 2324.0 |
| 46 | `kz_plate_46.jpg` | `771 DLA 02` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 4121.7 |
| 47 | `kz_plate_47.jpg` | `342 AOH 01` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 3621.9 |
| 48 | `kz_plate_48.jpg` | `848 TTA 01` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 4798.0 |
| 49 | `kz_plate_49.jpg` | `107 AES 10` | `107 AES 01` | Astana | `ACCESS_DENIED` | **DIFF** | 2102.6 |
| 50 | `kz_plate_50.jpg` | `416 AEP 02` | `NOT_FOUND` | - | `NO_PLATE_DETECTED` | **FAIL** | 3587.7 |
