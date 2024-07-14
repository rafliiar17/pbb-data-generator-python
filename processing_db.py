from pymongo import MongoClient
import json
import logging
from tqdm import tqdm  # You might need to install this with `pip install tqdm`

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
        print("Config loaded")
    return config

def connect_to_mongodb(uri, db_name):
    try:
        client = MongoClient(uri)
        db = client[db_name]
        print(f"Connected to MongoDB database: {db_name}")
        return db
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
uri = "mongodb://localhost:27017/"
db_name = "GW_PBB"
db = connect_to_mongodb(uri, db_name)

def export_json_to_mongo(db, json_file_path, collection_name):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            collection = db[collection_name]
            # Drop the existing collection if it exists
            db.drop_collection(collection_name)
            logging.info(f"Collection {collection_name} dropped.")
            
            total = len(data)
            for i, document in enumerate(data):
                collection.insert_one(document)
                logging.info(f"Document {i+1}/{total} inserted into {collection_name}")
            print(f"All data from {json_file_path} has been successfully inserted into the {collection_name} collection.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

# Load configuration
config = load_config()

# Example usage
tahun = config['tahun_pajak']
json_file_path = f"GW_PBB/{tahun}/pbb_sppt.json"  # Corrected string formatting
collection_name = "PBB_SPPT"
export_json_to_mongo(db, json_file_path, collection_name)