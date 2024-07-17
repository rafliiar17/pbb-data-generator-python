import json
import os
import random
from alive_progress import alive_bar
from colorama import Fore, init
import sys
import io
# Set the encoding to utf-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Change the default encoding for stdout and stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
init(autoreset=True)

def extract_and_copy_data(input_file, output_file):
    if not os.path.exists(input_file):
        print(Fore.RED + f"File not found: {input_file}")
        return False

    with open(input_file, 'r') as infile:
        try:
            data = json.load(infile)
        except json.decoder.JSONDecodeError as e:
            print(Fore.RED + "Error loading JSON data:", e)
            return False

    extracted_data = []
    with alive_bar(len(data), bar='circles', spinner='dots_waves') as bar:
        for record in data:
            if 'data_pembayaran' in record:
                extracted_record = {
                    "nop": record['data_pembayaran']['nop'],
                    "tahun_pajak": record['data_pembayaran']['tahun']
                }
                extracted_data.append(extracted_record)
            bar()

    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(output_file, 'w') as outfile:
        json.dump(extracted_data, outfile, indent=4)
    
    print(Fore.GREEN + f"Extracted data saved to {output_file} Output file size: {os.path.getsize(output_file)} bytes")
    print()
    return True

def get_bank_and_merchant_codes(config_file):
    if not os.path.exists(config_file):
        print(Fore.RED + f"Config file not found: {config_file}")
        return None, None, None
    
    with open(config_file, 'r') as cfile:
        try:
            config_data = json.load(cfile)
        except json.decoder.JSONDecodeError as e:
            print(Fore.RED + "Error loading config JSON data:", e)
            return None, None, None
    
    bank_code = config_data['bank_code'][0]['code']
    bank_name = config_data['bank_code'][0]['name']
    merchant_code = None
    return bank_code, config_data, merchant_code

def add_bank_and_merchant_codes(output_file, config_data):
    if not os.path.exists(output_file):
        print(Fore.RED + f"File not found: {output_file}")
        return False

    with open(output_file, 'r') as outfile:
        try:
            data = json.load(outfile)
        except json.decoder.JSONDecodeError as e:
            print(Fore.RED + "Error loading JSON data from output file:", e)
            return False
    
    bank_codes = [bank['code'] for bank in config_data['bank_code']]
    bank_names = [bank['name'] for bank in config_data['bank_code']]
    
    with alive_bar(len(data), bar='circles', spinner='dots_waves') as bar:
        for record in data:
            chosen_bank_code = random.choice(bank_codes)
            record['bank_code'] = chosen_bank_code
            record['bank_name'] = next((bank['name'] for bank in config_data['bank_code'] if bank['code'] == chosen_bank_code), None)
            record['merchant_code'] = None
            bar()
    
    with open(output_file, 'w') as outfile:
        json.dump(data, outfile, indent=4, ensure_ascii=False)
    
    print(Fore.GREEN + f"Bank and merchant codes added to {output_file} Output file size: {os.path.getsize(output_file)} bytes")
    print()
    return True

def generate_payment_code(index):
    payment_code = str(index).zfill(8)
    return f"{payment_code}"

def add_payment_codes(output_file, config_data):
    if not os.path.exists(output_file):
        print(Fore.RED + f"File not found: {output_file}")
        return False

    with open(output_file, 'r') as outfile:
        try:
            data = json.load(outfile)
        except json.decoder.JSONDecodeError as e:
            print(Fore.RED + "Error loading JSON data from output file:", e)
            return False

    new_data = []
    with alive_bar(len(data), bar='circles', spinner='dots_waves') as bar:
        for index, record in enumerate(data, start=1):
            record['payment_code'] = generate_payment_code(index)
            new_data.append(record)
            bar()
    
    with open(output_file, 'w') as outfile:
        json.dump(new_data, outfile, indent=4)
    
    print(Fore.GREEN + f"Payment codes added to {output_file} Output file size: {os.path.getsize(output_file)} bytes")
    print()
    return True

def update_pbb_determination(input_file, output_file):
    if not os.path.exists(output_file):
        print(Fore.RED + f"File not found: {output_file}")
        return False

    if not os.path.exists(input_file):
        print(Fore.RED + f"File not found: {input_file}")
        return False

    with open(output_file, 'r') as outfile:
        try:
            payment_data = json.load(outfile)
        except json.decoder.JSONDecodeError as e:
            print(Fore.RED + "Error loading JSON data from output file:", e)
            return False

    with open(input_file, 'r') as infile:
        try:
            pbb_data = json.load(infile)
        except json.decoder.JSONDecodeError as e:
            print(Fore.RED + "Error loading JSON data from input file:", e)
            return False
    
    payment_dict = {
        (record['nop'], record['tahun_pajak']): record['payment_code']
        for record in payment_data
    }
    
    with alive_bar(len(pbb_data), bar='circles', spinner='dots_waves') as bar:
        for record in pbb_data:
            key = (record['data_pembayaran']['nop'], record['data_pembayaran']['tahun']) if 'data_pembayaran' in record else None
            if key in payment_dict:
                record['data_pembayaran']['payment_code'] = payment_dict[key]
            bar()
    
    with open(input_file, 'w') as infile:
        json.dump(pbb_data, infile, indent=4)
    
    print(Fore.GREEN + f"PBB determination updated in {input_file}Input file size: {os.path.getsize(input_file)} bytes")
    return True

config_file = 'config.json'

bank_code, config_data, merchant_code = get_bank_and_merchant_codes(config_file)

if config_data is None:
    print(Fore.RED + "Failed to load config data. Exiting.")
    exit(1)

input_file = f'SW_PBB/pbb_data_payment/pbb_data_pembayaran.json'
output_file = 'SW_PBB/pbb_data_payment/pbb_data_codes.json'

if extract_and_copy_data(input_file, output_file):
    if add_bank_and_merchant_codes(output_file, config_data):
        if add_payment_codes(output_file, config_data):
            update_pbb_determination(input_file, output_file)
