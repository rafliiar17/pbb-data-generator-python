import json
import os
from datetime import datetime
from tqdm import tqdm
import uuid

# Load config data
def load_config():
    file_path = 'config.json'
    if not os.path.exists(file_path):
        print(f"Configuration file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load pbb_data_{tahun}.json data
def load_pbb_data(tahun_pajak):
    file_path = f'SW_PBB/pbb_data_op.json'
    if not os.path.exists(file_path):
        print(f"PBB data file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load znt_data.json data
def load_znt_data():
    file_path = 'CONFIG_DATA/znt_data.json'
    if not os.path.exists(file_path):
        print(f"ZNT data file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load kelas_bumi.json data
def load_kelas_bumi_data():
    file_path = 'CONFIG_DATA/kelas_bumi.json'
    if not os.path.exists(file_path):
        print(f"Kelas Bumi data file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load kelas_bgn.json data
def load_kelas_bgn_data():
    file_path = 'CONFIG_DATA/kelas_bangunan.json'
    if not os.path.exists(file_path):
        print(f"Kelas Bangunan data file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to generate filename based on current datetime
def generate_filename():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    directory = "SW_PBB/pbb_data_assesment"
    if not os.path.exists(directory):
        os.makedirs(directory)
    return f"{directory}/pbb_data_assesment_{timestamp}.json"

# Function to get nir based on kelurahan_code, znt_code, and znt_year
def process_assessment(pbb_data, znt_data, kelas_bumi_data, kelas_bgn_data, tahun_pajak, kab_code, kab_name):
    nir_results = []
    pbar = tqdm(total=len(pbb_data), desc='Processing Assessment PBB Data from ' + str(kab_code) + " - " + str(kab_name), position=0, leave=True)
    
    for pbb_record in pbb_data:
        nop = pbb_record['nop']
        luas_bumi = pbb_record['data_op'].get('op_luas_bumi', 0)
        luas_bgn = pbb_record['data_op'].get('op_luas_bgn', 0)
        kelurahan_code = int(nop[:10])
        op_znt = pbb_record['data_op'].get('op_znt', '')
        status_terbit = pbb_record['data_op'].get('status_terbit')

        for znt_record in znt_data:
            if (znt_record['kelurahan_code'] == kelurahan_code and
                znt_record['znt_code'] == op_znt and
                znt_record['znt_year'] == tahun_pajak):
                nir = znt_record['nir']

                for kelas_bumi_record in kelas_bumi_data:
                    if (kelas_bumi_record['fyear'] <= tahun_pajak <= kelas_bumi_record['lyear'] and
                        kelas_bumi_record['mnvalue'] <= nir <= kelas_bumi_record['mxvalue']):
                        
                        for kelas_bgn_record in kelas_bgn_data:
                            if (kelas_bgn_record['fyear'] <= tahun_pajak <= kelas_bgn_record['lyear'] and
                                kelas_bgn_record['mnvalue'] <= nir <= kelas_bgn_record['mxvalue']):
                                
                                result = {
                                    "penilaian_id": str(uuid.uuid4()),
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
                                    "user_assessment": "admin",
                                    "status_terbit" : status_terbit
                                }
                                nir_results.append(result)
                                break  # Exit the loop once a match is found
                        break  # Exit the loop once a match is found
                break  # Exit the loop once a match is found
        
        pbar.update(1)
    
    pbar.close()
    return nir_results

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

# Function to load and validate the latest assessment data
def load_and_validate_latest_assessment():
    folder_path = 'SW_PBB/pbb_data_assesment'
    if not os.path.exists(folder_path):
        return None

    files = os.listdir(folder_path)
    json_files = [file for file in files if file.endswith('.json')]
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
    
    if json_files:
        latest_file = json_files[0]
        file_path = os.path.join(folder_path, latest_file)
        
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            if validate_assessment_data(data):
                return data
            else:
                return None
        except Exception as e:
            return None
    else:
        return None

# Function to update time_assessment in pbb_data_op.json
def update_time_assessment(pbb_data, time_assessment, penilaian_id_to_update):
    for record in pbb_data:
        data_op = record.get('data_op', {})
        data_op['op_penilaian_time'] = time_assessment
        data_op['op_penilaian_status'] = True
        data_op['op_penilaian_id'] = penilaian_id_to_update
    return pbb_data

# Main function
def main():
    print("Starting the script...")

    config_data = load_config()
    if config_data is None:
        print("Failed to load config data. Exiting...")
        return

    if not validate_config(config_data):
        print("Invalid config data. Exiting...")
        return

    tahun_pajak = config_data['tahun_pajak']
    kab_code = config_data['kab_code']
    kab_name = config_data['kab_name']

    pbb_data = load_pbb_data(tahun_pajak)
    if pbb_data is None:
        print("Failed to load PBB data. Exiting...")
        return

    if not validate_pbb_data(pbb_data):
        print("Invalid PBB data. Exiting...")
        return

    znt_data = load_znt_data()
    if znt_data is None:
        print("Failed to load ZNT data. Exiting...")
        return

    kelas_bumi_data = load_kelas_bumi_data()
    if kelas_bumi_data is None:
        print("Failed to load Kelas Bumi data. Exiting...")
        return

    kelas_bgn_data = load_kelas_bgn_data()
    if kelas_bgn_data is None:
        print("Failed to load Kelas Bangunan data. Exiting...")
        return

    assessment_data = process_assessment(pbb_data, znt_data, kelas_bumi_data, kelas_bgn_data, tahun_pajak, kab_code, kab_name)
    if not validate_assessment_data(assessment_data):
        print("Invalid assessment data. Exiting...")
        return

    filename = generate_filename()
    with open(filename, 'w') as file:
        json.dump(assessment_data, file, indent=4)
    
    print(f"Assessment data saved to {filename}")

    # Update time_assessment in pbb_data_op.json
    time_assessment = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    penilaian_id_to_update = assessment_data[0]['penilaian_id']  # Replace with the actual ID
    updated_pbb_data = update_time_assessment(pbb_data, time_assessment, penilaian_id_to_update)
    with open(f'SW_PBB/pbb_data_op.json', 'w') as file:
        json.dump(updated_pbb_data, file, indent=4)
    
    print("Updated time_assessment in pbb_data_op.json")

    load_and_validate_latest_assessment()

if __name__ == "__main__":
    main()