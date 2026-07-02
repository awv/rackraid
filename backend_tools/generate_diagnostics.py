# backend_tools/generate_diagnostics.py
import json
import os
import re

def generate_diagnostics_page():
    # Target your existing data.js file in the root
    data_path = "data.js" 
    output_path = "diagnostics.html"

    if not os.path.exists(data_path):
        print(f"-> Error: Could not find data file at {data_path}")
        return

    with open(data_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Extract the JSON array from the JavaScript variable statement
    # e.g., const rackData = [...]; or var data = [...];
    match = re.search(r'=\s*(\s*\[.*\])\s*;?', raw_text, re.DOTALL)
    if not match:
        print("-> Error: Could not parse JSON array layout inside data.js")
        return
    
    try:
        records = json.loads(match.group(1))
    except json.JSONDecodeError as e:
        print(f"-> Error decoding JSON layer inside data.js: {e}")
        return

    # Standalone HTML string with table filters
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Runner Data Audit Dashboard</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 20px; color: #333; }}
        h1 {{ color: #111; margin-bottom: 5px; }}
        .controls {{ margin: 20px 0; display: flex; gap: 15px; }}
        input {{ padding: 8px 12px; font-size: 14px; width: 300px; border: 1px solid #ccc; border-radius: 4px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
        th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; font-size: 14px; }}
        th {{ background-color: #f5f5f5; cursor: pointer; user-select: none; }}
        th:hover {{ background-color: #eaeaea; }}
        tr:nth-child(even) {{ background-color: #fafafa; }}
        .meta {{ font-size: 12px; color: #666; margin-bottom: 20px; }}
    </style>
</head>
<body>

    <h1>Data Audit Diagnostics</h1>
    <div class="meta">Total Records Compiled: {len(records)}</div>

    <div class="controls">
        <input type="text" id="searchName" placeholder="Search by name..." onkeyup="filterTable()">
        <input type="text" id="searchClub" placeholder="Search by club..." onkeyup="filterTable()">
    </div>

    <table id="auditTable">
        <thead>
            <tr>
                <th onclick="sortTable(0)">Year</th>
                <th onclick="sortTable(1)">Stage</th>
                <th onclick="sortTable(2)">Pos</th>
                <th onclick="sortTable(3)">Runner Name</th>
                <th onclick="sortTable(4)">Club / Team</th>
                <th onclick="sortTable(5)">Time</th>
            </tr>
        </thead>
        <tbody>
    """

    for r in records:
        html_content += f"""
            <tr>
                <td>{r.get('year', '')}</td>
                <td>{r.get('stage', '')}</td>
                <td>{r.get('position', '')}</td>
                <td><strong>{r.get('name', '')}</strong></td>
                <td>{r.get('club', '')}</td>
                <td>{r.get('time', '')}</td>
            </tr>"""

    html_content += """
        </tbody>
    </table>

    <script>
    function filterTable() {
        var inputName = document.getElementById("searchName").value.toLowerCase();
        var inputClub = document.getElementById("searchClub").value.toLowerCase();
        var table = document.getElementById("auditTable");
        var tr = table.getElementsByTagName("tr");

        for (var i = 1; i < tr.length; i++) {
            var tdName = tr[i].getElementsByTagName("td")[3];
            var tdClub = tr[i].getElementsByTagName("td")[4];
            if (tdName && tdClub) {
                var txtName = tdName.textContent || tdName.innerText;
                var txtClub = tdClub.textContent || tdClub.innerText;
                if (txtName.toLowerCase().indexOf(inputName) > -1 && txtClub.toLowerCase().indexOf(inputClub) > -1) {
                    tr[i].style.display = "";
                } else {
                    tr[i].style.display = "none";
                }
            }
        }
    }

    function sortTable(n) {
        var table = document.getElementById("auditTable");
        var rows = table.rows;
        var switching = true;
        var direction = "asc"; 
        var switchcount = 0;
        
        while (switching) {
            switching = false;
            for (var i = 1; i < (rows.length - 1); i++) {
                var shouldSwitch = false;
                var x = rows[i].getElementsByTagName("td")[n];
                var y = rows[i + 1].getElementsByTagName("td")[n];
                
                var xVal = x.textContent || x.innerText;
                var yVal = y.textContent || y.innerText;
                
                if (!isNaN(xVal) && !isNaN(yVal)) {
                    if (direction == "asc") {
                        if (Number(xVal) > Number(yVal)) { shouldSwitch = true; break; }
                    } else if (direction == "desc") {
                        if (Number(xVal) < Number(yVal)) { shouldSwitch = true; break; }
                    }
                } else {
                    if (direction == "asc") {
                        if (xVal.toLowerCase() > yVal.toLowerCase()) { shouldSwitch = true; break; }
                    } else if (direction == "desc") {
                        if (xVal.toLowerCase() < yVal.toLowerCase()) { shouldSwitch = true; break; }
                    }
                }
            }
            if (shouldSwitch) {
                rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                switching = true;
                switchcount++;      
            } else {
                if (switchcount == 0 && direction == "asc") {
                    direction = "desc";
                    switching = true;
                }
            }
        }
    }
    </script>
</body>
</html>
    """

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"-> Diagnostics page built successfully at: {output_path}")

if __name__ == "__main__":
    generate_diagnostics_page()