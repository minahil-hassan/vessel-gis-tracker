from mongo_connection import db
# Test MongoDB connection and list collections

def test_mongo():
    collections = db.list_collection_names()
    print("Collections in DB:", collections)

if __name__ == "__main__":
    test_mongo()
