# backend_tools/dump_stage1.py
import pdfplumber

with pdfplumber.open("../downloads/results_2019.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text() or ""
        if "LEG 1" in text.upper():
            for line in text.split("\n"):
                if "Aimee" in line or "Rachel" in line or "00:34:30" in line:
                    print(repr(line))