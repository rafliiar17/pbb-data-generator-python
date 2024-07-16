import os  # Import the os module to interact with the filesystem
from pymongo import MongoClient
import json
import logging
from tqdm import tqdm  # You might need to install this with `pip install tqdm`
import subprocess  # Import subprocess to execute shell commands
import sys
import ctypes
import platform

# Ensure the log directory exists
log_directory = 'log'
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Configure logging to file
logging.basicConfig(filename=os.path.join(log_directory, 'log_db.txt'), level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    print("Trying to restart with administrative privileges")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    sys.exit(0)

def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
        print("Config loaded")
    return config

def check_and_start_mongodb_service():
    os_name = platform.system()
    if os_name == "Windows":
        try:
            result = subprocess.run(["sc", "query", "MongoDB"], capture_output=True, text=True)
            if "RUNNING" not in result.stdout:
                print("MongoDB service is not running. Attempting to start MongoDB service...")
                subprocess.run(["net", "start", "MongoDB"], check=True)
                print("MongoDB service started.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to start MongoDB service: {e}")
            print("Please ensure the script is running with administrator privileges.")
            sys.exit(1)
    elif os_name == "Linux":
        try:
            result = subprocess.run(["systemctl", "status", "mongodb"], capture_output=True, text=True)
            if "active (running)" not in result.stdout:
                print("MongoDB service is not running. Attempting to start MongoDB service...")
                subprocess.run(["sudo", "systemctl", "start", "mongodb"], check=True)
                print("MongoDB service started.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to start MongoDB service: {e}")
            print("Please ensure you have the necessary permissions.")
            sys.exit(1)
    else:
        print(f"Operating system {os_name} not supported for this script.")
        sys.exit(1)

def connect_to_mongodb(uri, db_name):
    max_retries = 3  # Maximum number of retries
    for attempt in range(max_retries):
        try:
            check_and_start_mongodb_service()  # Ensure MongoDB service is running
            client = MongoClient(uri)
            db = client[db_name]
            print(f"Connected to MongoDB database: {db_name}")
            return db
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                print("Attempting to restart MongoDB service...")
                # Restart MongoDB service
                subprocess.run(["net", "stop", "MongoDB"], check=True)
                subprocess.run(["net", "start", "MongoDB"], check=True)
                print("MongoDB service restarted. Retrying connection...")
            else:
                print("Failed to connect to MongoDB after several attempts.")
                return None

# Example usage
uri = "mongodb://localhost:27017/"
db_name = "GW_PBB"
db_name1 = "SW_PBB"
db = connect_to_mongodb(uri, db_name)
db1 = connect_to_mongodb(uri, db_name1)  # Ensure db1 is defined for SW_PBB

def export_json_to_mongo(db, json_file_path, collection_name, nop, tahun):
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            collection = db[collection_name]
            # Drop the existing collection if it exists
            db.drop_collection(collection_name)
            logging.info(f"Collection {collection_name} dropped.")
            
            total = len(data)
            for i, document in enumerate(tqdm(data, desc=f"Inserting documents into {collection_name} collection")):  # Utilize tqdm for progress indication
                collection.insert_one(document)
                logging.info(f"Processed record {document} for NOP: {nop}, Year: {tahun}")
            print(f"All data from {json_file_path} has been successfully inserted into the {collection_name} collection.")
    except Exception as e:
        logging.error(f"Error processing record for NOP: {nop}, Year: {tahun}: {e}")

# Load configuration
config = load_config()

# Example usage for PBB_SPPT
tahun = config['tahun_pajak']
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

json_file_path_keckel = "CONFIG_DATA/kecamatan_kelurahan_data.json"
collection_name_keckel = "WILAYAH"
export_json_to_mongo(db1, json_file_path_keckel, collection_name_keckel, nop="1234567890", tahun=tahun)

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