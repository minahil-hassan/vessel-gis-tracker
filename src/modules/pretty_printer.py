import json


def print_ais_data(filepath, limit=5):
    """
    Prints AIS PositionReport data from a local JSON file in a structured human-readable format.

    Args:
        filepath (str): Path to the JSON file containing AIS PositionReport messages.
    """
    navigational_status_map = {
        0: "Under way using engine",
        1: "At anchor",
        2: "Not under command",
        3: "Restricted manoeuverability",
        4: "Constrained by draught",
        5: "Moored",
        6: "Aground",
        7: "Engaged in fishing",
        8: "Under way sailing",
        9: "Reserved",
        10: "Reserved",
        11: "Reserved",
        12: "Reserved",
        13: "Reserved",
        14: "AIS-SART (SAR)",
        15: "Not defined"
    }

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return
    except json.JSONDecodeError:
        print(f"Invalid JSON format: {filepath}")
        return

    if not data:
        print("No AIS data found in file.")
        return

    print(f"\nLoaded {len(data)} AIS PositionReport messages from {filepath}\n")

    for i, report in enumerate(data[:limit], 1):
        nav_status = navigational_status_map.get(report.get("NavigationalStatus"), "Unknown")
        print(f"Ship #{i}")
        print(f"  MMSI/UserID     : {report.get('mmsi', 'N/A')}")
        print(f"  Position        : ({report.get('lat'):.5f}, {report.get('lon'):.5f})")
        print(f"  Course Over Ground (COG): {report.get('cog')}°")
        print(f"  Speed Over Ground (SOG): {report.get('sog')} knots")
        print(f"  True Heading    : {report.get('heading')}°")
        print(f"  Navigational Status: {nav_status}")
        print(f"  Timestamp       : {report.get('Timestamp')}")
        print(f"  Position Accuracy: {'High' if report.get('PositionAccuracy') else 'Low'}")
        print(f"  Valid Message?  : {'valid' if report.get('Valid') else 'invalid'}")
        print("=" * 60)
    


