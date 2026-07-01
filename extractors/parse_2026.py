# extractors/parse_2026.py
import re
import json

# Drop your manual corrections here. They will instantly override the PDF text data.
MANUAL_OVERRIDES = {
    # Format -> (stage, position): {"name": "Correct Name", "club": "Correct Club (00)", "time": "00:00:00"}
    # Example: (1, 30): {"name": "Melanie Hall", "club": "Brackla Harriers (04)", "time": "00:46:00"}
}

def extract_2026(pdf_path):
    import pdfplumber
    results = []
    
    # Trackers for multi-page alignment loops
    current_stage = 1
    stage_positions = {}
    
    print(f"-> Processing 2026 layout from: {pdf_path}")
    time_pattern = re.compile(r'(\d{1,2}:\d{2}:\d{2})')

    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, 1):
            full_text = page.extract_text() or ""
            lines = full_text.split('\n')
            
            # Identify Stage Context from Headings
            for line in lines:
                stage_match = re.search(r'(?:RESULT:\s+LEG|LEG|Leg)\s+(\d+)', line, re.IGNORECASE)
                if stage_match:
                    current_stage = int(stage_match.group(1))

            words = page.extract_words()
            if not words:
                continue

            # Sort and align visual rows horizontally using proximity bounds
            horizontal_rows = {}
            for w in words:
                text_content = w['text'].strip()
                # Skip layout noise and column headers
                if any(x in text_content.lower() for x in ["distance", "total time", "lead time", "interval", "rack raid", "pos", "pace"]):
                    continue
                
                approx_top = round(w['top'])
                matched_row = None
                for base_top in horizontal_rows:
                    if abs(base_top - w['top']) <= 5: # 5px baseline wiggle room
                        matched_row = base_top
                        break
                
                if matched_row is not None:
                    horizontal_rows[matched_row].append(w)
                else:
                    horizontal_rows[w['top']] = [w]

            # Process aligned rows chronologically down the page
            for r_top in sorted(horizontal_rows.keys()):
                row_items = sorted(horizontal_rows[r_top], key=lambda x: x['x0'])
                row_text_full = " ".join([item['text'] for item in row_items])
                
                time_matches = time_pattern.findall(row_text_full)
                if not time_matches:
                    continue
                    
                leg_time_val = time_matches[0]
                
                # Setup specific boundary columns based on your provided format structures
                # Note: First page handles 'Club Left / Name Center', later legs shift profiles.
                name_tokens = []
                club_tokens = []
                
                for item in row_items:
                    item_text = item['text'].strip()
                    item_center = (item['x0'] + item['x1']) / 2.0
                    
                    if time_pattern.match(item_text) or item_text in [":", "+"] or item_text.lower() in ["lead", "time", "interval"]:
                        continue
                    
                    # Sort words into Name or Club buckets by coordinate tracking
                    if page_num == 1: # First leg layout bounds
                        if page.width * 0.25 <= item_center <= page.width * 0.60:
                            name_tokens.append(item_text)
                        elif page.width * 0.60 < item_center <= page.width * 0.95:
                            club_tokens.append(item_text)
                    else: # Later legs layout bounds
                        if page.width * 0.05 <= item_center <= page.width * 0.35:
                            name_tokens.append(item_text)
                        elif page.width * 0.35 < item_center <= page.width * 0.70:
                            club_tokens.append(item_text)

                name_str = " ".join(name_tokens).strip()
                club_str = " ".join(club_tokens).strip()

                # Filter noise fragments out of names
                name_str = re.sub(r'(?:COURSE|RECORD|CUT|OFF|TIME|LEG|\d+)', '', name_str, flags=re.IGNORECASE).strip()
                if not name_str or len(name_str) < 3 or not re.match(r'^[A-Za-z]', name_str):
                    continue

                # Determine Position Assignment
                stage_pos = stage_positions.get(current_stage, 0) + 1
                stage_positions[current_stage] = stage_pos

                # Check for an Override Rule before committing data row
                if (current_stage, stage_pos) in MANUAL_OVERRIDES:
                    override = MANUAL_OVERRIDES[(current_stage, stage_pos)]
                    name_str = override.get("name", name_str)
                    club_str = override.get("club", club_str)
                    leg_time_val = override.get("time", leg_time_val)

                results.append({
                    "year": 2026,
                    "stage": current_stage,
                    "position": stage_pos,
                    "name": name_str,
                    "club": club_str if club_str else "Independent",
                    "time": leg_time_val
                })
                
    # Generate the Easy-Scan Verification Document
    generate_verification_log(results)
    return results

def generate_verification_log(results):
    """Outputs a text file layout for effortless human validation checks."""
    log_path = "verify_2026.txt"
    stages = {}
    for r in results:
        stages.setdefault(r["stage"], []).append(r)
        
    with open(log_path, "w", encoding="utf-8") as f:
        f.write("=== 2026 RACK RAID EXTRACTION AUDIT CHECKLIST ===\n\n")
        for stage_num in sorted(stages.keys()):
            f.write(f"--- LEG {stage_num} ---\n")
            # Sort checking profiles by ascending rank positions
            sorted_runners = sorted(stages[stage_num], key=lambda x: x["position"])
            for r in sorted_runners:
                f.write(f"Pos {r['position']:02d} | Time: {r['time']} | {r['name']} ({r['club']})\n")
            f.write(f"Total Runners Extracted for Leg {stage_num}: {len(sorted_runners)}\n\n")
    print(f"✓ Review checklist successfully generated here: {log_path}")