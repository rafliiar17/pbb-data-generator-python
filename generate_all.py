import subprocess
from tqdm import tqdm

if __name__ == "__main__":
    # Input tax year
    kab_code = input("Enter the kab_code (e.g., 8081): ")
    num_kecamatan = int(input("Enter the number of kecamatan (e.g., 5): "))
    num_kelurahan_per_kecamatan = int(input("Enter the number of kelurahan per kecamatan (e.g., 9): "))
    min_year = int(input("Enter ZNT/KELAS the min year (e.g., 2023): "))
    max_year = int(input("Enter ZNT/KELAS the max year (e.g., 2023): "))
    tahun_pajak = int(input("Enter DATA OP the tahun pajak (e.g., 2023): "))

    # Define the commands to be executed with the tax year passed as argument
    commands = [
        f'python generate_keckel.py --kab_code {kab_code} --num_kecamatan {num_kecamatan} --num_kelurahan_per_kecamatan {num_kelurahan_per_kecamatan}',
        f'python generate_znt.py --min_year {min_year} --max_year {max_year}',
        f'python generate_kelas.py --min_year {min_year} --max_year {max_year}',
        f'python generate_nop.py',
        f'python generate_op.py --tahun_pajak {tahun_pajak}',
    ]

    # Execute each command sequentially with a progress bar
    for command in tqdm(commands, desc="Executing commands", unit="command"):
        subprocess.run(command, shell=True)
