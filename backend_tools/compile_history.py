# backend_tools/compile_history.py
import os
import json
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from extractors.parse_2026 import extract_2026
from extractors.parse_2025 import extract_2025
from extractors.parse_2024 import extract_2024
from extractors.parse_2023 import extract_2023

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

# --- PROCESS 2023 ---
    # path_2023 = os.path.join(downloads_dir, "results_2023.pdf")
    # if os.path.exists(path_2023):
    #     try:
    #         data_2023 = extract_2023(path_2023)
    #         master_results.extend(data_2023)
    #         print(f"✓ Processed 2023 successfully ({len(data_2023)} records).")
    #     except Exception as e:
    #         print(f"⚠️ Error processing 2023: {e}")

    output_js_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data.js'))
    with open(output_js_path, "w", encoding="utf-8") as f:
        f.write("// data.js - Master Generated Historical Results Archive\n")
        f.write("const relayResults = ")
        json.dump(master_results, f, ensure_ascii=False, indent=2)
        f.write(";\n")

    print(f"\n🎉 Compilation complete! Saved {len(master_results)} total rows to: {output_js_path}")

if __name__ == "__main__":
    main()