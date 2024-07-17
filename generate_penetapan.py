import os
import json
import uuid
from faker import Faker
from datetime import datetime
from alive_progress import alive_bar
from colorama import Fore, init
import sys

# Set the encoding to utf-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Change the default encoding for stdout and stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
fake = Faker('id_ID')

def load_config():
    with open('config.json', 'r') as file:
        config = json.load(file)
    return config

def generate_data(num_records, tahun_pajak):
    try:
        with open('SW_PBB/pbb_data_op.json', 'r') as f:
            data_op_saja = json.load(f)
    except FileNotFoundError:
        print("The file was not found. Please check the file path.")
        return [], []
    except json.JSONDecodeError as e:
        print("Failed to decode JSON. The file may be empty or corrupted.")
        return [], []

    if not data_op_saja:
        print("No data found in the JSON file.")
        return [], []

    records = []
    pembayaran_records = []

    with alive_bar(num_records, title="Generating Data for Penetapan", bar='classic2', spinner='wait4') as bar:
        for record_data in data_op_saja[:num_records]:
            nop = record_data['nop']
            tahun_pajak_data = record_data['tahun_pajak']
            record = {
                "_id": str(uuid.uuid4()),
                "nop": nop,
                "tahun_pajak": tahun_pajak_data,
                "data_penetapan": {
                    "op_penilaian_id" : None,
                    "op_penilaian_time" : None,
                    "op_penilaian_status" : False,
                    "op_penetapan_id" : None,
                    "op_penetapan_status" : False,
                    "op_tahun_penetapan_terakhir" : 0,
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
                    "nop": nop,
                    "tahun": tahun_pajak,
                    "payment_code": {
                        "$numberLong": 0
                    },
                    "payment_coll_code": {
                        "$numberLong": 0
                    },
                    "payment_flag_status": 0,
                    "payment_deduction": False,
                    "payment_compensation": False,
                    "payment_settlement_date": None,
                    "payment_amount": 0,
                    "payment_amount_ded": 0,
                    "payment_penalty": 0,
                    "payment_bill": 0,
                    "payment_amount_ded": 0,
                    "payment_penalty_ded": 0,
                    "payment_amount_compensation": 0,
                    "payment_penalty_compensation": 0,
                    "payment_amount_after_compensation": 0,
                    "payment_penalty_after_compensation": 0,
                    "payment_amount_after_deduction": 0,
                    "payment_penalty_after_deduction": 0,
                    "payment_amount_after_penalty": 0,
                    "payment_penalty_after_penalty": 0,
                    "payment_payed_amount": 0,
                    "payment_payed_penalty": 0,
                    "payment_payed_total":0,
                    "payment_flag": True,
                    "payment_paid": {
                        "$date": None
                    },
                    "bank_code": None,
                    "merchant_code": None,
                    "channel_code": None,
                    "payment_ref_num": None,
                    "payment_gw_refnum": None,
                    "payment_sw_refnum": None,
                    "payment_settlemeant_date": None
                }
            }
            records.append(record)
            bar()  # Update the progress bar

    with alive_bar(len(records), title="Generating Payment Data", bar='classic2', spinner='wait4') as bar:
        for record in records:
            pembayaran_record = {"data_pembayaran": record.pop('data_pembayaran')}
            pembayaran_records.append(pembayaran_record)
            bar()  # Update the progress bar
            
    return records, pembayaran_records

def save_json(data, file_path):
    if os.path.exists(file_path):
        os.remove(file_path)

    with alive_bar(len(data), title=f"Saving to {os.path.basename(file_path)}", bar='classic2', spinner='wait4') as bar:
        with open(file_path, 'w') as file:
            file.write("[\n")  # Start of JSON array
            for index, item in enumerate(data):
                file.write(json.dumps(item, indent=4))  # Write JSON object with indentation
                if index < len(data) - 1:
                    file.write(',')  # Add comma if it's not the last item
                file.write('\n')  # Add newline after each object for readability
                bar()  # Update the progress bar for each record saved
            file.write("]\n")  # End of JSON array with newline at the end (optional)



if __name__ == "__main__":
    config = load_config()
    debug_max_nop = config.get('debug_max_nop', {'status'}==True)
    
    if debug_max_nop.get('status', False):
        num_records = debug_max_nop.get('maxnop')
    else:
        with open('SW_PBB/pbb_data_op.json') as f:
            data_op_saja = json.load(f)
            num_records = len(data_op_saja)  # Ensure this line is correctly determining the number of records

    tahun_pajak = datetime.now().year
    generated_data, pembayaran_data = generate_data(num_records, tahun_pajak)  # Unpack both datasets
    
    output_dir = 'SW_PBB'
    output_file_path = os.path.join(output_dir, 'pbb_data_penetapan.json')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Save main data
    save_json(generated_data, output_file_path)

    # Save payment data to a separate file
    output_dir_bayar = "SW_PBB/pbb_data_payment"
    if not os.path.exists(output_dir_bayar):
        os.makedirs(output_dir_bayar)

    pembayaran_file_path = os.path.join(output_dir_bayar, 'pbb_data_pembayaran.json')
    save_json(pembayaran_data, pembayaran_file_path)

    output_file_size = os.path.getsize(output_file_path) / (1024 * 1024)
    pembayaran_file_size = os.path.getsize(pembayaran_file_path) / (1024 * 1024)
    print()
    print(f"{Fore.GREEN}Generated {len(generated_data)} and saved records Penetapan to {output_file_path} Output file size: {output_file_size:.2f} MB")
    print(f"Generated {len(generated_data)} and saved records Payment to {pembayaran_file_path} Output file size: {pembayaran_file_size:.2f} MB{Fore.RESET}")