# backend_tools/compile_history.py
import os
import json
import sys

# Ensure the local folder is in the path before running imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractors.parse_2026 import extract_2026
from extractors.parse_2025 import extract_2025
from extractors.parse_2024 import extract_2024
from extractors.parse_2023 import extract_2023
from extractors.parse_2019 import extract_2019
from extractors.parse_2018 import extract_2018
from extractors.parse_2017 import extract_2017
from extractors.parse_2016 import extract_2016

def main():
    master_results = []
    downloads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'downloads'))

    print("🚀 Starting dedicated historical compilation engine...")

    # --- PROCESS 2026 ---
    path_2026 = os.path.join(downloads_dir, "results_2026.pdf")
    if os.path.exists(path_2026):
        try:
            data_2026 = extract_2026(path_2026)
            master_results.extend(data_2026)
            print(f"✓ Processed 2026 successfully ({len(data_2026)} records).")
        except Exception as e:
            print(f"⚠️ Error processing 2026: {e}")

    # --- PROCESS 2025 ---
    path_2025 = os.path.join(downloads_dir, "results_2025.pdf")
    if os.path.exists(path_2025):
        try:
            data_2025 = extract_2025(path_2025)
            master_results.extend(data_2025)
            print(f"✓ Processed 2025 successfully ({len(data_2025)} records).")
        except Exception as e:
            print(f"⚠️ Error processing 2025: {e}")

    # --- PROCESS 2024 ---
    path_2024 = os.path.join(downloads_dir, "results_2024.pdf")
    if os.path.exists(path_2024):
        try:
            data_2024 = extract_2024(path_2024)
            master_results.extend(data_2024)
            print(f"✓ Processed 2024 successfully ({len(data_2024)} records).")
        except Exception as e:
            print(f"⚠️ Error processing 2024: {e}")

    # --- PROCESS 2019 ---
    path_2019 = os.path.join(downloads_dir, "results_2019.pdf")
    if os.path.exists(path_2019):
        try:
            data_2019 = extract_2019(path_2019)
            master_results.extend(data_2019)
            print(f"✓ Processed 2019 successfully ({len(data_2019)} records).")
        except Exception as e:
            print(f"⚠️ Error processing 2019: {e}")

    # --- PROCESS 2018 ---
    path_2018 = os.path.join(downloads_dir, "results_2018.pdf")
    if os.path.exists(path_2018):
        try:
            data_2018 = extract_2018(path_2018)
            master_results.extend(data_2018)
            print(f"✓ Processed 2018 successfully ({len(data_2018)} records).")
        except Exception as e:
            print(f"⚠️ Error processing 2018: {e}")

    # --- PROCESS 2017 ---
    path_2017 = os.path.join(downloads_dir, "results_2017.pdf")
    if os.path.exists(path_2017):
        try:
            data_2017 = extract_2017(path_2017)
            master_results.extend(data_2017)
            print(f"✓ Processed 2017 successfully ({len(data_2017)} records).")
        except Exception as e:
            print(f"⚠️ Error processing 2017: {e}")
    
    # --- PROCESS 2016 ---
    path_2016 = os.path.join(downloads_dir, "results_2016.pdf")
    if os.path.exists(path_2016):
        try:
            data_2016 = extract_2016(path_2016)
            master_results.extend(data_2016)
            print(f"✓ Processed 2016 successfully ({len(data_2016)} records).")
        except Exception as e:
            print(f"⚠️ Error processing 2016: {e}")

    output_js_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data.js'))
    with open(output_js_path, "w", encoding="utf-8") as f:
        f.write("// data.js - Master Generated Historical Results Archive\n")
        f.write("const relayResults = ")
        json.dump(master_results, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"\n🎉 Compilation complete! Saved {len(master_results)} total rows to: {output_js_path}")

if __name__ == "__main__":
    main()