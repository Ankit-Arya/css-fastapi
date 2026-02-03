import pandas as pd
import csv
import os
import sys
import json
# --------------------------------------------- PARSE Command Line Input -----------------------------------------------

member_id = sys.argv[1]
json_str = sys.argv[2]
data = json.loads(json_str)
svvrRakes = data["svvrRakes"]

new_location = f"ALL_USER_TT/LINE7_{member_id}"

fileLocation = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/"
df = pd.read_csv(f"{fileLocation}InitialServices.csv")

csv_file = f"{fileLocation}Jurisdiction.csv"
# Reading back the lists from the CSV file
with open(csv_file, mode='r') as file:
    reader = csv.reader(file)
    retrieved_lists = [row for row in reader]

# Extracting the lists
cc1 = [str(line) for line in retrieved_lists[0]]
cc2 = [str(line) for line in retrieved_lists[1]]
# Crew Controls

CrewControl = [str(line) for line in retrieved_lists[2]]

svvrRake = [int(num) for num in svvrRakes]

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
#Firstly adding services which operate between crew controls and doesnt require stepback (e.g.. KKDA TO PVGW)

# for i in range(df.shape[0]):
#   if df.iloc[i,0] not in added_services and df.iloc[i,1] in svvrRake and hhmm2mins(df.iloc[i,3]) > 840:
#     if df.iloc[i,4] != "MUPR" and df.iloc[i,2] != "MUPR":
#       #print(df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])
#       added_services.append(df.iloc[i,0])
#       rakeNum.append(df.iloc[i,1])
#       startStn.append(df.iloc[i,2])
#       startTime.append(df.iloc[i,3])
#       endStn.append(df.iloc[i,4])
#       endTime.append(df.iloc[i,5])
#       direction.append(df.iloc[i,6])
#       #uniqueID.append(df.iloc[i,7])
#       serviceTime.append(df.iloc[i,7])
#       stepBackRake.append("No StepBack")
#       stepBackLocation.append("No StepBack")
#       mergedRakeNum1.append(df.iloc[i,0])
#       mergedRakeNum2.append("None")


for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:
    if df.iloc[i,4] == "IPE" and df.iloc[i,6] == "UP":
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "IPE" and df.iloc[j,6] == "UP" and df.iloc[j,1] not in svvrRake and df.iloc[j,0] not in added_services and df.iloc[i,1] == df.iloc[j,1] and 0 <= timeDiff(df.iloc[i,5], df.iloc[j,3]) <= 14:
          #print(df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5] , "with", df.iloc[j,1], df.iloc[j,2], df.iloc[j,3], df.iloc[j,4], df.iloc[j,5])
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
          stepBackRake.append("No StepBack")
          stepBackLocation.append("No StepBack")
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])


for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:
    if df.iloc[i,4] == "IPE" and df.iloc[i,6] == "DN":
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "IPE" and df.iloc[j,6] == "DN" and df.iloc[j,1] not in svvrRake and df.iloc[j,0] not in added_services and df.iloc[i,1] == df.iloc[j,1] and 0 <= timeDiff(df.iloc[i,5], df.iloc[j,3]) <= 14:
          #print(df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5] , "with", df.iloc[j,1], df.iloc[j,2], df.iloc[j,3], df.iloc[j,4], df.iloc[j,5])
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
          stepBackRake.append("No StepBack")
          stepBackLocation.append("No StepBack")
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])

"""
for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:
    if df.iloc[i,2] in CrewControl:
      if df.iloc[i,4] in CrewControl:
        added_services.append(df.iloc[i,0])
        rakeNum.append(df.iloc[i,1])
        startStn.append(df.iloc[i,2])
        startTime.append(df.iloc[i,3])
        endStn.append(df.iloc[i,4])
        endTime.append(df.iloc[i,5])
        direction.append(df.iloc[i,6])
        #uniqueID.append(df.iloc[i,7])
        serviceTime.append(df.iloc[i,7])
        stepBackRake.append("No StepBack")
        stepBackLocation.append("No StepBack")
        mergedRakeNum1.append(df.iloc[i,0])
        mergedRakeNum2.append("None")
"""
"""
#Merging services which end and start in MKPR
for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake: # and 414 <= hhmm2mins(df.iloc[i,5]) <= 1250:
    if df.iloc[i,2] == "PVGW UP" and df.iloc[i,4] == "MKPR" :
      flag = False
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "MKPR" and df.iloc[j,4] == "PVGW DN"and df.iloc[j,1] != df.iloc[i,1] and timeDiff(df.iloc[i,5], df.iloc[j,3]) > 0 and df.iloc[j,0] not in added_services and df.iloc[j,1] not in svvrRake:
          PVGW_to_MKPRJ, MKPR_to_PVGWI = False,False
          for k in range(i,j):
            if df.iloc[k,1] == df.iloc[j,1] and df.iloc[k,2] == "PVGW UP" and df.iloc[k,4] == "MKPR":
              PVGW_to_MKPRJ = True
            if df.iloc[k,1] == df.iloc[i,1] and df.iloc[k,2] == "MKPR" and df.iloc[k,4] == "PVGW DN":
              MKPR_to_PVGWI = True
          if not (PVGW_to_MKPRJ and MKPR_to_PVGWI):
            continue
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
          stepBackLocation.append(df.iloc[i,4])
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])
          #print(df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5] , "with", df.iloc[j,1], df.iloc[j,2], df.iloc[j,3], df.iloc[j,4], df.iloc[j,5])
          flag = True
          break

      if not flag: print("No StepBack Found at MKPR", df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])

"""
for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:
    if df.iloc[i,4] == "MKPR" and df.iloc[i,6] == "UP":
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "MKPR" and df.iloc[j,6] == "UP" and df.iloc[j,1] not in svvrRake and df.iloc[i,1] == df.iloc[j,1] and 0 <= timeDiff(df.iloc[i,5], df.iloc[j,3]) <= 14 and df.iloc[j,0] not in added_services:
          #print(df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5] , "with", df.iloc[j,1], df.iloc[j,2], df.iloc[j,3], df.iloc[j,4], df.iloc[j,5])
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
          stepBackRake.append("No StepBack")
          stepBackLocation.append("No StepBack")
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])


for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:
    if df.iloc[i,4] == "MKPR" and df.iloc[i,6] == "DN":
      for j in range(i, df.shape[0]):
        if df.iloc[j,2] == "MKPR" and df.iloc[j,6] == "DN" and df.iloc[j,1] not in svvrRake and df.iloc[i,1] == df.iloc[j,1] and 0 <= timeDiff(df.iloc[i,5], df.iloc[j,3]) <= 14 and df.iloc[j,0] not in added_services:
          #print(df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5] , "with", df.iloc[j,1], df.iloc[j,2], df.iloc[j,3], df.iloc[j,4], df.iloc[j,5])
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
          stepBackRake.append("No StepBack")
          stepBackLocation.append("No StepBack")
          mergedRakeNum1.append(df.iloc[i,0])
          mergedRakeNum2.append(df.iloc[j,0])


# # merging service from MUPR to SSVR and SVVR to MUPR
# for i in range(df.shape[0]):
#   if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:
#     if df.iloc[i,4] == "SVVR" :
#       flag = False
#       for j in range(i, df.shape[0]):
#         if df.iloc[j,2] == "SVVR" and  0 <= timeDiff(df.iloc[i,5], df.iloc[j,3]) <= 14 and df.iloc[j,0] not in added_services and df.iloc[j,1] not in svvrRake and df.iloc[i,1] == df.iloc[j,1]:
#           added_services.append(df.iloc[i,0])
#           added_services.append(df.iloc[j,0])
#           rakeNum.append(df.iloc[i,1])
#           startStn.append(df.iloc[i,2])
#           startTime.append(df.iloc[i,3])
#           endStn.append(df.iloc[j,4])
#           endTime.append(df.iloc[j,5])
#           direction.append(df.iloc[i,6])
#           #uniqueID.append(df.iloc[i,7] + "-" + df.iloc[j,7])
#           serviceTime.append(timeDiff(df.iloc[i,3], df.iloc[j,5]))
#           stepBackRake.append("No StepBack")
#           stepBackLocation.append("No StepBack")
#           mergedRakeNum1.append(df.iloc[i,0])
#           mergedRakeNum2.append(df.iloc[j,0])
#           #print(df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5] , "with", df.iloc[j,1], df.iloc[j,2], df.iloc[j,3], df.iloc[j,4], df.iloc[j,5])
#           flag = True
#           break

# #StepBack for MUPR is added

# for i in range(df.shape[0]):
#   if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:# and 420 <= hhmm2mins(df.iloc[i,5]) <= 1250:
#     if df.iloc[i,2] == 'KKDA DN' and df.iloc[i,4] == "MUPR":
#       flag = False
#       for j in range(i, df.shape[0]):
#         if df.iloc[j,2] == "MUPR" and df.iloc[j,4] == 'KKDA UP' and df.iloc[j,1] == df.iloc[i,1] and 0 <= timeDiff(df.iloc[i,5], df.iloc[j,3]) <= 15 and df.iloc[j,0] not in added_services and df.iloc[j,1] not in svvrRake:
#           # KKDA_to_MUPR_rakeJ, MUPR_to_KKDA_rakeI = False, False
#           # for k in range(i,j):
#           #     if df.iloc[k,1] == df.iloc[j,1] and df.iloc[k,2] == "KKDA DN" and df.iloc[k,4] == "MUPR":
#           #         KKDA_to_MUPR_rakeJ = True
#           #     if df.iloc[k,1] == df.iloc[i,1] and df.iloc[k,2] == "MUPR" and df.iloc[k,4] == "KKDA UP":
#           #         MUPR_to_KKDA_rakeI = True
#           # if not(KKDA_to_MUPR_rakeJ and MUPR_to_KKDA_rakeI):
#           #     continue
#           added_services.append(df.iloc[i,0])
#           added_services.append(df.iloc[j,0])
#           rakeNum.append(df.iloc[i,1])
#           startStn.append(df.iloc[i,2])
#           startTime.append(df.iloc[i,3])
#           endStn.append(df.iloc[j,4])
#           endTime.append(df.iloc[j,5])
#           direction.append(df.iloc[i,6])
#           #uniqueID.append(df.iloc[i,7] + "-" + df.iloc[j,7])
#           serviceTime.append(timeDiff(df.iloc[i,3], df.iloc[j,5]))
#           stepBackRake.append('No StepBack')
#           stepBackLocation.append('No StepBack')
#           mergedRakeNum1.append(df.iloc[i,0])
#           mergedRakeNum2.append(df.iloc[j,0])
#           #print(df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5] , "with", df.iloc[j,1], df.iloc[j,2], df.iloc[j,3], df.iloc[j,4], df.iloc[j,5])
#           flag = True
#           break

#       if not flag: print("No same train Found at MUPR", df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])

# #Not adding stepback for services which are ending in MKPR

# for i in range(df.shape[0]):
#   if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:
#     if df.iloc[i,4] == "MKPR":
#       added_services.append(df.iloc[i,0])
#       rakeNum.append(df.iloc[i,1])
#       startStn.append(df.iloc[i,2])
#       startTime.append(df.iloc[i,3])
#       endStn.append(df.iloc[i,4])
#       endTime.append(df.iloc[i,5])
#       direction.append(df.iloc[i,6])
#       #uniqueID.append(df.iloc[i,7])
#       serviceTime.append(df.iloc[i,7])
#       stepBackRake.append("No StepBack")
#       stepBackLocation.append("No StepBack")
#       mergedRakeNum1.append(df.iloc[i,0])
#       mergedRakeNum2.append("None")

# #Which are not starting or ending in MUPR

# for i in range(df.shape[0]):
#   if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:
#     if df.iloc[i,4] != "MUPR" and df.iloc[i,2] != "MUPR":
#       #print(df.iloc[i,0],df.iloc[i,1], df.iloc[i,2], df.iloc[i,3], df.iloc[i,4], df.iloc[i,5])
#       added_services.append(df.iloc[i,0])
#       rakeNum.append(df.iloc[i,1])
#       startStn.append(df.iloc[i,2])
#       startTime.append(df.iloc[i,3])
#       endStn.append(df.iloc[i,4])
#       endTime.append(df.iloc[i,5])
#       direction.append(df.iloc[i,6])
#       #uniqueID.append(df.iloc[i,7])
#       serviceTime.append(df.iloc[i,7])
#       stepBackRake.append("No StepBack")
#       stepBackLocation.append("No StepBack")
#       mergedRakeNum1.append(df.iloc[i,0])
#       mergedRakeNum2.append("None")

# len(added_services)

# len(rakeNum)

# #Services which are initiating and ending in MUPR (like sign ON and signOFF)

for i in range(df.shape[0]):
  if df.iloc[i,0] not in added_services and df.iloc[i,1] not in svvrRake:
    added_services.append(df.iloc[i,0])
    rakeNum.append(df.iloc[i,1])
    startStn.append(df.iloc[i,2])
    startTime.append(df.iloc[i,3])
    endStn.append(df.iloc[i,4])
    endTime.append(df.iloc[i,5])
    direction.append(df.iloc[i,6])
    #uniqueID.append(df.iloc[i,7])
    serviceTime.append(df.iloc[i,7])
    stepBackRake.append("No StepBack")
    stepBackLocation.append("No StepBack")
    mergedRakeNum1.append(df.iloc[i,0])
    mergedRakeNum2.append("None")

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
services

services.to_csv(f"{fileLocation}Mainloops.csv")