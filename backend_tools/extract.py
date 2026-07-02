import os
import re
import json

STAGE_MAP = {
    0: "2018 Special Prologue",
    1: "Grosmont to Skenfrith",
    2: "Skenfrith to White Castle",
    3: "White Castle to Abergavenny",
    4: "Abergavenny to Old Court Moat",
    5: "Old Court Moat to Monmouth",
    6: "Monmouth to Raglan",
    7: "Raglan to Usk",
    8: "Usk to Tintern",
    9: "Tintern to Chepstow",
    10: "Chepstow to Caldicot",
    11: "Caldicot to Penhow",
    12: "Penhow to Caerleon",
    13: "Caerleon to Castell-y-Bwch",
    14: "Castell-y-Bwch to Olive Tree"
}

DISTANCE_LOOKUP = {
    0:  {"miles": 4.1,  "km": 6.6},
    1:  {"miles": 5.1,  "km": 8.2},
    2:  {"miles": 6.93,  "km": 11.2},
    3:  {"miles": 7.51,  "km": 12.1},
    4:  {"miles": 6.7,  "km": 10.8},
    5:  {"miles": 8.1,  "km": 13.0},
    6:  {"miles": 12.6,  "km": 20.3},
    7:  {"miles": 5.53,  "km": 8.9},
    8:  {"miles": 13.1,  "km": 21.1},
    9:  {"miles": 10.0,  "km": 16.0},
    10: {"miles": 7.6,  "km": 12.16},
    11: {"miles": 8.4,  "km": 13.4},
    12: {"miles": 6.64,  "km": 10.7},
    13: {"miles": 5.43,  "km": 8.7},
    14: {"miles": 5.1,  "km": 8.2}
}

def get_stage_name(stage_num):
    return STAGE_MAP.get(stage_num, f"Unknown Stage {stage_num}")

def parse_pdf_robust(pdf_path, year):
    import pdfplumber
    results = []
    
    current_stage = 1
    current_cut_off = None
    stage_positions = {}
    
    team_name_master = {}
    
    print(f"Processing {pdf_path}...")
    time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2})')

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            full_text = page.extract_text() or ""
            lines = full_text.split('\n')
            for line in lines:
                line = line.strip()
                stage_match = re.search(r'(?:Stage|Leg)\s+(\d+)', line, re.IGNORECASE)
                if stage_match:
                    current_stage = int(stage_match.group(1))
                    continue
                elif year == 2018 and re.search(r'(?:Stage|Leg)\s+0', line, re.IGNORECASE):
                    current_stage = 0
                    continue
                
                cutoff_match = re.search(r'Cut\s*Off\s*Time\s*:\s*(\d{1,2}:\d{2}:\d{2})', line, re.IGNORECASE)
                if cutoff_match:
                    current_cut_off = cutoff_match.group(1)
                    continue

            words = page.extract_words()
            if not words:
                continue

            horizontal_rows = {}
            for w in words:
                text_content = w['text'].strip()
                if any(x in text_content.lower() for x in ["distance", "record", "total time", "lead time", "interval", "result", "rack raid", "pos", "name", "club", "time", "pace"]):
                    continue
                
                approx_top = round(w['top'])
                matched_row = None
                for base_top in horizontal_rows:
                    if abs(base_top - w['top']) <= 4:
                        matched_row = base_top
                        break
                
                if matched_row is not None:
                    horizontal_rows[matched_row].append(w)
                else:
                    horizontal_rows[w['top']] = [w]

            for r_top in sorted(horizontal_rows.keys()):
                row_items = sorted(horizontal_rows[r_top], key=lambda x: x['x0'])
                row_text_full = " ".join([item['text'] for item in row_items])
                
                time_matches = time_pattern.findall(row_text_full)
                if not time_matches:
                    if "cut off" in row_text_full.lower() or "winning time" in row_text_full.lower():
                        continue
                    continue
                    
                leg_time_val = time_matches[0]
                
                try:
                    hour_val = int(leg_time_val.split(':')[0])
                    if hour_val >= 2:
                        continue
                except ValueError:
                    pass
                
                name_tokens = []
                gender_flag = ""
                
                if current_stage == 1:
                    is_isolated_cutoff = "cut off" in row_text_full.lower() or "yellow" in row_text_full.lower()
                    name_min = page.width * 0.05 if is_isolated_cutoff else page.width * 0.20
                    name_max = page.width * 0.60
                    club_min = page.width * 0.40 if is_isolated_cutoff else page.width * 0.50
                    club_max = page.width * 0.95
                else:
                    name_min, name_max = page.width * 0.05, page.width * 0.26
                    club_min, club_max = page.width * 0.26, page.width * 0.60

                club_zone_tokens = []
                for item in row_items:
                    item_text = item['text'].strip()
                    item_center = (item['x0'] + item['x1']) / 2.0
                    
                    if time_pattern.match(item_text) or item_text == ":" or item_text.lower() == "lead":
                        continue
                        
                    clean_token = re.sub(r'[\(\)]', '', item_text).upper()
                    if clean_token in ['M', 'F'] or re.match(r'^[MF]\d+$', clean_token):
                        gender_flag = f"({clean_token})"
                        continue

                    if name_min <= item_center <= name_max:
                        # Filter out structural layout terminology
                        if item_text.lower() in ["course", "record", "stage", "cut", "off", "time", "miles", "km.", "rack", "raid", "highlighted", "yellow", "=", "rules", "applied"]:
                            continue
                        if current_stage == 1 and item_text.isdigit() and item_center < page.width * 0.35:
                            continue
                        if current_stage != 1 and item_text.isdigit() and item_center < page.width * 0.08:
                            continue
                        name_tokens.append(item_text)
                    elif club_min <= item_center <= club_max:
                        if item_text.lower() in ["stage", "cut", "off", "time", "highlighted", "yellow", "=", "rules", "applied"]:
                            continue
                        club_zone_tokens.append(item_text)

                name_str = " ".join(name_tokens).strip()
                name_str = re.sub(r'[\(\)\'\"]', '', name_str).strip()

                # Clean up stray forward slashes or punctuation remaining from header lines
                name_str = re.sub(r'^[\s/.\-]+|[\s/.\-]+$', '', name_str).strip()

                if not name_str or name_str == "-":
                    continue

                # Ensure name strictly starts with an alphabetical letter to stop header dimensions/numbers leaking
                if not re.match(r'^[A-Za-z]', name_str):
                    continue

                if gender_flag:
                    name_str = f"{name_str} {gender_flag}"

                club_zone_text = " ".join(club_zone_tokens).strip()
                club_numbers = re.findall(r'\d+', club_zone_text)
                
                clean_club_name = re.sub(r'\d+', '', club_zone_text)
                clean_club_name = re.sub(r'[\(\)\'\"]', '', clean_club_name)
                clean_club_name = re.sub(r'\b(?:TOTAL|TIME)\b', '', clean_club_name, flags=re.IGNORECASE)
                clean_club_name = re.sub(r'\s+', ' ', clean_club_name).strip()

                if not clean_club_name or clean_club_name == "-":
                    clean_club_name = "Independent"

                if club_numbers:
                    target_team_num = int(club_numbers[0])
                    
                    if target_team_num in team_name_master:
                        master_name = team_name_master[target_team_num]
                        if clean_club_name.lower().startswith(master_name.lower()) or master_name.lower().startswith(clean_club_name.lower()):
                            clean_club_name = master_name
                    else:
                        tokens = clean_club_name.split()
                        if len(tokens) > 1:
                            if tokens[1] in ['A', 'B', "'A'", "'B'"] or len(tokens[0]) > 3:
                                if tokens[1] in ['A', 'B', "'A'", "'B'"]:
                                    clean_club_name = f"{tokens[0]} {tokens[1]}"
                                else:
                                    clean_club_name = tokens[0]
                        
                        team_name_master[target_team_num] = clean_club_name

                    final_club_str = f"{clean_club_name} ({target_team_num:02d})"
                else:
                    final_club_str = clean_club_name

                dist_info = DISTANCE_LOOKUP.get(current_stage, {"miles": None, "km": None})
                
                stage_pos = stage_positions.get(current_stage, 0) + 1
                stage_positions[current_stage] = stage_pos

                results.append({
                    "year": int(year),
                    "stage": current_stage,
                    "stage_name": get_stage_name(current_stage),
                    "cut_off": current_cut_off,
                    "miles": dist_info["miles"],
                    "km": dist_info["km"],
                    "position": stage_pos,
                    "name": name_str,
                    "club": final_club_str,
                    "time": leg_time_val
                })
                    
    return results

if __name__ == "__main__":
    import glob
    downloads_dir = "downloads"
    all_compiled_results = []
    
    pdf_files = glob.glob(os.path.join(downloads_dir, "*.pdf"))
    print(f"Found {len(pdf_files)} local PDF files to process.")
    
    for pdf_path in pdf_files:
        clean_path = pdf_path.replace('\\', '/')
        year_match = re.search(r'(\d{4})', clean_path)
        if not year_match:
            continue
            
        year = int(year_match.group(1))
        if year == 2012 or year == 2023:
            continue
            
        try:
            year_results = parse_pdf_robust(pdf_path, year)
            if year_results:
                all_compiled_results.extend(year_results)
                print(f"-> Successfully compiled {len(year_results)} records for Year {year}.")
        except Exception as e:
            print(f"-> Error reading local file {pdf_path}: {e}")

    if all_compiled_results:
        output_path = "../data.js" if os.path.basename(os.getcwd()) == "scraper" else "data.js"
        all_compiled_results.sort(key=lambda x: (-x['year'], x['stage'], x['position']))
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("const relayResults = ")
            json.dump(all_compiled_results, f, indent=2, ensure_ascii=False)
            f.write(";\n")
            
        print(f"\nSuccess! Archive compiled: {len(all_compiled_results)} total records.")