import os
import random
import json
from alive_progress import alive_bar
from colorama import Fore, init

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

def check_znt_data(file_path):
    with open(file_path, 'r') as file:
        data = json.loads(file.read())
    if not data:
        print(f"{Fore.RED}ZNT data in {file_path} is empty. Exiting.{Fore.RESET}")
        exit()

# Load kecamatan_kelurahan data from JSON file
def load_kecamatan_kelurahan_data(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"{Fore.RED}Error: File '{file_path}' not found.{Fore.RESET}")
        exit(1)
    except json.JSONDecodeError:
        print(f"{Fore.RED}Error: File '{file_path}' is not a valid JSON.{Fore.RESET}")
        exit(1)

# Calculate maximum possible number of NOPs
def calculate_max_nops(kecamatan_kelurahan_data):
    n_kelurahan = sum(len([kelurahan for kelurahan in kecamatan['kelurahan'] if kelurahan.get('status_kel', False)]) 
                      for kecamatan in kecamatan_kelurahan_data.values())
    total_blok = 20
    total_no_urut = 999
    
    max_nops = n_kelurahan * (total_blok * total_no_urut)

    if debug_max_nop_status and debug_max_nop_status.get('status', True):
        return debug_max_nop_num
    else:
        return max_nops

# Generate NOP using loaded kecamatan_kelurahan data
def generate_nop(kode_kab, kecamatan_code, kelurahan_info, total_no_urut, current_blok, current_no_urut,
                 kode_blok_length=3, no_urut_length=4, kode_tanah_length=1):
    kode_kab = str(kode_kab).zfill(4)
    kode_kec = str(kecamatan_code)[-3:].zfill(3)
    kode_kel = str(kelurahan_info['kelurahan_code'])[-3:].zfill(3)
    kode_blok = str(current_blok).zfill(kode_blok_length)
    no_urut = str(current_no_urut).zfill(no_urut_length)
    kode_tanah = '0'
    
    nop = f"{kode_kab}{kode_kec}{kode_kel}{kode_blok}{no_urut}{kode_tanah}"
    
    next_no_urut = current_no_urut + 1
    
    return nop, next_no_urut

# Generate NOP and write to file
def generate_nop_and_write(kode_kab, count, kecamatan_kelurahan_data, kode_blok_start='001', no_urut_start='0001', output_dir='SW_PBB'):
    if not kecamatan_kelurahan_data:
        print(f"{Fore.RED}No kecamatan_kelurahan data available.{Fore.RESET}")
        return

    os.makedirs(output_dir, exist_ok=True)
    generated_nops = set()
    file_path = os.path.join(output_dir, "generated_nop.json")
    
    written_count = 0
    current_blok = int(kode_blok_start)
    current_no_urut = int(no_urut_start)
    
    total_no_urut = 999
    
    nop_data_list = []  # Collect NOP data
    
    with alive_bar(total=count, title=f"Generating NOP {kode_kab} {kab_name}",enrich_print=False, length=25, bar='classic2', spinner='circles') as pbar:
        while written_count < count:
            for kecamatan_code, kecamatan_info in kecamatan_kelurahan_data.items():
                for kelurahan_info in kecamatan_info['kelurahan']:
                    if not kelurahan_info.get('status_kel', False):
                        continue
                    
                    nop, current_no_urut = generate_nop(kode_kab, kecamatan_code, kelurahan_info, total_no_urut, current_blok, current_no_urut)
                    if nop in generated_nops:
                        continue

                    generated_nops.add(nop)
                    
                    kode_kec = nop[4:7]
                    kode_kel = nop[7:10]
                    kode_blok = nop[10:13]
                    no_urut = nop[13:17]
                    kode_tanah = nop[17]

                    nop_data = {
                        "kode_kab": kode_kab,
                        "kode_kec": kode_kec,
                        "kode_kel": kode_kel,
                        "kode_blok": kode_blok,
                        "no_urut": no_urut,
                        "kode_tanah": kode_tanah,
                        "nop": nop
                    }
                    
                    nop_data_list.append(nop_data)
                    written_count += 1
                    pbar()

                    if current_no_urut > total_no_urut:
                        current_blok += 1
                        current_no_urut = 1
            
            if written_count >= count:
                break
    
    # Write all NOP data to file
    print()
    with alive_bar(title="Saving NOP data", bar='classic2', stats=False) as progress:
        with open(file_path, 'w') as file:
            json.dump(nop_data_list, file, indent=4)  # Dump as a list for valid JSON
            progress()  # Update progress bar

    # Calculate file size in MB
    file_size = os.path.getsize(file_path) / (1024 * 1024)

    print(f"{count} NOP numbers generated and saved in {file_path} with {len(nop_data_list)} records. File size: {file_size:.2f} MB")

if __name__ == "__main__":
    config = load_config()
    kab_name = config.get('kab_name')
    debug_max_nop_status = config.get('debug_max_nop', {'status': True})
    debug_max_nop_num = config.get('debug_max_nop', {}).get('maxnop', 0)

    kecamatan_kelurahan_file = 'CONFIG_DATA/kecamatan_kelurahan_data.json'
    kecamatan_kelurahan_data = load_kecamatan_kelurahan_data(kecamatan_kelurahan_file)
    
    if not kecamatan_kelurahan_data:
        print(f"{Fore.RED}No kecamatan_kelurahan data available.{Fore.RESET}")
    else:
        max_nops = calculate_max_nops(kecamatan_kelurahan_data)
        print(f"Maximum possible NOP that can be generated: {max_nops}")
        
        random_kecamatan_code = random.choice(list(kecamatan_kelurahan_data.keys()))
        kode_kab_input = str(random_kecamatan_code)[:4]
        print(f"Generated kode_kab: {kode_kab_input} - {kab_name}")
        
        count = max_nops if isinstance(max_nops, int) else max_nops.get('maxnop', 0)
        kode_blok_start = '001'
        no_urut_start = '0001'
        
        generate_nop_and_write(kode_kab_input, count, kecamatan_kelurahan_data, kode_blok_start, no_urut_start)
