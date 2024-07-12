import json
import os
import random
from tqdm import tqdm

def extract_and_copy_data(input_file, output_file):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return

    with open(input_file, 'r') as infile:
        data = json.load(infile)
    
    extracted_data = []
    for record in data:
        extracted_record = {
            "nop": record.get("nop"),
            "tahun_pajak": record.get("tahun_pajak")
        }
        extracted_data.append(extracted_record)
    
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(output_file, 'w') as outfile:
        json.dump(extracted_data, outfile, indent=4)

config_file = 'config.json'

def get_bank_and_merchant_codes(config_file):
    with open(config_file, 'r') as cfile:
        config_data = json.load(cfile)
    bank_code = config_data['bank_code'][0]['code']  # Access the first element in the list
    bank_name = config_data['bank_code'][0]['name']  # Access the first element in the list
    merchant_code = None
    return bank_code,  config_data, merchant_code

bank_code, config_data, merchant_code = get_bank_and_merchant_codes(config_file)

tahun = config_data['tahun_pajak']
input_file = f'GW_PBB/{tahun}/pbb_sppt.json'
output_file = 'GW_PBB/payment_codes.json'

extract_and_copy_data(input_file, output_file)

def add_bank_and_merchant_codes(output_file, config_data):
    with open(output_file, 'r') as outfile:
        data = json.load(outfile)
        bank_codes = [bank['code'] for bank in config_data['bank_code']]
        bank_names = [bank['name'] for bank in config_data['bank_code']]
        for record in data:
            record['bank_code'] = random.choice(bank_codes)
            record['bank_name'] = bank_names
            record['merchant_code'] = None
    with open(output_file, 'w') as outfile:
        for record in tqdm(data, desc="Updating Payment Codes : "):
            bank_code = record['bank_code']
            bank_name = next((bank['name'] for bank in config_data['bank_code'] if bank['code'] == bank_code), None)
            record['bank_name'] = bank_name
        json.dump(data, outfile, indent=4)

add_bank_and_merchant_codes(output_file, config_data)

def generate_payment_code(index):
    payment_code = str(index).zfill(8)
    return f"{payment_code}"

def add_payment_codes(output_file, config_data):
    with open(output_file, 'r') as outfile:
        data = json.load(outfile)
        new_data = []
        for index, record in enumerate(data, start=1):
            record['payment_code'] = generate_payment_code(index)
            new_data.append(record)
    
    with open(output_file, 'w') as outfile:
        json.dump(new_data, outfile, indent=4)

    def update_pbb_determination(input_file, output_file):
        with open(output_file, 'r') as outfile:
            payment_data = json.load(outfile)
        
        with open(input_file, 'r') as infile:
            pbb_data = json.load(infile)
        
        payment_dict = {(record['nop'], record['tahun_pajak']): record['payment_code'] for record in payment_data}
        
        for record in pbb_data:
            key = (record['nop'], record['tahun_pajak'])
            if key in payment_dict:
                record['data_pembayaran']['payment_code'] = payment_dict[key]
        
        with open(input_file, 'w') as infile:
            json.dump(pbb_data, infile, indent=4)
    
    update_pbb_determination(f'GW_PBB/{tahun}/pbb_sppt.json', output_file)

add_payment_codes(output_file, config_data)