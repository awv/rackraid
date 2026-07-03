# backend_tools/test_2019_gaps.py
import re
import pdfplumber
from extractors.parse_2019 import extract_2019

pdf_path = "../downloads/results_2019.pdf"
parsed_data = extract_2019(pdf_path)

# Group parsed data by stage
stage_map = {}
for r in parsed_data:
    stage_map.setdefault(r["stage"], []).append(r)

with pdfplumber.open(pdf_path) as pdf:
    current_stage = 1
    for page_num, page in enumerate(pdf.pages, 1):
        text = page.extract_text() or ""
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            stage_match = re.search(r'(?:LEG|Stage)\s*:?\s*(\d+)', line, re.IGNORECASE)
            if stage_match:
                current_stage = int(stage_match.group(1))
                continue
            
            # Check for lines that contain a time string
            if re.search(r'\d{1,2}:\d{2}:\d{2}', line):
                # Ignore structural baseline metadata headers
                if any(x in line.lower() for x in ["distance :", "result :", "total time after", "course record", "cut off time"]):
                    continue
                if any(x in line.upper() for x in ["NUMBER OF TEAMS", "TOTAL NUMBER", "TOTAL DISTANCE", "TOTAL TIME"]):
                    continue
                    
                # Look for a match in our parsed array for this stage
                stage_entries = stage_map.get(current_stage, [])
                
                # Match by checking if any parsed runner's first name is present in this line
                matched = any(p["name"].split()[0].lower() in line.lower() for p in stage_entries if p["name"])
                
                # Check for DNF/DNS single token matches explicitly
                if not matched and ("DNF" in line.upper() or "DNS" in line.upper()):
                    matched = any(p["name"].upper() in ["DNF", "DNS"] for p in stage_entries)

                if not matched:
                    print(f"[Stage {current_stage} | Page {page_num}] MISSING FROM PARSED RESULTS:")
                    print(f"   Raw Text Line -> {line}\n")