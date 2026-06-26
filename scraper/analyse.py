import os
import re
import json

CLUB_NAME_REGISTRY = {
    # Aberdare
    "aberdare": "Aberdare",
    
    # Albany Road
    "albany road": "Albany Road Club",
    "albany road rc": "Albany Road Club",
    
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
    
    # Cornelly
    "cornelly": "Cornelly Striders",
    "cornelly striders": "Cornelly Striders",
    
    # Fairwater
    "fairwater": "Fairwater Runners",
    "fairwater runners": "Fairwater Runners",
    "fiarwater runners": "Fairwater Runners", 
    
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
    "porthcawl runers": "Porthcawl Runners",
    
    # Rhondda
    "rhondda": "Rhondda Valley Runners",
    "rhondda valley": "Rhondda Valley Runners",
    "rhondda valley runners": "Rhondda Valley Runners",
    
    # San Domenico
    "san domenico": "San Domenico RC",
    "san domenico rc": "San Domenico RC",
    
    # Spirit of Monmouth
    "spirit of monmouth": "Spirit of Monmouth",

    # Pegasus Alignment Standard
    "pegasus": "Pegasus RC",
    "pegasus running": "Pegasus RC"
}

def normalise_club_name(raw_club):
    if not raw_club:
        return "Independent"
    
    clean_base = re.sub(r'\s*\(\d+\)\s*$', '', str(raw_club)).strip().lower()
    clean_base = re.sub(r'\s+[a-e]$', '', clean_base).strip()
    
    if "cwmbran" in clean_base or "fairwater" in clean_base: return "Fairwater Runners"
    if "chepstow" in clean_base: return "Chepstow Harriers"
    if "parc" in clean_base: return "Parc Bryn Bach RC"
    if "pont-y-pwl" in clean_base or "pontypool" in clean_base: return "Pont-y-pwl & District Runners"
    if "liswerry" in clean_base or "lliswerry" in clean_base: return "Lliswerry Runners"
    if "caerleon" in clean_base: return "Caerleon RC"
    if "caerphilly" in clean_base: return "Caerphilly Runners"
    if "caldicot" in clean_base: return "Caldicot RC"
    if "cdf" in clean_base: return "CDF Runners"
    if "griffithstown" in clean_base: return "Griffithstown Harriers"
    if "islwyn" in clean_base: return "Islwyn RC"
    if "croupiers" in clean_base: return "Les Croupiers RC"
    if "monross" in clean_base: return "Monross Trailblazers"
    if "neath" in clean_base: return "Neath Harriers"
    if "ogmore" in clean_base: return "Ogmore Phoenix Runners"
    if "pontyclun" in clean_base: return "Pontyclun Road Runners"
    if "pontypridd" in clean_base: return "Pontypridd Roadents"
    if "porthcawl" in clean_base: return "Porthcawl Runners"
    if "rhondda" in clean_base: return "Rhondda Valley Runners"
    if "san domenico" in clean_base: return "San Domenico RC"
    if "aberdare" in clean_base: return "Aberdare"
    if "albany" in clean_base: return "Albany Road Club"
    if "brackla" in clean_base: return "Brackla Harriers"
    if "builth" in clean_base: return "Builth & District RC"
    if "cornelly" in clean_base: return "Cornelly Striders"
    if "monmouth" in clean_base or "spirit" in clean_base: return "Spirit of Monmouth"
    if "pegasus" in clean_base: return "Pegasus RC"
    
    if clean_base in ["-", "individual", "unattached", "unknown"]:
        return "Independent"
        
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

def cleanse_and_align_records(records):
    """
    Data Cleansing Block: Automatically overrides known historical layout anomalies
    and standardizes data points before analytics processing.
    """
    cleansed = []
    
    # Centralized ledger for one-off historic data corruptions (smudged PDFs, truncated times)
    HISTORIC_CORRECTIONS = {
        # (Year, Stage, Position): {field_to_fix: correct_value}
        (2022, 1, 2): {"name": "Niki Morgan", "club": "Chepstow Harriers", "time": "00:33:08"}
    }
    
    # 100% verified map for 2018 Stage 0 Prologue
    VERIFIED_2018_STAGE_0 = {
        1: {"name": "Martin Norton", "club": "Lliswerry Runners", "time": "01:08:30"},
        2: {"name": "James Blore", "club": "Chepstow Harriers", "time": "01:09:22"},
        3: {"name": "Iestyn Rhodes", "club": "Pont-y-pwl & District Runners", "time": "01:10:31"},
        4: {"name": "Gareth Jones", "club": "Spirit of Monmouth", "time": "01:14:07"},
        5: {"name": "Lee Mills", "club": "Islwyn RC", "time": "01:14:35"},
        6: {"name": "David Moore", "club": "Brackla Harriers", "time": "01:14:56"},
        7: {"name": "Josh Dixon", "club": "Les Croupiers RC", "time": "01:15:55"},
        8: {"name": "Matthew Pizey", "club": "Caerphilly Runners", "time": "01:17:21"},
        9: {"name": "Martin Jones", "club": "Islwyn RC", "time": "01:18:22"},
        10: {"name": "Gwyn Johnson", "club": "Pontypridd Roadents", "time": "01:18:49"},
        11: {"name": "Paul Lidgett", "club": "Chepstow Harriers", "time": "01:19:02"},
        12: {"name": "James White", "club": "San Domenico RC", "time": "01:19:33"},
        13: {"name": "Michael Cleaver", "club": "Lliswerry Runners", "time": "01:19:52"},
        14: {"name": "Gerard Gormley", "club": "Griffithstown Harriers", "time": "01:20:12"},
        15: {"name": "Bryan Meredith", "club": "Rhondda Valley Runners", "time": "01:21:17"},
        16: {"name": "Richard Sheehy", "club": "Parc Bryn Bach RC", "time": "01:21:40"},
        17: {"name": "Roger Mills", "club": "Fairwater Runners", "time": "01:28:03"},
        18: {"name": "Graham Viner", "club": "Caerleon RC", "time": "01:29:49"},
        19: {"name": "Robert Coles", "club": "Caerphilly Runners", "time": "01:29:52"},
        20: {"name": "Andrew Dickens", "club": "Pont-y-pwl & District Runners", "time": "01:31:45"},
        21: {"name": "Graham Carrick", "club": "Pegasus RC", "time": "01:31:47"},
        22: {"name": "Richard Beech", "club": "Caldicot RC", "time": "01:32:30"},
        23: {"name": "Marcus Smith", "club": "Parc Bryn Bach RC", "time": "01:32:40"},
        24: {"name": "Martyn Jenkins", "club": "Fairwater Runners", "time": "01:36:03"},
        25: {"name": "Darren Griffiths Warner", "club": "Pontypridd Roadents", "time": "01:39:36"},
        26: {"name": "Steve Houghton", "club": "Caerleon RC", "time": "01:40:47"}
    }

    # 100% verified map for 2018 Stage 1
    VERIFIED_2018_STAGE_1 = {
        1: {"name": "Mike Lewis", "club": "Fairwater Runners", "time": "00:29:02"},
        2: {"name": "Jamie Davies", "club": "Lliswerry Runners", "time": "00:31:27"},
        3: {"name": "Lou Summers", "club": "Pont-y-pwl & District Runners", "time": "00:34:51"},
        4: {"name": "Jane Horler", "club": "Chepstow Harriers", "time": "00:35:13"},
        5: {"name": "Mike Gwynne", "club": "Pontypridd Roadents", "time": "00:35:21"},
        6: {"name": "Keri-Lyn Jones", "club": "Parc Bryn Bach RC", "time": "00:36:33"},
        7: {"name": "Nathan Priest", "club": "Islwyn RC", "time": "00:37:21"},
        8: {"name": "Jan Morris", "club": "Chepstow Harriers", "time": "00:37:46"},
        9: {"name": "Nick Davies", "club": "Lliswerry Runners", "time": "00:38:01"},
        10: {"name": "Tammy Fry", "club": "Caerleon RC", "time": "00:38:29"},
        11: {"name": "Hannah Davies", "club": "Islwyn RC", "time": "00:38:36"},
        12: {"name": "Kerry Budden", "club": "Griffithstown Harriers", "time": "00:38:39"},
        13: {"name": "Sara Williams", "club": "Caerphilly Runners", "time": "00:38:50"},
        14: {"name": "Emma Sowrey", "club": "Pont-y-pwl & District Runners", "time": "00:38:55"},
        15: {"name": "Sophie Williams", "club": "Spirit of Monmouth", "time": "00:40:00"},
        16: {"name": "Luke Heslop", "club": "Pegasus RC", "time": "00:40:20"},
        17: {"name": "Natalie Cartlidge", "club": "San Domenico RC", "time": "00:40:21"},
        18: {"name": "Paige Luff", "club": "Caldicot RC", "time": "00:40:57"},
        19: {"name": "Mary Beech", "club": "Brackla Harriers", "time": "00:41:03"},
        20: {"name": "Eve Gallop-Evans", "club": "Les Croupiers RC", "time": "00:41:07"},
        21: {"name": "Charlene Henshaw", "club": "Caerleon RC", "time": "00:41:29"},
        22: {"name": "Lianne Willetts", "club": "Caerphilly Runners", "time": "00:41:59"},
        23: {"name": "Teresa Davies", "club": "Parc Bryn Bach RC", "time": "00:43:02"},
        24: {"name": "Gemma Green", "club": "Rhondda Valley Runners", "time": "00:46:00"},
        25: {"name": "Sheree Mann", "club": "Fairwater Runners", "time": "00:46:01"},
        26: {"name": "Helen Welch", "club": "Pontypridd Roadents", "time": "00:46:02"}
    }

    for row in records:
        # Quick type conversion safety checks
        try:
            year = int(row.get("year", 0))
            stage = int(row.get("stage", -1))
            pos = int(row.get("position", -1))
        except ValueError:
            year, stage, pos = 0, -1, -1

        # 1. Apply targeted historical corrections first
        lookup_key = (year, stage, pos)
        if lookup_key in HISTORIC_CORRECTIONS:
            for field, accurate_value in HISTORIC_CORRECTIONS[lookup_key].items():
                row[field] = accurate_value

        name_raw = str(row.get("name", "")).strip()
        club_raw = str(row.get("club", "")).strip()
        
        # Strip trailing gender brackets
        name_raw = re.sub(r'\s*\([MFmf]\)\s*$', '', name_raw).strip()

        # Skip residual layout noise text
        if "RACK" in name_raw or "RAID" in club_raw:
            continue

        # Standard double-club extraction filters for older years
        if year <= 2019 and club_raw:
            split_match = re.search(r'^([A-Za-z\s\-&]+?)\s+[A-E]\s+', club_raw)
            if split_match:
                club_raw = split_match.group(1).strip()
                
        row["name"] = name_raw
        row["club"] = normalise_club_name(club_raw)
        cleansed.append(row)
        
    return cleansed

def process_analytics(records):
    stage_winning_trends = {}
    club_counts = {}

    for row in records:
        seconds = def_time_to_seconds(row["time"])
        if seconds < 600: 
            continue
            
        stage = int(row["stage"])
        year = int(row["year"])
        club_base = row["club"]
        
        if club_base and club_base not in ["Independent", "-"]:
            club_counts[club_base] = club_counts.get(club_base, 0) + 1

        if stage not in stage_winning_trends:
            stage_winning_trends[stage] = {}
        if year not in stage_winning_trends[stage]:
            stage_winning_trends[stage][year] = {"time": row["time"], "seconds": seconds}
        else:
            if seconds < stage_winning_trends[stage][year]["seconds"]:
                stage_winning_trends[stage][year] = {"time": row["time"], "seconds": seconds}

    formatted_trends = {}
    for stage, years_dict in stage_winning_trends.items():
        sorted_years = sorted(years_dict.keys())
        formatted_trends[f"stage_{stage}"] = [
            {"year": y, "time": years_dict[y]["time"], "seconds": years_dict[y]["seconds"]} 
            for y in sorted_years
        ]

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
        # 1. Run the standard cleaning loop over the data
        clean_data = cleanse_and_align_records(raw_data)
        
        # 2. Force-purge any existing 2018 Stage 0 or Stage 1 entries to avoid duplicates
        clean_data = [r for r in clean_data if not (str(r.get("year")) == "2018" and str(r.get("stage")) in ["0", "1"])]
        
        # 3. Explicitly inject the 100% accurate 26-runner blocks
        VERIFIED_STAGE_0 = {
            1: {"name": "Martin Norton", "club": "Lliswerry Runners", "time": "01:08:30"},
            2: {"name": "James Blore", "club": "Chepstow Harriers", "time": "01:09:22"},
            3: {"name": "Iestyn Rhodes", "club": "Pont-y-pwl & District Runners", "time": "01:10:31"},
            4: {"name": "Gareth Jones", "club": "Spirit of Monmouth", "time": "01:14:07"},
            5: {"name": "Lee Mills", "club": "Islwyn RC", "time": "01:14:35"},
            6: {"name": "David Moore", "club": "Brackla Harriers", "time": "01:14:56"},
            7: {"name": "Josh Dixon", "club": "Les Croupiers RC", "time": "01:15:55"},
            8: {"name": "Matthew Pizey", "club": "Caerphilly Runners", "time": "01:17:21"},
            9: {"name": "Martin Jones", "club": "Islwyn RC", "time": "01:18:22"},
            10: {"name": "Gwyn Johnson", "club": "Pontypridd Roadents", "time": "01:18:49"},
            11: {"name": "Paul Lidgett", "club": "Chepstow Harriers", "time": "01:19:02"},
            12: {"name": "James White", "club": "San Domenico RC", "time": "01:19:33"},
            13: {"name": "Michael Cleaver", "club": "Lliswerry Runners", "time": "01:19:52"},
            14: {"name": "Gerard Gormley", "club": "Griffithstown Harriers", "time": "01:20:12"},
            15: {"name": "Bryan Meredith", "club": "Rhondda Valley Runners", "time": "01:21:17"},
            16: {"name": "Richard Sheehy", "club": "Parc Bryn Bach RC", "time": "01:21:40"},
            17: {"name": "Roger Mills", "club": "Fairwater Runners", "time": "01:28:03"},
            18: {"name": "Graham Viner", "club": "Caerleon RC", "time": "01:29:49"},
            19: {"name": "Robert Coles", "club": "Caerphilly Runners", "time": "01:29:52"},
            20: {"name": "Andrew Dickens", "club": "Pont-y-pwl & District Runners", "time": "01:31:45"},
            21: {"name": "Graham Carrick", "club": "Pegasus RC", "time": "01:31:47"},
            22: {"name": "Richard Beech", "club": "Caldicot RC", "time": "01:32:30"},
            23: {"name": "Marcus Smith", "club": "Parc Bryn Bach RC", "time": "01:32:40"},
            24: {"name": "Martyn Jenkins", "club": "Fairwater Runners", "time": "01:36:03"},
            25: {"name": "Darren Griffiths Warner", "club": "Pontypridd Roadents", "time": "01:39:36"},
            26: {"name": "Steve Houghton", "club": "Caerleon RC", "time": "01:40:47"}
        }

        VERIFIED_STAGE_1 = {
            1: {"name": "Mike Lewis", "club": "Fairwater Runners", "time": "00:29:02"},
            2: {"name": "Jamie Davies", "club": "Lliswerry Runners", "time": "00:31:27"},
            3: {"name": "Lou Summers", "club": "Pont-y-pwl & District Runners", "time": "00:34:51"},
            4: {"name": "Jane Horler", "club": "Chepstow Harriers", "time": "00:35:13"},
            5: {"name": "Mike Gwynne", "club": "Pontypridd Roadents", "time": "00:35:21"},
            6: {"name": "Keri-Lyn Jones", "club": "Parc Bryn Bach RC", "time": "00:36:33"},
            7: {"name": "Nathan Priest", "club": "Islwyn RC", "time": "00:37:21"},
            8: {"name": "Jan Morris", "club": "Chepstow Harriers", "time": "00:37:46"},
            9: {"name": "Nick Davies", "club": "Lliswerry Runners", "time": "00:38:01"},
            10: {"name": "Tammy Fry", "club": "Caerleon RC", "time": "00:38:29"},
            11: {"name": "Hannah Davies", "club": "Islwyn RC", "time": "00:38:36"},
            12: {"name": "Kerry Budden", "club": "Griffithstown Harriers", "time": "00:38:39"},
            13: {"name": "Sara Williams", "club": "Caerphilly Runners", "time": "00:38:50"},
            14: {"name": "Emma Sowrey", "club": "Pont-y-pwl & District Runners", "time": "00:38:55"},
            15: {"name": "Sophie Williams", "club": "Spirit of Monmouth", "time": "00:40:00"},
            16: {"name": "Luke Heslop", "club": "Pegasus RC", "time": "00:40:20"},
            17: {"name": "Natalie Cartlidge", "club": "San Domenico RC", "time": "00:40:21"},
            18: {"name": "Paige Luff", "club": "Caldicot RC", "time": "00:40:57"},
            19: {"name": "Mary Beech", "club": "Brackla Harriers", "time": "00:41:03"},
            20: {"name": "Eve Gallop-Evans", "club": "Les Croupiers RC", "time": "00:41:07"},
            21: {"name": "Charlene Henshaw", "club": "Caerleon RC", "time": "00:41:29"},
            22: {"name": "Lianne Willetts", "club": "Caerphilly Runners", "time": "00:41:59"},
            23: {"name": "Teresa Davies", "club": "Parc Bryn Bach RC", "time": "00:43:02"},
            24: {"name": "Gemma Green", "club": "Rhondda Valley Runners", "time": "00:46:00"},
            25: {"name": "Sheree Mann", "club": "Fairwater Runners", "time": "00:46:01"},
            26: {"name": "Helen Welch", "club": "Pontypridd Roadents", "time": "00:46:02"}
        }

        for pos, d in VERIFIED_STAGE_0.items():
            clean_data.append({"year": 2018, "stage": 0, "stage_name": "Llanthony to Grosmont", "cut_off": "01:43:00", "miles": 11.4, "km": 18.3, "position": pos, "name": d["name"], "club": normalise_club_name(d["club"]), "time": d["time"]})
            
        for pos, d in VERIFIED_STAGE_1.items():
            clean_data.append({"year": 2018, "stage": 1, "stage_name": "Grosmont to Skenfrith", "cut_off": "00:46:00", "miles": 5.1, "km": 8.2, "position": pos, "name": d["name"], "club": normalise_club_name(d["club"]), "time": d["time"]})

        # 4. Save everything down normally
        is_in_scraper = os.path.basename(os.getcwd()) == "scraper"
        data_output_path = "../data.js" if is_in_scraper else "data.js"
        stats_output_path = "../stats.js" if is_in_scraper else "stats.js"
        
        with open(data_output_path, "w", encoding="utf-8") as f:
            f.write("const relayResults = ")
            json.dump(clean_data, f, indent=2, ensure_ascii=False)
            f.write(";\n")
        
        analytics_data = process_analytics(clean_data)
        with open(stats_output_path, "w", encoding="utf-8") as f:
            f.write("const relayStats = ")
            json.dump(analytics_data, f, indent=2, ensure_ascii=False)
            f.write(";\n")
            
        print("Success! Data forced to 26 runners per stage.")