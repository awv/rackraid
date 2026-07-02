# compile.py
import os
import json
import glob

# Import your isolated 2026 extractor module
from backend_tools.extractors.parse_pdf import extract_2026

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
            sorted_runners = sorted(stages[stage_num], key=lambda x: x["position"])
            for r in sorted_runners:
                f.write(f"Pos {r['position']:02d} | Time: {r['time']} | {r['name']} ({r['club']})\n")
            f.write(f"Total Runners Extracted for Leg {stage_num}: {len(sorted_runners)}\n\n")
    print(f"✓ Review checklist successfully generated here: {log_path}")

def main():
    all_compiled_results = []
    downloads_dir = "downloads"
    
    pdf_2026 = os.path.join(downloads_dir, "results_2026.pdf")
    if not os.path.exists(pdf_2026):
        matches = glob.glob("**/results_2026.pdf", recursive=True) + glob.glob("*2026*.pdf")
        if matches:
            pdf_2026 = matches[0]

    if os.path.exists(pdf_2026):
        try:
            results_2026 = extract_2026(pdf_2026)
            all_compiled_results.extend(results_2026)
            print(f"✓ Successfully processed {len(results_2026)} records for Year 2026.")
            
            # GENERATE THE TEXT VERIFICATION LOG FIRST
            generate_verification_log(results_2026)
            
        except Exception as e:
            print(f"✗ Error compiling Year 2026 results: {e}")
    else:
        print(f"✗ Missing file error: Could not locate 'results_2026.pdf' in your directories.")

    # Write out the independent data matrix file if records were extracted
    if all_compiled_results:
        output_path = "results_2026.js"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("const results2026 = ")
            json.dump(all_compiled_results, f, indent=2, ensure_ascii=False)
            f.write(";\n")
        print(f"✓ Master export complete: File written cleanly to {output_path}")

if __name__ == "__main__":
    main()