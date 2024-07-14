import os
import json
import random
import uuid
import ijson
from faker import Faker
from datetime import datetime
from tqdm import tqdm


fake = Faker('id_ID')

def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def load_generated_nops(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)  # Load the JSON to check validity
        print("NOP JSON file is valid.")
        return data  # Return the loaded data instead of an empty list
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return []
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
        return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def load_znt_data(file_path, tahun_pajak):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print("ZNT JSON file is valid.")
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return []
    
    # Filter ZNT options based on the provided tahun_pajak
    filtered_znt_options = [
        entry['znt_code'] for entry in data 
        if entry['znt_year'] == tahun_pajak
    ]
    
    return filtered_znt_options

def save_pbb_wajib_pajak(data, file_path):
    # Ensure the directory exists
    output_dir = os.path.dirname(file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def load_pbb_data(file_path):
    records = []
    with open(file_path, 'rb') as file:
        # Use ijson to parse file iteratively
        objects = ijson.items(file, 'item')
        for obj in objects:
            records.append(obj)
            # Process records one at a time or in small batches
    return records

def generate_data(generated_nops, num_records, wp_pekerjaan_options, wp_status_options, op_znt_options, op_nilai_bgn_options, tahun_pajak):
    total_nops = len(generated_nops)
    
    records = []
    data_wp_list = []  # List to store data_wp entries
    used_nops = set()  # Set to store used NOPs
    generated_keys = set()  # Initialize as an empty set to store unique (nop, tahun_pajak) pairs
    max_attempts = 100  # Define max_attempts here

    with tqdm(total=min(total_nops, num_records), desc=f"Generating Data OP {kab_name} - {tahun_pajak}") as pbar:
        while len(records) < total_nops and len(records) < num_records:
            attempts = 0
            while attempts < max_attempts:
                # Randomly select a NOP from generated_nops
                nop_entry = random.choice(generated_nops)
                nop = nop_entry['nop']
                
                # Check if NOP has already been used
                if nop in used_nops:
                    attempts += 1
                    continue
                
                # Extract components from NOP
                kab_code = nop[:4]
                kecamatan_code = int(nop[4:7])
                kelurahan_code = int(nop[7:10])
                blok = nop[10:14]
                no_urut = nop[14:18]

                # Generate other fields
                wp_pekerjaan = random.choice(wp_pekerjaan_options)
                wp_status = random.choice(wp_status_options)
                op_znt = random.choice(op_znt_options)
                op_nilai_bgn = random.choice(op_nilai_bgn_options)
                if op_nilai_bgn == "Manual":
                    op_nilai_bgn_value = random.randint(0, 100000)
                else:
                    op_nilai_bgn_value = 0

                op_kecamatan_nama = fake.city().upper()  # Example of fake data for kecamatan_nama
                op_kelurahan_nama = fake.city().upper()  # Example of fake data for kelurahan_nama
                
                # Generate jenis_tanah
                op_jenis_tanah = random.randint(1, 13)
                
                # Generate dafnom
                op_dafnom = random.randint(1, 8)

                # Generate NIK based on the format
                born_date = fake.date_of_birth().strftime('%m%d%y')
                code = str(random.choice([0, 7]))
                nik = f"{kab_code}{kecamatan_code:02d}{born_date}{no_urut}{code}"
                nik = nik[:16]

                # Generate record
                record = {
                    "_id": str(uuid.uuid4()),
                    "nop": nop,
                    "tahun_pajak": tahun_pajak,
                    "data_wp": {
                        "nik": nik,
                        "wp_pekerjaan": wp_pekerjaan,
                        "wp_status": wp_status,
                        "wp_nama": fake.name().upper(),
                        "wp_alamat": fake.street_address(),
                        "wp_rt": 0,
                        "wp_rw": 0,
                        "wp_kelurahan": fake.city().upper(),
                        "wp_kecamatan": fake.city().upper(),
                        "wp_kotakab": fake.city().upper(),
                        "wp_provinsi": fake.state(),
                        "wp_kodepos": fake.postcode(),
                        "wp_email": fake.email(),
                        "wp_whatsapp": fake.phone_number()
                    },
                    "data_alamat_op": {
                        "op_kecamatan_kode": kecamatan_code,
                        "op_kelurahan_kode": kelurahan_code,
                        "op_kecamatan_nama": op_kecamatan_nama,
                        "op_kelurahan_nama": op_kelurahan_nama,
                        "op_alamat": fake.street_address() + f" BLOK. {blok}",
                        "op_rt": 0,
                        "op_rw": 0,
                        "op_kodepos": fake.postcode()
                    },
                    "data_op": {
                        "op_jenis_tanah": op_jenis_tanah,
                        "op_znt": op_znt,
                        "op_dafnom": op_dafnom,
                        "op_jml_bgn": random.randint(1, 10),
                        "op_luas_bumi": random.randint(1000, 3000),
                        "op_luas_bgn": random.randint(10, 100),
                        "op_status_nilai_bgn" : op_nilai_bgn,
                        "op_nilai_bgn" : op_nilai_bgn_value,
                        "op_penilaian_status" : False,
                        "op_penilaian_id": None,
                        "op_penilaian_time" : None,
                        "op_penetapan_status" : False,
                        "op_penetapan_id": None,
                        "op_penetapan_time" : None,
                        "status_terbit" : random.choice([True, False])
                    }
                }
                
                record_key = (nop, tahun_pajak)  # Create a unique key for the record
                
                if record_key not in generated_keys:
                    generated_keys.add(record_key)
                    records.append(record)
                    data_wp_list.append(record["data_wp"])
                    used_nops.add(nop)  # Mark NOP as used
                    pbar.update(1)
                    break
                else:
                    attempts += 1

    return records, data_wp_list

if __name__ == "__main__":
    config = load_config()
    kab_name = config.get('kab_name')
    kode_kab = config.get('kab_code')
    get_debug_max_nop = config.get('debug_max_nop', {'status'})
    # Provide default values if keys are missing
    wp_pekerjaan_options = config.get('wp_pekerjaan_options', ["PNS", "Swasta", "Wiraswasta", "Lainnya"])
    wp_status_options = config.get('wp_status_options', ["Pemakai", "Pemilik", "Pengelola", "Penyewa", "Sengketa"])
    tahun_pajak = config.get('tahun_pajak', datetime.now().year)
    
    # Load generated NOPs once here
    generated_nops_file_path = 'SW_PBB/generated_nop.json'
    if not os.path.exists(generated_nops_file_path):
        print(f"File not found: {generated_nops_file_path}")
        exit()
    
    generated_nops = load_generated_nops(generated_nops_file_path)
    
    if not generated_nops:
        print("No valid NOP data found. Exiting.")
        exit()
    
    debug_max_nop = config.get('debug_max_nop')
    if debug_max_nop.get('status', True): 
        num_records = debug_max_nop.get('maxnop')
    else:
        num_records = len(generated_nops)
 
    op_znt_options = load_znt_data('CONFIG_DATA/znt_data.json', tahun_pajak)
    op_nilai_bgn_options = config['op_nilai_bgn_options']
    
    # Print the count of generated NOPs
    print(f"Number of generated NOP on {kode_kab} - {kab_name} : {len(generated_nops)}")
    
    znt_data_file_path = 'CONFIG_DATA/znt_data.json'
    
    # Load ZNT options based on tahun_pajak
    OP_ZNT_OPTIONS = load_znt_data('CONFIG_DATA/znt_data.json', tahun_pajak)
    OP_NILAI_BGN_OPTIONS = ["System", "Manual"]


    pbb_data_records, data_wp_list = generate_data(
        generated_nops,
        num_records,
        wp_pekerjaan_options,
        wp_status_options,
        op_znt_options,
        op_nilai_bgn_options,
        tahun_pajak
    )
    
    output_dir = 'SW_PBB'
    output_file_path = os.path.join(output_dir, f'pbb_data_op.json')
    save_pbb_wajib_pajak(pbb_data_records, output_file_path)
    
    output_wp_file_path = os.path.join(output_dir, f'pbb_data_wp.json')
    save_pbb_wajib_pajak(data_wp_list, output_wp_file_path)
    
    print(f"Generated {len(pbb_data_records)} records and saved to {output_file_path}.")
    print(f"Generated {len(data_wp_list)} WP records and saved to {output_wp_file_path}.")