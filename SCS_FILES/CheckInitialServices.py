import csv
import os
from datetime import datetime, timedelta
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
parser.add_argument("line_no", type=str, help="Provide the line number.")
args = parser.parse_args()
member_id = args.member_id
line_no = args.line_no

new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"

def parse_extended_time(time_str):
    parts = time_str.strip().split(':')
    if len(parts) == 2:
        hours, minutes = map(int, parts)
        seconds = 0
    elif len(parts) == 3:
        hours, minutes, seconds = map(int, parts)
    else:
        raise ValueError(f"Invalid time format: {time_str}")
    
    base_date = datetime(1900, 1, 1)
    return base_date + timedelta(hours=hours, minutes=minutes, seconds=seconds)


def read_csv_and_check(filename):
    train_ids_set = set()
    rows = []

    # Read CSV and collect rows and train_ids
    with open(filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for i,row in enumerate(reader):
            if i == 0:  # Skip header row
                header = row
                continue
            rows.append(row)
            train_ids_set.add(int(row[1]))
    
    with open(f"{inputFileLocation}/Jurisdiction.csv", 'r', newline='') as f:
        reader = csv.reader(f)
        jurisdiction_list = [row for row in reader]
    i = len(jurisdiction_list)
    if i == 2:
        cc1 = [str(line) for line in jurisdiction_list[0]]
        cc2 = [str(line) for line in jurisdiction_list[0]]
        crew_control = [str(line) for line in jurisdiction_list[1]]
    elif i == 3:
        cc1 = [str(line) for line in jurisdiction_list[0]]
        cc2 = [str(line) for line in jurisdiction_list[1]]
        crew_control = [str(line) for line in jurisdiction_list[2]]
    elif i == 4:
        cc1 = [str(line) for line in jurisdiction_list[0]]
        cc2 = [str(line) for line in jurisdiction_list[1]]
        crew_control = [str(line) for line in jurisdiction_list[2]]

    train_ids = sorted(train_ids_set)
    check_list1 = []
    check_list_2 = []
    check_list_3 = []
    stabling_rows = []
    induction_rows = []


    with open(f"{inputFileLocation}/Outstations.csv", 'r', newline='') as f:
            reader = csv.reader(f)
            outstation_list = [row for row in reader]
    outstation_list = [stn for stn in outstation_list[0]]
    if line_no == '7' or line_no == '7N':
        outstation_list.extend(['IPE', 'MKPR'])
    # print(outstation_list)

    for train_id in train_ids:
        # Find all rows with this train_id
        train_rows = [row for row in rows if int(row[1]) == train_id]

        # check for first and last rows which should be having stabling and induction
        train_ind_stb_error = []
        induction_row = train_rows[0]
        stabling_row = train_rows[-1]
        if (induction_row[2] in outstation_list and stabling_row[4] in outstation_list):
            pass
        else: 
            train_ind_stb_error.append(train_rows[0])
            train_ind_stb_error.append(train_rows[-1])
        

        # Iterate in pairs
        for i in range(len(train_rows) - 1):
            # Parse time from 6th column of first row and 4th column of second row
            time_i_end = parse_extended_time(train_rows[i][5])
            time_j_start = parse_extended_time(train_rows[i+1][3])
            diff = (time_j_start - time_i_end).total_seconds() / 60
            if diff > time_diff_check or diff < 0:
                check_list1.append(train_rows[i])
                check_list1.append(train_rows[i+1])

            dur_1 = int(train_rows[i][7])
            dur_2 = int(train_rows[i+1][7])
            if dur_1 <= 0:
                check_list_2.append(train_rows[i])
            if dur_2 <= 0:
                check_list_2.append(train_rows[i+1])
            # if i == 1:
            #     print(diff_2)
            #CHECK ENDING STATION NAME OF CURRENT ROW WITH STARTING STATION NAME OF NEXT ROW
            if train_rows[i][4] != train_rows[i+1][2]:
                if train_rows[i][4] in crew_control and train_rows[i+1][2] in crew_control:
                    pass
                else:
                    check_list_3.append(train_rows[i])
                    check_list_3.append(train_rows[i+1])

        


        # to show all the induction and stabling rows
        stabling_rows.append(train_rows[-1])
        induction_rows.append(train_rows[0])

        stable_CC1 = 0
        stable_CC2 = 0
        induct_CC2 = 0
        induct_CC1 = 0
        for stabling_row in stabling_rows:
            if stabling_row[4] in cc1:
                stable_CC1 += 1
            else: stable_CC2 += 1
        for induction_row in induction_rows:
            if induction_row[2] in cc1:
                induct_CC1 += 1
            else: induct_CC2 += 1
    
    mismatch_CC1 = (stable_CC1 - induct_CC1)
    mismatch_CC2 = (stable_CC2 - induct_CC2)



    print(mismatch_CC1, mismatch_CC2, len(check_list1)/2, len(check_list_2), len(check_list_3)/2, len(train_ind_stb_error)/2, sep='\n')
    print(f"Mismatch in CC1 induction and stabling: {mismatch_CC1}")

    print(f"Mismatch in CC2 induction and stabling: {mismatch_CC2}")
          

    print("same train time difference conflicts found:", len(check_list1)/2)

    
    print("Service time Conflicts found =",int(len(check_list_2)))
    
    print("STATION Conflicts found =",int(len(check_list_3)/2))

    print("Same Train Induction or Stabling error found:", len(train_ind_stb_error)/2)
    with open(f"{inputFileLocation}/InitialServices_check.csv", 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        writer.writerow(['CC1 INDUCTIONS', induct_CC1, '', 'CC1 STABLING', stable_CC1,'','',''])
        writer.writerow(['CC2 INDUCTIONS', induct_CC2, '', 'CC2 STABLING', stable_CC2,'','',''])
        writer.writerow(['TOTAL INDUCTIONS',induct_CC1 + induct_CC2, '', 'TOTAL STABLING', stable_CC1 + stable_CC2,'','',''])
        

        for i,row in enumerate(check_list1):
            if i == 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
                writer.writerow([f"More than {time_diff_check} minutes reversal rows are as follows:", '', '', '', '', '', '', ''])
            if i % 2 == 0 and i != 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
            writer.writerow(row)

        for i,row in enumerate(check_list_2):
            if i == 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
                writer.writerow(["TIME Conflict rows are as follows:", '', '', '', '', '', '', ''])
            if i % 2 == 0 and i != 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
            writer.writerow(row)

        for i,row in enumerate(check_list_3):
            if i == 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
                writer.writerow(["STATION name Conflict rows are as follows:", '', '', '', '', '', '', ''])
            if i % 2 == 0 and i != 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
            writer.writerow(row)

        for i,row in enumerate(train_ind_stb_error):
            if i == 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
                writer.writerow(["Induction and Stabling error rows are as follows:", '', '', '', '', '', '', ''])
            if i % 2 == 0 and i != 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
            writer.writerow(row)

        for i,induction_row in enumerate(induction_rows):
            if i == 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
                writer.writerow(["Induction Rows are as follows:", '', '', '', '', '', '', ''])
            writer.writerow(['', '', '', '', '', '', '', ''])
            writer.writerow(induction_row)

        for i,stabling_row in enumerate(stabling_rows):
            if i == 0:
                writer.writerow(['', '', '', '', '', '', '', ''])
                writer.writerow(["Stabling Rows are as follows:", '', '', '', '', '', '', ''])
            writer.writerow(['', '', '', '', '', '', '', ''])
            writer.writerow(stabling_row)
        
        
        

# Example usage:
path = os.getcwd()
inputFileLocation = os.path.join(path, f'{new_location}/USEFUL OUTPUT_{member_id}')
time_diff_check = 30  # minutes
read_csv_and_check(f"{inputFileLocation}/InitialServices.csv")