# backend_tools/extractors/parse_pdf.py
import re
import json
import os

# Drop your manual corrections here. They will instantly override the PDF text data.
MANUAL_OVERRIDES = {
    # Format -> (year, stage, position): {"name": "Correct Name", "club": "Correct Club", "time": "00:00:00"}
}

# Master list used to intercept club data within noisy text lines
KNOWN_CLUBS = [
    "Aberdare Valley", "Aberdare", "Albany Road", "Brackla Harriers", "Brackla", 
    "Builth & District", "Builth", "Caerleon RC", "Caerleon", "Caerphilly Runners", 
    "Caerphilly", "Caldicot RC", "Caldicot", "CDF Runners", "CDF", "Chepstow Harriers", 
    "Chepstow", "Cornelly Striders", "Cornelly", "Fairwater Runners", "Fairwater", 
    "Griffithstown Harriers", "Griffithstown", "Islwyn RC", "Islwyn", "Les Croupiers RC", 
    "Les Croupiers", "Croupiers", "Lliswerry Runners", "Lliswerry", "Monross Trailblazers", 
    "Monross", "Neath Harriers", "Neath", "Ogmore Phoenix", "Ogmore", "Phoenix",
    "Pont-y-pwl & District", "Pont-y-pwl", "Pontypool", "Pontyclun Road Runners", 
    "Pontyclun", "Pontypridd Roadents", "Pontypridd", "Porthcawl", "Rhondda Valley", 
    "Rhondda", "San Domenico", "Spirit of Monmouth", "Monmouth", "Torfaen", "Pegasus"
]

def extract_stage_data(pdf_path, year):
    import pdfplumber
    results = []
    
    current_stage = 1
    stage_positions = {}
    
    print(f"-> Processing {year} layout from: {pdf_path}")
    time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2})')

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            full_text = page.extract_text() or ""
            lines = full_text.split('\n')
            
            for line in lines:
                stage_match = re.search(r'(?:RESULT\s*:?\s*LEG|LEG|Leg)\s*:?\s*(\d+)', line, re.IGNORECASE)
                if stage_match:
                    new_stage = int(stage_match.group(1))
                    if new_stage != current_stage:
                        current_stage = new_stage

            words = page.extract_words()
            if not words:
                continue

            horizontal_rows = {}
            for w in words:
                text_content = w['text'].strip()
                if any(x in text_content.lower() for x in ["distance", "total time", "lead time", "interval", "rack raid", "pos", "pace"]):
                    continue
                
                matched_row = None
                for base_top in horizontal_rows:
                    if abs(base_top - w['top']) <= 5:
                        matched_row = base_top
                        break
                
                if matched_row is not None:
                    horizontal_rows[matched_row].append(w)
                else:
                    horizontal_rows[w['top']] = [w]

            for r_top in sorted(horizontal_rows.keys()):
                row_items = sorted(horizontal_rows[r_top], key=lambda x: x['x0'])
                
                # Build a clean base text line from the horizontal items
                raw_tokens = [item['text'].strip() for item in row_items]
                row_line_text = " ".join(raw_tokens)
                
                time_matches = time_pattern.findall(row_line_text)
                if not time_matches:
                    continue
                    
                leg_time_val = time_matches[0]

                # Filter out numbers and punctuation noise
                clean_tokens = []
                for item in row_items:
                    t_text = item['text'].strip()
                    if (time_pattern.match(t_text) or t_text.isdigit() or 
                        t_text in [":", "+", "*", "***", "****"] or
                        t_text.upper() in ["CLUB", "ARE", "PLUS", "MINUTES", "MINUTES.", "AWARDED", "RESULT", "TOTAL", "AFTER", "LEG", "LEAD", "INTERVAL", "TIME"]):
                        continue
                    if re.match(r'^\s*\(.*?\)\s*$', t_text):
                        continue
                    clean_tokens.append(t_text)

                if not clean_tokens:
                    continue

                # Match against known club names to separate fields cleanly
                detected_club = "Independent"
                combined_line_snippet = " ".join(clean_tokens)
                
                # Scan for matches from longest to shortest name string
                for club_candidate in sorted(KNOWN_CLUBS, key=len, reverse=True):
                    # Uses word boundaries to protect shorter matches like "Neath" vs "Fairwater"
                    if re.search(r'\b' + re.escape(club_candidate) + r'\b', combined_line_snippet, re.IGNORECASE):
                        detected_club = club_candidate
                        break

                # Extract the athlete name by taking everything before the club match
                name_tokens = []
                for token in clean_tokens:
                    if token.lower() in detected_club.lower() or detected_club.lower() in token.lower():
                        break
                    name_tokens.append(token)

                # Fallback if the name bounds match immediately
                if not name_tokens and len(clean_tokens) >= 2:
                    name_tokens = clean_tokens[0:2]

                name_str = " ".join(name_tokens).strip()
                club_str = detected_club

                # Polish the name string
                name_str = re.sub(r'(?:COURSE|RECORD|CUT|OFF|TIME|LEG|\d+)', '', name_str, flags=re.IGNORECASE).strip()
                name_str = re.sub(r'\s*\(.*?\)\s*', '', name_str).strip()

                if not name_str or len(name_str) < 3 or not re.match(r'^[A-Za-z]', name_str):
                    continue

                # Clean up specific team suffixes like "A", "B", or "Valley"
                suffix_match = re.search(r'\b([A-C])\b', combined_line_snippet)
                if suffix_match and not club_str.endswith(f" {suffix_match.group(1)}"):
                    club_str = f"{club_str} {suffix_match.group(1)}"
                elif "valley" in combined_line_snippet.lower() and not club_str.lower().endswith("valley"):
                    club_str = f"{club_str} Valley"

                stage_pos = stage_positions.get(current_stage, 0) + 1
                stage_positions[current_stage] = stage_pos

                if (year, current_stage, stage_pos) in MANUAL_OVERRIDES:
                    override = MANUAL_OVERRIDES[(year, current_stage, stage_pos)]
                    name_str = override.get("name", name_str)
                    club_str = override.get("club", club_str)
                    leg_time_val = override.get("time", leg_time_val)

                results.append({
                    "year": int(year),
                    "stage": current_stage,
                    "position": stage_pos,
                    "name": name_str,
                    "club": club_str,
                    "time": leg_time_val
                })
                
    generate_verification_log(results, year)
    return results

def generate_verification_log(results, year):
    os.makedirs("audit_logs", exist_ok=True)
    log_path = f"audit_logs/verify_{year}.txt"
    stages = {}
    for r in results:
        stages.setdefault(r["stage"], []).append(r)
        
    with open(log_path, "w", encoding="utf-8") as f:
        f.write(f"=== {year} RACK RAID EXTRACTION AUDIT CHECKLIST ===\n\n")
        for stage_num in sorted(stages.keys()):
            f.write(f"--- LEG {stage_num} ---\n")
            sorted_runners = sorted(stages[stage_num], key=lambda x: x["position"])
            for r in sorted_runners:
                f.write(f"Pos {r['position']:02d} | Time: {r['time']} | {r['name']} ({r['club']})\n")
            f.write(f"Total Runners Extracted for Leg {stage_num}: {len(sorted_runners)}\n\n")
    print(f"✓ Review checklist successfully generated here: {log_path}")