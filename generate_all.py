import subprocess
import json
import logging
from datetime import datetime
import os
from alive_progress import alive_bar
from colorama import Fore
import sys


def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

config_data = load_config()

kab_code = config_data.get('kab_code')
kab_name = config_data.get('kab_name')
print(f"Generating Data of {kab_code} - {kab_name}")
# Set the encoding to utf-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Change the default encoding for stdout and stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# Create the log directory if it doesn't exist
log_dir = 'log'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Define the log file path
log_filename = f'{log_dir}/log_process.txt'

# Setup logging to display in console and save to the specified log file
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

# Create backup directory only if all specified directories exist
directories_to_backup = ['CONFIG_DATA', 'GW_PBB', 'SW_PBB', 'log']
backup_dir = None  # Initialize backup_dir as None
if all(os.path.exists(directory) for directory in directories_to_backup):
    backup_dir = f'PBB_BACKUP_MASTER/DATA_PBB_{datetime.now().strftime("%Y%m%d_%H%M%S")}'
    os.makedirs(backup_dir, exist_ok=True)

if backup_dir is not None:
    for directory in directories_to_backup:
        if os.path.exists(directory):
            # Perform the copy operation using robocopy or rsync based on OS
            if os.name == 'nt':  # Windows
                result = subprocess.run(['robocopy', directory, f"{backup_dir}\\{directory}", '/E'], capture_output=True, text=True, encoding='utf-8')
            else:  # Linux or other Unix-like OS
                result = subprocess.run(['rsync', '-a', directory, f"{backup_dir}/{directory}"], capture_output=True, text=True, encoding='utf-8')
            
            if result.returncode in [0, 1]:  # robocopy returns 1 for successful copies, rsync returns 0
                logging.info(f"Successfully copied {directory} to {backup_dir}")
            else:
                logging.error(f"Failed to copy {directory}. Error: {result.stderr}")

# Define the scripts to run in sequence
scripts_to_run = [
    'mongo_status.py',
    'generate_keckel.py',
    'generate_kelas.py',
    'generate_znt.py',
    'generate_nop.py',
    'generate_op.py',
    'generate_penetapan.py',
    'generate_paycode.py',
    'processing_assesment.py',
    'processing_determination.py',
    'processing_final.py',
    'processing_db.py'
]

def run_scripts(scripts):
    try:
        # Update the progress bar display to handle encoding properly
        with alive_bar(len(scripts), title='Running Scripts', bar='smooth', spinner='classic') as bar:
            for script_name in scripts:
                if script_name.startswith('generate'):
                    logging.info(f"Running {script_name}...")
                try:
                    if script_name == 'mongo_status.py':
                        result = subprocess.run(['python', script_name], input='yes\n', capture_output=True, text=True, encoding='utf-8')
                    else:
                        result = subprocess.run(['python', script_name], capture_output=True, text=True, encoding='utf-8')
                    if result.returncode == 0:
                        logging.info(f"{Fore.GREEN}[{scripts.index(script_name)+1}/{len(scripts)}] Success: {script_name}{Fore.RESET}")
                    else:
                        logging.error(f"Execution of {script_name} failed. Error: {result.stderr}")
                except KeyboardInterrupt:
                    logging.error("Script execution interrupted by user.")
                    break
                bar()
        
        logging.info("All scripts executed successfully.")
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")

# Run the scripts
run_scripts(scripts_to_run)
