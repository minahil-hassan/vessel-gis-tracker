NAV_STATUS_MAP = {
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

SHIP_TYPE_MAP = {
    0: "Not available",

    # Reserved (1–19)
    1: "Reserved",
    2: "Reserved",
    3: "Reserved",
    4: "Reserved",
    5: "Reserved",
    6: "Reserved",
    7: "Reserved",
    8: "Reserved",
    9: "Reserved",
    10: "Reserved",
    11: "Reserved",
    12: "Reserved",
    13: "Reserved",
    14: "Reserved",
    15: "Reserved",
    16: "Reserved",
    17: "Reserved",
    18: "Reserved",
    19: "Reserved",

    # Wing in Ground (WIG) — 20–29
    20: "Wing in Ground (WIG)",
    21: "Wing in Ground (WIG), Hazardous Category A",
    22: "Wing in Ground (WIG), Hazardous Category B",
    23: "Wing in Ground (WIG), Hazardous Category C",
    24: "Wing in Ground (WIG), Hazardous Category D",
    25: "Wing in Ground (WIG), Reserved",
    26: "Wing in Ground (WIG), Reserved",
    27: "Wing in Ground (WIG), Reserved",
    28: "Wing in Ground (WIG), Reserved",
    29: "Wing in Ground (WIG), Reserved",

    # Miscellaneous — 30–39
    30: "Fishing Vessel",
    31: "Towing Vessel",
    32: "Towing Vessel with Length Exceeding Limits",
    33: "Dredging or Underwater Operations",
    34: "Diving Operations",
    35: "Military Operations",
    36: "Sailing Vessel",
    37: "Pleasure Craft",
    38: "Reserved",
    39: "Reserved",

    # High-Speed Craft (HSC) — 40–49
    40: "High-Speed Craft (HSC)",
    41: "High-Speed Craft (HSC), Hazardous Category A",
    42: "High-Speed Craft (HSC), Hazardous Category B",
    43: "High-Speed Craft (HSC), Hazardous Category C",
    44: "High-Speed Craft (HSC), Hazardous Category D",
    45: "High-Speed Craft (HSC), Reserved",
    46: "High-Speed Craft (HSC), Reserved",
    47: "High-Speed Craft (HSC), Reserved",
    48: "High-Speed Craft (HSC), Reserved",
    49: "High-Speed Craft (HSC), No Additional Information",

    # Special Purpose — 50–59
    50: "Pilot Vessel",
    51: "Search and Rescue Vessel",
    52: "Tug",
    53: "Port Tender",
    54: "Anti-Pollution Equipment",
    55: "Law Enforcement Vessel",
    56: "Spare for Local Use",
    57: "Spare for Local Use",
    58: "Medical Transport",
    59: "Noncombatant Ship",

    # Passenger Vessels — 60–69
    60: "Passenger Vessel",
    61: "Passenger Vessel, Hazardous Category A",
    62: "Passenger Vessel, Hazardous Category B",
    63: "Passenger Vessel, Hazardous Category C",
    64: "Passenger Vessel, Hazardous Category D",
    65: "Passenger Vessel, Reserved",
    66: "Passenger Vessel, Reserved",
    67: "Passenger Vessel, Reserved",
    68: "Passenger Vessel, Reserved",
    69: "Passenger Vessel, No Additional Information",

    # Cargo Vessels — 70–79
    70: "Cargo Vessel",
    71: "Cargo Vessel, Hazardous Category A",
    72: "Cargo Vessel, Hazardous Category B",
    73: "Cargo Vessel, Hazardous Category C",
    74: "Cargo Vessel, Hazardous Category D",
    75: "Cargo Vessel, Reserved",
    76: "Cargo Vessel, Reserved",
    77: "Cargo Vessel, Reserved",
    78: "Cargo Vessel, Reserved",
    79: "Cargo Vessel, No Additional Information",

    # Tankers — 80–89
    80: "Tanker",
    81: "Tanker, Hazardous Category A",
    82: "Tanker, Hazardous Category B",
    83: "Tanker, Hazardous Category C",
    84: "Tanker, Hazardous Category D",
    85: "Tanker, Reserved",
    86: "Tanker, Reserved",
    87: "Tanker, Reserved",
    88: "Tanker, Reserved",
    89: "Tanker, No Additional Information",

    # Other Types — 90–99
    90: "Other Type of Vessel",
    91: "Reserved for Future Use",
    92: "Reserved for Future Use",
    93: "Reserved for Future Use",
    94: "Reserved for Future Use",
    95: "Reserved for Future Use",
    96: "Reserved for Future Use",
    97: "Reserved for Future Use",
    98: "Reserved for Future Use",
    99: "Reserved for Future Use",
}


# Grouping vessel type labels into broader UI-friendly categories
# Grouping vessel type labels into broader UI-friendly categories
VESSEL_TYPE_GROUPS = {
    "Cargo Vessels": [
        "Cargo Vessel",
        "Cargo Vessel, Hazardous Category A",
        "Cargo Vessel, Hazardous Category B",
        "Cargo Vessel, Hazardous Category C",
        "Cargo Vessel, Hazardous Category D",
        "Cargo Vessel, Reserved",
        "Cargo Vessel, No Additional Information"
    ],
    "Passenger Vessels": [
        "Passenger Vessel",
        "Passenger Vessel, Hazardous Category A",
        "Passenger Vessel, Hazardous Category B",
        "Passenger Vessel, Hazardous Category C",
        "Passenger Vessel, Hazardous Category D",
        "Passenger Vessel, Reserved",
        "Passenger Vessel, No Additional Information",
        "High-Speed Craft (HSC)",
        "High-Speed Craft (HSC), Hazardous Category A",
        "High-Speed Craft (HSC), Hazardous Category B",
        "High-Speed Craft (HSC), Hazardous Category C",
        "High-Speed Craft (HSC), Hazardous Category D",
        "High-Speed Craft (HSC), Reserved",
        "High-Speed Craft (HSC), No Additional Information"
    ],
    "Tankers": [
        "Tanker",
        "Tanker, Hazardous Category A",
        "Tanker, Hazardous Category B",
        "Tanker, Hazardous Category C",
        "Tanker, Hazardous Category D",
        "Tanker, Reserved",
        "Tanker, No Additional Information"
    ],
    "Tugs & Service Vessels": [
        "Tug",
        "Pilot Vessel",
        "Port Tender",
        "Anti-Pollution Equipment",
        "Search and Rescue Vessel"
    ],
    "Military & Government": [
        "Law Enforcement Vessel",
        "Medical Transport",
        "Noncombatant Ship",
        "Military Operations"
    ],
    "Leisure Craft": [
        "Pleasure Craft",
        "Sailing Vessel",
        "Fishing Vessel"
    ],
    "Wing in Ground (WIG)": [
        "Wing in Ground (WIG)",
        "Wing in Ground (WIG), Hazardous Category A",
        "Wing in Ground (WIG), Hazardous Category B",
        "Wing in Ground (WIG), Hazardous Category C",
        "Wing in Ground (WIG), Hazardous Category D",
        "Wing in Ground (WIG), Reserved"
    ],
    "Reserved / Other": [
        "Other Type of Vessel",
        "Reserved",
        "Reserved for Future Use",
        "Spare for Local Use",
        "No Additional Information",
        "Dredging or Underwater Operations",
        "Diving Operations"
    ]
}


# Bounding box for Liverpool port (used for spatial query)
# LIVERPOOL_BBOX = {
#     "type": "Polygon",
#     "coordinates": [[
#         [-3.0329433, 53.427],
#         [-3.0329433, 53.4617416],
#         [-3.00611,   53.4617416],
#         [-3.00611,   53.427],
#         [-3.0329433, 53.427]
#     ]]
# }
LIVERPOOL_BBOX = {
    "type": "Polygon",
    "coordinates": [[
        [-3.0077999305775336, 53.396248523303115],
        [-3.0094217137084627, 53.395973449991544],
        [-3.0096527515848663, 53.39647894409191],
        [-3.01057603578667, 53.397719550875195],
        [-3.0114229645027706, 53.398638684258714],
        [-3.0120392492759436, 53.39992565717063],
        [-3.013581448730207, 53.40323483854445],
        [-3.01481688628553, 53.40571543981227],
        [-3.0189789996380227, 53.40452072062007],
        [-3.0213681585902634, 53.40410731090509],
        [-3.0232181014377772, 53.40442868466465],
        [-3.0266862737318263, 53.404888062553624],
        [-3.029306608519562, 53.405806913845424],
        [-3.0304625222478023, 53.40580677535067],
        [-3.0327748157350243, 53.40589888300494],
        [-3.037245276967184, 53.405301776826775],
        [-3.040405569632128, 53.40475051156906],
        [-3.0441040962081445, 53.40566915300178],
        [-3.04664684773482, 53.407460769799826],
        [-3.0499607383256944, 53.40870116843112],
        [-3.052271618987646, 53.41058422535153],
        [-3.05365863773045, 53.4112732080406],
        [-3.061215352461062, 53.41380129158003],
        [-3.0628265145676608, 53.41209914058186],
        [-3.0604477183924814, 53.41118372101121],
        [-3.062371421292454, 53.40819643727545],
        [-3.058441806186238, 53.40635884544699],
        [-3.05088632044243, 53.40341780130248],
        [-3.0460294269348935, 53.40157974377297],
        [-3.0416378095017933, 53.4013960564867],
        [-3.035549484441816, 53.401396083598826],
        [-3.0241429452036073, 53.39827134237598],
        [-3.02167627168609, 53.3978115799317],
        [-3.016667200083333, 53.39693872896308],
        [-3.013278983286199, 53.39519355214608],
        [-3.01219862306192, 53.39533081449488],
        [-3.0114272818112795, 53.39514676027832],
        [-3.0114282967172414, 53.39464165503648],
        [-3.007491736646699, 53.39560503107782],
        [-3.0077999305775336, 53.396248523303115]
    ]]
}



