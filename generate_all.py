import json
import subprocess
from tqdm import tqdm

def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

if __name__ == "__main__":
    # Load configuration from config.json
    config = load_config('config.json')

    # Extract values from config
    kab_code = config["kab_code"]
    num_kecamatan = config["kec_kel"]["number_kecamatan"]
    num_kelurahan_per_kecamatan = config["kec_kel"]["number_kelurahan"]
    min_year = config["year"]["min_year"]
    max_year = config["year"]["max_year"]
    tahun_pajak = config["tahun_pajak"]

    # Define the commands to be executed with the tax year passed as argument
    commands = [
        f'python generate_keckel.py --kab_code {kab_code} --num_kecamatan {num_kecamatan} --num_kelurahan_per_kecamatan {num_kelurahan_per_kecamatan}',
        f'python generate_znt.py --min_year {min_year} --max_year {max_year}',
        f'python generate_kelas.py --min_year {min_year} --max_year {max_year}',
        f'python generate_nop.py',
        f'python generate_op.py --tahun_pajak {tahun_pajak}',
        f'python process_assdet.py'
    ]

    # Execute each command sequentially with a progress bar
    for command in tqdm(commands, desc="Executing commands", unit="command"):
        subprocess.run(command, shell=True)