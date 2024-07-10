import json
from datetime import datetime
import os
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
    file_path = f'GENERATED_DATA/pbb_data_{tahun_pajak}.json'
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
    return f"DATA_PENILAIAN/assessment_{timestamp}.json"

# Function to get nir based on kelurahan_code, znt_code, and znt_year
def process_assessment():
    # Load config data
    config_data = load_config()
    tahun_pajak = config_data.get('tahun_pajak')
    
    # Load data
    pbb_data = load_pbb_data(tahun_pajak)
    znt_data = load_znt_data()
    kelas_bumi_data = load_kelas_bumi_data()
    kelas_bgn_data = load_kelas_bgn_data()
    
    nir_results = []  # List to store results
    
    # Initialize tqdm for progress bar
    pbar = tqdm(total=len(pbb_data), desc='Processing Assessment PBB Data', position=0, leave=True)
    
    # Iterate through pbb_data
    for pbb_record in pbb_data:
        nop = pbb_record['nop']  # Properly assign the nop variable
        luas_bumi = pbb_record['data_op']['op_luas_bumi']
        luas_bgn = pbb_record['data_op']['op_luas_bgn']
        kelurahan_code = int(nop[:10])  # Extract kelurahan_code from nop
        op_znt = pbb_record['data_op']['op_znt']  # Get the op_znt from data_op

        # Check for matching znt_record in znt_data
        for znt_record in znt_data:
            if (znt_record['kelurahan_code'] == kelurahan_code and
                znt_record['znt_code'] == op_znt and
                znt_record['znt_year'] == tahun_pajak):
                nir = znt_record['nir']
                
                # Find the matching kelas_bumi record
                for kelas_bumi_record in kelas_bumi_data:
                    if (kelas_bumi_record['fyear'] <= tahun_pajak <= kelas_bumi_record['lyear'] and
                        kelas_bumi_record['mnvalue'] <= nir <= kelas_bumi_record['mxvalue']):
                        
                        # Find the matching kelas_bgn record
                        for kelas_bgn_record in kelas_bgn_data:
                            if (kelas_bgn_record['fyear'] <= tahun_pajak <= kelas_bgn_record['lyear'] and
                                kelas_bgn_record['mnvalue'] <= nir <= kelas_bgn_record['mxvalue']):
                                
                                # Prepare result dictionary
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
                                break  # Exit kelas_bgn_record loop after finding a match
                        break  # Exit kelas_bumi_record loop after finding a match
        
        pbar.update(1)  # Update progress bar
    
    pbar.close()  # Close progress bar
    
    # Generate filename based on current datetime
    filename = generate_filename()
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Write results to JSON file
    with open(filename, 'w') as file:
        json.dump(nir_results, file, indent=4)
    
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

# Main script
if __name__ == '__main__':
    # Load config data
    config_data = load_config()
    tahun_pajak = config_data.get('tahun_pajak')
    
    # Validate config data
    if not validate_config(config_data):
        print("Invalid config data")
        exit(1)
    
    # Backup existing PBB data
    pbb_file_path = f'GENERATED_DATA/pbb_data_{tahun_pajak}.json'
    backup_file_path = f'GENERATED_DATA/pbb_data_{tahun_pajak}_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    shutil.copy(pbb_file_path, backup_file_path)
    print(f"Backup of PBB data created at {backup_file_path}")
    
    # Load PBB data
    pbb_data = load_pbb_data(tahun_pajak)
    
    # Validate PBB data
    if not validate_pbb_data(pbb_data):
        print("Invalid PBB data")
        exit(1)
    
    # Process assessment
    assessment_data = process_assessment()
    
    # Validate assessment data
    if not validate_assessment_data(assessment_data):
        print("Invalid assessment data")
        exit(1)
    
    # Update PBB data based on assessment data
    updated_pbb_data = update_pbb_data(pbb_data, assessment_data, config_data)
    
    # Save updated PBB data to JSON file
    with open(pbb_file_path, 'w') as file:
        json.dump(updated_pbb_data, file, indent=4)
    
    print(f"Updated PBB data saved to {pbb_file_path}")
    
    # Load and validate the latest assessment data
    latest_assessment_data = load_and_validate_latest_assessment()
    
    if latest_assessment_data:
        print("Successfully loaded and validated the latest assessment data")
    else:
        print("Failed to load or validate the latest assessment data")
