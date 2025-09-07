# src/database/update_port_facilities.py

import sys
from pathlib import Path
import json
from pymongo import UpdateOne
from mongo_connection import get_mongo_connection

# Full facility data for Liverpool Dock Estate terminals, docks, and facilities
facilities_data = [
    {"name": "Seaforth Container Terminal", "facilities": "Deep-sea and short-sea container services; STS cranes; expanded Seaforth Basin; ACL RoRo and container handling; automated gates; intermodal road-rail access."},
    {"name": "Royal Seaforth Dock", "facilities": "Shared infrastructure with RSCT; wind turbines; connected to Gladstone Dock; served by Canada Dock Branch rail line with 48-train capacity per day."},
    {"name": "Steel Terminal", "facilities": "UK's first fully automated steel terminal; multi-user covered storage; direct rail siding; handles steel coil, plate, and long products."},
    {"name": "Gladstone Grain Terminal", "facilities": "Large-scale bulk grain handling; TASCC and GAFTA compliant; conveyor systems; adjacent to grain mills and road access to M57/M62."},
    {"name": "Grain Mills", "facilities": "Onsite grain processing facilities linked to terminal silos; used by Cargill and AB Agri; road-based distribution."},
    {"name": "Cargill Crushing Plant", "facilities": "Cargill's integrated rapeseed and soy crushing facility; supplies edible oil refinery and biodiesel plant; integrated with biomass logistics."},
    {"name": "Gladstone Dock No. 2", "facilities": "Connected to biomass and scrap handling; part of 3-dock complex with deep-water berths and coal import history."},
    {"name": "Gladstone Dock No. 1", "facilities": "Container and dry bulk support; links to biomass and project cargo operations; integrated with RSCT rail upgrades."},
    {"name": "Liverpool Biomass Terminal", "facilities": "£100M terminal for imported biomass (mainly from North America); conveyor discharge to Drax rail network; supports decarbonisation strategy."},
    {"name": "Gladstone Dock No. 3", "facilities": "Access to heavy-lift and scrap cargo quay; used for overflow or support services."},
    {"name": "P&O European Ferries Terminal", "facilities": "Dedicated RoRo ferry terminal; vehicle holding yards; customs clearance zones; serves European RoRo network."},
    {"name": "Gladstone Lock", "facilities": "Large lock gate (1,400ft × 140ft × 60ft); connects Mersey to Gladstone complex; handles vessels up to 14,000 TEU."},
    {"name": "Hornby Dock", "facilities": "Historic timber trade dock; now partially infilled to expand adjacent coal terminal; limited current use."},
    {"name": "Alexandra Dock", "facilities": "Handles recycled metal export and breakbulk; three branch docks; former grain and cold storage facilities."},
    {"name": "Alexandra Branch Dock No. 2", "facilities": "Part of Alexandra Dock; used for scrap metal, general cargo; connected by rail and road; legacy cold storage links."},
    {"name": "Langton Dock", "facilities": "Former cruise embarkation dock; Langton Lock connects to river; heritage pump house and filled-in graving docks."},
    {"name": "Seatruck Ferries", "facilities": "Seatruck Ferries RoRo terminal for unaccompanied freight; vehicle marshaling and secure gate system."},
    {"name": "Logistics Park", "facilities": "Peel Ports Logistics Park; warehouse and container cross-dock sites; proximity to RSCT and motorway network."},
    {"name": "Maritime Centre", "facilities": "Port management and admin offices; operations coordination; integrated Peel Ports logistics planning hub."},
    {"name": "Rail Terminal", "facilities": "Intermodal rail terminal serving RSCT and biomass terminal; direct West Coast Mainline connection via Olive Mount chord."},
    {"name": "Brocklebank Dock", "facilities": "Historic timber and liner terminal; used for freight to Belfast; access via Langton River entrance; semi-active."},
    {"name": "Brocklebank Branch Dock", "facilities": "Support basin to Brocklebank Dock; limited current use; legacy timber wharf structures."},
    {"name": "Canada Dock", "facilities": "Timber handling heritage; three branch docks and graving dock; Canada Dock Branch railway legacy site."},
    {"name": "Huskisson Dock", "facilities": "Former grain and passenger dock; large basin and two branch docks; North American liner trade history."},
    {"name": "World Fuel Services", "facilities": "Fuel storage and bunkering operations; linked to World Fuel Services; secure hazardous goods handling."},
    {"name": "Cargill Edible Oil Refinery", "facilities": "Processes edible oils for food and industrial use; linked to Cargill Crushing Plant; piping and tank storage."},
    {"name": "Sandon Half Tide Dock", "facilities": "Historic dock site now part of sewage infrastructure; formerly graving dock hub; enclosed water basin."},
    {"name": "Wellington Dock", "facilities": "Former dock used for Tall Ships Race; now part of United Utilities treatment facility; historic dock walls remain."},
    {"name": "Bromley-Moore Dock", "facilities": "Now filled and home to Everton FC Stadium; formerly used for coal exports; Grade II-listed hydraulic tower on site."},
    {"name": "Liverpool Cruise Terminal", "facilities": "Cruise embarkation terminal; customs and passport control; tender and cruise ship docking infrastructure."},
    {"name": "Super Secret Ferry Terminal", "facilities": "Placeholder name (Super Secret Ferry Terminal); assumed additional ferry operations staging area."},
    {"name": "Liverpool Produce Terminal", "facilities": "Fruit and vegetable cargo import terminal; cold storage capacity; links to supermarkets and wholesale logistics."},
    {"name": "Tranmere Oil Terminal", "facilities": "Tranmere Oil Terminal handles import/export of crude and refined oil. Includes 3 deep-water berths and connection to national pipeline and refinery infrastructure."},
    {"name": "Cammell Laird Shipyard", "facilities": "Cammell Laird Shipyard is a major shipbuilding and repair facility with deep water dry docks, outfitting berths, fabrication halls, and naval contracts."},
    {"name": "Woodside Ferry Terminal", "facilities": "Woodside Ferry Terminal serves Mersey Ferry passenger services between Liverpool and Birkenhead. It has a historic terminal building and small vessel berths with tourist and commuter access."},
    {"name": "Twelve Quays Terminal", "facilities": "Twelve Quays is a RoRo terminal serving daily unaccompanied freight and passenger ferry services to Belfast and Dublin. Includes customs facilities, marshaling yards, and warehousing nearby."},
    {"name": "Morpeth Dock", "facilities": "Morpeth Dock is a heritage dock now partly used for leisure craft and museum exhibits. Historically used for inland barge cargo and linked to the Egerton Dock basin."},
    {"name": "Egerton Dock", "facilities": "Egerton Dock was once used for timber and coastal cargo, now partially filled or decommissioned. Historic dock walls remain visible with restricted access."},
    {"name": "Alfred Dock", "facilities": "Alfred Dock is used for commercial bulk cargo handling. Connected via Alfred Lock to the river; services include dry bulk and short-sea shipping operations."},
    {"name": "Alfred Lock", "facilities": "Alfred Lock provides river access for Alfred Dock and East Float; allows vessels to enter Birkenhead system from the River Mersey. Operates during tidal windows."},
    {"name": "East Float", "facilities": "East Float is a large multipurpose dock formerly used for grain, steel, and timber. Now includes Cammell Laird’s outfitting quay and part of Wirral Waters redevelopment."},
    {"name": "Victoria Dock", "facilities": "Victoria Dock is under redevelopment for marine industrial and mixed-use. Historically handled timber and bagged cargo with railway sidings nearby."},
    {"name": "West Float", "facilities": "West Float is one of the largest Birkenhead basins; currently used for project cargo, dry bulk, and heavy lift; includes deep water quays and ample laydown area."},
    {"name": "Bidston Graving Dock No.3", "facilities": "Bidston Graving Dock No.3 is a historic dry dock, now disused and partially filled. Formerly used for ship maintenance within the Birkenhead ship repair cluster."},
    {"name": "Mobil Oil Works Site", "facilities": "Mobil Oil Works Site formerly held petrochemical and fuel infrastructure. Now cleared and under regeneration as part of the Bidston industrial corridor."},
    {"name": "Bidston Dev Site", "facilities": "Bidston Dev Site is a planned logistics and industry hub, part of Peel’s wider Wirral Waters project. Vacant land intended for port-centric development."}
]

def update_facilities():
    db = get_mongo_connection()
    collection = db["port_areas"]

    operations = []
    for item in facilities_data:
        operations.append(
            UpdateOne(
                {"properties.name": item["name"]},
                {"$set": {"properties.facilities": item["facilities"]}}
            )
        )

    if operations:
        result = collection.bulk_write(operations)
        print(f"Matched: {result.matched_count}, Modified: {result.modified_count}")
    else:
        print("No updates to perform.")

if __name__ == "__main__":
    update_facilities()
