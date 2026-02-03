import pandas as pd
import sys
import os
import argparse
import datetime
from datetime import datetime, timedelta, time

parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Member ID.")
parser.add_argument("line_no", type=str, help="Line No.")
args = parser.parse_args()
member_id = args.member_id
line_no = args.line_no

new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"
blank_tc_path = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/SOLUTION 1/BLANK TC {member_id} LINE {line_no}.xlsx"
excel_path = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/{member_id}.xlsx"

# Function to convert Excel float to time
def convert_excel_time(val):
    # Case 1: Excel numeric time (fraction of a day)
    if isinstance(val, (int, float)) and 0 <= val < 2:
        return (datetime(1899, 12, 30) + timedelta(days=val)).time()
    
    # Case 2: pandas Timestamp or datetime.datetime
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.time()
    
    # Case 3: already a datetime.time
    if isinstance(val, time):
        return val
    
    # Case 4: string values like "08:30:00"
    if isinstance(val, str):
        try:
            return datetime.strptime(val, "%H:%M:%S").time()
        except ValueError:
            return val  # leave unchanged if parsing fails
    
    # Default: return as-is
    return val

if not os.path.exists(excel_path):
    print(f"Error: The file {excel_path} does not exist.")
    sys.exit(1)

try:
    df = pd.read_excel(f"{excel_path}",sheet_name="Sheet1", header = None)
    df = df.map(lambda x: x.strip() if isinstance(x, str) else x)
    df[df.columns[1:]] = df[df.columns[1:]].astype("object")
    # your Excel ranges (convert to 0-based indices)
    if line_no == "AEL":
        ranges = [
            (1, 2),      # Excel B2:XFD2
            (4, 11),     # Excel B5:XFD11
            (16, 23),    # Excel B17:XFD23
            (24, 25)     # Excel B25:XFD25
        ]
    elif line_no == "34":
        ranges = [
            (1, 2),      # Excel B2:XFD2
            (4, 54),     # Excel B5:XFD54
            (59, 109),    # Excel B60:XFD109
            (111, 112)     # Excel B25:XFD25
        ]
    elif line_no == "7":
        ranges = [
            (1, 2),      # Excel B2:XFD2
            (6, 50),     # Excel B7:XFD50
            (51, 52),    # Excel B52:XFD52
            (54,55),    # Excel B55:XFD55
            (56, 100),    # Excel B57:XFD100
            (102, 103)     # Excel B103:XFD103
        ]
    # Step 1: cast all relevant rows/cols to object dtype first
    for start, end in ranges:
        df.iloc[start:end, 1:] = df.iloc[start:end, 1:].astype("object")
    # Step 2: now safely apply your time conversion function
    for start, end in ranges:
        df.iloc[start:end, 1:] = df.iloc[start:end, 1:].map(convert_excel_time)

    # print(df)
    df_transposed = df.transpose()
    print("Transposed DataFrame:")
    print(df_transposed)

except Exception as e:
    print(f"Error reading the Excel file: {e}")
    sys.exit(1)
# Step 2:
# Select columns by index: 0, 1, 3, 16
if line_no == "AEL":
    final_df = df_transposed.iloc[:, [0, 1, 3, 16,17,22,3,4,9,10,3,24,23]].copy()
elif line_no == "34":
    final_df = df_transposed.iloc[:, [3, 0, 1, 4,12,37,44,53,54,3,59,68,75,100,3,108,109,3,111,110]].copy()
elif line_no == "7":
    final_df = df_transposed.iloc[:, [0, 1, 3, 16,17,22,3,4,9,10,3,24,23]].copy()


final_df.to_excel(blank_tc_path, index=False, header=False)
print(f"Trip Chart saved to {blank_tc_path}")
# sys.exit(0)
# Insert a blank column named "Duty No" at position 3
if line_no == "AEL":
    duty_columns = [3,5,7,9,12,14]
elif line_no == "34":
    duty_columns = [3,5,7,15,17,20,24]
else: duty_columns = []


for i,value in enumerate(duty_columns):
    final_df.insert(value, f"Duty No_{i+1}", "")
for value in duty_columns:
    final_df.iloc[0,value] = "Duty No"

#---------line34 SPECIFIC CODE--------
if line_no == "34":
    #--------COLUMN RENAMING--------
    final_df.iloc[0,22] = "REVERSAL FROM"
    #--------FILLING REVERSAL FROM COLUMN--------
    for row in range(1, final_df.shape[0]):
        if not pd.isna(final_df.iloc[row, 21]):
            final_df.iloc[row, 22] = 'DSTO'
        elif not pd.isna(final_df.iloc[row, 18]):
            final_df.iloc[row, 22] = 'DW'
        else:
            final_df.iloc[row, 22] = ''
print(final_df)

# Save the final DataFrame to a new Excel file
final_df.to_excel(blank_tc_path, index=False, header=False)
print(f"Trip Chart saved to {blank_tc_path}")