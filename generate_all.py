import subprocess
import logging
import json
from datetime import datetime
import os

# Create log directory if it doesn't exist
if not os.path.exists('log'):
    os.makedirs('log')

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