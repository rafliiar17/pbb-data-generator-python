import json
import argparse
import random
import os

from faker import Faker

fake = Faker()

# Define options for znt_code
OP_ZNT_OPTIONS = [chr(i) + chr(j) for i in range(65, 91) for j in range(65, 91)]  # AA to ZZ

def load_kecamatan_kelurahan_data():
    filename = 'CONFIG_DATA/kecamatan_kelurahan_data.json'  # Adjust path as necessary
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def generate_znt_data(tahun_pajak_range, kecamatan_kelurahan_data):
    min_year, max_year = tahun_pajak_range
    znt_data = []
    previous_nir_dict = {}

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
                    previous_nir_dict[key] = previous_nir + 10  # Increment nir by 1000 for the next entry

    return znt_data

def save_znt_data(znt_data):
    output_dir = 'CONFIG_DATA'  # Adjust output directory as necessary
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, 'znt_data.json')
    with open(filename, 'w') as f:
        json.dump(znt_data, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--min_year', type=int, required=True, help='Minimum year')
    parser.add_argument('--max_year', type=int, required=True, help='Maximum year')
    args = parser.parse_args()

    tahun_pajak_range = (args.min_year, args.max_year)

    kecamatan_kelurahan_data = load_kecamatan_kelurahan_data()

    znt_data = generate_znt_data(tahun_pajak_range, kecamatan_kelurahan_data)

    save_znt_data(znt_data)

    print(f"Generated ZNT records for years {args.min_year}-{args.max_year} and saved to 'CONFIG_DATA/znt_data.json'.")
