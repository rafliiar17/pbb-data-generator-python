import json
import os
from alive_progress import alive_bar
from colorama import Fore, init
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
# Initialize colorama
init(autoreset=True)

def load_config():
    file_path = 'config.json'
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"{Fore.RED}Error: Config file '{file_path}' not found.{Fore.RESET}")
        exit(1)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: Config file '{file_path}' is not a valid JSON.{Fore.RESET}")
        exit(1)

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
        pbar()  # Update the progress bar by 1 for each record processed

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
        pbar()  # Update the progress bar by 1 for each record processed

    return kelas_bgn_data

def save_data_with_progress(data, filename, title):
    total_records = len(data)
    
    # Remove the file if it already exists
    if os.path.exists(filename):
        os.remove(filename)

    print()
    # Use alive_bar to display progress
    with alive_bar(total_records, title=title) as progress:
        with open(filename, 'w') as file:
            file.write('[')  # Add opening bracket
            for i, record in enumerate(data):
                json.dump(record, file, indent=4)
                if i < total_records - 1:  # Add comma if not the last record
                    file.write(',')
                progress()  # Update progress bar
            file.write(']')  # Add closing bracket
    
    # Calculate file size in MB
    file_size = os.path.getsize(filename) / (1024 * 1024)  # Convert bytes to MB
    return file_size, total_records

if __name__ == "__main__":
    config_data = load_config()

    min_year = config_data.get('year', {}).get('min_year')
    max_year = config_data.get('year', {}).get('max_year')
    num_records = config_data.get('maxkelas', 150)  # Default to 150 if 'maxkelas' is not defined in config
    kode_kab = config_data['kab_code']
    kab_name = config_data['kab_name']

    if not min_year or not max_year:
        print(f"{Fore.RED}Error: 'min_year' and 'max_year' must be defined in config.json.{Fore.RESET}")
        exit(1)

    # Use alive_bar to display progress
    total_records = num_records * 2
    with alive_bar(total=total_records, title=f"Generating Kelas Bumi dan Bangunan : Kode {kode_kab} - {kab_name}", enrich_print=False,length=25, bar='classic2', spinner='wait4', stats=True, monitor=True) as pbar:
        kelas_bumi_records = generate_kelas_bumi_data(min_year, max_year, num_records, pbar)
        kelas_bgn_records = generate_kelas_bangunan_data(min_year, max_year, num_records, pbar)

    # Ensure the directory exists
    output_dir = 'CONFIG_DATA'
    os.makedirs(output_dir, exist_ok=True)

    # Save data with progress bar and file size calculation
    bumi_filename = os.path.join(output_dir, 'kelas_bumi.json')
    bumi_size, bumi_records = save_data_with_progress(kelas_bumi_records, bumi_filename, "Saving Kelas Bumi Data")
    print(f"{Fore.GREEN}Saved Kelas Bumi records for {kode_kab} - {kab_name} to {bumi_filename} with {bumi_records} records. File size: {bumi_size:.2f} MB")

    bgn_filename = os.path.join(output_dir, 'kelas_bangunan.json')
    bgn_size, bgn_records = save_data_with_progress(kelas_bgn_records, bgn_filename, "Saving Kelas Bangunan Data")
    print(f"{Fore.GREEN}Saved Kelas Bangunan records for {kode_kab} - {kab_name} to {bgn_filename} with {bgn_records} records. File size: {bgn_size:.2f} MB")
