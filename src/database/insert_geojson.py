import json
from pymongo import MongoClient, UpdateOne

GEOJSON_PATH = "temp.geojson"
MONGO_URI = "mongodb://intern:SUhs*d2EqWh&kHmo@dif-fs01.liv.ac.uk:27017/metaliverpool-intern?authSource=metaliverpool-intern"
MONGO_DB = "metaliverpool-intern"
COLL = "port_areas"

with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    fc = json.load(f)

client = MongoClient(MONGO_URI)
db = client[MONGO_DB]
coll = db[COLL]

ops = []
for feat in fc.get("features", []):
    props = feat.get("properties", {})
    name = props.get("name")
    source = props.get("source", "Drawn manually with Geojson.io using official port plans by peel ports, UK govt, ABP Ports, and others.")
    if not name or not isinstance(feat.get("geometry", {}), dict):
        continue
    filt = {"properties.name": name, "properties.source": source}
    ops.append(UpdateOne(filt, {"$set": feat}, upsert=True))

if ops:
    res = coll.bulk_write(ops, ordered=False)
    print(f"Matched={res.matched_count} Modified={res.modified_count} Upserted={len(res.upserted_ids)}")
else:
    print("No valid features to insert.")
