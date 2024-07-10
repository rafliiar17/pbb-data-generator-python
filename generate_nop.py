import os
import random
import json
from tqdm import tqdm

def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

config = load_config()
kab_name = config.get('kab_name')
debug_max_nop_status = config.get('debug_max_nop', {'status'})
debug_max_nop_num = config.get('debug_max_nop', {'maxnop'})

# Function to load kecamatan_kelurahan data from JSON file
def load_kecamatan_kelurahan_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

# Function to calculate maximum possible number of NOPs
def calculate_max_nops(kecamatan_kelurahan_data):
    n_kelurahan = sum(len([kelurahan for kelurahan in kecamatan['kelurahan'] if kelurahan.get('status_kel', False)]) 
                      for kecamatan in kecamatan_kelurahan_data.values())
    total_blok = 20  # 001 to 999
    total_no_urut = 999  # 0001 to 999
    
    max_nops = n_kelurahan * (total_blok * total_no_urut)
    
    # Check if debug_max_nop is set to True and use the maxnop value
    if debug_max_nop_status and debug_max_nop_status.get('status', False):
        return debug_max_nop_num
    
    return max_nops

# Function to generate NOP and write to file
def generate_nop_and_write(kode_kab, count, kecamatan_kelurahan_data, kode_blok_start='001', no_urut_start='0001', output_dir='GENERATED_DATA'):
    os.makedirs(output_dir, exist_ok=True)
    generated_nops = set()
    file_path = os.path.join(output_dir, f"generated_nop.json")
    
    with open(file_path, 'w') as file:
        written_count = 0
        current_blok = int(kode_blok_start)
        current_no_urut = int(no_urut_start)
        
        total_no_urut = 999  # Assuming total_no_urut is 999
        
        nop_data_list = []  # List to collect NOP data
        
        with tqdm(total=count, desc="Generating NOP " + str(kode_kab) + " " + str(kab_name)) as pbar:
            while written_count < count:
                # Iterate through each kelurahan
                for kecamatan_code, kecamatan_info in kecamatan_kelurahan_data.items():
                    for kelurahan_info in kecamatan_info['kelurahan']:
                        if not kelurahan_info.get('status_kel', False):  # Check if status_kel is true
                            continue  # Skip if status_kel is false
                        
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
                        
                        nop_data_list.append(nop_data)  # Append each NOP data to the list
                        written_count += 1
                        pbar.update(1)

                        if current_no_urut > total_no_urut:
                            current_blok += 1
                            current_no_urut = 1  # Reset to 0001 if exceeds 999
                
                if written_count >= count:
                    break  # Exit while loop if written_count reaches the required count
        
        # Write all NOP data to file as a JSON array
        file.write(json.dumps(nop_data_list, indent=4))

    print(f"{count} NOP numbers generated and saved in {file_path}")

# Function to generate NOP using loaded kecamatan_kelurahan data
def generate_nop(kode_kab, kecamatan_code, kelurahan_info, total_no_urut, current_blok, current_no_urut,
                 kode_blok_length=3, no_urut_length=4, kode_tanah_length=1):
    kode_kab = str(kode_kab).zfill(4)
    kode_kec = str(kecamatan_code)[-3:].zfill(3)
    kode_kel = str(kelurahan_info['kelurahan_code'])[-3:].zfill(3)
    kode_blok = str(current_blok).zfill(kode_blok_length)
    no_urut = str(current_no_urut).zfill(no_urut_length)
    kode_tanah = '0'
    
    nop = f"{kode_kab}{kode_kec}{kode_kel}{kode_blok}{no_urut}{kode_tanah}"
    
    # Increment no_urut for the next call
    next_no_urut = current_no_urut + 1
    
    return nop, next_no_urut

if __name__ == "__main__":
    kecamatan_kelurahan_file = 'CONFIG_DATA/kecamatan_kelurahan_data.json'
    kecamatan_kelurahan_data = load_kecamatan_kelurahan_data(kecamatan_kelurahan_file)
    
    max_nops = calculate_max_nops(kecamatan_kelurahan_data)
    print(f"Maximum possible NOP that can be generated: {max_nops}")
    
    random_kecamatan_code = random.choice(list(kecamatan_kelurahan_data.keys()))
    kode_kab_input = str(random_kecamatan_code)[:4]
    print(f"Generated kode_kab: {kode_kab_input} - {kab_name}")
    
    count = max_nops if isinstance(max_nops, int) else max_nops.get('maxnop', 0)
    kode_blok_start = '001'
    no_urut_start = '0001'
    
    generate_nop_and_write(kode_kab_input, count, kecamatan_kelurahan_data, kode_blok_start, no_urut_start)