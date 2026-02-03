import pandas as pd
import csv
import json
import sys
import os
from concurrent.futures import ProcessPoolExecutor
import shutil


# --------------------------------------------- PARSE Command Line Input -----------------------------------------------
member_id = sys.argv[1]
line_no = sys.argv[2]
json_str = sys.argv[3]
data = json.loads(json_str)
crew_control = data["crew_control"]
depots = data["depots"]

new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"


inputFileLocation = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/"
tempLocation = f"{inputFileLocation}SOLUTION 1/"
outputLocation = tempLocation

ijk=0
tookServices = []
dutiesDict = {}

with open(f"{tempLocation}solution_{member_id}.csv", 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        dutiesDict[ijk] = [int(value) for value in row]
        tookServices += [int(value) for value in row]
        ijk += 1

print(len(tookServices), ijk)

df = pd.read_csv(f"{inputFileLocation}MainLoops.csv")#input services
df1 = pd.read_csv(f"{inputFileLocation}InitialServices.csv")
servicesAll = [df.iloc[i,0] for i in range(len(df)) ]



"""
for service in servicesAll:
    if service not in tookServices:
        dutiesDict[ijk] = [service]
        ijk += 1
"""
print(ijk,"yoyooy")

def hhmm2mins(hhmm):
    if True:
        hrs = hhmm[:2]
        min = hhmm[-2:]
        mins = int(hrs)*60 + int(min)
        return mins
    
def min2hhmm(mins):
    """ gives hh:mm string and takes integer minutes 0 to 1440"""
    if True:
        h = mins//60
        mins = mins - (h*60)
        if len(str(h)) == 1: h = "0" + str(h)
        if len(str(mins)) == 1: mins = "0" + str(mins)
        return str(h) + ":" + str(mins)
    
#Crew Control Jurisdiction
csv_file = f"{inputFileLocation}Jurisdiction.csv"
# Reading back the lists from the CSV file
with open(csv_file, mode='r') as file:
    reader = csv.reader(file)
    retrieved_lists = [row for row in reader]
with open(csv_file, mode='r') as file:
    reader = csv.reader(file)
    juris_rows = sum(1 for item in reader)

# Extracting the lists
if juris_rows == 2:
    cc1 = [str(line) for line in retrieved_lists[0]]
    cc2 = [str(line) for line in retrieved_lists[0]]
    # Crew Controls
    crewControl = [str(line) for line in retrieved_lists[1]]
elif juris_rows == 3:
    cc1 = [str(line) for line in retrieved_lists[0]]
    cc2 = [str(line) for line in retrieved_lists[1]]
    # Crew Controls
    crewControl = [str(line) for line in retrieved_lists[2]]

def printSummary(dutiesDict, outputFile):
    # global verbose, worstDT
    sameCC = 0
    CC1_no, CC2_no, CCdiff_no = 201,401,901
    
    with open(outputFile, mode='w', newline='') as file:
        writer = csv.writer(file)
        #header = [f"{ordinal(i)} Service" for i in range(1, 20 + 1)]
        #writer.writerow(["Duty No", "Sign On Time", "Sign On Loc", "Sign Off Loc", "Sign Off Time", "Driving Hrs", "Duty Hrs"] + header)
        writer.writerow(["Duty No", "Sign On Time", "Sign On Loc", "Sign Off Loc", "Sign Off Time", "Driving Hrs", "Duty Hrs", "Same Jurisdiction",'1st Trip','2nd Trip','3rd Trip','4th Trip','1st Break','2nd Break','3rd Break','1st break Jursd','2nd break Jursd','3rd break Jursd'])


        for index, servSet in dutiesDict.items():
                #print(servSet.breaksTaken,servSet.breaksRemaining,index)
                servSet1 = []
                for ax in servSet:
                    for ss in range(len(df)):
                        if ax == df.iloc[ss,0]:
                            servSet1.append([df.iloc[ss,1],df.iloc[ss,2],df.iloc[ss,3],df.iloc[ss,4],df.iloc[ss,5],df.iloc[ss,6],df.iloc[ss,7],df.iloc[ss,9]])
                

                # dutyDur = min2hhmm(hhmm2mins(servSet1[-1][4]) - hhmm2mins(servSet1[0][2]) + 25)
                # drivingTimes.append(servSet.totalDriveDur)
                # dutyHrs.append(servSet.dutyHrs)
                dutyNo = 0
                if (servSet1[0][1] in cc1 and servSet1[-1][3] in cc1):
                    dutyNo = CC1_no
                    CC1_no += 1
                elif (servSet1[0][1] in cc2 and servSet1[-1][3] in cc2):
                    dutyNo = CC2_no
                    CC2_no += 1
                else:
                    dutyNo = CCdiff_no
                    CCdiff_no += 1
                if servSet1[0][1] not in outstation_locations:
                    signOnTime = min2hhmm(hhmm2mins(servSet1[0][2]) - 15)
                else:
                    signOnTime = min2hhmm(hhmm2mins(servSet1[0][2]) - 25)
                # signOnDur = servSet.signOn()[1]
                signOnLoc = servSet1[0][1]
                if servSet1[-1][3] not in outstation_locations:
                    signOffTime = min2hhmm(hhmm2mins(servSet1[-1][4]) + 10)
                else:
                    signOffTime = min2hhmm(hhmm2mins(servSet1[-1][4]) + 20)
                
                dutyDur = min2hhmm(hhmm2mins(signOffTime) - hhmm2mins(signOnTime))
                driveDur = hhmm2mins(servSet1[-1][4])-hhmm2mins(servSet1[0][2])
                signOffLoc = servSet1[-1][3]
                if (servSet1[0][1] in cc1 and servSet1[-1][3] in cc1) or (servSet1[0][1] in cc2 and servSet1[-1][3] in cc2):
                    sameJuris = "Yes"
                    sameCC += 1
                else: sameJuris = "No"

                breaks = []
                breakJurisd = []
                tripDur = []

# Iterate over the sublists
                for i in range(len(servSet1) - 1):  # Iterate until the second to last sublist
                    diff = hhmm2mins(servSet1[i + 1][2]) - hhmm2mins(servSet1[i][4])  # Calculate the difference
                    if diff >= 30:
                        tripDur.append(hhmm2mins(servSet1[i][4]) - hhmm2mins(servSet1[0][2]) - sum(tripDur) - sum(breaks))
                        breaks.append(diff)
                        if (servSet1[i][3] in cc1):
                            breakJurisd.append(crew_control[0])
                        else:
                            breakJurisd.append(crew_control[-1])
                        driveDur -= diff
                tripDur.append(hhmm2mins(servSet1[-1][4]) - hhmm2mins(servSet1[0][2]) - sum(tripDur) - sum(breaks))
                driveDur = min2hhmm(driveDur)

                tripDur = list(map(lambda x: min2hhmm(x), tripDur))
                breaks = list(map(lambda x: min2hhmm(x), breaks))
                if len(tripDur) < 4:
                    tripDur.extend([""] * (4 - len(tripDur)))
                if len(breaks) < 3:
                    breaks.extend([""] * (3 - len(breaks)))
                if len(breakJurisd) < 3:
                    breakJurisd.extend([""] * (3 - len(breakJurisd)))

                writer.writerow([dutyNo, signOnTime,signOnLoc, signOffLoc, signOffTime, driveDur, dutyDur, sameJuris] + tripDur + breaks + breakJurisd)
    print("same Juris % = ", sameCC/len(dutiesDict))
    print("Roster Summary generated and saved in outputFiles")


def printRoster(dutiesDict, outputFile):
    # global verbose, worstDT
    sameCC = 0
    CC1_no, CC2_no, CCdiff_no = 201,401,901
    
    with open(outputFile, mode='w', newline='') as file:
        writer = csv.writer(file)
        #header = [f"{ordinal(i)} Service" for i in range(1, 20 + 1)]
        #writer.writerow(["Duty No", "Sign On Time", "Sign On Loc", "Sign Off Loc", "Sign Off Time", "Driving Hrs", "Duty Hrs"] + header)
        writer.writerow(["Duty No", "Sign On Time", "Sign On Loc", "Sign Off Loc", "Sign Off Time", "Driving Hrs", "Duty Hrs", "Same Jurisdiction","Rake Num", "Start Stn", "Start Time", "End Stn", "End Time","Service Duration", "Break","StepBack Rake"])


        for index, servSet in dutiesDict.items():
                #print(servSet.breaksTaken,servSet.breaksRemaining,index)
                servSet1 = []
                for ax in servSet:
                    for ss in range(len(df)):
                        if ax == df.iloc[ss,0]:
                            servSet1.append([df.iloc[ss,1],df.iloc[ss,2],df.iloc[ss,3],df.iloc[ss,4],df.iloc[ss,5],df.iloc[ss,6],df.iloc[ss,7],df.iloc[ss,9]])
                

                # dutyDur = min2hhmm(hhmm2mins(servSet1[-1][4]) - hhmm2mins(servSet1[0][2]) + 25)
                # drivingTimes.append(servSet.totalDriveDur)
                # dutyHrs.append(servSet.dutyHrs)
                dutyNo = 0
                if (servSet1[0][1] in cc1 and servSet1[-1][3] in cc1):
                    dutyNo = CC1_no
                    CC1_no += 1
                elif (servSet1[0][1] in cc2 and servSet1[-1][3] in cc2):
                    dutyNo = CC2_no
                    CC2_no += 1
                else:
                    dutyNo = CCdiff_no
                    CCdiff_no += 1
                if servSet1[0][1] not in outstation_locations:
                    signOnTime = min2hhmm(hhmm2mins(servSet1[0][2]) - 15)
                else:
                    signOnTime = min2hhmm(hhmm2mins(servSet1[0][2]) - 25)
                # signOnDur = servSet.signOn()[1]
                signOnLoc = servSet1[0][1]
                if servSet1[-1][3] not in outstation_locations:
                    signOffTime = min2hhmm(hhmm2mins(servSet1[-1][4]) + 10)
                else:
                    signOffTime = min2hhmm(hhmm2mins(servSet1[-1][4]) + 20)
                
                dutyDur = min2hhmm(hhmm2mins(signOffTime) - hhmm2mins(signOnTime))
                driveDur = hhmm2mins(servSet1[-1][4])-hhmm2mins(servSet1[0][2])
                signOffLoc = servSet1[-1][3]
                if (servSet1[0][1] in cc1 and servSet1[-1][3] in cc1) or (servSet1[0][1] in cc2 and servSet1[-1][3] in cc2):
                    sameJuris = "Yes"
                    sameCC += 1
                else: sameJuris = "No"

                breaks = []

# Iterate over the sublists
                for i in range(len(servSet1) - 1):  # Iterate until the second to last sublist
                    diff = hhmm2mins(servSet1[i + 1][2]) - hhmm2mins(servSet1[i][4])  # Calculate the difference
                    breaks.append(diff)
                    if diff>=30:
                        driveDur -= diff
                driveDur = min2hhmm(driveDur)
# Rishuv
                First_Serv = True
                brake = 0
                for service in servSet1:
                    if brake == len(servSet1) - 1:
                        new_header = [service[0] , service[1] ,service[2] ,service[3], service[4] , service[6] , 0, service[7]]
                    else:
                        new_header = [service[0] , service[1] ,service[2] ,service[3], service[4] , service[6] , breaks[brake], service[7]]
                        brake += 1
                    if First_Serv:
                        writer.writerow([dutyNo, signOnTime,signOnLoc, signOffLoc, signOffTime, driveDur, dutyDur, sameJuris] + new_header)    
                        First_Serv = False
                    else:
                        #writer.writerow([dutyNo, signOnTime,signOnLoc, signOffLoc, signOffTime, driveDur, dutyDur, sameJuris] + new_header)
                        writer.writerow([dutyNo, "","", "", "", "", "",""] + new_header)    
                writer.writerow(["","" ,"" ,"" ,"" ,"" ,"" ,"" ,"" ,"" ,"" ,"" ,"",""])
    print("same Juris % = ", sameCC/len(dutiesDict))
    print("Roster generated and saved in outputFiles")

def verification(dutiesDict, op):
    trainDuty = {}
    CC1_no, CC2_no, CCdiff_no = 201,401,901
    dutyNo = 0

    for dutyNum, servSet in dutiesDict.items():
        servSet1 = []
        for ax in servSet:
            for ss in range(len(df)):
                if ax == df.iloc[ss,0]:
                    for serv in range(len(df1)):
                        if float(df1.iloc[serv,0]) == df.iloc[ss,12] or df1.iloc[serv,0] == df.iloc[ss,11]:
                            servSet1.append([df1.iloc[serv,1],df1.iloc[serv,2],df1.iloc[serv,3],df1.iloc[serv,4],df1.iloc[serv,5],df1.iloc[serv,6],df1.iloc[serv,7]])

        if (servSet1[0][1] in cc1 and servSet1[-1][3] in cc1):
            dutyNo = CC1_no
            CC1_no += 1
        elif (servSet1[0][1] in cc2 and servSet1[-1][3] in cc2):
            dutyNo = CC2_no
            CC2_no += 1
        else:
            dutyNo = CCdiff_no
            CCdiff_no += 1

        for service in servSet1:
            trainNum = service[0]               
            if trainNum not in trainDuty:
                trainDuty[trainNum] = list()
            trainDuty[trainNum].append([dutyNo] + service[1:])  
    """
    with open(op, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        header = [f"{ordinal(i)} person" for i in range(1, 40 + 1)]
        writer.writerow(['Train No.'] + header)
        # Write data
        for trainNum, dutySet in trainDuty.items():
            dutySet.sort(key=lambda x:x[2])
            writer.writerow([trainNum] + dutySet)

    sys.exit()
    """
    for trainNum, dutySet in trainDuty.items(): 
        dutySet.sort(key=lambda x:x[2])
    
    if True:
        sheet = []
        for trainNum, dutySet in trainDuty.items():
            for duty in dutySet:
                sheet.append([trainNum,duty[1],duty[2],duty[3],duty[4],duty[0]])
        sheet.sort(key=lambda x:x[0])
        with open(op, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            header = ["Rake Num", "Start Stn", "Start Time", "End Stn", "End Time", "Duty Num"]
            writer.writerow(header)
            writer.writerow(sheet[0])
            for i in range(1,len(sheet)):
                if sheet[i][0] != sheet[i-1][0]:
                    writer.writerow([" "," "," "," "," "," "])
                writer.writerow(sheet[i])
    print("verification file is generated")


with open(f"{inputFileLocation}Outstations.csv", mode='r') as file:
    reader = csv.reader(file)
    outstation_locations = next(reader)
# if __name__ == '__main__':

    # with ProcessPoolExecutor() as executer:
    #     executer.submit(printSummary,dutiesDict, f"{outputLocation}RosterSummary.csv")
    #     executer.submit(printRoster,dutiesDict, f"{outputLocation}RosterDMRC.csv")
    #     executer.submit(verification,dutiesDict, f"{outputLocation}mainLoopVerification.csv")

print("Generating Roster Summary...")
printSummary(dutiesDict,f"{outputLocation}RosterSummary_{member_id}.csv")

print("Generating Roster file...")
printRoster(dutiesDict, f"{outputLocation}RosterDMRC_{member_id}.csv")

print("Generating Train Loop verification file...")
verification(dutiesDict, f"{outputLocation}TrainLoopVerification_{member_id}.csv")

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUTPUT_FILE = os.path.join(parent_dir, f'temp_files/trip_chart_{member_id}.xlsx')
roster_csv = pd.read_csv(f"{outputLocation}RosterDMRC_{member_id}.csv")
roster_csv.to_excel(OUTPUT_FILE, index=False)

os.remove(f"{outputLocation}solution_{member_id}.csv")