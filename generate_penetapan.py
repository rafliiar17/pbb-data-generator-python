import os
import json
import random
import uuid
from faker import Faker
from datetime import datetime
from tqdm import tqdm  # Import tqdm for the progress bar

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
    except json.JSONDecodeError:
        print("Failed to decode JSON. The file may be empty or corrupted.")
        return [], []

    if not data_op_saja:
        print("No data found in the JSON file.")
        return [], []

    records = []
    pembayaran_records = []  # Initialize list to hold payment data

    # Generate data for Penetapan
    for record_data in tqdm(data_op_saja[:num_records], desc="Generating Data for Penetapan"):
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

    # Generate data for Payment
    for record in tqdm(records, desc="Generating Payment Data"):
        pembayaran_record = {"data_pembayaran": record.pop('data_pembayaran')}  # Wrap payment data under 'data_pembayaran' key
        pembayaran_records.append(pembayaran_record)  # Append wrapped payment data to separate list

    return records, pembayaran_records  # Return both records and payment records

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
    with open(output_file_path, 'w') as file:
        json.dump(generated_data, file, indent=4)

    # Save payment data to a separate file
    output_dir_bayar = "SW_PBB/pbb_data_payment"
    if not os.path.exists(output_dir_bayar):
        os.makedirs(output_dir_bayar)

    pembayaran_file_path = os.path.join(output_dir_bayar, 'pbb_data_pembayaran.json')
    with open(pembayaran_file_path, 'w') as file:
        json.dump(pembayaran_data, file, indent=4)

    print(f"Generated {len(generated_data)} records and saved to {output_file_path}.")
    print(f"Payment data saved to {pembayaran_file_path}.")