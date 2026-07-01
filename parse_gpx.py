# parse_gpx.py
import os
import glob
import re
import json
import math
import xml.etree.ElementTree as ET

def haversine(lat1, lon1, lat2, lon2):
    """Calculates the distance in miles between two coordinate points."""
    R = 3958.8  # Earth radius in miles
    d_lat = math.radians(lat2 - lat1)
    d_lon = math.radians(lon2 - lon1)
    a = (math.sin(d_lat / 2) ** 2 + 
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(d_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def parse_gpx_file(file_path):
    """Parses a single GPX file to calculate total distance and elevation gain."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # Handle standard GPX namespaces
    namespaces = {'gpx': 'http://www.topografix.com/GPX/1/1'}
    
    total_distance = 0.0
    total_gain = 0.0
    
    prev_lat, prev_lon, prev_ele = None, None, None
    coordinate_profile = []
    
    # Extract track points
    for trkpt in root.findall('.//gpx:trkpt', namespaces):
        lat = float(trkpt.get('lat'))
        lon = float(trkpt.get('lon'))
        
        ele_node = trkpt.find('gpx:ele', namespaces)
        ele = float(ele_node.text) if ele_node is not None else 0.0
        
        coordinate_profile.append([lat, lon])
        
        if prev_lat is not None:
            dist = haversine(prev_lat, prev_lon, lat, lon)
            total_distance += dist
            
            ele_diff = ele - prev_ele
            if ele_diff > 0:
                total_gain += ele_diff
                
        prev_lat, prev_lon, prev_ele = lat, lon, ele
        
    return {
        "distance": round(total_distance, 2),
        "elevation_gain": round(total_gain),
        "coordinates": coordinate_profile[::10]  # Downsample for quick map renders
    }

# parse_gpx.py (Updated main() metadata map)
def main():
    gpx_dir = os.path.join("assets", "gpx_files")
    search_pattern = os.path.join(gpx_dir, "RACK_RAID_*.gpx")
    gpx_files = glob.glob(search_pattern)
    
    if not gpx_files:
        print(f"✗ No GPX files found in {gpx_dir}")
        return
        
    gpx_files = sorted(gpx_files, key=lambda x: [int(s) for s in re.findall(r'\d+', x)] if re.findall(r'\d+', x) else x)

    # Master list of Stage Names, Descriptions, and Photos
    STAGE_METADATA = {
        1:  {"name": "Grosmont to Skenfrith", "toughness": 2, "desc": "A rolling start from the castle...", "facts": "Leg 1 opener."},
        2:  {"name": "Skenfrith to White Castle", "toughness": 5, "desc": "Brutal testing climbs...", "facts": "The castle hill hurts."},
        3:  {"name": "White Castle to Abergavenny", "toughness": 4, "desc": "Long descents into town...", "facts": "Fast road section."},
        4:  {"name": "Abergavenny to Old Court Moat", "toughness": 3, "desc": "Undulating lanes...", "facts": "Scenic route."},
        5:  {"name": "Old Court Moat to Monmouth", "toughness": 3, "desc": "Steady, rhythmic leg...", "facts": "Approaching halfway."},
        6:  {"name": "Monmouth to Raglan", "toughness": 4, "desc": "The longest leg of the raid...", "facts": "Stamina required."},
        7:  {"name": "Raglan to Usk", "toughness": 3, "desc": "Historic road race lanes...", "facts": "Mid-afternoon warmth leg."},
        8:  {"name": "Usk to Tintern", "toughness": 5, "desc": "Brutal woodland trail climbs...", "facts": "Universally feared ridge climb."},
        9:  {"name": "Tintern to Chepstow", "toughness": 4, "desc": "Up through the Wye Valley views...", "facts": "Beautiful but testing terrain."},
        10: {"name": "Chepstow to Caldicot", "toughness": 2, "desc": "Flat road run heading home...", "facts": "High speed potential."},
        11: {"name": "Caldicot to Penhow", "toughness": 4, "desc": "Tough dragging hills...", "facts": "Tactical leg."},
        12: {"name": "Penhow to Caerleon", "toughness": 3, "desc": "Dropping down into history...", "facts": "Fast final miles."},
        13: {"name": "Caerleon to Castell-y-Bwch", "toughness": 4, "desc": "Brutal uphill lane finish...", "facts": "Short but steep hill test."},
        14: {"name": "Castell-y-Bwch to Olive Tree", "toughness": 3, "desc": "The final dash to the line...", "facts": "Glory leg."}
    }

    js_output = "const stageProfiles = {\n"
    
    for file_path in gpx_files:
        stage_num_match = re.search(r'RACK_RAID_(\d+)', os.path.basename(file_path))
        if not stage_num_match:
            continue
        stage_num = int(stage_num_match.group(1))
        
        meta = STAGE_METADATA.get(stage_num, {"name": f"Stage {stage_num}", "toughness": 3, "desc": "", "facts": ""})
        
        try:
            stats = parse_gpx_file(file_path)
            web_safe_path = file_path.replace('\\', '/')
            
            js_output += f"  {stage_num}: {{\n"
            js_output += f"    name: \"{meta['name']}\",\n"
            js_output += f"    distanceMiles: {stats['distance']},\n"
            js_output += f"    elevationGainMetres: {stats['elevation_gain']},\n"
            js_output += f"    toughness: {meta['toughness']},\n"
            js_output += f"    gpxPath: \"/{web_safe_path}\",\n"
            js_output += f"    description: \"{meta['desc']}\",\n"
            js_output += f"    facts: \"{meta['facts']}\",\n"
            js_output += f"    imagePath: \"/assets/images/stages/stage_${stage_num}.jpg\",\n" # Standard convention
            js_output += f"    simplifiedRoute: {json.dumps(stats['coordinates'])}\n"
            js_output += "  },\n"
        except Exception as e:
            print(f"✗ Error parsing {file_path}: {e}")
            
    js_output = js_output.rstrip(",\n") + "\n};\n"
    with open("stages.js", "w", encoding="utf-8") as f:
        f.write(js_output)
    print("✓ stages.js rebuilt cleanly with master names!")

if __name__ == "__main__":
    main()