import subprocess
import json

def load_config():
    file_path = 'config.json'
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

config = load_config()
tahun = config.get('tahun_pajak')
kode = config.get('kab_code')
nama = config.get('kab_name')
auto_assdet = config.get('auto_assdet', True)

# Define the base commands to be executed
commands = [
    'python generate_keckel.py',
    'python generate_kelas.py',
    'python generate_znt.py',
    'python generate_nop.py',
    'python generate_op.py',
    'python generate_penetapan.py'
]

# Execute each base command and print result
for command in commands:
    subprocess.run(command, shell=True)
    print()  # Add a newline after the command execution
    print(f"{command.split()[1]} completed.")  # Print which script has completed

# Append assessment and determination commands if auto_assdet is True
if auto_assdet:
    commands.append('python processing_assesment.py')
    full_command = ' && '.join(commands)
    subprocess.run(full_command, shell=True)
    print()  # Add a newline after the command execution
    print("Assessment processing completed.")

    commands.append('python processing_determination.py')
    full_command = ' && '.join(commands)
    subprocess.run(full_command, shell=True)
    print()  # Add a newline after the command execution
    print("Determination processing completed.")

    commands.append('python generate_paycode.py')
    full_command = ' && '.join(commands)
    subprocess.run(full_command, shell=True)
    print()  # Add a newline after the command execution
    print("Paycode generation completed.")

    commands.append('python processing_final.py')

# Combine commands into a single command string with '&&' to ensure sequential execution
full_command = ' && '.join(commands)

# Execute the combined command
subprocess.run(full_command, shell=True)
print()  # Add a newline after the command execution
print("Final processing completed.")

print("GENERATING DATA IS SUCCESSED!!")