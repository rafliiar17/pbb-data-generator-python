import os
import json
import random
import uuid
import ijson
from faker import Faker
from datetime import datetime
from alive_progress import alive_bar
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)
fake = Faker('id_ID')

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

def load_generated_nops(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)  # Load the JSON to check validity
        print("NOP JSON file is valid.")
        return data
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
    
    filtered_znt_options = [
        entry['znt_code'] for entry in data 
        if entry['znt_year'] == tahun_pajak
    ]
    
    return filtered_znt_options

def save_pbb_wajib_pajak(data, file_path):
    output_dir = os.path.dirname(file_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    with alive_bar(title=f"{Fore.GREEN}Saving data to {file_path}", enrich_print=False,length=25, bar='classic2', spinner='wait4', stats=False, monitor=True) as bar:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
            bar()  # Update the progress bar
            print()

    
    file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert bytes to MB
    print(f"Data saved to {file_path}. File size: {file_size:.2f} MB")

def load_pbb_data(file_path):
    records = []
    try:
        with open(file_path, 'rb') as file:
            objects = ijson.items(file, 'item')
            for obj in objects:
                records.append(obj)
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File '{file_path}' not found.{Fore.RESET}")
    return records

def generate_data(generated_nops, num_records, wp_pekerjaan_options, wp_status_options, op_znt_options, op_nilai_bgn_options, tahun_pajak):
    total_nops = len(generated_nops)
    
    records = []
    data_wp_list = []
    used_nops = set()
    generated_keys = set()
    max_attempts = 100

    with alive_bar(total=min(total_nops, num_records), title=f"Generating Data OP from {kab_name} - {tahun_pajak}", length=25, bar='classic2', spinner='wait4', stats=True, monitor=True) as bar:
        while len(records) < total_nops and len(records) < num_records:
            attempts = 0
            while attempts < max_attempts:
                nop_entry = random.choice(generated_nops)
                nop = nop_entry['nop']
                
                if nop in used_nops:
                    attempts += 1
                    continue
                
                kab_code = nop[:4]
                kecamatan_code = int(nop[4:7])
                kelurahan_code = int(nop[7:10])
                blok = nop[10:14]
                no_urut = nop[14:18]

                wp_pekerjaan = random.choice(wp_pekerjaan_options)
                wp_status = random.choice(wp_status_options)
                op_znt = random.choice(op_znt_options)
                op_nilai_bgn = random.choice(op_nilai_bgn_options)
                op_nilai_bgn_value = random.randint(0, 100000) if op_nilai_bgn == "Manual" else 0

                op_kecamatan_nama = fake.city().upper()
                op_kelurahan_nama = fake.city().upper()
                op_jenis_tanah = random.randint(1, 13)
                op_dafnom = random.randint(1, 8)

                born_date = fake.date_of_birth().strftime('%m%d%y')
                code = str(random.choice([0, 7]))
                nik = f"{kab_code}{kecamatan_code:02d}{born_date}{no_urut}{code}"[:16]

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
                        "op_status_nilai_bgn": op_nilai_bgn,
                        "op_nilai_bgn": op_nilai_bgn_value,
                        "op_penilaian_status": False,
                        "op_penilaian_id": None,
                        "op_penilaian_time": None,
                        "op_penetapan_status": False,
                        "op_penetapan_id": None,
                        "op_penetapan_time": None,
                        "status_terbit": random.choice([True, False])
                    }
                }
                
                record_key = (nop, tahun_pajak)
                
                if record_key not in generated_keys:
                    generated_keys.add(record_key)
                    records.append(record)
                    data_wp_list.append(record["data_wp"])
                    used_nops.add(nop)
                    bar()
                    break
                else:
                    attempts += 1

    return records, data_wp_list

if __name__ == "__main__":
    config = load_config()
    kab_name = config.get('kab_name')
    kode_kab = config.get('kab_code')
    get_debug_max_nop = config.get('debug_max_nop', {'status'})
    wp_pekerjaan_options = config.get('wp_pekerjaan_options', ["PNS", "Swasta", "Wiraswasta", "Lainnya"])
    wp_status_options = config.get('wp_status_options', ["Pemakai", "Pemilik", "Pengelola", "Penyewa", "Sengketa"])
    tahun_pajak = config.get('tahun_pajak', datetime.now().year)
    
    generated_nops_file_path = 'SW_PBB/generated_nop.json'
    if not os.path.exists(generated_nops_file_path):
        print(f"{Fore.RED}File not found: {generated_nops_file_path}{Fore.RESET}")
        exit()
    
    generated_nops = load_generated_nops(generated_nops_file_path)
    
    if not generated_nops:
        print(f"{Fore.RED}No valid NOP data found. Exiting.{Fore.RESET}")
        exit()
    
    debug_max_nop = config.get('debug_max_nop')
    if debug_max_nop.get('status', True): 
        num_records = debug_max_nop.get('maxnop', len(generated_nops))
    else:
        num_records = len(generated_nops)
 
    op_znt_options = load_znt_data('CONFIG_DATA/znt_data.json', tahun_pajak)
    op_nilai_bgn_options = config.get('op_nilai_bgn_options', ["Manual", "Default"])
    
    print(f"Number of generated NOP on {kode_kab} - {kab_name}: {len(generated_nops)}")
    
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
    
    pbb_data_size = os.path.getsize(output_file_path) / (1024 * 1024)
    data_wp_size = os.path.getsize(output_wp_file_path) / (1024 * 1024)