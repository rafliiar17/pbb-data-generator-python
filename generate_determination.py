import os
import json
from tqdm import tqdm

def load_config():
    file_path = 'config.json'
    print(f"Loading data from {file_path}")
    with open(file_path, 'r') as file:
        data = json.load(file)
    if validate_config(data):
        print(f"Validation result for {file_path}: True")
        print(f"Successfully Loaded and validated from {file_path}")
    else:
        print(f"Validation result for {file_path}: False")
    return data

def load_pbb_data(tahun_pajak):
    file_path = f'DATA_SW/pbb_data_{tahun_pajak}.json'
    print(f"Loading data from {file_path}")
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return None
    
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        print(f"Successfully loaded {file_path}")
        return data
    except Exception as e:
        print(f"Error loading data from {file_path}: {e}")
        return None

def load_and_validate_latest_assessment():
    folder_path = 'assessment/'
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
                print(f"Successfully Loaded and validated assessment data from {latest_file}")
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

def validate_config(data):
    if isinstance(data, dict) and 'tahun_pajak' in data:
        return True
    else:
        return False

def validate_pbb_data(data):
    # Check if data is a dictionary
    if not isinstance(data, dict):
        print("Data is not a dictionary")
        return False
    
    # Check if each key in the dictionary has the expected structure
    for key, value in data.items():
        if not isinstance(value, dict):
            print(f"Value for key {key} is not a dictionary")
            return False
        if 'data_penetapan' not in value:
            print(f"'data_penetapan' not found in value for key {key}")
            return False
        if not isinstance(value['data_penetapan'], dict):
            print(f"'data_penetapan' for key {key} is not a dictionary")
            return False
        # Add more checks as needed for the expected structure of 'data_penetapan'
    
    return True

def validate_assessment_data(data):
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return True
    else:
        return False

def update_pbb_data(pbb_data, assessment_data, config_data):
    op_tahun_penetapan_terakhir = config_data.get('tahun_pajak')
    
    # Use tqdm to create a progress bar
    for assessment_record in tqdm(assessment_data, desc="Updating pbb_data"):
        nop = assessment_record.get('nop')
        
        # Find the matching record in pbb_data
        matching_record = next((item for item in pbb_data if item['nop'] == nop), None)
        
        if matching_record:
            # Update data_penetapan
            if 'data_penetapan' in matching_record:
                matching_record['data_penetapan']['op_kelas_bumi'] = assessment_record.get('kelas_bumi')
                matching_record['data_penetapan']['op_kelas_bgn'] = assessment_record.get('kelas_bgn')
                matching_record['data_penetapan']['op_njop_bumi'] = assessment_record.get('njop_bumi')
                matching_record['data_penetapan']['op_njop_bgn'] = assessment_record.get('njop_bgn')
                matching_record['data_penetapan']['op_njop'] = assessment_record.get('total_njop')
                matching_record['data_penetapan']['op_status_penetapan'] = True
                matching_record['data_penetapan']['op_tahun_penetapan_terakhir'] = op_tahun_penetapan_terakhir 
                matching_record['data_penetapan']['op_njkp_b4_pengenaan'] = assessment_record.get('total_njop') - matching_record['data_penetapan']['op_njoptkp']
    return pbb_data

def save_pbb_data(pbb_data, tahun_pajak):
    file_path = f'DATA_SW/pbb_data_{tahun_pajak}.json'
    print(f"Saving updated data to {file_path}")
    try:
        with open(file_path, 'w') as file:
            json.dump(pbb_data, file, indent=4)
        print(f"Successfully saved updated data to {file_path}")
    except Exception as e:
        print(f"Error saving data to {file_path}: {e}")

# Example usage
def main():
    # Load config to get tahun_pajak
    config_data = load_config()
    tahun_pajak = config_data.get('tahun_pajak')
    if not tahun_pajak:
        print("No tahun_pajak found in config.json. Exiting.")
        return
    
    # Load and validate pbb_data_{tahun_pajak}.json
    pbb_data = load_pbb_data(tahun_pajak)
    if not pbb_data:
        print(f"Unable to load or validate pbb_data_{tahun_pajak}.json. Skipping to next step.")
        return
    
    # Load and validate latest assessment data
    assessment_data = load_and_validate_latest_assessment()
    if not assessment_data:
        print("Unable to load or validate latest assessment data. Exiting.")
        return
    
    # Update pbb_data_{tahun_pajak}.json based on assessment data and config data
    updated_pbb_data = update_pbb_data(pbb_data, assessment_data, config_data)
    
    # Save updated pbb_data_{tahun_pajak}.json
    save_pbb_data(updated_pbb_data, tahun_pajak)

if __name__ == "__main__":
    main()