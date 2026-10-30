import urllib.request
import urllib.parse
import json
import os

STREET_TITLES = [
    ("VW_Teramont_Almaty", "File:VW Teramont R-Line, Almaty (P1180145).jpg"),
    ("VW_Polo_Almaty", "File:VW Polo CK, Almaty (LRM 20240331 130451).jpg"),
    ("Geely_Emgrand_Astana", "File:Geely Emgrand, Astana (P1190778).jpg"),
    ("Tank_500_Astana", "File:Tank 500, Astana (P1190744).jpg"),
    ("Kia_K9_Astana", "File:Kia K9, Astana (P1190736).jpg"),
    ("Lada_Vesta_Almaty", "File:Алматы, Lada Vesta на Каримова.jpg"),
]

API_URL = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "SmartGateResearch/1.0 (academic; gate_system@edu.kz)"}

def download_street():
    os.makedirs("dataset/images", exist_ok=True)
    meta_path = "dataset/metadata.json"
    with open(meta_path, "r", encoding="utf-8") as f:
        meta = json.load(f)

    start_id = len(meta) + 1

    for key, title in STREET_TITLES:
        params = {
            "action": "query",
            "titles": title,
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "iiurlwidth": "1024",
            "format": "json"
        }
        req = urllib.request.Request(f"{API_URL}?{urllib.parse.urlencode(params)}", headers=HEADERS)
        try:
            resp = urllib.request.urlopen(req)
            data = json.loads(resp.read().decode())
            page = list(data.get("query", {}).get("pages", {}).values())[0]
            info = page["imageinfo"][0]
            thumb_url = info.get("thumburl", info.get("url"))
            filename = f"kz_plate_{start_id:02d}.jpg"
            filepath = os.path.join("dataset/images", filename)

            img_req = urllib.request.Request(thumb_url, headers=HEADERS)
            with urllib.request.urlopen(img_req) as img_resp, open(filepath, "wb") as f:
                f.write(img_resp.read())
            sz = os.path.getsize(filepath)
            print(f"[{start_id:02d}] Saved street car: {filename} ({sz} bytes) - {title}")

            meta.append({
                "id": start_id,
                "filename": filename,
                "filepath": filepath,
                "title": title,
                "url": thumb_url,
                "size_bytes": sz,
                "type": "street_scene"
            })
            start_id += 1
        except Exception as e:
            print(f"Failed to fetch {title}: {e}")

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    print(f"Total dataset count now: {len(meta)} images.")

if __name__ == "__main__":
    download_street()
