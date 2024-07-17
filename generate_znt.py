import json
import os
import random
from alive_progress import alive_bar
from colorama import Fore, init
import io
import sys
# Redirect stdout to a file
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# Function to load configuration data from config.json
def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to load kecamatan_kelurahan_data from JSON file
def load_kecamatan_kelurahan_data():
    file_path = 'CONFIG_DATA/kecamatan_kelurahan_data.json'  # Adjust path as necessary
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Define options for znt_code
OP_ZNT_OPTIONS = [chr(i) + chr(j) for i in range(65, 91) for j in range(65, 91)]  # AA to ZZ

# Function to generate ZNT data
def generate_znt_data(tahun_pajak_range, kecamatan_kelurahan_data):
    min_year, max_year = tahun_pajak_range
    znt_data = []
    previous_nir_dict = {}
    total_iterations = len(kecamatan_kelurahan_data) * (max_year - min_year)

    # Use alive_bar to display progress
    with alive_bar(total_iterations, title="Generating ZNT data") as progress:
        for kecamatan_code, kecamatan_info in kecamatan_kelurahan_data.items():
            for kelurahan in kecamatan_info.get('kelurahan', []):
                if not kelurahan.get('status_kel', False):  # Check if status_kel is true
                    continue  # Skip if status_kel is false

                kelurahan_code = kelurahan['kelurahan_code']
                possible_combinations = list(OP_ZNT_OPTIONS)  # Create a copy of OP_ZNT_OPTIONS for each kelurahan_code
                random.shuffle(possible_combinations)

                for tahun_pajak in range(min_year, max_year + 1):
                    for znt_code in possible_combinations:
                        key = (kelurahan_code, znt_code)

                        # Fetch previous nir value or initialize to 1000 if not present
                        previous_nir = previous_nir_dict.get(key, random.randint(100, 300))

                        znt_entry = {
                            "kecamatan_code": int(kecamatan_code),
                            "kelurahan_code": int(kelurahan_code),
                            "znt_code": znt_code,
                            "znt_year": tahun_pajak,
                            "nir": previous_nir  # Set nir value
                        }

                        znt_data.append(znt_entry)

                        # Update previous_nir_dict for the current combination
                        previous_nir_dict[key] = previous_nir + 10  # Increment nir by 10 for the next entry

                        progress()  # Update progress bar

    return znt_data

# Function to save ZNT data to JSON file
def save_znt_data(znt_data, kode_kab, kab_name):
    output_dir = 'CONFIG_DATA'  # Adjust output directory as necessary
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, 'znt_data.json')
    
    total_records = len(znt_data)
    print()
    # Use alive_bar to display progress
    with alive_bar(total_records, title="Saving ZNT records" ,enrich_print=False,length=25, bar=None, stats=False, monitor=True) as progress:
        with open(filename, 'w') as file:
            json.dump(znt_data, file, indent=4)
            progress()  # Update progress bar
    
    # Calculate file size in MB
    file_size = os.path.getsize(filename) / (1024 * 1024)  # Convert bytes to MB
    
    print(f"{Fore.GREEN}Saved ZNT records for {kode_kab} - {kab_name} to {filename} with {total_records} records. File size: {file_size:.2f} MB{Fore.RESET}")

# Main function to execute the script
if __name__ == "__main__":
    config_data = load_config()
    min_year = config_data.get('year', {}).get('min_year')
    max_year = config_data.get('year', {}).get('max_year')
    kode_kab = config_data.get('kab_code')
    kab_name = config_data.get('kab_name')

    if min_year is None or max_year is None:
        print("Error: 'min_year' and 'max_year' must be defined in config.json")
        exit(1)

    tahun_pajak_range = (min_year, max_year)

    kecamatan_kelurahan_data = load_kecamatan_kelurahan_data()

    znt_data = generate_znt_data(tahun_pajak_range, kecamatan_kelurahan_data)

    save_znt_data(znt_data, kode_kab, kab_name)