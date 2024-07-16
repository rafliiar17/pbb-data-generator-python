import json
import os
from tqdm import tqdm
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def generate_kelas_bumi_data(min_year, max_year, num_records, pbar):
    kelas_bumi_data = []

    for i in range(num_records):
        kelas_bumi = f"A{i + 1}"
        mnvalue = 200 + (i * 50)
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
        pbar.update(1)  # Update the progress bar by 1 for each record processed

    return kelas_bumi_data

def generate_kelas_bangunan_data(min_year, max_year, num_records, pbar):
    kelas_bgn_data = []

    for i in range(num_records):
        kelas_bgn = f"A{i + 1}"
        mnvalue = 250 + (i * 50)
        mxvalue = mnvalue + 49
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
        pbar.update(1)  # Update the progress bar by 1 for each record processed

    return kelas_bgn_data

if __name__ == "__main__":
    config_data = load_config()

    min_year = config_data.get('year', {}).get('min_year')
    max_year = config_data.get('year', {}).get('max_year')
    num_records = config_data.get('maxkelas', 150)  # Default to 150 if 'maxkelas' is not defined in config

    # Example values for kode_kab and kab_name
    kode_kab = config_data['kab_code']
    kab_name = config_data['kab_name']
    written_count = 0

    with tqdm(total=num_records * 2, desc="Generating NOP " + str(kode_kab) + " " + str(kab_name), bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.GREEN, Fore.RESET)) as pbar:
        kelas_bumi_records = generate_kelas_bumi_data(min_year, max_year, num_records, pbar)
        kelas_bgn_records = generate_kelas_bangunan_data(min_year, max_year, num_records, pbar)

    # Ensure the directory exists
    output_dir = 'GENERATED_DATA'
    os.makedirs(output_dir, exist_ok=True)

    # Save to JSON files
    output_path_bumi = os.path.join(output_dir, 'kelas_bumi.json')
    with open(output_path_bumi, 'w') as f:
        json.dump(kelas_bumi_records, f, indent=4)

    # Calculate file size in MB
    file_size_bumi = os.path.getsize(output_path_bumi) / (1024 * 1024)
    print(f"Generated and saved kelas bumi records to '{output_path_bumi}' - Size: {file_size_bumi:.2f} MB.")

    output_path_bgn = os.path.join(output_dir, 'kelas_bangunan.json')
    with open(output_path_bgn, 'w') as f:
        json.dump(kelas_bgn_records, f, indent=4)

    # Calculate file size in MB
    file_size_bgn = os.path.getsize(output_path_bgn) / (1024 * 1024)
    print(f"Generated and saved kelas bangunan records to '{output_path_bgn}' - Size: {file_size_bgn:.2f} MB.")
