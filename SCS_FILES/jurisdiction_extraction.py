import csv
import os
import argparse
import sys
import json

# parser = argparse.ArgumentParser()
# parser.add_argument("member_id", type=str, help="Provide the current time.")
# parser.add_argument("line_no", type=str, help="Provide the line no.")
# args = parser.parse_args()
member_id = sys.argv[1]
line_no = sys.argv[2]

json_str = sys.argv[3]
data = json.loads(json_str)
crew_control = data["crew_control"]
depots = data["depots"]
new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"
# member_id = 160925123842  # For testing purposes only, comment out in production
InitialServices_csv_file = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/InitialServices.csv"  # Replace with your CSV file path
Jurisdiction_csv_file = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/Jurisdiction.csv"  # Replace with your output CSV file path
outstation_file = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/Outstations.csv"  # Replace with your output CSV file path

col3_set = set()
col5_set = set()

with open(InitialServices_csv_file, 'r', newline='', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)  # Skip header or first row
    for row in reader:
        if len(row) >= 5:
            col3_set.add(row[2].strip())
            col5_set.add(row[4].strip())

merged_set = col3_set.union(col5_set)
merged_list = sorted(list(merged_set))
if line_no == '34':
    keywords = ["DSTO", "DW", "JPW", "KNR", "NFD"]
    cc1_list = [item for item in merged_list if any(k in item for k in keywords)]
    cc2_list = [item for item in merged_list if item not in cc1_list]
elif line_no == '7':
    keywords = ["PBGW", "MKPR", "SAKP", "DDSC"]
    cc1_list = [item for item in merged_list if any(k in item for k in keywords)]
    cc2_list = [item for item in merged_list if item not in cc1_list]
elif line_no == '7N':
    keywords = ["PBGW", "MKPR", "SAKP", "DDSC"]
    cc1_list = [item for item in merged_list if any(k in item for k in keywords)]
    cc2_list = [item for item in merged_list if item not in cc1_list]





stations_list = [item for item in merged_list if ' ' not in item and item not in depots]


crew_control_list = [cc + ' DN' for cc in crew_control] + [cc + ' UP' for cc in crew_control] + [cc for cc in crew_control]

outstations_list = [
    item for item in merged_list
    if item not in crew_control_list and ' ' in item
]
outstations_list = outstations_list + depots


print(stations_list)
print(outstations_list)
print(crew_control_list)

with open(Jurisdiction_csv_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    # for item in merged_list:
    if line_no == '34' or line_no =='7' or line_no == '7N':
        writer.writerow(cc1_list)
        writer.writerow(cc2_list)
        writer.writerow(crew_control_list)
    else:
        writer.writerow(merged_list)
        writer.writerow(crew_control_list)  # Write each jurisdiction in a new row

with open(outstation_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(outstations_list)
