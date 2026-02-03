import os
import pandas as pd
import sys
import csv
from datetime import datetime, timedelta, time
import argparse

def convert_excel_time(val):
    # Case 1: Excel numeric time (fraction of a day)
    if isinstance(val, (int, float)) and 0 <= val :
        return (datetime(1899, 12, 30) + timedelta(days=val)).time()
    
    # Case 2: pandas Timestamp or datetime.datetime
    if isinstance(val, (pd.Timestamp, datetime)):
        return val.time()
    
    # Case 3: already a datetime.time
    if isinstance(val, time):
        return val
    
    # Case 4: string values like "08:30:00" or "31-12-1900 04:01:53"
    if isinstance(val, str): 
      for fmt in ("%H:%M:%S", "%d-%m-%Y %H:%M:%S"): 
        try: 
          return datetime.strptime(val, fmt).time() 
        except ValueError: 
          continue 
      return val # leave unchanged if parsing fails
    
    # Default: return as-is
    return val

# --------------------------------------------- PARSE Command Line Input -----------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
parser.add_argument("excel_fileName", type=str, help="Provide the location of the input file.")
args = parser.parse_args()
excel_fileName = args.excel_fileName
member_id = args.member_id

new_location = f"ALL_USER_TT/LINE7N_{member_id}"
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
inputFile = excel_fileName
folder_name = f"{member_id}"
outputFileLocation = os.path.join(current_dir, f"{new_location}/USEFUL OUTPUT_{folder_name}/")
os.makedirs(outputFileLocation, exist_ok= True)


df = pd.read_excel(f"{inputFile}",sheet_name="Sheet1",header = None)
df = df.map(lambda x: x.strip() if isinstance(x, str) else x)


df[df.columns[1:]] = df[df.columns[1:]].astype("object")
# your Excel ranges (convert to 0-based indices)
ranges = [
    (1, 2),      # Excel B2:XFD2
    (6, 44),     # Excel B7:XFD50
    (46, 84),    # Excel B52:XFD52
    (86, 87),    # Excel B57:XFD100
]
# Step 1: cast all relevant rows/cols to object dtype first
for start, end in ranges:
    df.iloc[start:end, 1:] = df.iloc[start:end, 1:].astype("object")
# Step 2: now safely apply your time conversion function
for start, end in ranges:
    df.iloc[start:end, 1:] = df.iloc[start:end, 1:].map(convert_excel_time)




rakes = []
for i in range(1,df.shape[1]):
  rakes.append(df.iloc[0,i])

rakes = set(rakes)

# Convert the set back to a list
rakes = list(rakes)

# Print the unique elements
#print(rakes)

def hhmm2mins(hhmm):
    hrs = hhmm[:2]
    min = hhmm[-2:]
    mins = int(hrs)*60 + int(min)
    return mins

def timeDiff(x, y):
  return hhmm2mins(y) - hhmm2mins(x)

RakeNum = []
startStn = []
startTime = []
endStn = []
endTime = []
direction = []
serviceTime = []
category = []
inductingRakes = []
stablingRakes = []
# uniqueID = []
reqIndexofStn = [6,11,32,34,40,43]
reqIndexofStn1 = [46,49,55,57,78,83]


for i in range(1,df.shape[1]):
  if not pd.isna(df.iloc[1,i]) and type(df.iloc[1,i]) != str :
    inductingRakes.append(df.iloc[3,i])  # 1,i for line 3,4 TT
    RakeNum.append(df.iloc[3,i])     # rakenum 1,i for line 3,4 TT
    startStn.append(df.iloc[0,i])
    startTime.append(df.iloc[1,i].strftime('%H:%M'))
    for j in reqIndexofStn:
      flag = False
      if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str:
        endStn.append(df.iloc[j,0])
        endTime.append(df.iloc[j,i].strftime('%H:%M'))
        if j <= 49:
          direction.append("DN")
          # uniqueID.append(df.iloc[92,i]+"D")
        else:
          direction.append("UP")
          # uniqueID.append(df.iloc[92,i]+"U")
        flag = True
        req = j
        break
    for j in reqIndexofStn1:
      if not flag:
        if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str:
          endStn.append(df.iloc[j,0])
          endTime.append(df.iloc[j,i].strftime('%H:%M'))
          if j <= 43:
            direction.append("DN")
            # uniqueID.append(df.iloc[92,i]+"D")
          else: 
            direction.append("UP")
            # uniqueID.append(df.iloc[92,i]+"U")
          req = j
          break

    if flag: list1 = reqIndexofStn
    elif not flag: list1 = reqIndexofStn1
    else: print("error1",df.iloc[0,i])

    for j in list1:
      if j >= req:
        if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
          if j != list1[-1]:
            RakeNum.append(df.iloc[3,i])
            startStn.append(df.iloc[j,0])
            startTime.append(df.iloc[j,i].strftime('%H:%M'))
            k = list1.index(j)
            for p in range(k, len(list1)-1):
              flag3 = False
              if not pd.isna(df.iloc[list1[p+1],i]) and type(df.iloc[list1[p+1],i]) != str:
                endStn.append(df.iloc[list1[p+1],0])
                try:
                  endTime.append(df.iloc[list1[p+1],i].strftime('%H:%M'))
                except Exception as e:
                  print("Exception:", e)
                  print(f"error at row = {list1[p+1]} and column = {i} value = ", df.iloc[list1[p+1],i])
                  sys.exit(1)
                if j <= 43:
                  direction.append("DN")
                  # uniqueID.append(df.iloc[92,i]+"D")
                else: 
                  direction.append("UP")
                  # uniqueID.append(df.iloc[92,i]+"U")
                flag3 = True
                break
              else:
                for q in range(list1[p+1],list1[p],-1):
                  if not pd.isna(df.iloc[q,i]) and type(df.iloc[q,i]) != str:
                    endStn.append(df.iloc[q,0])
                    endTime.append(df.iloc[q,i].strftime('%H:%M'))
                    if q <= 43: 
                      direction.append("DN")
                      # uniqueID.append(df.iloc[92,i]+"D")
                    else: 
                      direction.append("UP")
                      # uniqueID.append(df.iloc[92,i]+"U")
                    flag3 = True
                    break
                if flag3: break
      
            if not flag3:
              endStn.append(df.iloc[j,0])
              endTime.append(df.iloc[j,i].strftime('%H:%M'))
              if j <= 43: 
                direction.append("DN")
                # uniqueID.append(df.iloc[92,i]+"D")
              else: 
                direction.append("UP")
              # print("error3", df.iloc[0,i])

    if flag:
      for j in range(46,df.shape[0]):
        flagX = False
        if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
          RakeNum.append(df.iloc[3,i])
          startStn.append(df.iloc[j,0])
          startTime.append(df.iloc[j,i].strftime('%H:%M'))
          for k in reqIndexofStn1:
            if not pd.isna(df.iloc[k,i]) and type(df.iloc[k,i]) != str and type(df.iloc[k,i]) != int:
              endStn.append(df.iloc[k,0])
              endTime.append(df.iloc[k,i].strftime('%H:%M'))
              req = k
              flagX = True
              if j <= 43: 
                direction.append("DN")
                # uniqueID.append(df.iloc[92,i]+"D")
              else: 
                direction.append("UP")
                # uniqueID.append(df.iloc[92,i]+"U")
              break
          if flagX: break
          else: print("error-X",df.iloc[0,i],df.iloc[6,i])
      for j in reqIndexofStn1:
        if j >= req:
          if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
            if j != reqIndexofStn1[-1]:
              RakeNum.append(df.iloc[3,i])
              startStn.append(df.iloc[j,0])
              startTime.append(df.iloc[j,i].strftime('%H:%M'))
              k = reqIndexofStn1.index(j)
              for p in range(k, len(reqIndexofStn1)-1):
                flagXX = False
                if not pd.isna(df.iloc[reqIndexofStn1[p+1],i]) and type(df.iloc[reqIndexofStn1[p+1],i]) != str:
                  endStn.append(df.iloc[reqIndexofStn1[p+1],0])
                  endTime.append(df.iloc[reqIndexofStn1[p+1],i].strftime('%H:%M'))
                  if j <= 43:
                    direction.append("DN")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  else: 
                    direction.append("UP")
                    # uniqueID.append(df.iloc[92,i]+"U")
                  flagXX = True
                  break
                else:
                  for q in range(reqIndexofStn1[p+1],reqIndexofStn1[p],-1):
                    if not pd.isna(df.iloc[q,i]) and type(df.iloc[q,i]) != str:
                      endStn.append(df.iloc[q,0])
                      endTime.append(df.iloc[q,i].strftime('%H:%M'))
                      if q <= 43: 
                        direction.append("DN")
                        # uniqueID.append(df.iloc[92,i]+"D")
                      else: 
                        direction.append("UP")
                        # uniqueID.append(df.iloc[92,i]+"U")
                      flagXX = True
                      break
                  if flagXX: break
        
              if not flagXX:
                endStn.append(df.iloc[j,0])
                endTime.append(df.iloc[j,i].strftime('%H:%M'))
                if j <= 43: 
                  direction.append("DN")
                  # uniqueID.append(df.iloc[92,i]+"D")
                else: 
                  direction.append("UP")
                # print("error3", df.iloc[0,i])
  else:
    for j in range(6,df.shape[0]):
      flag2 = False
      if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
        RakeNum.append(df.iloc[3,i])
        startStn.append(df.iloc[j,0])
        startTime.append(df.iloc[j,i].strftime('%H:%M'))
        if j < 43:
          dnservice = True
          list1 = reqIndexofStn
        else:
          dnservice = False
          list1 = reqIndexofStn1
        for k in list1:
          if k > j:
            if not pd.isna(df.iloc[k,i]) and type(df.iloc[k,i]) != str and type(df.iloc[k,i]) != int:
              endStn.append(df.iloc[k,0])
              endTime.append(df.iloc[k,i].strftime('%H:%M'))
              req = k
              flag2 = True
              if j <= 43:
                direction.append("DN")
                # uniqueID.append(df.iloc[92,i]+"D")
              else: 
                direction.append("UP")
                # uniqueID.append(df.iloc[92,i]+"U")
              break
        if flag2: break
        else: 
          endStn.append(df.iloc[j,0])
          endTime.append(df.iloc[j,i].strftime('%H:%M'))
          direction.append("DN" if j <= 43 else "UP")
          print("default value added in end station at ",df.iloc[0,i],df.iloc[6,i])
          req = k
          break
    for j in list1:
      if j >= req:
        if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
          if j != list1[-1]:
            RakeNum.append(df.iloc[3,i])
            startStn.append(df.iloc[j,0])
            startTime.append(df.iloc[j,i].strftime('%H:%M'))
            k = list1.index(j)
            if not pd.isna(df.iloc[list1[k+1],i]) and type(df.iloc[list1[k+1],i]) != str:
              endStn.append(df.iloc[list1[k+1],0])
              endTime.append(df.iloc[list1[k+1],i].strftime('%H:%M'))
              if j <= 43:
                direction.append("DN")
                # uniqueID.append(df.iloc[92,i]+"D")
              else: 
                direction.append("UP")
                # uniqueID.append(df.iloc[92,i]+"U")
            else:
              for j in range(list1[k+1],list1[k]-1,-1):
                flag3 = False
                if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str:
                  endStn.append(df.iloc[j,0])
                  endTime.append(df.iloc[j,i].strftime('%H:%M'))
                  if j <= 43: 
                    direction.append("DN")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  else: 
                    direction.append("UP")
                    # uniqueID.append(df.iloc[92,i]+"U")
                  flag3 = True
                  break
              if not flag3: print("error3", df.iloc[0,i])

    if dnservice:
      for j in reqIndexofStn1:
        if j != reqIndexofStn1[-1]:
          if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
            RakeNum.append(df.iloc[3,i])
            startStn.append(df.iloc[j,0])
            startTime.append(df.iloc[j,i].strftime('%H:%M'))
            k = reqIndexofStn1.index(j)
            if  not pd.isna(df.iloc[reqIndexofStn1[k+1],i]) and type(df.iloc[reqIndexofStn1[k+1],i]) != str:
              endStn.append(df.iloc[reqIndexofStn1[k+1],0])
              endTime.append(df.iloc[reqIndexofStn1[k+1],i].strftime('%H:%M'))
              if j <= 43: 
                direction.append("DN")
                # uniqueID.append(df.iloc[92,i]+"D")
              else: 
                direction.append("UP")
                # uniqueID.append(df.iloc[92,i]+"D")
            else:
              entryFlag = False
              if k != len(reqIndexofStn1):
                for x in range(k+1,len(reqIndexofStn1)):
                  if pd.isna(df.iloc[reqIndexofStn1[x],i]):
                    continue
                  else:
                    endStn.append(df.iloc[reqIndexofStn1[x],0])
                    endTime.append(df.iloc[reqIndexofStn1[x],i].strftime('%H:%M'))
                    if j <= 43:
                      direction.append("DN")
                    else:
                      direction.append("UP")
                    entryFlag = True
                    break
                if entryFlag:
                  continue
              for j in range(reqIndexofStn1[k+1],reqIndexofStn1[k]-1,-1):
                flag3 = False
                if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str:
                  endStn.append(df.iloc[j,0])
                  endTime.append(df.iloc[j,i].strftime('%H:%M'))
                  if j <= 43:
                    direction.append("DN")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  else: 
                    direction.append("UP")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  flag3 = True
                  break
            

  if not pd.isna(df.iloc[86,i]) and type(df.iloc[86,i]) != str:# and 'SVVR' not in df.iloc[85,i]:
    RakeNum.append(df.iloc[3,i])
    startStn.append(endStn[-1])
    startTime.append(endTime[-1])
    endStn.append(df.iloc[85,i])
    endTime.append(df.iloc[86,i].strftime('%H:%M'))
    direction.append('UP')
  




print(len(RakeNum),len(startStn),len(startTime),len(endStn),len(endTime)) #, len(uniqueID))

services = pd.DataFrame(list(zip(RakeNum,startStn,startTime,endStn,endTime,direction)),#uniqueID)),
               columns =['Rake Num','Start Station','Start Time','End Station','End Time','Direction'])#,'Uniques ID'])

#services = services.sort_values(by=['Start Time'])
services

rowsRemoved = []
for i in range(services.shape[0]):
  if services.iloc[i,1] == services.iloc[i,3] and services.iloc[i,2] == services.iloc[i,4]:
    rowsRemoved.append(i)

services = services.drop(rowsRemoved)

services

services = services[services.iloc[:, 1] != "MKPD"]
services = services[services.iloc[:, 1] != "VND"]
services = services[services.iloc[:, 3] != "MKPD"]
services = services[services.iloc[:, 3] != "VND"]


# services.iloc[10,1]

serviceTime = []
for i in range(services.shape[0]):
  if services.iloc[i,1] == "PVGW" or services.iloc[i,1] == "KKDA":
    services.iloc[i,1] = services.iloc[i,1] + " " +services.iloc[i,5]
  if services.iloc[i,3] == "PVGW" or services.iloc[i,3] == "KKDA":
    services.iloc[i,3] = services.iloc[i,3] + " " +services.iloc[i,5]
  if services.iloc[i,2][:2] == '00':
    services.iloc[i,2] = '24' + services.iloc[i,2][2:]
  elif services.iloc[i,2][:2] == '01':
    services.iloc[i,2] = '25' + services.iloc[i,2][2:]

  if services.iloc[i,4][:2] == '00':
    services.iloc[i,4] = '24' + services.iloc[i,4][2:]
  elif services.iloc[i,4][:2] == '01':
    services.iloc[i,4] = '25' + services.iloc[i,4][2:]

for i in range(services.shape[0]):
  serviceTime.append(timeDiff(services.iloc[i,2],services.iloc[i,4]))

services["Service Time"] = serviceTime
services["Rake Num"] = services['Rake Num'].astype(int)
services = services.sort_values(by='Start Time')


services.to_csv(f"{outputFileLocation}InitialServices.csv")

