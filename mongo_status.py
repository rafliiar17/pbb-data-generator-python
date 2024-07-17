import os  # Import the os module to interact with the filesystem
from pymongo import MongoClient
import subprocess  # Import subprocess to execute shell commands
import sys
import platform

def check_and_start_mongodb_service():
    os_name = platform.system()
    if os_name == "Windows":
        try:
            result = subprocess.run(["sc", "query", "MongoDB"], capture_output=True, text=True)
            if "RUNNING" not in result.stdout:
                print("MongoDB service is not running.")
                start_service = input("Do you want to start the MongoDB service? (yes/no): ").strip().lower()
                if start_service == 'yes':
                    try:
                        subprocess.run(["net", "start", "MongoDB"], check=True)
                        print("MongoDB service started.")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to start MongoDB service: {e}")
                        print("Please ensure the script is running with administrator privileges.")
                        run_as_admin = input("Do you want to run as administrator? (yes/no): ").strip().lower()
                        if run_as_admin == 'yes':
                            subprocess.run(["run_as_admin.bat"], check=True)
                            sys.exit(0)
                        else:
                            sys.exit(1)
                else:
                    print("Exiting as MongoDB service is not started.")
                    sys.exit(1)
            else:
                print("MongoDB service is already running.")
        except subprocess.CalledProcessError as e:
            print(f"Error checking MongoDB service: {e}")
            sys.exit(1)
    elif os_name == "Linux":
        try:
            result = subprocess.run(["systemctl", "status", "mongodb"], capture_output=True, text=True)
            if "active (running)" not in result.stdout:
                print("MongoDB service is not running.")
                start_service = input("Do you want to start the MongoDB service? (yes/no): ").strip().lower()
                if start_service == 'yes':
                    try:
                        subprocess.run(["sudo", "systemctl", "start", "mongodb"], check=True)
                        print("MongoDB service started.")
                    except subprocess.CalledProcessError as e:
                        print(f"Failed to start MongoDB service: {e}")
                        sys.exit(1)
                else:
                    print("Exiting as MongoDB service is not started.")
                    sys.exit(1)
            else:
                print("MongoDB service is already running.")
        except subprocess.CalledProcessError as e:
            print(f"Error checking MongoDB service: {e}")
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
                if platform.system() == "Windows":
                    subprocess.run(["net", "stop", "MongoDB"], check=True)
                    subprocess.run(["net", "start", "MongoDB"], check=True)
                elif platform.system() == "Linux":
                    subprocess.run(["sudo", "systemctl", "restart", "mongodb"], check=True)
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

if db is None or db1 is None:
    print("If access is denied, please run run_as_admin.bat")

def get_mongodb_uri():
    # Replace this with your actual logic to fetch the MongoDB URI dynamically
    # Example: Read from a configuration file, environment variables, etc.
    uri = "mongodb://localhost:27017/"  # Placeholder URI, replace with actual logic
    return uri

if __name__ == "__main__":
    uri = get_mongodb_uri()
    print(f"MongoDB URI fetched: {uri}")
