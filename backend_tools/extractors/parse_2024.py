# backend_tools/extractors/parse_2024.py
import re
import pdfplumber

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
    13: {"miles": 5.43, "km": 8.7, "name": "Caerleon Amphitheatre to Castell-y-Bwch"},
    14: {"miles": 5.1, "km": 8.3, "name": "Castell-y-Bwch to Olive Tree"}
}

def extract_2024(pdf_path):
    results = []
    current_stage = 1
    time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2})')

    print(f"-> Parsing stable digital text layer for 2024: {pdf_path}")

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            for line in text.split('\n'):
                if not line.strip(): 
                    continue

                # Strip layout banner notices
                line = re.sub(r'^Times\s+less\s+than\s+course\s+record\s+highlighted\s+GREEN\s+', '', line, flags=re.IGNORECASE)
                line = re.sub(r'^TIME\s+highlighted\s+YELLOW\s+=\s+CUT\s+OFF\s+RULES\s+APPLIED\s+', '', line, flags=re.IGNORECASE)

                # Parse and lock stage headers safely
                stage_match = re.search(r'(?:LEG|Stage)\s*:?\s*(\d+)', line, re.IGNORECASE)
                if stage_match:
                    current_stage = int(stage_match.group(1))
                    continue

                if any(x in line.lower() for x in ["www.", "total time", "after leg", "course record", "result :", "distance :", "total number of", "total distance run"]): 
                    continue

                if any(x in line.lower() for x in ["www.", "total time", "after leg", "course record"]):
                    continue

                times = time_pattern.findall(line)
                if not times:
                    continue
                leg_time = times[0]

                # Filter out time-of-day cumulative timestamps from wrapped lines
                if any(leg_time.startswith(p) for p in ["10:", "11:", "12:", "13:", "14:", "15:", "16:"]):
                    continue

                # --- STAGE 1 LOGIC ENGINE ---
                if current_stage == 1:
                    parts = line.split(leg_time)
                    right_side = parts[1].strip() if len(parts) > 1 else ""

                    bracket_split = re.split(r'\s*\(\d+\)\s*', right_side)
                    if len(bracket_split) >= 2:
                        runner_name = bracket_split[0].strip()
                        
                        right_tokens = bracket_split[1].split()
                        club_words = []
                        for token in right_tokens:
                            if token.isdigit() or ":" in token or token.lower() in ["lead", "time"]:
                                break
                            club_words.append(token)
                        runner_club = " ".join(club_words).strip()
                    else:
                        right_tokens = right_side.split()
                        runner_name = f"{right_tokens[0]} {right_tokens[1]}" if len(right_tokens) >= 2 else right_tokens[0]
                        runner_club = "Independent"

                # --- STAGES 2 - 14 LOGIC ENGINE ---
                else:
                    parts = line.split(leg_time)
                    right_side = parts[1].strip() if len(parts) > 1 else ""

                    # Find the first team ID bracket context anchor point
                    bracket_match = re.search(r'\s*\(\d+\)\s*', right_side)
                    if bracket_match:
                        # Everything before the bracket is the runner's full name
                        runner_name = right_side[:bracket_match.start()].strip()
                        
                        # Everything after the bracket contains the club, followed by the position digit
                        after_bracket = right_side[bracket_match.end():].strip()
                        after_tokens = after_bracket.split()
                        
                        club_words = []
                        for token in after_tokens:
                            # Stop grabbing club name characters when we reach the position integer
                            if token.isdigit() or ":" in token:
                                break
                            club_words.append(token)
                        runner_club = " ".join(club_words).strip()
                    else:
                        runner_name = "Unknown Runner"
                        runner_club = "Independent"

                # --- DATA SANITISATION ---
                if runner_club.isupper() and len(runner_club) > 3:
                    runner_club = runner_club.title()
                
                if runner_club.upper() == "CDF":
                    runner_club = "CDF"

                if runner_club.upper() in ["A", "B", "C", ""]:
                    runner_club = "Independent"

                position = len([r for r in results if r["stage"] == current_stage]) + 1
                stage_meta = STAGE_DISTANCES.get(current_stage, {"miles": None, "km": None, "name": ""})

                results.append({
                    "year": 2024, 
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