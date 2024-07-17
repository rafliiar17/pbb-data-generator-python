import os
import sys
import json
import logging
from tqdm import tqdm
from pymongo import MongoClient
import platform
from subprocess import CalledProcessError, run
from sys import exit
from mongo_status import get_mongodb_uri  # Import the function to fetch MongoDB URI

# Set the encoding to utf-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Change the default encoding for stdout and stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Ensure the log directory exists
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configure logging to file
logging.basicConfig(filename=os.path.join(log_directory, 'log_db.txt'), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
        print("Config loaded")
    return config

def export_json_to_mongo(db, json_file_path, collection_name, nop, tahun):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            collection = db[collection_name]
            # Drop the existing collection if it exists
            db.drop_collection(collection_name)
            logging.info(f"Collection {collection_name} dropped.")
            
            total = len(data)
            for i, document in enumerate(tqdm(data, desc=f"Inserting documents into {collection_name} collection")):
                collection.insert_one(document)
                logging.info(f"Processed record {document} for NOP: {nop}, Year: {tahun}")
            print(f"All data from {json_file_path} has been successfully inserted into the {collection_name} collection.")
    except Exception as e:
        logging.error(f"Error processing record for NOP: {nop}, Year: {tahun}: {e}")

# Load configuration
config = load_config()
tahun = config['tahun_pajak']

# Fetch MongoDB URI using the function from mongo_status.py
uri = get_mongodb_uri()

# Connect to MongoDB using the fetched URI
client = MongoClient(uri)
db = client["GW_PBB"]
db1 = client["SW_PBB"]  # Assuming db1 is for SW_PBB collections

# Example usage for PBB_SPPT
json_file_path_pbb = f"GW_PBB/{tahun}/pbb_sppt.json"
collection_name_pbb = "PBB_SPPT"
export_json_to_mongo(db, json_file_path_pbb, collection_name_pbb, nop="1234567890", tahun=tahun)

# Example usage for SW_PBB
json_file_path_sw = "SW_PBB/pbb_data_wp.json"
collection_name_sw = "WAJIB_PAJAK"
export_json_to_mongo(db1, json_file_path_sw, collection_name_sw, nop="1234567890", tahun=tahun)

# Example usage for ZNT_DATA
json_file_path_znt = "CONFIG_DATA/znt_data.json"
collection_name_znt = "ZNT_DATA"
export_json_to_mongo(db1, json_file_path_znt, collection_name_znt, nop="1234567890", tahun=tahun)

# Example usage for WILAYAH
json_file_path_keckel = "CONFIG_DATA/kecamatan_kelurahan_data.json"
collection_name_keckel = "WILAYAH"
export_json_to_mongo(db1, json_file_path_keckel, collection_name_keckel, nop="1234567890", tahun=tahun)

# Example usage for GENERATED_NOP
json_file_path_nop = "SW_PBB/generated_nop.json"
collection_name_nop = "GENERATED_NOP"
export_json_to_mongo(db1, json_file_path_nop, collection_name_nop, nop="1234567890", tahun=tahun)

# Dynamically find the latest assessment file
assessment_dir = "SW_PBB/pbb_data_assesment"
assessment_files = [f for f in os.listdir(assessment_dir) if f.startswith('pbb_data_assesment_')]
latest_file = max(assessment_files, key=lambda x: os.path.getctime(os.path.join(assessment_dir, x)))
json_file_path_assesment = os.path.join(assessment_dir, latest_file)
collection_name_assesment = "ASSESMENT_DATA"
export_json_to_mongo(db1, json_file_path_assesment, collection_name_assesment, nop="1234567890", tahun=tahun)

def check_os():
    os_name = platform.system()
    os_version = platform.release()
    return f"Operating System: {os_name}, Version: {os_version}"

# Example usage
print(check_os())
