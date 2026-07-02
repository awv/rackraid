# backend_tools/extractors/parse_2023.py
import re
from pdf2image import convert_from_path
import pytesseract

STAGE_DISTANCES = {
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
    13: {"miles": 5.43, "km": 8.7, "name": "Caerleon Amphitheatre to Castell-y-Bwch"}
}

def extract_2023(pdf_path):
    results = []
    current_stage = 1
    time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2})')

    print(f"-> Converting and line-parsing 2023 dataset from: {pdf_path}")
    pages = convert_from_path(pdf_path, dpi=200)

    for page_num, page_img in enumerate(pages, 1):
        page_text = pytesseract.image_to_string(page_img, config='--psm 6') or ""
        lines = page_text.split('\n')

        for line in lines:
            clean_line = line.strip()
            if not clean_line:
                continue

            if any(x in clean_line.lower() for x in ["www.", "total time", "after leg", "course record", "cut off", "number of teams"]):
                continue

            stage_match = re.search(r'(?:RESULT\s*:?\s*LEG|LEG|Leg|Stage)\s*:?\s*(\d+)', clean_line, re.IGNORECASE)
            if stage_match:
                current_stage = int(stage_match.group(1))
                continue

            times = time_pattern.findall(clean_line)
            if not times:
                continue
            leg_time = times[0]

            # --- INVERTED LAYOUT (Page 1 / Stage 1) ---
            if "|" in clean_line and clean_line.index("|") > len(clean_line) * 0.3:
                left_side, right_side = clean_line.split("|", 1)
                
                pos_match = re.search(r'(\d+)\s*$', left_side.strip())
                if not pos_match:
                    continue
                position = int(pos_match.group(1))

                parts = right_side.split(leg_time)
                content = parts[1].strip() if len(parts) > 1 else parts[0].strip()
                content = re.sub(r'\d{1,2}:\d{2}:\d{2}.*$', '', content).strip()
                content = re.sub(r'[\=\|\.\,\-\_\+]', '', content).strip()
                
                tokens = content.split()
                if len(tokens) >= 2:
                    if tokens[0].isupper() and tokens[1].isupper() and not tokens[0].isdigit():
                        club_words = []
                        runner_words = []
                        for t in tokens:
                            if t.isupper() and len(runner_words) == 0:
                                club_words.append(t)
                            else:
                                runner_words.append(t)
                        runner_club = " ".join(club_words).strip()
                        runner_name = " ".join(runner_words).strip()
                    else:
                        runner_name = f"{tokens[0]} {tokens[1]}"
                        runner_club = " ".join(tokens[2:]).strip()

                    stage_meta = STAGE_DISTANCES.get(current_stage, {"miles": None, "km": None, "name": ""})
                    results.append({
                        "year": 2023, "stage": current_stage, "stage_name": stage_meta["name"],
                        "miles": stage_meta["miles"], "km": stage_meta["km"],
                        "position": position, "name": runner_name, "club": runner_club, "time": leg_time
                    })

            # --- STANDARD LAYOUT (Pages 2-14 / Stages 2-13) ---
            else:
                parts = clean_line.split(leg_time)
                content_block = parts[1].strip() if len(parts) > 1 and clean_line.startswith(leg_time) else parts[0].strip()

                content_block = re.sub(r'\s+([MF])\s+', ' ', content_block)
                content_block = re.sub(r'[\=\|\.\,\-\_\+]', '', content_block).strip()

                split_match = re.search(r'\s+(\d+)\s+[A-Z|{]', content_block)
                if split_match:
                    content_block = content_block[:split_match.span()[0]].strip()

                tokens = content_block.split()
                if len(tokens) >= 2:
                    runner_name = f"{tokens[0]} {tokens[1]}"
                    runner_club = " ".join(tokens[2:]).strip()

                    runner_club = re.sub(r'\s+[a-z]{1,2}$', '', runner_club).strip()
                    if runner_club.upper() in ["A", "B", "C", ""]:
                        runner_club = "Independent"

                    position = len([r for r in results if r["stage"] == current_stage]) + 1
                    stage_meta = STAGE_DISTANCES.get(current_stage, {"miles": None, "km": None, "name": ""})

                    results.append({
                        "year": 2023, "stage": current_stage, "stage_name": stage_meta["name"],
                        "miles": stage_meta["miles"], "km": stage_meta["km"],
                        "position": position, "name": runner_name, "club": runner_club, "time": leg_time
                    })

    return results