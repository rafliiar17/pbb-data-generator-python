import json
import os
import time
from datetime import datetime
from tqdm import tqdm  # Import tqdm for progress bar
import shutil  # Import shutil for file copying

# Load config data
def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load pbb_data_{tahun}.json data
def load_pbb_data(tahun_pajak):
    file_path = f'DATA_OP/pbb_data_{tahun_pajak}.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load znt_data.json data
def load_znt_data():
    file_path = 'CONFIG_DATA/znt_data.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load kelas_bumi.json data
def load_kelas_bumi_data():
    file_path = 'CONFIG_DATA/kelas_bumi.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load kelas_bgn.json data
def load_kelas_bgn_data():
    file_path = 'CONFIG_DATA/kelas_bangunan.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to generate filename based on current datetime
def generate_filename():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    directory = "DATA_PENILAIAN"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return f"{directory}/assessment_{timestamp}.json"

# Function to get nir based on kelurahan_code, znt_code, and znt_year
def process_assessment(pbb_data, znt_data, kelas_bumi_data, kelas_bgn_data, tahun_pajak):
    nir_results = []
    pbar = tqdm(total=len(pbb_data), desc='Processing Assessment PBB Data', position=0, leave=True)
    
    for pbb_record in pbb_data:
        nop = pbb_record['nop']
        luas_bumi = pbb_record['data_op'].get('op_luas_bumi', 0)
        luas_bgn = pbb_record['data_op'].get('op_luas_bgn', 0)
        kelurahan_code = int(nop[:10])
        op_znt = pbb_record['data_op'].get('op_znt', '')

        # print(f"Processing NOP: {nop}, Kelurahan Code: {kelurahan_code}, ZNT Code: {op_znt}")

        for znt_record in znt_data:
            if (znt_record['kelurahan_code'] == kelurahan_code and
                znt_record['znt_code'] == op_znt and
                znt_record['znt_year'] == tahun_pajak):
                nir = znt_record['nir']
                # print(f"Found ZNT Record with NIR: {nir}")

                for kelas_bumi_record in kelas_bumi_data:
                    if (kelas_bumi_record['fyear'] <= tahun_pajak <= kelas_bumi_record['lyear'] and
                        kelas_bumi_record['mnvalue'] <= nir <= kelas_bumi_record['mxvalue']):
                        
                        for kelas_bgn_record in kelas_bgn_data:
                            if (kelas_bgn_record['fyear'] <= tahun_pajak <= kelas_bgn_record['lyear'] and
                                kelas_bgn_record['mnvalue'] <= nir <= kelas_bgn_record['mxvalue']):
                                
                                result = {
                                    "nop": nop,
                                    "kelurahan_code": kelurahan_code,
                                    "znt_code": op_znt,
                                    "znt_year": tahun_pajak,
                                    "znt_nir": nir,
                                    "luas_bumi": luas_bumi,
                                    "luas_bgn": luas_bgn,
                                    "kelas_bumi": kelas_bumi_record['kelas_bumi'],
                                    "njopm_bumi": kelas_bumi_record['avgvalue'],
                                    "kelas_bgn": kelas_bgn_record['kelas_bangunan'],
                                    "njopm_bgn": kelas_bgn_record['avgvalue'],
                                    "njop_bumi": round(luas_bumi * kelas_bumi_record['avgvalue'], 0),
                                    "njop_bgn": round(luas_bgn * kelas_bgn_record['avgvalue'], 0),
                                    "total_njop": round((luas_bumi * kelas_bumi_record['avgvalue']) + (luas_bgn * kelas_bgn_record['avgvalue']), 0),
                                    "time_assessment": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "user_assessment": "admin"
                                }
                                nir_results.append(result)
                                # print(f"Appended assessment result for NOP: {nop}")
                                break  # Exit the loop once a match is found
                        break  # Exit the loop once a match is found
                break  # Exit the loop once a match is found
        
        pbar.update(1)
    
    pbar.close()
    return nir_results

# Function to load and validate the latest assessment data
def load_and_validate_latest_assessment():
    folder_path = 'DATA_PENILAIAN/'
    files = os.listdir(folder_path)
    json_files = [file for file in files if file.endswith('.json')]
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
    
    if json_files:
        latest_file = json_files[0]
        file_path = os.path.join(folder_path, latest_file)
        
        print(f"Latest assessment filename: {latest_file}")
        print(f"Loading data from {file_path}")
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            if validate_assessment_data(data):
                print(f"Validation result for {latest_file}: True")
                print(f"Successfully loaded and validated assessment data from {latest_file}")
                return data
            else:
                print(f"Validation result for {latest_file}: False")
                return None
        except Exception as e:
            print(f"Error loading data from {latest_file}: {e}")
            return None
    else:
        print("No assessment files found in the folder.")
        return None

# Function to validate configuration data
def validate_config(data):
    if isinstance(data, dict) and 'tahun_pajak' in data:
        return True
    else:
        return False

# Function to validate PBB data
def validate_pbb_data(data):
    if not isinstance(data, list):
        print("Data is not a list")
        return False
    
    for item in data:
        if not isinstance(item, dict):
            print(f"Item in list is not a dictionary: {item}")
            return False
        if 'nop' not in item or 'data_penetapan' not in item:
            print(f"Missing 'nop' or 'data_penetapan' in item: {item}")
            return False
        if not isinstance(item['data_penetapan'], dict):
            print(f"'data_penetapan' is not a dictionary: {item}")
            return False
    
    return True

# Function to validate assessment data
def validate_assessment_data(data):
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return True
    else:
        return False

# Function to update PBB data based on assessment data
def update_pbb_data(pbb_data, assessment_data, config_data):
    op_tahun_penetapan_terakhir = config_data.get('tahun_pajak')
    
    for assessment_record in tqdm(assessment_data, desc="Processing Determination Data PBB : "):
        nop = assessment_record.get('nop')
        
        matching_record = next((item for item in pbb_data if item['nop'] == nop), None)
        
        if matching_record:
            if 'data_penetapan' in matching_record:
                matching_record['data_penetapan']['op_kelas_bumi'] = assessment_record.get('kelas_bumi')
                matching_record['data_penetapan']['op_kelas_bgn'] = assessment_record.get('kelas_bgn')
                matching_record['data_penetapan']['op_njop_bumi'] = assessment_record.get('njop_bumi')
                matching_record['data_penetapan']['op_njop_bgn'] = assessment_record.get('njop_bgn')
                matching_record['data_penetapan']['op_njop'] = assessment_record.get('total_njop')
                matching_record['data_penetapan']['op_status_penetapan'] = True
                matching_record['data_penetapan']['op_tahun_penetapan_terakhir'] = op_tahun_penetapan_terakhir
            else:
                matching_record['data_penetapan'] = {
                    'op_kelas_bumi': assessment_record.get('kelas_bumi'),
                    'op_kelas_bgn': assessment_record.get('kelas_bgn'),
                    'op_njop_bumi': assessment_record.get('njop_bumi'),
                    'op_njop_bgn': assessment_record.get('njop_bgn'),
                    'op_njop': assessment_record.get('total_njop'),
                    'op_status_penetapan': True,
                    'op_tahun_penetapan_terakhir': op_tahun_penetapan_terakhir
                }
    
    return pbb_data

def save_assessment_data(data):
    filename = generate_filename()
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"Assessment data saved to {filename}")

def save_pbb_data(tahun_pajak, data):
    directory = 'DATA_OP'
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, f'pbb_data_{tahun_pajak}.json')
    
    # Backup the original file before overwriting
    if os.path.exists(file_path):
        backup_directory = 'DATA_OP_BACKUP'
        if not os.path.exists(backup_directory):
            os.makedirs(backup_directory)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file_path = os.path.join(backup_directory, f'pbb_data_{tahun_pajak}_{timestamp}.json')
        shutil.copy2(file_path, backup_file_path)
        print(f"Backup of original file created at {backup_file_path}")
    
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)
    print(f"PBB data saved to {file_path}")

def main():
    start_time = time.time()
    
    print("Loading configuration data...")
    config_data = load_config()
    if not validate_config(config_data):
        print("Invalid configuration data.")
        return

    tahun_pajak = config_data['tahun_pajak']

    print(f"Loading PBB data for tax year {tahun_pajak}...")
    pbb_data = load_pbb_data(tahun_pajak)
    if not validate_pbb_data(pbb_data):
        print("Invalid PBB data.")
        return

    print("Loading ZNT data...")
    znt_data = load_znt_data()
    print("Loading Kelas Bumi data...")
    kelas_bumi_data = load_kelas_bumi_data()
    print("Loading Kelas Bangunan data...")
    kelas_bgn_data = load_kelas_bgn_data()

    print("Processing assessment...")
    assessment_results = process_assessment(pbb_data, znt_data, kelas_bumi_data, kelas_bgn_data, tahun_pajak)
    if not assessment_results:
        print("No assessment results generated.")
        return

    save_assessment_data(assessment_results)

    latest_assessment_data = load_and_validate_latest_assessment()
    if latest_assessment_data is None:
        print("No valid assessment data found.")
        return

    print("Updating PBB data with assessment data...")
    updated_pbb_data = update_pbb_data(pbb_data, latest_assessment_data, config_data)
    save_pbb_data(tahun_pajak, updated_pbb_data)

    end_time = time.time()
    print(f"Process completed in {end_time - start_time:.2f} seconds.")

if __name__ == "__main__":
    main()
