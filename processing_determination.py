import json
import os
import time
from datetime import datetime
from tqdm import tqdm
import shutil
import uuid
import sys

# Set the encoding to utf-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Change the default encoding for stdout and stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
# Global debug flag
DEBUG = False

def print_debug(message):
    if DEBUG:
        print(message)

# Load config data
def load_config():
    file_path = 'config.json'
    if not os.path.exists(file_path):
        print_debug(f"Configuration file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load pbb_data_{tahun}.json data
def load_pbb_data():
    file_path = f'SW_PBB/pbb_data_op.json'
    if not os.path.exists(file_path):
        print_debug(f"PBB data file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def load_pbb_data_penetapan():
    file_path = f'SW_PBB/pbb_data_penetapan.json'
    if not os.path.exists(file_path):
        print_debug(f"PBB data file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load znt_data.json data
def load_znt_data():
    file_path = 'CONFIG_DATA/znt_data.json'
    if not os.path.exists(file_path):
        print_debug(f"ZNT data file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load kelas_bumi.json data
def load_kelas_bumi_data():
    file_path = 'CONFIG_DATA/kelas_bumi.json'
    if not os.path.exists(file_path):
        print_debug(f"Kelas Bumi data file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load kelas_bgn.json data
def load_kelas_bgn_data():
    file_path = 'CONFIG_DATA/kelas_bangunan.json'
    if not os.path.exists(file_path):
        print_debug(f"Kelas Bangunan data file not found: {file_path}")
        return None
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to load and validate the latest assessment data
def load_and_validate_latest_assessment():
    folder_path = 'SW_PBB/pbb_data_assesment'
    if not os.path.exists(folder_path):
        print_debug(f"Directory not found: {folder_path}")
        return None

    files = os.listdir(folder_path)
    json_files = [file for file in files if file.endswith('.json')]
    json_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder_path, x)), reverse=True)
    
    if json_files:
        latest_file = json_files[0]
        file_path = os.path.join(folder_path, latest_file)
        
        print_debug(f"\nLatest assessment filename: {latest_file}")
        print_debug(f"Loading data from {file_path}")
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            if validate_assessment_data(data):
                print_debug(f"Validation result for {latest_file}: True")
                print_debug(f"Successfully loaded and validated assessment data from {latest_file}")
                return data
            else:
                print_debug(f"Validation result for {latest_file}: False")
                return None
        except Exception as e:
            print_debug(f"Error loading data from {latest_file}: {e}")
            return None
    else:
        print_debug("No assessment files found in the folder.")
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
        print_debug("Data is not a list")
        return False
    
    for item in data:
        if not isinstance(item, dict):
            print_debug(f"Item in list is not a dictionary: {item}")
            return False
        if 'nop' not in item:
            print_debug(f"Missing 'nop' in item: {item}")
            return False
        if 'data_penetapan' not in item:
            print_debug(f"Missing 'data_penetapan' in item: {item}")
            item['data_penetapan'] = {}  # Ensure there is a data_penetapan dictionary
        if not isinstance(item['data_penetapan'], dict):
            print_debug(f"'data_penetapan' is not a dictionary: {item}")
            return False
    
    return True

# Function to validate assessment data
def validate_assessment_data(data):
    if isinstance(data, list) and all(isinstance(item, dict) for item in data):
        return True
    else:
        return False

# Function to update PBB data based on assessment data
def update_pbb_data(pbb_data, assessment_data, config_data, kab_code, kab_name, persen_pengenaan_data, tarif_op_data, jatuh_tempo_data):
    op_tahun_penetapan_terakhir = config_data.get('tahun_pajak')
    time_penetapan = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    tanggal_penetapan = datetime.now().strftime("%Y-%m-%d")
    
    not_published_data = []

    # Create a dictionary for quick lookup of PBB data by NOP
    pbb_data_dict = {item['nop']: item for item in pbb_data}

    # for assessment_record in tqdm(assessment_data, desc="Processing Determination Data PBB from " + str(kab_code) + " - " + str(kab_name) + " : "):
    for assessment_record in tqdm(assessment_data, desc="Processing Determination Data PBB from " + str(kab_code) + " - " + str(kab_name) + " : ", mininterval=0.1):
        nop = assessment_record.get('nop')
        matching_record = pbb_data_dict.get(nop)

        if matching_record:
            data_op = matching_record['data_op']
            if data_op['status_terbit']:
                data_penetapan = matching_record['data_penetapan']
                total_njop = assessment_record.get('total_njop')
                op_njkp_b4_pengenaan = total_njop - 0
                op_persen_pengenaan = get_persen_pengenaan(op_njkp_b4_pengenaan, op_tahun_penetapan_terakhir, persen_pengenaan_data)
                op_njkp_after_pengenaan = round(op_njkp_b4_pengenaan - (op_njkp_b4_pengenaan * (op_persen_pengenaan / 100)), 0)
                op_tarif = get_tarif_op(op_njkp_after_pengenaan, op_tahun_penetapan_terakhir, tarif_op_data)
                ketetapan_bayar = round(op_tarif * (op_njkp_b4_pengenaan - (op_njkp_b4_pengenaan * (op_persen_pengenaan / 100))), 0)

                data_penetapan.update({
                    'op_kelas_bumi': assessment_record.get('kelas_bumi'),
                    'op_kelas_bgn': assessment_record.get('kelas_bgn'),
                    'op_njop_bumi': assessment_record.get('njop_bumi'),
                    'op_njop_bgn': assessment_record.get('njop_bgn'),
                    'op_njop': total_njop,
                    'status_penetapan': True,
                    'op_tahun_penetapan_terakhir': op_tahun_penetapan_terakhir,
                    'op_njkp_b4_pengenaan': op_njkp_b4_pengenaan,
                    'op_persen_pengenaan': op_persen_pengenaan,
                    'op_njkp_after_pengenaan': op_njkp_after_pengenaan,
                    'op_tarif': op_tarif,
                    'sebelum_stimulus': ketetapan_bayar,
                    'ketetapan_bayar': ketetapan_bayar,
                    'tanggal_penetapan': time_penetapan,
                    'user_penetapan': "admin",
                    'tanggal_terbit': tanggal_penetapan,
                    'jatuh_tempo': get_jatuh_tempo(time_penetapan, ketetapan_bayar, jatuh_tempo_data),
                    'op_penetapan_id': str(uuid.uuid4()),
                    'op_penetapan_status': True,
                    'op_penetapan_time': time_penetapan
                })

                data_op.update({
                    'op_penetapan_id': str(uuid.uuid4()),
                    'op_penetapan_status': True,
                    'op_penetapan_time': time_penetapan
                })
            else:
                not_published_data.append(matching_record)
    
    # Filter out not published data from pbb_data
    pbb_data = [item for item in pbb_data if item['data_op']['status_terbit'] == True]
            
    return pbb_data, not_published_data

# Function to save updated PBB data to a new file
def save_updated_pbb_data(pbb_data, config_data, kab_code, kab_name, not_published_data):
    tahun_pajak = config_data.get('tahun_pajak')
    directory = f"SW_PBB/pbb_data_determination/{tahun_pajak}"
    if not os.path.exists(directory):
        os.makedirs(directory)
    filename = f"{directory}/pbb_sppt.json"
    
    with open(filename, 'w') as file:
        json.dump(pbb_data, file, indent=4)
    
    print_debug(f"\nUpdated PBB data saved to {filename}")

    if not_published_data:
        not_published_filename = f"{directory}/pbb_sppt_not_published.json"
        with open(not_published_filename, 'w') as file:
            json.dump(not_published_data, file, indent=4)
        print_debug(f"\nNot published PBB data saved to {not_published_filename}")

# Function to create a backup of the original PBB data file
def create_backup(tahun_pajak):
    source_path = f"SW_PBB/pbb_data_op.json"
    backup_dir = f"SW_PBB/BACKUP_DIR/{tahun_pajak}"
    
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, f"pbb_data_op_{time.strftime('%Y%m%d_%H%M%S')}.json")
    shutil.copy(source_path, backup_path)
    print_debug(f"Backup created: {backup_path}")

# Function to get persen pengenaan
def get_persen_pengenaan(njkp_b4_pengenaan, tahun_pajak, persen_pengenaan_data):
    for persen_pengenaan in persen_pengenaan_data:
        if (persen_pengenaan['tahun_pajak_awal'] <= tahun_pajak <= persen_pengenaan['tahun_pajak_akhir'] and
            persen_pengenaan['mnvalue'] <= njkp_b4_pengenaan <= persen_pengenaan['mxvalue']):
            return persen_pengenaan['persentase']
    return 0  # Default to 0 if no matching range is found

def get_tarif_op(njkp_after_pengenaan, tahun_pajak, tarif_op_data):
    for tarif_op in tarif_op_data:
        if (tarif_op['tahun_pajak_awal'] <= tahun_pajak <= tarif_op['tahun_pajak_akhir'] and
            tarif_op['mnvalue'] <= njkp_after_pengenaan <= tarif_op['mxvalue']):
            return tarif_op['persentase']
    return 0  # Default to 0 if no matching range is found

def get_jatuh_tempo(tanggal_penetapan, ketetapan_bayar, jatuh_tempo_data):
    for jatuh_tempo in jatuh_tempo_data:
        if (jatuh_tempo['tanggal_awal'] <= tanggal_penetapan <= jatuh_tempo['tanggal_akhir'] and
                jatuh_tempo['mnvalue'] <= ketetapan_bayar <= jatuh_tempo['mxvalue']):
                return jatuh_tempo['jatuh_tempo']
        # return 0  # Default to 0 if no matching range is found

def update_time_determination(pbb_data, time_determination, penilaian_id_to_update, op_tahun_penetapan_terakhir):
    for record in pbb_data:
        data_op = record.get('data_op', {})
        data_op['op_penetapan_time'] = time_determination
        data_op['op_penetapan_status'] = True
        data_op['op_penetapan_id'] = penilaian_id_to_update
        data_penetapan = record.get('data_penetapan', {})
        data_penetapan['op_penetapan_time'] = time_determination
        data_penetapan['op_penetapan_status'] = True
        data_penetapan['op_penetapan_id'] = penilaian_id_to_update
        data_penetapan['op_tahun_penetapan_terakhir'] = op_tahun_penetapan_terakhir
    return pbb_data

# Main function
def main():
    print_debug("Starting the script...")

    config_data = load_config()
    persen_pengenaan_data = config_data.get('persen_pengenaan', [])
    tarif_op_data = config_data.get('tarif_op', [])
    jatuh_tempo_data = config_data.get('jatuh_tempo',[])

    if config_data is None:
        print_debug("Failed to load config data. Exiting...")
        return

    if not validate_config(config_data):
        print_debug("Invalid config data. Exiting...")
        return

    tahun_pajak = config_data['tahun_pajak']
    kab_code = config_data['kab_code']
    kab_name = config_data['kab_name']

    pbb_data = load_pbb_data()
    if pbb_data is None:
        print_debug("Failed to load PBB data. Exiting...")
        return

    if not validate_pbb_data(pbb_data):
        print_debug("Invalid PBB data. Exiting...")
        return

    znt_data = load_znt_data()
    if znt_data is None:
        print_debug("Failed to load ZNT data. Exiting...")
        return

    kelas_bumi_data = load_kelas_bumi_data()
    if kelas_bumi_data is None:
        print_debug("Failed to load Kelas Bumi data. Exiting...")
        return

    kelas_bgn_data = load_kelas_bgn_data()
    if kelas_bgn_data is None:
        print_debug("Failed to load Kelas Bangunan data. Exiting...")
        return


    time_determination = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    penetapan_id_to_update = str(uuid.uuid4())  # Replace with the actual ID
    op_tahun_penetapan_terakhir = config_data.get('tahun_pajak')
    updated_pbb_data = update_time_determination(pbb_data, time_determination, penetapan_id_to_update, op_tahun_penetapan_terakhir)
    with open(f'SW_PBB/pbb_data_op.json', 'w') as file:
        json.dump(updated_pbb_data, file, indent=4)
    
    print_debug("Updated status Penetapan in pbb_data_op.json")
    create_backup(tahun_pajak)

    latest_assessment_data = load_and_validate_latest_assessment()
    if latest_assessment_data is None:
        print_debug("No valid assessment data found.")
        return

    updated_pbb_data, not_published_data = update_pbb_data(pbb_data, latest_assessment_data, config_data, kab_code, kab_name, persen_pengenaan_data, tarif_op_data, jatuh_tempo_data)
    save_updated_pbb_data(updated_pbb_data, config_data, kab_code, kab_name, not_published_data)

if __name__ == "__main__":
    main()