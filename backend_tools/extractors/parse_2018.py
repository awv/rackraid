# backend_tools/extractors/parse_2018.py
import re
import pdfplumber
import json
import os

STAGE_DISTANCES = {
    0: {"miles": 11.4, "km": 18.3, "name": "Llanthony to Grosmont"},
    1: {"miles": 5.1, "km": 8.2, "name": "Grosmont Castle to Skenfrith Castle"},
    2: {"miles": 6.93, "km": 11.2, "name": "Skenfrith Castle to White Castle"},
    3: {"miles": 7.51, "km": 12.1, "name": "White Castle to Abergavenny"},
    4: {"miles": 6.7, "km": 10.8, "name": "Abergavenny to Old Court Moat"},
    5: {"miles": 8.1, "km": 13.0, "name": "Old Court Moat to Monmouth"},
    6: {"miles": 12.6, "km": 20.3, "name": "Monmouth to Raglan"},
    7: {"miles": 5.53, "km": 8.9, "name": "Raglan to Usk"},
    8: {"miles": 13.1, "km": 21.1, "name": "Usk to Tintern Abbey"},
    9: {"miles": 9.42, "km": 15.2, "name": "Tintern Abbey to Chepstow Castle"},
    10: {"miles": 6.6, "km": 10.6, "name": "Chepstow Castle to Caldicot Castle"},
    11: {"miles": 8.3, "km": 13.4, "name": "Caldicot Castle to Penhow"},
    12: {"miles": 6.64, "km": 10.7, "name": "Penhow to Caerleon Amphitheatre"},
    13: {"miles": 5.43, "km": 8.7, "name": "Caerleon Amphitheatre to Castell-y-Bwch"},
    14: {"miles": 5.1, "km": 8.3, "name": "Castell-y-Bwch to Olive Tree"}
}

CLUB_KEYWORDS = [
    "parc", "lliswerry", "chepstow", "pont-y-pwl", "caerleon", "caerphilly", 
    "caldicot", "cdf", "griffithstown", "islwyn", "les", "croupiers", "monross", 
    "neath", "ogmore", "pontyclun", "pegasus", "pontypridd", "porthcawl", 
    "rhondda", "san", "domenico", "aberdare", "albany", "brackla", "builth", 
    "cornelly", "fairwater", "spirit", "monmouth", "independent", "unattached", "usk"
]

def extract_2018(pdf_path):
    results = []
    current_stage = 0
    time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2})')

    mappings = {}
    mapping_path = os.path.join(os.path.dirname(__file__), "..", "club_mappings.json")
    if os.path.exists(mapping_path):
        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                mappings = json.load(f)
        except Exception as e:
            print(f"-> Warning: Could not read club_mappings.json: {e}")

    print(f"-> Parsing stable digital text layer for 2018: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split('\n'):
                line = line.strip()
                if not line: 
                    continue

                stage_match = re.search(r'(?:LEG|Stage)\s*:?\s*(\d+)', line, re.IGNORECASE)
                if stage_match:
                    current_stage = int(stage_match.group(1))
                    continue

                if any(x in line.lower() for x in ["distance :", "result :", "total time after", "interval"]):
                    continue

                times = time_pattern.findall(line)
                if not times:
                    continue
                leg_time = times[0]

                parts = line.split(leg_time)
                right_side = parts[1].strip() if len(parts) > 1 else ""

                # Strip layout noise strings cleanly before tokenizer operations
                right_side = re.split(r'\s+\d{2}:\d{2}:\d{2}', right_side)[0].strip()
                right_side = re.split(r'\s+lead\s+', right_side, flags=re.IGNORECASE)[0].strip()
                right_side = re.sub(r'2018\s+RACK\s+RAID.*$', '', right_side, flags=re.IGNORECASE).strip()
                right_side = re.sub(r'See\s+us\s+on\s+facebook.*$', '', right_side, flags=re.IGNORECASE).strip()

                # Crop cumulative team standings column cleanly for Stage 1+
                if current_stage > 0:
                    right_side = re.split(r'\s+\d+\s+', right_side)[0].strip()

                tokens = right_side.split()
                if not tokens:
                    continue

                has_club_keyword = any(t.lower().replace("&", "").replace(".", "").strip() in CLUB_KEYWORDS for t in tokens)

                name_words = []
                club_words = []

                if has_club_keyword:
                    found_club = False
                    for token in tokens:
                        clean_token = token.lower().replace("&", "").replace(".", "").strip()
                        if token.isdigit():
                            continue
                        if clean_token in CLUB_KEYWORDS or found_club:
                            found_club = True
                            club_words.append(token)
                        else:
                            name_words.append(token)
                else:
                    name_words = tokens
                    club_words = []

                runner_name = " ".join(name_words).strip()
                runner_club = " ".join(club_words).strip() if club_words else "Independent"

                runner_name = re.sub(r'\s+\d+\s*$', '', runner_name).strip()
                runner_club = re.sub(r'\s+\d+\s+.*$', '', runner_club).strip()

                # Relax constraint to allow DNF entries and single-word names
                if not runner_name or runner_name.upper() == "NOTE":
                    continue

                if runner_club.isupper() and len(runner_club) > 3:
                    runner_club = runner_club.title()
                
                if runner_club.upper() == "CDF":
                    runner_club = "CDF"

                if runner_club.upper() in ["A", "B", "C", ""]:
                    runner_club = "Independent"

                runner_club_clean = runner_club.strip().lower()
                if runner_club_clean in mappings:
                    runner_club = mappings[runner_club_clean]

                if any(r["name"] == runner_name and r["stage"] == current_stage for r in results):
                    continue

                position = len([r for r in results if r["stage"] == current_stage]) + 1
                stage_meta = STAGE_DISTANCES.get(current_stage, {"miles": None, "km": None, "name": ""})

                results.append({
                    "year": 2018, 
                    "stage": current_stage, 
                    "stage_name": stage_meta["name"],
                    "miles": stage_meta["miles"], 
                    "km": stage_meta["km"],
                    "position": position, 
                    "name": runner_name, 
                    "club": runner_club, 
                    "time": leg_time
                })
                
    return results