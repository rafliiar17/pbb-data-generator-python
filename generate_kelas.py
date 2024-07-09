import json
import random
import os

def generate_kelas_bumi_data(min_year, max_year):
    kelas_bumi_data = []

    # Limit num_records to 150
    num_records = 250

    for i in range(num_records):
        kelas_bumi = f"A{i + 1}"
        mnvalue = round(random.uniform(100, 200), 0)
        mxvalue = round(random.uniform(201, 300), 0)
        avgvalue = round((mnvalue + mxvalue) / 2, 0)

        record = {
            "kelas_bumi": kelas_bumi,
            "fyear": min_year,
            "lyear": max_year,
            "mnvalue": mnvalue,
            "mxvalue": mxvalue,
            "avgvalue": avgvalue
        }
        kelas_bumi_data.append(record)

    return kelas_bumi_data

def generate_kelas_bangunan_data(min_year, max_year):
    kelas_bgn_data = []

    # Limit num_records to 150
    num_records = 250

    for i in range(num_records):
        kelas_bgn = f"A{i + 1}"
        mnvalue = round(random.uniform(101, 201), 0)
        mxvalue = round(random.uniform(201, 301), 0)
        avgvalue = round((mnvalue + mxvalue) / 2, 0)

        record = {
            "kelas_bangunan": kelas_bgn,
            "fyear": min_year,
            "lyear": max_year,
            "mnvalue": mnvalue,
            "mxvalue": mxvalue,
            "avgvalue": avgvalue
        }
        kelas_bgn_data.append(record)

    return kelas_bgn_data

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--min_year', type=int, required=True, help='Minimum year for data generation')
    parser.add_argument('--max_year', type=int, required=True, help='Maximum year for data generation')
    args = parser.parse_args()

    min_year = args.min_year
    max_year = args.max_year

    kelas_bumi_records = generate_kelas_bumi_data(min_year, max_year)
    kelas_bgn_records = generate_kelas_bangunan_data(min_year, max_year)

    # Ensure the directory exists
    output_dir = 'GENERATED_DATA'
    os.makedirs(output_dir, exist_ok=True)

    # Save to JSON files
    output_path_bumi = os.path.join(output_dir, 'kelas_bumi.json')
    with open(output_path_bumi, 'w') as f:
        json.dump(kelas_bumi_records, f, indent=4)
    print(f"Generated and saved kelas bumi records to '{output_path_bumi}'.")

    output_path_bgn = os.path.join(output_dir, 'kelas_bangunan.json')
    with open(output_path_bgn, 'w') as f:
        json.dump(kelas_bgn_records, f, indent=4)
    print(f"Generated and saved kelas bangunan records to '{output_path_bgn}'.")
