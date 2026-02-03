import csv
import os
import shutil
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
parser.add_argument("line_no", type=str, help="Provide the line number.")
args = parser.parse_args()
member_id = args.member_id
line_no = args.line_no

new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"

def windows_sort_key(filename):
    # Split filename into numeric and non-numeric parts for Windows Explorer-like sorting
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', filename)]

def merge_sorted_csv_files(input_folder, output_file):
    # List all CSV files in the folder and sort them as per Windows Explorer
    files = [f for f in os.listdir(input_folder) if f.lower().endswith('.csv')]
    files.sort(key=windows_sort_key)

    with open(output_file, 'w', newline='') as outfile:
        writer = csv.writer(outfile)
        for filename in files:
            print(f"Processing file: {filename}")
            file_path = os.path.join(input_folder, filename)
            with open(file_path, 'r', newline='') as infile:
                reader = csv.reader(infile)
                for row in reader:
                    writer.writerow(row)
    

# Example usage:
input_folder = os.path.dirname(os.path.abspath(__file__)) + f'/{new_location}/USEFUL OUTPUT_{member_id}/TEMP_OUTPUT_FILES/'
output_folder = os.path.dirname(os.path.abspath(__file__)) + f'/{new_location}/USEFUL OUTPUT_{member_id}/'
output_file = f'{output_folder}SetOfDuties.csv'
merge_sorted_csv_files(input_folder, output_file)
shutil.rmtree(input_folder)
print("Temp Output folder deleted and SetofDuties.csv file created.")