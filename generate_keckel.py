import json
import random
import os
from faker import Faker

fake = Faker()

def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def generate_kecamatan_kelurahan_data(kab_code, num_kecamatan, num_kelurahan_per_kecamatan):
    kecamatan_data = {}

    for kecamatan_index in range(1, num_kecamatan + 1):
        kecamatan_code = int(f"{int(kab_code)}{kecamatan_index:03d}")  # Ensure kecamatan_code is an integer
        kecamatan_nama = fake.city()

        status_kec = random.choice([True, False])  # Generate status_kec here

        kecamatan_record = {
            "kecamatan_code": kecamatan_code,
            "kecamatan_nama": kecamatan_nama,
            "sektor_kec": random.choice([10, 20]),
            "status_kec": status_kec,
            "kelurahan": []
        }

        for kelurahan_index in range(1, num_kelurahan_per_kecamatan + 1):
            kelurahan_code = int(f"{kecamatan_code}{kelurahan_index:03d}")  # Ensure kelurahan_code is an integer
            kelurahan_nama = fake.street_name()

            # Set status_kel based on status_kec
            status_kel = status_kec if not status_kec else random.choice([True, False])

            kelurahan_record = {
                "kelurahan_code": kelurahan_code,
                "kelurahan_nama": kelurahan_nama,
                "sektor_kel": random.choice([10, 20]),
                "status_kel": status_kel
            }
            kecamatan_record["kelurahan"].append(kelurahan_record)

        kecamatan_data[kecamatan_code] = kecamatan_record

    return kecamatan_data

def save_data(data, filename):
    # Ensure the directory exists
    output_dir = os.path.dirname(filename)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    config_data = load_config()

    kab_code = config_data.get('kab_code')
    kab_name = config_data.get('kab_name')
    num_kecamatan = config_data.get('kec_kel', {}).get('number_kecamatan')
    num_kelurahan_per_kecamatan = config_data.get('kec_kel', {}).get('number_kelurahan')

    if not kab_code or not num_kecamatan or not num_kelurahan_per_kecamatan:
        print("Error: 'kab_code', 'num_kecamatan', and 'num_kelurahan_per_kecamatan' must be defined in config.json")
        exit(1)

    kecamatan_records = generate_kecamatan_kelurahan_data(kab_code, num_kecamatan, num_kelurahan_per_kecamatan)

    # Ensure the directory exists
    output_dir = 'CONFIG_DATA'
    os.makedirs(output_dir, exist_ok=True)

    # Save kecamatan and kelurahan data to a single JSON file
    output_path = os.path.join(output_dir, 'kecamatan_kelurahan_data.json')
    save_data(kecamatan_records, output_path)

    print(f"Generated and saved {num_kecamatan} kecamatan and {num_kelurahan_per_kecamatan} kelurahan records for {kab_code} - {kab_name} to '{output_path}'.")