import subprocess
import json
from tqdm import tqdm

def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

config = load_config()
tahun = config.get('tahun_pajak')
kode = config.get('kab_code')
nama = config.get('kab_name')

# Define the commands to be executed with the tax year passed as argument
initial_commands = [ 
    'python generate_keckel.py',
    'python generate_znt.py',
    'python generate_kelas.py',
    'python generate_nop.py',
    'python generate_op.py'
]

# Execute initial commands sequentially with a progress bar
for command in tqdm(initial_commands, desc="Executing initial commands", unit="command"):
    subprocess.run(command, shell=True)
    print()  # Add a newline after each command execution

# Check if auto_assdet is false and prompt for confirmation
if not config.get('auto_assdet', True):
    confirm = input(f"Do you want to execute Assesment and Determination for {kode} : {nama} year {tahun} (yes/no): ").strip().lower()
    if confirm == 'yes':
        subprocess.run('python processing_assesment.py', shell=True)
        print()  # Add a newline after the command execution
        subprocess.run('python processing_determination.py', shell=True)
        print()  # Add a newline after the command execution
else:
    subprocess.run('python processing_assesment.py', shell=True)
    print()  # Add a newline after the command execution
    subprocess.run('python processing_determination.py', shell=True)
    print()  # Add a newline after the command execution