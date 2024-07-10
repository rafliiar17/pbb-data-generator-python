import os
import json
import random
import uuid
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

def generate_data(generated_nops, num_records, wp_pekerjaan_options, wp_status_options, op_znt_options, op_nilai_bgn_options, tahun_pajak):
    total_nops = len(generated_nops)
    
    records = []
    data_wp_list = []  # List to store data_wp entries
    used_nops = set()  # Set to store used NOPs
    generated_keys = set()  # Initialize as an empty set to store unique (nop, tahun_pajak) pairs
    max_attempts = 100  # Define max_attempts here

    with tqdm(total=min(total_nops, num_records), desc=f"Generating Data OP : {tahun_pajak}") as pbar:
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
                        "op_nilai_bgn" : op_nilai_bgn_value
                    },
                    "data_penetapan": {
                        "op_status_penetapan" : False,
                        "op_tahun_penetapan_terakhir" : 0,
                        "status_penetapan" : False,
                        "op_kelas_bumi": "",
                        "op_kelas_bgn": "",
                        "op_njop_bumi": 0,
                        "op_njop_bgn": 0,
                        "op_njop" : 0,
                        "op_njoptkp": 0,
                        "op_njkp_b4_pengenaan": 0,
                        "op_persen_pengenaan": 0,
                        "op_njkp_after_pengenaan": 0,
                        "op_tarif": 0,
                        "sebelum_stimulus": 0,
                        "pengali_stimulus": 0,
                        "pengurang_stimulus": 0,
                        "selisih_stimulus": 0,
                        "ketetapan_bayar": 0,
                        "tanggal_penetapan": {
                            "$date": None
                        },
                        "user_penetapan": "",
                        "tanggal_terbit": {
                            "$date": None
                        },
                        "jatuh_tempo": {
                            "$date": None
                        },
                        "user_input": fake.user_name(),
                        "createdAt": {
                            "$date": None
                        },
                        "updatedAt": {
                            "$date": None
                        }
                    },
                    "data_pembayaran": {
                        "payment_code": {
                            "$numberLong": 0
                        },
                        "payment_coll_code": {
                            "$numberLong": 0
                        },
                        "payment_flag_status": 0,
                        "payment_deduction": False,
                        "payment_installment": False,
                        "payment_compensation": False,
                        "payment_flag": True,
                        "payment_paid": {
                            "$date": None
                        },
                        "payment_settlement_date": None, ## fake.date_time_this_year().strftime('%Y%m%d')
                        "bank_code": None,
                        "merchant_code": None,
                        "channel_code": None,
                        "payment_ref_num": None, ## str(uuid.uuid4()) -> UUID if payment_flag_status = 1
                        "payment_gw_refnum": None, ## str(uuid.uuid4()) -> UUID if payment_flag_status = 1
                        "payment_sw_refnum": None, ## str(uuid.uuid4()) -> UUID if payment_flag_status = 1
                        "payment_amount": 0,
                        "payment_amount_ded": 0,
                        "payment_penalty": 0,
                        "payment_bill": 0
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
    
    # Provide default values if keys are missing
    wp_pekerjaan_options = config.get('wp_pekerjaan_options', ["PNS", "Swasta", "Wiraswasta", "Lainnya"])
    wp_status_options = config.get('wp_status_options', ["Pemakai", "Pemilik", "Pengelola", "Penyewa", "Sengketa"])
    tahun_pajak = config.get('tahun_pajak', datetime.now().year)
    
    # Load generated NOPs once here
    generated_nops_file_path = 'GENERATED_DATA/generated_nop.json'
    if not os.path.exists(generated_nops_file_path):
        print(f"File not found: {generated_nops_file_path}")
        exit()
    
    generated_nops = load_generated_nops(generated_nops_file_path)
    
    if not generated_nops:
        print("No valid NOP data found. Exiting.")
        exit()
    
    # Default to the length of generated_nops if 'num_records' is not found
    num_records = config.get('num_records', len(generated_nops))
    
    op_znt_options = load_znt_data('CONFIG_DATA/znt_data.json', tahun_pajak)
    op_nilai_bgn_options = config['op_nilai_bgn_options']
    
    # Print the count of generated NOPs
    print(f"Number of generated NOPs: {len(generated_nops)}")
    
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
    
    output_dir = 'DATA_OP'
    output_file_path = os.path.join(output_dir, f'pbb_data_{tahun_pajak}.json')
    save_pbb_wajib_pajak(pbb_data_records, output_file_path)
    
    print(f"Generated {len(pbb_data_records)} records and saved to {output_file_path}.")