import os
import re
import json

CLUB_NAME_REGISTRY = {
    # Aberdare
    "aberdare": "Aberdare",
    
    # Albany Road
    "albany road": "Albany Road Run Club",
    "albany road rc": "Albany Road Run Club",
    
    # Brackla
    "brackla": "Brackla Harriers",
    "brackla harriers": "Brackla Harriers",
    
    # Builth
    "builth": "Builth & District RC",
    "builth & district": "Builth & District RC",
    "builth & district rc": "Builth & District RC",
    
    # Caerleon
    "caerleon": "Caerleon RC",
    "caerleon rc": "Caerleon RC",
    
    # Caerphilly
    "caerphilly": "Caerphilly Runners",
    "caerphilly runners": "Caerphilly Runners",
    
    # Caldicot
    "caldicot": "Caldicot RC",
    "caldicot rc": "Caldicot RC",
    
    # CDF
    "cdf": "CDF Runners",
    "cdf runners": "CDF Runners",
    
    # Chepstow
    "chepstow": "Chepstow Harriers",
    "chepstow harriers": "Chepstow Harriers",
    "chepstow a": "Chepstow Harriers (A)",
    "chepstow b": "Chepstow Harriers (B)",
    
    # Cornelly
    "cornelly": "Cornelly Striders",
    "cornelly striders": "Cornelly Striders",
    
    # Fairwater
    "fairwater": "Fairwater Runners",
    "fairwater runners": "Fairwater Runners",
    "fiarwater runners": "Fairwater Runners", # Common typo override
    
    # Griffithstown
    "griffithstown": "Griffithstown Harriers",
    "griffithstown harriers": "Griffithstown Harriers",
    
    # Islwyn
    "islwyn": "Islwyn RC",
    "islwyn rc": "Islwyn RC",
    
    # Les Croupiers
    "les croupiers": "Les Croupiers RC",
    "les croupiers rc": "Les Croupiers RC",
    "croupiers": "Les Croupiers RC",
    
    # Lliswerry
    "lliswerry": "Lliswerry Runners",
    "lliswerry runners": "Lliswerry Runners",
    "liswerry": "Lliswerry Runners",
    
    # Monross
    "monross": "Monross Trailblazers",
    "monross trailblazers": "Monross Trailblazers",
    
    # Neath
    "neath": "Neath Harriers",
    "neath harriers": "Neath Harriers",
    
    # Ogmore
    "ogmore": "Ogmore Phoenix Runners",
    "ogmore phoenix": "Ogmore Phoenix Runners",
    "ogmore phoenix runners": "Ogmore Phoenix Runners",
    
    # Parc Bryn Bach
    "parc": "Parc Bryn Bach RC",
    "parc bryn bach": "Parc Bryn Bach RC",
    "parc bryn bach rc": "Parc Bryn Bach RC",
    
    # Pont-y-pwl
    "pontypool": "Pont-y-pwl & District Runners",
    "pont-y-pwl": "Pont-y-pwl & District Runners",
    "pont-y-pwl b": "Pont-y-pwl & District Runners (B)",
    "pont-y-pwl & district runners": "Pont-y-pwl & District Runners",
    
    # Pontyclun
    "pontyclun": "Pontyclun Road Runners",
    "pontyclun road runners": "Pontyclun Road Runners",
    
    # Pontypridd
    "pontypridd": "Pontypridd Roadents",
    "pontypridd roadents": "Pontypridd Roadents",
    
    # Porthcawl
    "porthcawl": "Porthcawl Runners",
    "porthcawl runners": "Porthcawl Runners",
    "porthcawl runers": "Porthcawl Runners", # Common typo override
    
    # Rhondda
    "rhondda": "Rhondda Valley Runners",
    "rhondda valley": "Rhondda Valley Runners",
    "rhondda valley runners": "Rhondda Valley Runners",
    
    # San Domenico
    "san domenico": "San Domenico RC",
    "san domenico rc": "San Domenico RC",
    
    # Spirit of Monmouth
    "spirit of monmouth": "Spirit of Monmouth"
}

def normalise_club_name(raw_club):
    if not raw_club:
        return "-"
    
    # Strip any trailing category numbers like "Chepstow Harriers (1)" or "Parc (2)"
    import re
    clean_base = re.sub(r'\s*\(\d+\)\s*$', '', str(raw_club)).strip().lower()
    
    if clean_base in ["-", "individual", "unattached", "unknown"]:
        return "-"
        
    # Return matched formal value or capitalised fallback if new club emerges
    return CLUB_NAME_REGISTRY.get(clean_base, raw_club.strip())

def load_raw_archive():
    data_path = "../data.js" if os.path.basename(os.getcwd()) == "scraper" else "data.js"
    if not os.path.exists(data_path):
        return []
    with open(data_path, "r", encoding="utf-8") as f:
        content = f.read()
        json_str = content.replace("const relayResults = ", "").strip().rstrip(";")
        return json.loads(json_str)

def def_time_to_seconds(t_str):
    if not t_str: return 999999
    try:
        p = t_str.split(':')
        return int(p[0]) * 3600 + int(p[1]) * 60 + int(p[2])
    except (ValueError, IndexError):
        return 999999

def process_analytics(records):
    stage_winning_trends = {}
    club_counts = {}

    for row in records:
        seconds = def_time_to_seconds(row["time"])
        
        # Filter out obvious data oddities (e.g., placeholder times under 10 minutes)
        if seconds < 600: 
            continue
            
        stage = int(row["stage"])
        year = int(row["year"])
        full_club = row["club"]
        
        # Clean team suffixes for club metrics
        club_base = re.sub(r'\s*\(\d+\)\s*$', '', full_club).strip()
        
        # Tally club appearances (ignoring empty or individual markers)
        if club_base and club_base.lower() not in ["individual", "unknown", "-", "none"]:
            club_counts[club_base] = club_counts.get(club_base, 0) + 1

        # Track winning times per stage per year
        if stage not in stage_winning_trends:
            stage_winning_trends[stage] = {}
        if year not in stage_winning_trends[stage]:
            stage_winning_trends[stage][year] = {"time": row["time"], "seconds": seconds}
        else:
            if seconds < stage_winning_trends[stage][year]["seconds"]:
                stage_winning_trends[stage][year] = {"time": row["time"], "seconds": seconds}

    # Format Stage Progression Trends
    formatted_trends = {}
    for stage, years_dict in stage_winning_trends.items():
        # Sort chronologically by year
        sorted_years = sorted(years_dict.keys())
        formatted_trends[f"stage_{stage}"] = [
            {"year": y, "time": years_dict[y]["time"], "seconds": years_dict[y]["seconds"]} 
            for y in sorted_years
        ]

    # Format Club Attendance Leaderboard (Top 15 most frequent clubs)
    sorted_clubs = sorted(club_counts.items(), key=lambda x: x[1], reverse=True)[:15]
    formatted_clubs = [{"club": c, "appearances": count} for c, count in sorted_clubs]

    return {
        "stage_trends": formatted_trends,
        "club_attendance": formatted_clubs
    }

if __name__ == "__main__":
    print("Compiling progression curves and club analytics...")
    raw_data = load_raw_archive()
    
    if raw_data:
        analytics_data = process_analytics(raw_data)
        
        output_path = "../stats.js" if os.path.basename(os.getcwd()) == "scraper" else "stats.js"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("const relayStats = ")
            json.dump(analytics_data, f, indent=2, ensure_ascii=False)
            f.write(";\n")
            
        print(f"Success! Updated analytics datasets saved to {output_path}")