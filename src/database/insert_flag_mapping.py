# insert_flag_mapping.py

import pandas as pd
from pymongo import MongoClient

# Step 1: Read the CSV
df = pd.read_csv("C:\\Users\\minahil\\vec\\vehicle-gis-platform\\data\\csv\\mid_to_iso.csv")

# Step 2: Optional - clean ISO values to lowercase
df["ISO"] = df["ISO"].str.lower()

# Step 3: Connect to MongoDB
from src.database.mongo_connection import get_mongo_connection
db = get_mongo_connection()

# Step 4: Create or access the collection
flag_collection = db["mmsi_flags"]

# Step 5: Insert documents
documents = df.to_dict(orient="records")
flag_collection.insert_many(documents)
flag_collection.create_index("MID", unique=True)


print(f"Inserted {len(documents)} MID → ISO flag mappings into 'mmsi_flags' collection.")
