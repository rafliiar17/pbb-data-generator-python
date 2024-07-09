import os
import json
import random
import uuid
from faker import Faker
from datetime import datetime
from tqdm import tqdm

fake = Faker('id_ID')

def load_generated_nops(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        print("JSON file is valid.")
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return []
    return data

def generate_data(num_records, wp_pekerjaan_options, wp_status_options, op_znt_options, tahun_pajak):
    generated_nops = load_generated_nops('GENERATED_DATA/generated_nop.json')
    total_nops = len(generated_nops)
    
    records = []
    generated_keys = set()  # Initialize as an empty set to store unique (nop, tahun_pajak) pairs
    max_attempts = 10000  # Maximum number of attempts to generate a unique record

    with tqdm(total=min(total_nops, num_records), desc="Generating Data") as pbar:
        while len(records) < total_nops and len(records) < num_records:
            attempts = 0
            while attempts < max_attempts:
                # Randomly select a NOP from generated_nops
                nop_entry = random.choice(generated_nops)
                nop = nop_entry['nop']
                
                # Check if (nop, tahun_pajak) pair is already generated
                if (nop, tahun_pajak) in generated_keys:
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

                # Generate kelas_bumi
                kelas_bumi = f"B{random.randint(1, 10)}"  # Example generation logic

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
                        "op_alamat": f"BLOK. {blok}",
                        "op_rt": 0,
                        "op_rw": 0,
                        "op_kodepos": fake.postcode()
                    },
                    "data_op": {
                        "op_jenis_tanah": op_jenis_tanah,
                        "op_znt": op_znt,
                        "op_dafnom": op_dafnom,
                        "op_luas_bumi": random.randint(1000, 3000),
                        "op_luas_bgn": random.randint(10, 100),
                        "op_jml_bgn": random.randint(1, 10)
                    },
                    "data_penetapan": {
                        "op_kelas_bumi": kelas_bumi,
                        "op_kelas_bgn": f"A{random.randint(80, 100)}",
                        "op_njop_bumi": 0,
                        "op_njop_bgn": random.randint(1000000, 2000000),
                        "op_njoptkp": 1000000,
                        "op_njkp_b4_pengenaan": random.randint(2000000, 3000000),
                        "op_persen_pengenaan": random.randint(20, 30),
                        "op_njkp_after_pengenaan": random.randint(1000000, 1500000),
                        "op_tarif": random.choice([0.100, 0.200, 0.300, 0.400, 0.500]),
                        "sebelum_stimulus": random.randint(50000, 100000),
                        "pengali_stimulus": 10,
                        "pengurang_stimulus": random.randint(20000, 50000),
                        "selisih_stimulus": random.randint(20000, 50000),
                        "ketetapan_bayar": random.randint(50000, 100000),
                        "tanggal_penetapan": {
                            "$date": fake.date_time_this_year().isoformat()
                        },
                        "user_penetapan": fake.user_name(),
                        "tanggal_terbit": {
                            "$date": fake.date_time_this_year().isoformat()
                        },
                        "jatuh_tempo": {
                            "$date": fake.date_time_this_year().isoformat()
                        },
                        "user_input": fake.user_name(),
                        "createdAt": {
                            "$date": fake.date_time_this_year().isoformat()
                        },
                        "updatedAt": {
                            "$date": fake.date_time_this_year().isoformat()
                        }
                    },
                    "data_pembayaran": {
                        "payment_code": {
                            "$numberLong": str(random.randint(90000000000, 99999999999))
                        },
                        "payment_coll_code": {
                            "$numberLong": str(random.randint(1900000000000, 1999999999999))
                        },
                        "payment_flag_status": 1,
                        "payment_deduction": False,
                        "payment_installment": False,
                        "payment_compensation": False,
                        "payment_flag": True,
                        "payment_paid": {
                            "$date": fake.date_time_this_year().isoformat()
                        },
                        "payment_settlement_date": fake.date_time_this_year().strftime('%Y%m%d'),
                        "bank_code": random.randint(600000, 700000),
                        "merchant_code": random.randint(800, 900),
                        "channel_code": random.randint(800, 900),
                        "payment_ref_num": str(uuid.uuid4()),
                        "payment_gw_refnum": str(uuid.uuid4()),
                        "payment_sw_refnum": str(uuid.uuid4()),
                        "payment_amount": random.randint(50000, 100000),
                        "payment_amount_ded": 0,
                        "payment_penalty": random.randint(5000, 15000),
                        "payment_penalty_ded": 0,
                        "payment_total": random.randint(50000, 100000),
                        "user_payment": fake.user_name(),
                        "installment_flag": 1,
                        "booking_expired": {
                            "$date": fake.date_time_this_year().isoformat()
                        }
                    }
                }

                generated_keys.add((nop, tahun_pajak))
                records.append(record)
                pbar.update(1)
                break  # Break out of attempts loop once record is generated

            if attempts == max_attempts:
                print("Max attempts reached, skipping record generation.")
                break  # Break out of records generation loop if max attempts reached

    return records

# Function to save data to JSON file
def save_data(data, output_dir, filename):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

# Main execution
if __name__ == "__main__":
    import argparse
    import time

    parser = argparse.ArgumentParser(description="Generate PBB data.")
    parser.add_argument("--tahun_pajak", type=int, required=True, help="Tahun Pajak")

    args = parser.parse_args()

    WP_PEKERJAAN_OPTIONS = ["PNS", "Swasta", "Wiraswasta", "Lainnya"]
    WP_STATUS_OPTIONS = ["Pemakai","Pemilik","Pengelola","Penyewa","Sengketa"]
    OP_ZNT_OPTIONS = ["A", "B", "C", "D"]

    # Load generated NOPs to determine the number of records
    generated_nops = load_generated_nops('GENERATED_DATA/generated_nop.json')
    num_records = len(generated_nops)

    start_time = time.time()
    generated_data = generate_data(num_records, WP_PEKERJAAN_OPTIONS, WP_STATUS_OPTIONS, OP_ZNT_OPTIONS, args.tahun_pajak)
    save_data(generated_data, "DATA_OP", f"pbb_data_{args.tahun_pajak}.json")
    end_time = time.time()

    print(f"Data generation completed in {end_time - start_time:.2f} seconds")