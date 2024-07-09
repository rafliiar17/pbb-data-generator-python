import json
import random
import os
from faker import Faker

fake = Faker()

def generate_kecamatan_kelurahan_data(kab_code, num_kecamatan, num_kelurahan_per_kecamatan):
    kecamatan_data = {}

    for kecamatan_index in range(1, num_kecamatan + 1):
        kecamatan_code = int(f"{int(kab_code)}{kecamatan_index:03d}")
        kecamatan_nama = fake.city()

        kecamatan_record = {
            "kecamatan_code": kecamatan_code,
            "kecamatan_nama": kecamatan_nama,
            "sektor_kec": random.choice([10, 20]),
            "status_kec": random.choice([True, False]),
            "kelurahan": []
        }

        for kelurahan_index in range(1, num_kelurahan_per_kecamatan + 1):
            kelurahan_code = int(f"{kecamatan_code}{kelurahan_index:03d}")
            kelurahan_nama = fake.street_name()

            kelurahan_record = {
                "kelurahan_code": kelurahan_code,
                "kelurahan_nama": kelurahan_nama,
                "sektor_kel": random.choice([10, 20]),
                "status_kel": random.choice([True, False])
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
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--kab_code', type=str, required=True, help='Prefix for kode kabupaten')
    parser.add_argument('--num_kecamatan', type=int, required=True, help='Number of kecamatan to generate')
    parser.add_argument('--num_kelurahan_per_kecamatan', type=int, required=True, help='Number of kelurahan per kecamatan to generate')
    args = parser.parse_args()

    kab_code = args.kab_code
    num_kecamatan = args.num_kecamatan
    num_kelurahan_per_kecamatan = args.num_kelurahan_per_kecamatan

    kecamatan_records = generate_kecamatan_kelurahan_data(kab_code, num_kecamatan, num_kelurahan_per_kecamatan)

    # Ensure the directory exists
    output_dir = 'GENERATED_DATA'
    os.makedirs(output_dir, exist_ok=True)

    # Save kecamatan and kelurahan data to a single JSON file
    output_path = os.path.join(output_dir, 'kecamatan_kelurahan_data.json')
    save_data(kecamatan_records, output_path)

    print(f"Generated and saved kecamatan and kelurahan records to '{output_path}'.")