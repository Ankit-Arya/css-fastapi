import pandas as pd
import csv
import os
import argparse
import json
# --------------------------------------------- PARSE Command Line Input -----------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
parser.add_argument("stepping_back_raw", type=str, help="Provide the stepping back data as a JSON string.")
args = parser.parse_args()
member_id = args.member_id
stepping_back_raw = args.stepping_back_raw

user_stepping_back = json.loads(stepping_back_raw)

start_time_sbc1 = user_stepping_back['SBC1']['start']
if start_time_sbc1 == "":
    start_time_sbc1 = "07:15"
end_time_sbc1 = user_stepping_back['SBC1']['end']
if end_time_sbc1 == "":
    end_time_sbc1 = "21:45"
start_time_sbc2 = user_stepping_back['SBC2']['start']
if start_time_sbc2 == "":
    start_time_sbc2 = "07:15"
end_time_sbc2 = user_stepping_back['SBC2']['end']
if end_time_sbc2 == "":
    end_time_sbc2 = "21:45"

print("SBC1 Start Time:", start_time_sbc1)
print("SBC1 End Time:", end_time_sbc1)
print("SBC2 Start Time:", start_time_sbc2)
print("SBC2 End Time:", end_time_sbc2)

new_location = f"ALL_USER_TT/LINE1_{member_id}"

fileLocation = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/"
df = pd.read_csv(f"{fileLocation}InitialServices.csv")

csv_file = f"{fileLocation}Jurisdiction.csv"
# Reading back the lists from the CSV file
with open(csv_file, mode='r') as file:
    reader = csv.reader(file)
    retrieved_lists = [row for row in reader]

# Extracting the lists
cc1 = [str(line) for line in retrieved_lists[0]]
cc2 = [str(line) for line in retrieved_lists[0]]
# Crew Controls

CrewControl = [str(line) for line in retrieved_lists[1]]

#svvrRake = [int(num) for num in retrieved_lists[3]]

added_services = [] #index of services added will get into this
#CrewControl = ["KKDA DN", "KKDA UP", "PVGW UP", "PVGW DN"]
#cc1 = ['MKPR','MKPR UP', 'MKPR DN','SAKP','DDSC','DDSC DN','DDSC SDG', 'PVGW','PBGW','PBGW UP','PBGW DN','PVGW UP','PVGW DN','MKPD', 'MKPD ', 'SAKP 3RD']
#cc2 = ['SVVR','SVVR DN ','MUPR','MUPR DN','MUPR 4TH','MUPR 3RD SDG','KKDA DN', 'KKDA UP','IPE','IPE 3RD','VND','MVPO','MVPO DN','NZM','NIZM', 'KKDA', 'MUPR DN SDG']

def hhmm2mins(hhmm):
    hrs = hhmm[:2]
    min = hhmm[-2:]
    mins = int(hrs)*60 + int(min)
    return mins

def timeDiff(x, y):
  return hhmm2mins(y) - hhmm2mins(x)

rakeNum = []
startStn = []
startTime = []
endStn = []
endTime = []
direction = []
#uniqueID = []
serviceTime = []
stepBackRake = []
stepBackLocation = []
mergedRakeNum1 = []
mergedRakeNum2 = []



#Merging services which have stepback at RI, train id 398 and 399 are not considered for stepback due to OCC instructions
for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services and hhmm2mins(start_time_sbc1) <= hhmm2mins(df.iloc[i,5]) <= hhmm2mins(end_time_sbc1):# and int(df.iloc[i,1]) != 398 and int(df.iloc[i,1]) != 399 and 435 <= hhmm2mins(df.iloc[i,5]) <= 1309:# STEP BACK FOR TIME 07 AM TO 09:49 PM
    if df.iloc[i,4] == "RI" and df.iloc[i,6] =='DN' :
      flag = False
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "RI" and df.iloc[j,6] == 'UP' and df.iloc[j,1] != df.iloc[i,1] and 30 >= timeDiff(df.iloc[i,5], df.iloc[j,3]) > 4 and df.iloc[j,0] not in added_services: # and int(df.iloc[j,1]) != 398 and int(df.iloc[j,1]) != 399 and 
          added_services.append(df.iloc[i,0])
          added_services.append(df.iloc[j,0])
          rakeNum.append(df.iloc[i,1])
          startStn.append(df.iloc[i,2])
          startTime.append(df.iloc[i,3])
          endStn.append(df.iloc[j,4])
          endTime.append(df.iloc[j,5])
          direction.append(df.iloc[i,6])
          serviceTime.append(timeDiff(df.iloc[i,3], df.iloc[j,5]))
          stepBackRake.append(df.iloc[j,1])
          stepBackLocation.append(df.iloc[j,2])
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])
          flag = True
          break
      if not flag: print("No stepback train found at RI", df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])





#StepBack for DSG is added such that XYZ-DSG-NBAA:

  if df.iloc[i,0] not in added_services:# and int(df.iloc[i,1]) != 398 and int(df.iloc[i,1]) != 399 and 450 <= hhmm2mins(df.iloc[i,5]) <= 1309:
    if df.iloc[i,4] == "DSG" and df.iloc[i,6] == 'UP':
      flag = False
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "DSG" and df.iloc[j,6] == 'UP'and df.iloc[j,1] == df.iloc[i,1] and hhmm2mins(df.iloc[i,5]) == hhmm2mins(df.iloc[j,3]) and df.iloc[j,0] not in added_services: #and int(df.iloc[j,1]) != 398 and int(df.iloc[j,1]) != 399
          added_services.append(df.iloc[i,0])
          added_services.append(df.iloc[j,0])
          rakeNum.append(df.iloc[i,1])
          startStn.append(df.iloc[i,2])
          startTime.append(df.iloc[i,3])
          endStn.append(df.iloc[j,4])
          endTime.append(df.iloc[j,5])
          direction.append(df.iloc[i,6])
          serviceTime.append(timeDiff(df.iloc[i,3], df.iloc[j,5]))
          stepBackRake.append("No StepBack")
          stepBackLocation.append("No StepBack")
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])
          flag = True
          break

      if not flag: print("No same train found at DSG UP DIRECTION", df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])





# for DSG is added such that NBAA-DSG-XYZ:

  if df.iloc[i,0] not in added_services:# and int(df.iloc[i,1]) != 398 and int(df.iloc[i,1]) != 399 and 450 <= hhmm2mins(df.iloc[i,5]) <= 1309:
    if df.iloc[i,4] == "DSG" and df.iloc[i,6] == 'DN':
      flag = False
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "DSG" and df.iloc[j,6] == 'DN'and df.iloc[j,1] == df.iloc[i,1] and hhmm2mins(df.iloc[i,5]) == hhmm2mins(df.iloc[j,3]) and df.iloc[j,0] not in added_services: #and int(df.iloc[j,1]) != 398 and int(df.iloc[j,1]) != 399
          added_services.append(df.iloc[i,0])
          added_services.append(df.iloc[j,0])
          rakeNum.append(df.iloc[i,1])
          startStn.append(df.iloc[i,2])
          startTime.append(df.iloc[i,3])
          endStn.append(df.iloc[j,4])
          endTime.append(df.iloc[j,5])
          direction.append(df.iloc[i,6])
          serviceTime.append(timeDiff(df.iloc[i,3], df.iloc[j,5]))
          stepBackRake.append("No StepBack")
          stepBackLocation.append("No StepBack")
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])
          flag = True
          break

      if not flag: print("No same train found at DSG DN DIRECTION", df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])




#StepBack for DSG ending trains is added:
for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services and hhmm2mins(start_time_sbc2) <= hhmm2mins(df.iloc[i,5]) < hhmm2mins(end_time_sbc2):
    if df.iloc[i,4] == "DSG" and df.iloc[i,6] == 'UP':
      flag = False
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "DSG" and df.iloc[j,6] == 'DN' and df.iloc[j,1] != df.iloc[i,1] and 30 >= timeDiff(df.iloc[i,5], df.iloc[j,3]) >= 0 and df.iloc[j,0] not in added_services:
          # LN_to_ILOK_rakeJ, ILOK_to_LN_rakeI = False, False
          # for k in range(i-100,j):
          #     if df.iloc[k,1] == df.iloc[j,1] and df.iloc[k,4] == "ILOK" and df.iloc[k,6] == 'DN' and 0 <= timeDiff(df.iloc[k,5], df.iloc[j,3]) <= 15:
          #         LN_to_ILOK_rakeJ = True
          #     if df.iloc[k,1] == df.iloc[i,1] and df.iloc[k,2] == "ILOK" and df.iloc[k,6] == 'UP' and 0 <= timeDiff(df.iloc[i,5], df.iloc[k,3]) <= 15:
          #         ILOK_to_LN_rakeI = True
          # if not(LN_to_ILOK_rakeJ and ILOK_to_LN_rakeI):
          #     continue

          added_services.append(df.iloc[i,0])
          added_services.append(df.iloc[j,0])
          rakeNum.append(df.iloc[i,1])
          startStn.append(df.iloc[i,2])
          startTime.append(df.iloc[i,3])
          endStn.append(df.iloc[j,4])
          endTime.append(df.iloc[j,5])
          direction.append(df.iloc[i,6])
          #uniqueID.append(df.iloc[i,7] + "-" + df.iloc[j,7])
          serviceTime.append(timeDiff(df.iloc[i,3], df.iloc[j,5]))
          stepBackRake.append(df.iloc[j,1])
          stepBackLocation.append(df.iloc[j,2])
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])
          #print(df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5] , "with", df.iloc[j,1], df.iloc[j,2], df.iloc[j,3], df.iloc[j,4], df.iloc[j,5])
          flag = True
          break

      if not flag: print("No Stepback train found at DSG", df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])



#  for SLAP is added such that SHD DN-SLAP-SPKD:

  # if df.iloc[i,0] not in added_services:# and int(df.iloc[i,1]) != 398 and int(df.iloc[i,1]) != 399 and 450 <= hhmm2mins(df.iloc[i,5]) <= 1309:
  #   if df.iloc[i,4] == "SLAP" and df.iloc[i,6] == 'DN':
  #     flag = False
  #     for j in range(i, df.shape[0]):
  #       if df.iloc[j,2] == "SLAP" and df.iloc[j,6] == 'UP' and df.iloc[j,1] == df.iloc[i,1] and df.iloc[j,0] not in added_services: #and int(df.iloc[j,1]) != 398 and int(df.iloc[j,1]) != 399
  #         added_services.append(df.iloc[i,0])
  #         added_services.append(df.iloc[j,0])
  #         rakeNum.append(df.iloc[i,1])
  #         startStn.append(df.iloc[i,2])
  #         startTime.append(df.iloc[i,3])
  #         endStn.append(df.iloc[j,4])
  #         endTime.append(df.iloc[j,5])
  #         direction.append(df.iloc[i,6])
  #         serviceTime.append(timeDiff(df.iloc[i,3], df.iloc[j,5]))
  #         stepBackRake.append("No StepBack")
  #         stepBackLocation.append("No StepBack")
  #         mergedRakeNum1.append(df.iloc[i,0])
  #         mergedRakeNum2.append(df.iloc[j,0])
  #         flag = True
  #         break
  #     if not flag: print("No same reversal train found at SLAP DN DIRECTION TO DEPOT", df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])




#Self reversal for NBAA ending trains is added:
for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services: # and 425 <= hhmm2mins(df.iloc[i,5]):
    if df.iloc[i,4] == "NBAA" and df.iloc[i,6] == 'UP':
      flag = False
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "NBAA" and df.iloc[j,6] == 'DN' and df.iloc[j,1] == df.iloc[i,1] and 30 >= timeDiff(df.iloc[i,5], df.iloc[j,3]) >= 0 and df.iloc[j,0] not in added_services:
          added_services.append(df.iloc[i,0])
          added_services.append(df.iloc[j,0])
          rakeNum.append(df.iloc[i,1])
          startStn.append(df.iloc[i,2])
          startTime.append(df.iloc[i,3])
          endStn.append(df.iloc[j,4])
          endTime.append(df.iloc[j,5])
          direction.append(df.iloc[i,6])
          serviceTime.append(timeDiff(df.iloc[i,3], df.iloc[j,5]))
          stepBackRake.append("No StepBack")
          stepBackLocation.append("No StepBack")
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])
          flag = True
          break

      if not flag: print("No same reversal train found at NBAA", df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])





#Services which are NOT ADDED YET:

for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services:
    added_services.append(df.iloc[i,0])
    rakeNum.append(df.iloc[i,1])
    startStn.append(df.iloc[i,2])
    startTime.append(df.iloc[i,3])
    endStn.append(df.iloc[i,4])
    endTime.append(df.iloc[i,5])
    direction.append(df.iloc[i,6])
    serviceTime.append(df.iloc[i,7])
    stepBackRake.append("No StepBack")
    stepBackLocation.append("No StepBack")
    mergedRakeNum1.append(df.iloc[i,0])
    mergedRakeNum2.append("None")



len(added_services)

len(rakeNum)

services = pd.DataFrame(list(zip(rakeNum,startStn,startTime,endStn,endTime,direction,serviceTime, stepBackRake, stepBackLocation, mergedRakeNum1, mergedRakeNum2)),
               columns =['Rake Num','Start Station','Start Time','End Station','End Time','Direction','service time', "Step Back Rake", "Step Back Location", "mergedRakeNum1", "mergedRakeNum2"])

services = services.sort_values(by=['Start Time'])
services

services.iloc[0,0]

same_juris = []


for i in range(services.shape[0]):
  if (services.iloc[i,1] in cc1 and services.iloc[i,3] in cc1) or (services.iloc[i,1] in cc2 and services.iloc[i,3] in cc2):
    #print( services.iloc[i,0],services.iloc[i,1], services.iloc[i,2], services.iloc[i,3], services.iloc[i,4], services.iloc[i,5])
    same_juris.append("yes")
  else: same_juris.append("no")

print(len(same_juris))

services['Same Jurisdiction'] = same_juris
services = services[['Rake Num','Start Station','Start Time','End Station','End Time','Direction','service time', "Same Jurisdiction" ,"Step Back Rake", "Step Back Location", "mergedRakeNum1", "mergedRakeNum2"]]
print(len(services))


services.to_csv(f"{fileLocation}Mainloops.csv")
