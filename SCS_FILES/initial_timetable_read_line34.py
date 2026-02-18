# -*- coding: utf-8 -*-

import os
import pandas as pd
import sys
import csv
from datetime import datetime, timedelta, time
import argparse

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

# --------------------------------------------- PARSE Command Line Input -----------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
parser.add_argument("excel_fileName", type=str, help="Provide the location of the input file.")
args = parser.parse_args()
excel_fileName = args.excel_fileName
member_id = args.member_id
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
inputFile = excel_fileName
folder_name = f"{member_id}"

new_location = f"ALL_USER_TT/LINE34_{member_id}"

outputFileLocation = os.path.join(current_dir, f"{new_location}/USEFUL OUTPUT_{folder_name}/")
os.makedirs(outputFileLocation, exist_ok= True)


df = pd.read_excel(f"{inputFile}",sheet_name="Sheet1",header = None)
df = df.map(lambda x: x.strip() if isinstance(x, str) else x)



df[df.columns[1:]] = df[df.columns[1:]].astype("object")
# your Excel ranges (convert to 0-based indices)
ranges = [
    (1, 2),      # Excel B2:XFD2
    (4, 54),     # Excel B5:XFD54
    (59, 109),    # Excel B60:XFD109
    (111, 112)     # Excel B112:XFD112
]
# Step 1: cast all relevant rows/cols to object dtype first
for start, end in ranges:
    df.iloc[start:end, 1:] = df.iloc[start:end, 1:].astype("object")
# Step 2: now safely apply your time conversion function
for start, end in ranges:
    df.iloc[start:end, 1:] = df.iloc[start:end, 1:].map(convert_excel_time)




rakes = []
for i in range(1,df.shape[1]):
  rakes.append(df.iloc[3,i]) # 1,i for line 34

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

def addedTime(x,y):
  totmin = hhmm2mins(x) + hhmm2mins(y)
  finhr = totmin // 60
  finmin = totmin % 60
  if finhr in range(10):
    finhr = '0' + str(finhr)
  else: pass
  if finmin in range(10):
    finmin = '0' + str(finmin)
  else: pass
  fintime = fintime = str(finhr) + ":" + str(finmin)
  return fintime

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
reqIndexofStn = [4,12,37,44,53]
reqIndexofStn1 = [59,68,75,100,108]



for i in range(1,df.shape[1]):
  state = df.iloc[54,i]  # this train belongs to vasi or necc
  if not pd.isna(df.iloc[1,i]) and type(df.iloc[1,i]) != str :  ## 4,i for line 3,4 TT
    inductingRakes.append(df.iloc[3,i])  # 1,i for line 3,4 TT
    RakeNum.append(df.iloc[3,i])     # rakenum 1,i for line 3,4 TT
    startStn.append(df.iloc[0,i])
    startTime.append(df.iloc[1,i].strftime('%H:%M'))
    for j in reqIndexofStn:
      flag = False
      if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
        
        checkstn = df.iloc[j,0]
        if checkstn.find('/') > 0:
          if state == 'VASI UP' or state == 'VASI DN':
              indx = checkstn.find('/')
              endStn.append(df.iloc[j,0][indx+1:])
          elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
              indx = checkstn.find('/')
              if df.iloc[j,0][:indx] == "NSET":
                continue
              else:
                endStn.append(df.iloc[j,0][:indx])
          else: 
            endStn.append(df.iloc[j,0])
            print("error of finding state = ", state, 'at', j,',', i)
        else: endStn.append(df.iloc[j,0])  #
        
        endTime.append(df.iloc[j,i].strftime('%H:%M'))
        if j <= 53:              # 53 for line 3,4 TT
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
        if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
          
          checkstn = df.iloc[j,0]
          if checkstn.find('/') > 0:
            if state == 'VASI UP' or state == 'VASI DN':
                indx = checkstn.find('/')
                endStn.append(df.iloc[j,0][indx+1:])
            elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                indx = checkstn.find('/')
                if df.iloc[j,0][:indx] == "NSET":
                  continue
                else:
                  endStn.append(df.iloc[j,0][:indx])
            else: 
              endStn.append(df.iloc[j,0])
              print("error of finding state = ", state, 'at', j,',', i)
          else: endStn.append(df.iloc[j,0])

          endTime.append(df.iloc[j,i].strftime('%H:%M'))
          if j <= 53:
            direction.append("DN")
            # uniqueID.append(df.iloc[92,i]+"D")
          else: 
            direction.append("UP")
            # uniqueID.append(df.iloc[92,i]+"U")
          req = j
          break

    if flag: list1 = reqIndexofStn
    elif not flag: list1 = reqIndexofStn1
    else: print("error1",df.iloc[1,i])

    for j in list1:
      if j >= req:
        if j != list1[-1]:
          if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
            

            checkstn = df.iloc[j,0]
            if checkstn.find('/') > 0:
              if state == 'VASI UP' or state == 'VASI DN':
                indx = checkstn.find('/')
                RakeNum.append(df.iloc[3,i])
                startStn.append(df.iloc[j,0][indx+1:])
              elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                indx = checkstn.find('/')
                if df.iloc[j,0][:indx] == "NSET":
                  continue
                else:
                  RakeNum.append(df.iloc[3,i])
                  startStn.append(df.iloc[j,0][:indx])
              else: 
                RakeNum.append(df.iloc[3,i])
                startStn.append(df.iloc[j,0])
                print("error of finding state = ", state, 'at', j,',', i)
            else: 
              RakeNum.append(df.iloc[3,i])
              startStn.append(df.iloc[j,0])
            
            startTime.append(df.iloc[j,i].strftime('%H:%M'))
            k = list1.index(j)

            checkstn = df.iloc[list1[k+1],0]
            nsetFlag = False
            if checkstn.find('/') > 0:
              if state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                    indx = checkstn.find('/')
                    if df.iloc[list1[k+1],0][:indx] == "NSET":
                      nsetFlag = True
            if  not pd.isna(df.iloc[list1[k+1],i]) and type(df.iloc[list1[k+1],i]) != str and nsetFlag == False:

              checkstn = df.iloc[list1[k+1],0]
              if checkstn.find('/') > 0:
                if state == 'VASI UP' or state == 'VASI DN':
                    indx = checkstn.find('/')
                    endStn.append(df.iloc[list1[k+1],0][indx+1:])
                elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                    indx = checkstn.find('/')
                    if df.iloc[list1[k+1],0][:indx] == "NSET":
                      continue
                    else:
                      endStn.append(df.iloc[list1[k+1],0][:indx])
                else: 
                  endStn.append(df.iloc[list1[k+1],0])
                  print("error of finding state = ", state, 'at', j,',', i)
              else: endStn.append(df.iloc[list1[k+1],0])
              
              endTime.append(df.iloc[list1[k+1],i].strftime('%H:%M'))
              if j <= 53: 
                direction.append("DN")
                # uniqueID.append(df.iloc[92,i]+"D")
              else: 
                direction.append("UP")
                # uniqueID.append(df.iloc[92,i]+"D")
            else:
              entryFlag = False
              if k != len(list1):
                for x in range(k+1,len(list1)):
                  if pd.isna(df.iloc[list1[x],i]) or type(df.iloc[list1[x],i]) == str:
                    continue
                  else:

                    checkstn = df.iloc[list1[x],0]
                    if checkstn.find('/') > 0:
                      if state == 'VASI UP' or state == 'VASI DN':
                          indx = checkstn.find('/')
                          endStn.append(df.iloc[list1[x],0][indx+1:])
                      elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                          indx = checkstn.find('/')
                          if df.iloc[list1[x],0][:indx] == "NSET":
                            continue
                          else:
                            endStn.append(df.iloc[list1[x],0][:indx])
                      else: 
                        endStn.append(df.iloc[list1[x],0])
                        print("error of finding state = ", state, 'at', j,',', i)
                    else: endStn.append(df.iloc[list1[x],0])
                    
                    # print(df.iloc[reqIndexofStn1[x],i], x,i, '\n')
                    endTime.append(df.iloc[list1[x],i].strftime('%H:%M'))
                    
                    if j <= 53:
                      direction.append("DN")
                    else:
                      direction.append("UP")
                    entryFlag = True
                    break
                if entryFlag:
                  continue
              for j in range(list1[k+1],list1[k]-1,-1):
                flag3 = False
                if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str:

                  checkstn = df.iloc[j,0]
                  if checkstn.find('/') > 0:
                    if state == 'VASI UP' or state == 'VASI DN':
                        indx = checkstn.find('/')
                        endStn.append(df.iloc[j,0][indx+1:])
                    elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                        indx = checkstn.find('/')
                        if df.iloc[j,0][:indx] == "NSET":
                          continue
                        else:
                          endStn.append(df.iloc[j,0][:indx])
                    else: 
                      endStn.append(df.iloc[j,0])
                      print("error of finding state = ", state, 'at', j,',', i)
                  else: endStn.append(df.iloc[j,0])
                  
                  endTime.append(df.iloc[j,i].strftime('%H:%M'))
                  if j <= 53:
                    direction.append("DN")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  else: 
                    direction.append("UP")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  flag3 = True
                  break

    if flag:
      for j in reqIndexofStn1:
        if j != reqIndexofStn1[-1]:
          entryFlag2 = False
          if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
            

            checkstn = df.iloc[j,0]
            if checkstn.find('/') > 0:
              if state == 'VASI UP' or state == 'VASI DN':
                indx = checkstn.find('/')
                RakeNum.append(df.iloc[3,i])
                startStn.append(df.iloc[j,0][indx+1:])
              elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                indx = checkstn.find('/')
                if df.iloc[j,0][:indx] == "NSET":
                  continue
                else:
                  RakeNum.append(df.iloc[3,i])
                  startStn.append(df.iloc[j,0][:indx])
              else: 
                RakeNum.append(df.iloc[3,i])
                startStn.append(df.iloc[j,0])
                print("error of finding state = ", state, 'at', j,',', i)
            else: 
              RakeNum.append(df.iloc[3,i])
              startStn.append(df.iloc[j,0])
            
            startTime.append(df.iloc[j,i].strftime('%H:%M'))
            entryFlag2 = True
          else:
            k = reqIndexofStn1.index(j)
            for p in range(reqIndexofStn1[k],reqIndexofStn1[k+1]):
                
              if not pd.isna(df.iloc[p,i]) and type(df.iloc[p,i]) != str:
                
                checkstn = df.iloc[p,0]
                if checkstn.find('/') > 0:
                  if state == 'VASI UP' or state == 'VASI DN':
                      indx = checkstn.find('/')
                      RakeNum.append(df.iloc[3,i])
                      startStn.append(df.iloc[p,0][indx+1:])
                  elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                      indx = checkstn.find('/')
                      if df.iloc[p,0][:indx] == "NSET":
                        continue
                      else:
                        RakeNum.append(df.iloc[3,i])
                        startStn.append(df.iloc[p,0][:indx])
                  else: 
                    RakeNum.append(df.iloc[3,i])
                    startStn.append(df.iloc[p,0])
                    print("error of finding state = ", state, 'at', p,',', i)
                else: 
                  RakeNum.append(df.iloc[3,i])
                  startStn.append(df.iloc[p,0])
                
                startTime.append(df.iloc[p,i].strftime('%H:%M'))
                entryFlag2 = True
                break
          if entryFlag2:
            k = reqIndexofStn1.index(j)

            checkstn = df.iloc[reqIndexofStn1[k+1],0]
            nsetFlag = False
            if checkstn.find('/') > 0:
              if state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                    indx = checkstn.find('/')
                    if df.iloc[reqIndexofStn1[k+1],0][:indx] == "NSET":
                      nsetFlag = True
            if  not pd.isna(df.iloc[reqIndexofStn1[k+1],i]) and type(df.iloc[reqIndexofStn1[k+1],i]) != str and nsetFlag == False:

              checkstn = df.iloc[reqIndexofStn1[k+1],0]
              if checkstn.find('/') > 0:
                if state == 'VASI UP' or state == 'VASI DN':
                    indx = checkstn.find('/')
                    endStn.append(df.iloc[reqIndexofStn1[k+1],0][indx+1:])
                elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                    indx = checkstn.find('/')
                    if df.iloc[reqIndexofStn1[k+1],0][:indx] == "NSET":
                      continue
                    else:
                      endStn.append(df.iloc[reqIndexofStn1[k+1],0][:indx])
                else: 
                  endStn.append(df.iloc[reqIndexofStn1[k+1],0])
                  print("error of finding state = ", state, 'at', j,',', i)
              else: endStn.append(df.iloc[reqIndexofStn1[k+1],0])
              
              endTime.append(df.iloc[reqIndexofStn1[k+1],i].strftime('%H:%M'))
              if j <= 53: 
                direction.append("DN")
                # uniqueID.append(df.iloc[92,i]+"D")
              else: 
                direction.append("UP")
                # uniqueID.append(df.iloc[92,i]+"D")
            else:
              entryFlag = False
              if k != len(reqIndexofStn1):
                for x in range(k+1,len(reqIndexofStn1)):
                  if pd.isna(df.iloc[reqIndexofStn1[x],i]) or type(df.iloc[reqIndexofStn1[x],i]) == str:
                    continue
                  else:

                    checkstn = df.iloc[reqIndexofStn1[x],0]
                    if checkstn.find('/') > 0:
                      if state == 'VASI UP' or state == 'VASI DN':
                          indx = checkstn.find('/')
                          endStn.append(df.iloc[reqIndexofStn1[x],0][indx+1:])
                      elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                          indx = checkstn.find('/')
                          if df.iloc[reqIndexofStn1[x],0][:indx] == "NSET":
                            continue
                          else:
                            endStn.append(df.iloc[reqIndexofStn1[x],0][:indx])
                      else: 
                        endStn.append(df.iloc[reqIndexofStn1[x],0])
                        print("error of finding state = ", state, 'at', j,',', i)
                    else: endStn.append(df.iloc[reqIndexofStn1[x],0])
                    
                    # print(df.iloc[reqIndexofStn1[x],i], x,i, '\n')
                    endTime.append(df.iloc[reqIndexofStn1[x],i].strftime('%H:%M'))
                    
                    if j <= 53:
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

                  checkstn = df.iloc[j,0]
                  if checkstn.find('/') > 0:
                    if state == 'VASI UP' or state == 'VASI DN':
                        indx = checkstn.find('/')
                        endStn.append(df.iloc[j,0][indx+1:])
                    elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                        indx = checkstn.find('/')
                        if df.iloc[j,0][:indx] == "NSET":
                          continue
                        else:
                          endStn.append(df.iloc[j,0][:indx])
                    else: 
                      endStn.append(df.iloc[j,0])
                      print("error of finding state = ", state, 'at', j,',', i)
                  else: endStn.append(df.iloc[j,0])
                  
                  endTime.append(df.iloc[j,i].strftime('%H:%M'))
                  if j <= 53:
                    direction.append("DN")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  else: 
                    direction.append("UP")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  flag3 = True
                  break
          
          


  else:
    for j in range(4,df.shape[0]):  # 4,df.shape[0] for line 3,4
      flag2 = False
      if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
        
        checkstn = df.iloc[j,0]
        if checkstn.find('/') > 0:
          if state == 'VASI UP' or state == 'VASI DN':
              indx = checkstn.find('/')
              RakeNum.append(df.iloc[3,i])
              startStn.append(df.iloc[j,0][indx+1:])
          elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
              indx = checkstn.find('/')
              if df.iloc[j,0][:indx] == "NSET":
                continue
              else:
                RakeNum.append(df.iloc[3,i])
                startStn.append(df.iloc[j,0][:indx])
          else: 
            RakeNum.append(df.iloc[3,i])
            startStn.append(df.iloc[j,0])
            print("error of finding state = ", state, 'at', j,',', i)
        else: 
          RakeNum.append(df.iloc[3,i])
          startStn.append(df.iloc[j,0])
        
        startTime.append(df.iloc[j,i].strftime('%H:%M'))
        if j <= 53:
          dnservice = True
          list1 = reqIndexofStn
        else:
          dnservice = False
          list1 = reqIndexofStn1
        for k in list1:
          # print(df.iloc[k,i])
          if not pd.isna(df.iloc[k,i]) and type(df.iloc[k,i]) != str and type(df.iloc[k,i]) != int:
            checkstn = df.iloc[k,0]
            if checkstn.find('/') > 0:
              if state == 'VASI UP' or state == 'VASI DN':
                  indx = checkstn.find('/')
                  endStn.append(df.iloc[k,0][indx+1:])
              elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                  indx = checkstn.find('/')
                  if df.iloc[k,0][:indx] == "NSET":
                    continue
                  else:
                    endStn.append(df.iloc[k,0][:indx])
              else: 
                endStn.append(df.iloc[k,0])
                print("error of finding state = ", state, 'at', j,',', i)
            else: endStn.append(df.iloc[k,0])
            
            endTime.append(df.iloc[k,i].strftime('%H:%M'))
            req = k
            flag2 = True
            if j <= 53: 
              direction.append("DN")
              # uniqueID.append(df.iloc[92,i]+"D")
            else: 
              direction.append("UP")
              # uniqueID.append(df.iloc[92,i]+"U")
            break
        if flag2: break
        else: 
          print("error2 ","with value ", df.iloc[j,i], " at row j = ", j, ' row k = ', k, ",column = ", i )  # 1,i for line 3,4
    for j in list1:
      if j >= req:
        if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
          if j != list1[-1]:
            

            checkstn = df.iloc[j,0]
            if checkstn.find('/') > 0:
              if state == 'VASI UP' or state == 'VASI DN':
                indx = checkstn.find('/')
                RakeNum.append(df.iloc[3,i])
                startStn.append(df.iloc[j,0][indx+1:])
              elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                indx = checkstn.find('/')
                if df.iloc[j,0][:indx] == "NSET":
                  continue
                else:
                  RakeNum.append(df.iloc[3,i])
                  startStn.append(df.iloc[j,0][:indx])
              else: 
                RakeNum.append(df.iloc[3,i])
                startStn.append(df.iloc[j,0])
                print("error of finding state = ", state, 'at', j,',', i)
            else: 
              RakeNum.append(df.iloc[3,i])
              startStn.append(df.iloc[j,0])

            startTime.append(df.iloc[j,i].strftime('%H:%M'))
            k = list1.index(j)

            checkstn = df.iloc[list1[k+1],0]
            nsetFlag = False
            if checkstn.find('/') > 0:
              if state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                    indx = checkstn.find('/')
                    if df.iloc[list1[k+1],0][:indx] == "NSET":
                      nsetFlag = True

            if not pd.isna(df.iloc[list1[k+1],i]) and type(df.iloc[list1[k+1],i]) != str and nsetFlag == False:

              checkstn = df.iloc[list1[k+1],0]
              if checkstn.find('/') > 0:
                if state == 'VASI UP' or state == 'VASI DN':
                    indx = checkstn.find('/')
                    endStn.append(df.iloc[list1[k+1],0][indx+1:])
                elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                    indx = checkstn.find('/')
                    if df.iloc[list1[k+1],0][:indx] == "NSET":
                      continue
                    else:
                      endStn.append(df.iloc[list1[k+1],0][:indx])
                else: 
                  endStn.append(df.iloc[list1[k+1],0])
                  print("error of finding state = ", state, 'at', j,',', i)
              else: endStn.append(df.iloc[list1[k+1],0])
              
              endTime.append(df.iloc[list1[k+1],i].strftime('%H:%M'))
              if j <= 53:
                direction.append("DN")
                # uniqueID.append(df.iloc[92,i]+"D")
              else: 
                direction.append("UP")
                # uniqueID.append(df.iloc[92,i]+"U")
            else:


              entryFlag = False
              if k != len(list1):
                for x in range(k+1,len(list1)):
                  if pd.isna(df.iloc[list1[x],i]) or type(df.iloc[list1[x],i]) == str:
                    continue
                  else:

                    checkstn = df.iloc[list1[x],0]
                    if checkstn.find('/') > 0:
                      if state == 'VASI UP' or state == 'VASI DN':
                          indx = checkstn.find('/')
                          endStn.append(df.iloc[list1[x],0][indx+1:])
                      elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                          indx = checkstn.find('/')
                          if df.iloc[list1[x],0][:indx] == "NSET":
                            continue
                          else:
                            endStn.append(df.iloc[list1[x],0][:indx])
                      else: 
                        endStn.append(df.iloc[list1[x],0])
                        print("error of finding state = ", state, 'at', j,',', i)
                    else: endStn.append(df.iloc[list1[x],0])
                    
                    # print(df.iloc[reqIndexofStn1[x],i], x,i, '\n')
                    endTime.append(df.iloc[list1[x],i].strftime('%H:%M'))
                    
                    if j <= 53:
                      direction.append("DN")
                    else:
                      direction.append("UP")
                    entryFlag = True
                    break
                if entryFlag:
                  continue
              
              
              
              for j in range(list1[k+1],list1[k]-1,-1):
                flag3 = False
                if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str:

                  checkstn = df.iloc[j,0]
                  if checkstn.find('/') > 0:
                    if state == 'VASI UP' or state == 'VASI DN':
                        indx = checkstn.find('/')
                        endStn.append(df.iloc[j,0][indx+1:])
                    elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                        indx = checkstn.find('/')
                        if df.iloc[j,0][:indx] == "NSET":
                          continue
                        else:
                          endStn.append(df.iloc[j,0][:indx])
                    else: 
                      endStn.append(df.iloc[j,0])
                      print("error of finding state = ", state, 'at', j,',', i)
                  else: endStn.append(df.iloc[j,0])
                  
                  endTime.append(df.iloc[j,i].strftime('%H:%M'))
                  if j <= 53: 
                    direction.append("DN")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  else: 
                    direction.append("UP")
                    # uniqueID.append(df.iloc[92,i]+"U")
                  flag3 = True
                  break
              if not flag3: print("error3", df.iloc[1,i])

    if 'dnservice' in locals() and dnservice:
      for j in reqIndexofStn1:
        if j != reqIndexofStn1[-1]:
          if not pd.isna(df.iloc[j,i]) and type(df.iloc[j,i]) != str and type(df.iloc[j,i]) != int:
            

            checkstn = df.iloc[j,0]
            if checkstn.find('/') > 0:
              if state == 'VASI UP' or state == 'VASI DN':
                indx = checkstn.find('/')
                RakeNum.append(df.iloc[3,i])
                startStn.append(df.iloc[j,0][indx+1:])
              elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                indx = checkstn.find('/')
                if df.iloc[j,0][:indx] == "NSET":
                  continue
                else:
                  RakeNum.append(df.iloc[3,i])
                  startStn.append(df.iloc[j,0][:indx])
              else: 
                RakeNum.append(df.iloc[3,i])
                startStn.append(df.iloc[j,0])
                print("error of finding state = ", state, 'at', j,',', i)
            else: 
              RakeNum.append(df.iloc[3,i])
              startStn.append(df.iloc[j,0])
            
            startTime.append(df.iloc[j,i].strftime('%H:%M'))
            k = reqIndexofStn1.index(j)

            checkstn = df.iloc[reqIndexofStn1[k+1],0]
            nsetFlag = False
            if checkstn.find('/') > 0:
              if state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                    indx = checkstn.find('/')
                    if df.iloc[reqIndexofStn1[k+1],0][:indx] == "NSET":
                      nsetFlag = True

            if  not pd.isna(df.iloc[reqIndexofStn1[k+1],i]) and type(df.iloc[reqIndexofStn1[k+1],i]) != str and nsetFlag == False:

              checkstn = df.iloc[reqIndexofStn1[k+1],0]
              if checkstn.find('/') > 0:
                if state == 'VASI UP' or state == 'VASI DN':
                    indx = checkstn.find('/')
                    endStn.append(df.iloc[reqIndexofStn1[k+1],0][indx+1:])
                elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                    indx = checkstn.find('/')
                    if df.iloc[reqIndexofStn1[k+1],0][:indx] == "NSET":
                      continue
                    else:
                      endStn.append(df.iloc[reqIndexofStn1[k+1],0][:indx])
                else: 
                  endStn.append(df.iloc[reqIndexofStn1[k+1],0])
                  print("error of finding state = ", state, 'at', j,',', i)
              else: endStn.append(df.iloc[reqIndexofStn1[k+1],0])
              
              endTime.append(df.iloc[reqIndexofStn1[k+1],i].strftime('%H:%M'))
              if j <= 53: 
                direction.append("DN")
                # uniqueID.append(df.iloc[92,i]+"D")
              else: 
                direction.append("UP")
                # uniqueID.append(df.iloc[92,i]+"D")
            else:
              entryFlag = False
              if k != len(reqIndexofStn1):
                for x in range(k+1,len(reqIndexofStn1)):
                  if pd.isna(df.iloc[reqIndexofStn1[x],i]) or type(df.iloc[reqIndexofStn1[x],i]) == str:
                    continue
                  else:

                    checkstn = df.iloc[reqIndexofStn1[x],0]
                    if checkstn.find('/') > 0:
                      if state == 'VASI UP' or state == 'VASI DN':
                          indx = checkstn.find('/')
                          endStn.append(df.iloc[reqIndexofStn1[x],0][indx+1:])
                      elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                          indx = checkstn.find('/')
                          if df.iloc[reqIndexofStn1[x],0][:indx] == "NSET":
                            continue
                          else:
                            endStn.append(df.iloc[reqIndexofStn1[x],0][:indx])
                      else: 
                        endStn.append(df.iloc[reqIndexofStn1[x],0])
                        print("error of finding state = ", state, 'at', j,',', i)
                    else: endStn.append(df.iloc[reqIndexofStn1[x],0])
                    
                    # print(df.iloc[reqIndexofStn1[x],i], x,i, '\n')
                    endTime.append(df.iloc[reqIndexofStn1[x],i].strftime('%H:%M'))
                    
                    if j <= 53:
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

                  checkstn = df.iloc[j,0]
                  if checkstn.find('/') > 0:
                    if state == 'VASI UP' or state == 'VASI DN':
                        indx = checkstn.find('/')
                        endStn.append(df.iloc[j,0][indx+1:])
                    elif state == "NEC UP" or state == "NEC DN" or state == "NCC UP" or state == "NCC DN":
                        indx = checkstn.find('/')
                        if df.iloc[j,0][:indx] == "NSET":
                          continue
                        else:
                          endStn.append(df.iloc[j,0][:indx])
                    else: 
                      endStn.append(df.iloc[j,0])
                      print("error of finding state = ", state, 'at', j,',', i)
                  else: endStn.append(df.iloc[j,0])
                  
                  endTime.append(df.iloc[j,i].strftime('%H:%M'))
                  if j <= 53:
                    direction.append("DN")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  else: 
                    direction.append("UP")
                    # uniqueID.append(df.iloc[92,i]+"D")
                  flag3 = True
                  break
            

  if not pd.isna(df.iloc[111,i]) and type(df.iloc[111,i]) != str:# and df.iloc[109,i] != "DWTO UP" and df.iloc[109,i] != "DWTO DN" and df.iloc[109,i] != "DW DN":# and 'SVVR' not in df.iloc[85,i]:
    RakeNum.append(RakeNum[-1])
    startStn.append(endStn[-1])
    startTime.append(endTime[-1])
    endStn.append(df.iloc[110,i])
    endTime.append(df.iloc[111,i].strftime('%H:%M'))
    direction.append('UP') 





print(len(RakeNum),len(startStn),len(startTime),len(endStn),len(endTime)) #, len(uniqueID))

services = pd.DataFrame(list(zip(RakeNum,startStn,startTime,endStn,endTime,direction)),#uniqueID)),
               columns =['Rake Num','Start Station','Start Time','End Station','End Time','Direction'])#,'Uniques ID'])

#services = services.sort_values(by=['Start Time'])
services




# services.iloc[10,1]

serviceTime = []
for i in range(services.shape[0]):
  if services.iloc[i,1] == "DW" or services.iloc[i,1] == "YB":
    services.iloc[i,1] = services.iloc[i,1] + " " +services.iloc[i,5]
  if services.iloc[i,3] == "DW" or services.iloc[i,3] == "YB":
    services.iloc[i,3] = services.iloc[i,3] + " " +services.iloc[i,5]
  if services.iloc[i,2][:2] == '00':
    services.iloc[i,2] = '24' + services.iloc[i,2][2:]
  elif services.iloc[i,2][:2] == '01':
    services.iloc[i,2] = '25' + services.iloc[i,2][2:]

  if services.iloc[i,4][:2] == '00':
    services.iloc[i,4] = '24' + services.iloc[i,4][2:]
  elif services.iloc[i,4][:2] == '01':
    services.iloc[i,4] = '25' + services.iloc[i,4][2:]


rowsRemoved = []
for i in range(services.shape[0]):
  if services.iloc[i,1] == services.iloc[i,3] and services.iloc[i,2] == services.iloc[i,4]:
    rowsRemoved.append(i)
services = services.drop(rowsRemoved)
services

for i in range(services.shape[0]):
  serviceTime.append(timeDiff(services.iloc[i,2],services.iloc[i,4]))

services["Service Time"] = serviceTime
services["Rake Num"] = services['Rake Num'].astype(int)
services = services.sort_values(by='Start Time')


services.to_csv(f"{outputFileLocation}InitialServices.csv")