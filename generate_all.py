import subprocess
import logging
import json
from datetime import datetime
import os

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure the log directory exists
if not os.path.exists('log'):
    os.makedirs('log', exist_ok=True)

# Create backup directory only if all specified directories exist
directories_to_backup = ['CONFIG_DATA', 'GW_PBB', 'SW_PBB', 'log']
backup_dir = None  # Initialize backup_dir as None
if all(os.path.exists(directory) for directory in directories_to_backup):
    backup_dir = f'PBB_BACKUP_MASTER_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}'
    os.makedirs(backup_dir, exist_ok=True)

if backup_dir is not None:
    for directory in directories_to_backup:
        if os.path.exists(directory):
            # Perform the copy operation using robocopy or rsync based on OS
            if os.name == 'nt':  # Windows
                result = subprocess.run(['robocopy', directory, f"{backup_dir}\\{directory}", '/E'], capture_output=True, text=True)
            else:  # Linux or other Unix-like OS
                result = subprocess.run(['rsync', '-a', directory, f"{backup_dir}/{directory}"], capture_output=True, text=True)
            
            if result.returncode in [0, 1]:  # robocopy returns 1 for successful copies, rsync returns 0
                logging.info(f"Successfully copied {directory} to {backup_dir}")
                # Remove the directory after successful backup using appropriate command
                if os.name == 'nt':  # Windows
                    subprocess.run(['cmd.exe', '/c', 'rmdir', '/s', '/q', directory], capture_output=True, text=True)
                else:  # Linux or other Unix-like OS
                    subprocess.run(['rm', '-rf', directory], capture_output=True, text=True)
                logging.info(f"Successfully removed {directory}")
            else:
                logging.error(f"Failed to copy {directory}. Error: {result.stderr}")

# Setup logging with timestamp in the filename
current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
log_filename = f'log/log_{current_time}.json'
logging.basicConfig(level=logging.INFO, filename=log_filename, filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')

def run_script(script_name):
    """ Helper function to run a script and log the result """
    try:
        subprocess.run(['python', script_name], check=True)
        logging.info(f"Execution of {script_name} completed successfully.")
    except subprocess.CalledProcessError:
        logging.error(f"Execution of {script_name} failed.")

def main():
    # Load configuration
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
    
    scripts = [
        'generate_keckel.py',
        'generate_kelas.py',
        'generate_znt.py',
        'generate_nop.py',
        'generate_op.py',
        'generate_penetapan.py',
        'generate_paycode.py'
    ]
    
    # Automatically add assessment scripts if enabled in config
    if config.get('auto_assdet', False):
        scripts.extend([
            'processing_assesment.py',
            'processing_determination.py',
            'processing_final.py',
            'processing_db.py'
        ])
    
    for script in scripts:
        run_script(script)

if __name__ == "__main__":
    main()