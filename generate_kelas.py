import json
import random
import os


def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def generate_kelas_bumi_data(min_year, max_year):
    kelas_bumi_data = []

    # Limit num_records to 150
    num_records = 250

    for i in range(num_records):
        kelas_bumi = f"A{i + 1}"
        mnvalue = 100 + (i * 50)
        mxvalue = mnvalue + 49
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
        mnvalue = 100 + (i * 50)
        mxvalue = mnvalue + 49
        avgvalue = round((mnvalue + mxvalue) / 2, 0)
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
    config_data = load_config()

    min_year = config_data.get('year', {}).get('min_year')
    max_year = config_data.get('year', {}).get('max_year')

    kelas_bumi_records = generate_kelas_bumi_data(min_year, max_year)
    kelas_bgn_records = generate_kelas_bangunan_data(min_year, max_year)

    # Ensure the directory exists
    output_dir = 'CONFIG_DATA'
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