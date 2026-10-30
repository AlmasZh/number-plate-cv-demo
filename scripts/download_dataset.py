import urllib.request
import urllib.parse
import json
import os
import sys

TITLES = [
    "File:Казахстанский автомобильный номер выданный на физическое лицо - Е.JPG",
    "File:235CTOm48 k.jpg",
    "File:Diplomatic license plate 1992 Kazakhstan D 001618.jpg",
    "File:Diplomatic license plates of Kazakhstan, диппредставительства в Казахстан.jpg",
    "File:Kazakh license plate for foreigners.JPG",
    "File:Kazakh license plate for non-private vehicles.png",
    "File:Kazakh license plate for trailers.png",
    "File:Kazakhstan (foreign company) license plate 2012.jpg",
    "File:Kazakhstan (trailer) license plate 2012.jpg",
    "File:Kazakhstan automobile license plate 2012 (rear).jpg",
    "File:Kazakhstan company license plate (old).png",
    "File:Kazakhstan company license plate 2012.png",
    "File:Kazakhstan foreign company license plate 2012.png",
    "File:Kazakhstan foreign joint venture license plate 2026.jpg",
    "File:Kazakhstan license plate 1993 privat square.jpg",
    "File:Kazakhstan license plate 2012 public.jpg",
    "File:Kazakhstan motorcycle license plate 1993.jpg",
    "File:Kazakhstan motorcycle license plate 2012.png",
    "File:Kazakhstan non-resident license plate 2012 (back).png",
    "File:Kazakhstan non-resident license plate 2012.png",
    "File:Kazakhstan Police license plate E-146-KP.jpg",
    "File:Kazakhstan trailer license plate 2012.png",
    "File:Kazakhstan transit license plate 2012.png",
    "File:KZDefenseLicensePlate.JPG",
    "File:License plate Kazakhstan 2012 two line.png",
    "File:License plate Kazakhstan 2012.png",
    "File:License plate Kazakhstan trailer truck.JPG",
    "File:License plate Kazakhstan.jpg",
    "File:License plate Kazakhstan.png",
    "File:License plate of Kazakhstan.jpg",
    "File:Pelake jadide qazaq.jpg",
    "File:Registration plates of Kazakhstan (PC).JPG",
    "File:Казахстан Номерной знак - A-001-KAZ.jpg",
    "File:Казахстанский автомобильный номер выданный на физическое лицо - H.JPG",
    "File:Казахстанский автомобильный номер выданный на физическое лицо - M.JPG",
    "File:Казахстанский автомобильный номер выданный на физическое лицо - P.JPG",
    "File:Казахстанский автомобильный номер выданный на физическое лицо с окончанием серии на О.JPG",
    "File:Казахстанский автомобильный номер выданный на физическое лицо.jpg",
    "File:Казахстанский автомобильный номер выданный на юридическое лицо - B.JPG",
    "File:Казахстанский автомобильный номер выданный на юридическое лицо - N.JPG",
    "File:Казахстанский автомобильный номер выданный на юридическое лицо - X..JPG",
    "File:Казахстанский автомобильный номер выданный на юридическое лицо - Z..JPG",
    "File:Казахстанский автомобильный номер выданный на юридическое лицо.JPG",
    "File:Казахстанский номер серии AST.JPG",
]

API_URL = "https://commons.wikimedia.org/w/api.php"
HEADERS = {"User-Agent": "SmartGateResearch/1.0 (academic; gate_system@edu.kz)"}

def download_dataset():
    os.makedirs("dataset/images", exist_ok=True)
    metadata = []
    count = 1

    for i in range(0, len(TITLES), 20):
        batch = TITLES[i:i+20]
        params = {
            "action": "query",
            "titles": "|".join(batch),
            "prop": "imageinfo",
            "iiprop": "url|size|mime",
            "format": "json"
        }
        req = urllib.request.Request(f"{API_URL}?{urllib.parse.urlencode(params)}", headers=HEADERS)
        try:
            resp = urllib.request.urlopen(req)
            data = json.loads(resp.read().decode())
        except Exception as e:
            print(f"Failed to query batch {i}: {e}")
            continue

        pages = data.get("query", {}).get("pages", {})
        for pid, pdata in sorted(pages.items(), key=lambda x: x[1].get("title", "")):
            if "imageinfo" in pdata and pdata["imageinfo"]:
                info = pdata["imageinfo"][0]
                url = info["url"]
                parsed_ext = os.path.splitext(urllib.parse.urlparse(url).path)[1].lower()
                if not parsed_ext or parsed_ext not in [".jpg", ".jpeg", ".png", ".gif"]:
                    parsed_ext = ".jpg"
                filename = f"kz_plate_{count:02d}{parsed_ext}"
                filepath = os.path.join("dataset/images", filename)
                try:
                    img_req = urllib.request.Request(url, headers=HEADERS)
                    with urllib.request.urlopen(img_req) as img_resp, open(filepath, "wb") as f:
                        f.write(img_resp.read())
                    sz = os.path.getsize(filepath)
                    title = pdata.get("title", "")
                    metadata.append({
                        "id": count,
                        "filename": filename,
                        "filepath": filepath,
                        "title": title,
                        "url": url,
                        "size_bytes": sz
                    })
                    print(f"[{count:02d}] Saved {filename} ({sz} bytes) - {title}")
                    count += 1
                except Exception as e:
                    print(f"Failed to download {pdata.get('title')}: {e}")

    meta_file = "dataset/metadata.json"
    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nSuccessfully downloaded {len(metadata)} license plate images to dataset/images/")

if __name__ == "__main__":
    download_dataset()
