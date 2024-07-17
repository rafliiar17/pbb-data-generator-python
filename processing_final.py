import json
import os  # Import os module to check file existence
import tqdm  # Import tqdm for progress bar functionality
import sys

# Set the encoding to utf-8
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Change the default encoding for stdout and stderr
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
# Function to validate file existence
def validate_file(path):
    if not os.path.exists(path):
        raise FileNotFoundError(f"The file {path} does not exist.")

# Load config.json
config_path = 'config.json'
validate_file(config_path)  # Validate file before loading
with open(config_path, 'r') as file:
    config = json.load(file)
print("Loaded config.json successfully.")  # Confirmation message

tahun = config['tahun_pajak']
pbb_sppt_path = f'SW_PBB/pbb_data_determination/{tahun}/pbb_sppt.json'
validate_file(pbb_sppt_path)  # Validate file before loading
with open(pbb_sppt_path, 'r') as file:
    pbb_sppt = json.load(file)
print("Loaded pbb_sppt.json successfully.")  # Confirmation message

# Load pbb_data_pembayaran.json
pbb_data_pembayaran_path = 'SW_PBB/pbb_data_payment/pbb_data_pembayaran.json'
validate_file(pbb_data_pembayaran_path)  # Validate file before loading
with open(pbb_data_pembayaran_path, 'r') as file:
    pbb_data_pembayaran = json.load(file)
print("Loaded pbb_data_pembayaran.json successfully.")  # Confirmation message

# Create an index for quick lookup
sppt_index = {(record['nop'], record['tahun_pajak']): record for record in pbb_sppt}

# Insert data from pbb_data_pembayaran.json to pbb_sppt.json
for payment_record in tqdm.tqdm(pbb_data_pembayaran, desc="Updating records"):
    payment_nop = payment_record['data_pembayaran']['nop']
    payment_tahun = payment_record['data_pembayaran']['tahun']
    key = (payment_nop, payment_tahun)

    # Include '_id' by removing it from the exclusion list
    data_pembayaran = {k: v for k, v in payment_record['data_pembayaran'].items() if k not in ['nop', 'tahun', '_id']}

    # Find the corresponding record in pbb_sppt.json using the index
    if key in sppt_index:
        sppt_record = sppt_index[key]
        sppt_record['data_pembayaran'] = data_pembayaran

# Save the updated pbb_sppt data to a new file
output_path = f'GW_PBB/{tahun}/pbb_sppt.json'
os.makedirs(os.path.dirname(output_path), exist_ok=True)  # Create directory if it does not exist
with open(output_path, 'w') as file:
    json.dump(pbb_sppt, file, indent=4)
print(f"Updated pbb_sppt.json has been saved to {output_path}.")  # Confirmation message