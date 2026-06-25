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
    1:  {"miles": 5.5,  "km": 8.8},
    2:  {"miles": 7.1,  "km": 11.4},
    3:  {"miles": 4.9,  "km": 7.9},
    4:  {"miles": 6.3,  "km": 10.1},
    5:  {"miles": 7.3,  "km": 11.7},
    6:  {"miles": 5.6,  "km": 9.0},
    7:  {"miles": 6.8,  "km": 10.9},
    8:  {"miles": 7.8,  "km": 12.5},
    9:  {"miles": 5.4,  "km": 8.7},
    10: {"miles": 6.2,  "km": 10.0},
    11: {"miles": 6.6,  "km": 10.6},
    12: {"miles": 5.8,  "km": 9.3},
    13: {"miles": 6.9,  "km": 11.1},
    14: {"miles": 6.1,  "km": 9.8}
}

def get_stage_name(stage_num):
    return STAGE_MAP.get(stage_num, f"Unknown Stage {stage_num}")

def parse_pdf_robust(pdf_path, year):
    import pdfplumber
    results = []
    
    current_stage = 1
    current_cut_off = None
    
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
                
                if "cut off" in row_text_full.lower():
                    continue
                
                time_matches = time_pattern.findall(row_text_full)
                if not time_matches:
                    continue
                    
                leg_time_val = time_matches[0]
                
                name_tokens = []
                club_tokens = []
                all_found_numbers = []
                
                if current_stage == 1:
                    # Stage 1: Tightened bounds to isolate Name completely from trailing metadata fields
                    name_min, name_max = page.width * 0.40, page.width * 0.60
                    club_min, club_max = page.width * 0.60, page.width * 0.85
                else:
                    # Stages 2-14: Lower boundary captures leading club registration indices smoothly
                    name_min, name_max = page.width * 0.05, page.width * 0.26
                    club_min, club_max = page.width * 0.03, page.width * 0.55

                for item in row_items:
                    item_text = item['text'].strip()
                    item_center = (item['x0'] + item['x1']) / 2.0
                    
                    if time_pattern.match(item_text) or item_text == ":" or item_text.lower() == "lead":
                        continue
                        
                    if name_min <= item_center <= name_max:
                        if current_stage != 1 and item_text.isdigit() and item_center < page.width * 0.08:
                            continue
                        # Prevent bracketed layout artifacts leaking straight into the clean runner name
                        if not (item_text.startswith('(') and item_text.endswith(')')) and item_text.upper() not in ['M', 'F']:
                            name_tokens.append(item_text)
                        
                    elif club_min <= item_center <= club_max:
                        # Extract any standalone digit sequences to identify team references
                        digits = re.findall(r'\d+', item_text)
                        if digits:
                            all_found_numbers.extend(digits)
                        elif item_text.upper() not in ['M', 'F'] and not re.match(r'^[MF]\d+$', item_text.upper()):
                            club_tokens.append(item_text)

                name_str = " ".join(name_tokens).strip()
                club_str = " ".join(club_tokens).strip()

                if not name_str or name_str == "-":
                    continue
                if not club_str or club_str == "-":
                    club_str = "Individual"

                # Standardise Team Identification layout to your exact preference: Club Name (##)
                if all_found_numbers:
                    # The first sequence parsed is always the master club registration number entry
                    target_team_num = all_found_numbers[0]
                    final_club_str = f"{club_str} ({int(target_team_num):02d})"
                else:
                    final_club_str = club_str

                dist_info = DISTANCE_LOOKUP.get(current_stage, {"miles": None, "km": None})
                stage_pos = sum(1 for res in results if res['stage'] == current_stage) + 1

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
        if year == 2012:
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