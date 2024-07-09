import json
from datetime import datetime
import os
from tqdm import tqdm  # Import tqdm for progress bar

def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load pbb_data_{tahun}.json data
def load_pbb_data(tahun_pajak):
    file_path = f'DATA_SW/pbb_data_{tahun_pajak}.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load znt_data.json data
def load_znt_data():
    file_path = 'GENERATED_DATA/znt_data.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load kelas_bumi.json data
def load_kelas_bumi_data():
    file_path = 'GENERATED_DATA/kelas_bumi.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Load kelas_bgn.json data
def load_kelas_bgn_data():
    file_path = 'GENERATED_DATA/kelas_bangunan.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to generate filename based on current datetime
def generate_filename():
    now = datetime.now()
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    return f"assessment/assessment_{timestamp}.json"

# Function to get nir based on kelurahan_code, znt_code, and znt_year
def get_nir():
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
    pbar = tqdm(total=len(pbb_data), desc='Processing PBB Data', position=0, leave=True)
    
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
                                    "njop_bumi": round(luas_bumi * kelas_bumi_record['avgvalue'],0),
                                    "njop_bgn": round(luas_bgn * kelas_bgn_record['avgvalue'],0),
                                    "total_njop": round((luas_bumi * kelas_bumi_record['avgvalue']) + (luas_bgn * kelas_bgn_record['avgvalue']),0),
                                    "time_assesment" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    "user_assesment" : "admin"
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

# Example usage
nir_list = get_nir()