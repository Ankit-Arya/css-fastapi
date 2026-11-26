import sys
import csv
import pytz
#from tqdm import tqdm
# import time
import time
from datetime import datetime
# from google.colab import drive
import argparse
import os
from zoneinfo import ZoneInfo
import pandas as pd

# Then in your script, write to /content/drive/MyDrive/

sys.setrecursionlimit(2000)
starttime = time.time()
print(time.strftime('%H:%M:%S'), flush=True)




ist_time = datetime.now(ZoneInfo("Asia/Kolkata"))
print("IST time:", ist_time.strftime('%Y-%m-%d %H:%M:%S'), flush=True)

parser = argparse.ArgumentParser(description='Process crew scheduling with specified range')
parser.add_argument('--member_id', type=str, required=True, help='Current time string for file naming')
parser.add_argument('--initial_start', type=int, default=0, help='Initial start value')
parser.add_argument('--final_end', type=int, default=1338, help='Final end value')
parser.add_argument('--short_break', type=int, default=30, help='Duration of short breaks.')
parser.add_argument('--long_break', type=int, default=50, help='Duration of long breaks.')
parser.add_argument('--duty_hours', type=int, default=8*60, help='Total duty hours.')
parser.add_argument('--continuous_drive', type=int, default=3*60, help='Maximum continuous driving time.')
parser.add_argument('--driving_duration', type=int, default=6*60, help='Maximum driving duration in a duty.')
parser.add_argument('--juris_conflict', type=int, help='Jurisdiction conflict count.')
args = parser.parse_args()

member_id = args.member_id
short_break = args.short_break
long_break = args.long_break
Duty_hours = args.duty_hours
Continuous_Driving_time = args.continuous_drive
Driving_duration = args.driving_duration
juris_conflict = args.juris_conflict

new_location = f"ALL_USER_TT/LINE1_{member_id}"

home_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
inputFileLocation = home_path + f"/{new_location}/USEFUL OUTPUT_{member_id}/Mainloops.csv"

csv_file = home_path + f"/{new_location}/USEFUL OUTPUT_{member_id}/Jurisdiction.csv"
# Reading back the lists from the CSV file
with open(csv_file, mode='r') as file:
    reader = csv.reader(file)
    retrieved_lists = [row for row in reader]

# Extracting the lists
cc1 = [str(line) for line in retrieved_lists[0]]
cc2 = [str(line) for line in retrieved_lists[0]]
# Crew Controls

crewControl = [str(line) for line in retrieved_lists[1]]
# depots_outstations = [str(line) for line in retrieved_lists[3]]
step_back_location = ["DSG", "RI"]
other_outstations = []


def find_specific_services(inputFileLocation, outstation_path):
    inputFileLocation = inputFileLocation
    outstation_path = outstation_path
    try:
        df_mainloops = pd.read_csv(inputFileLocation, header=None)
        # print(f"Read Mainloops into DataFrame with {len(df_mainloops)} rows")
    except Exception as e:
        # print(f"Failed to read {inputFileLocation}: {e}")
        df_mainloops = pd.DataFrame()

    # read outstation.csv using csv.reader
    outstations = []
    try:
        with open(outstation_path, newline='') as f:
            reader = csv.reader(f)
            outstations = [row for row in reader]
        # print(f"Read Outstations.csv with {len(outstations)} rows")
    except Exception as e:
        # print(f"Failed to read {outstation_path}: {e}")
        outstations = []

    # display DataFrame contents to console
    # try:
    #     if df_mainloops.empty:
    #         print("df_mainloops is empty")
    #     else:
    #         nrows, ncols = df_mainloops.shape
    #         print(f"Displaying df_mainloops ({nrows} rows x {ncols} cols)")
    #         # if small enough, print entire DataFrame; otherwise print a preview
    #         if nrows <= 100:
    #             print(df_mainloops.to_string(index=False), flush=True)
    #         else:
    #             print(df_mainloops.head(50).to_string(index=False), flush=True)
    #             print(f"Printed first 50 rows of {nrows}. To view all rows, save with df_mainloops.to_csv(...) or adjust this preview limit.")
    # except Exception as e:
    #     print(f"Failed to display df_mainloops: {e}")
        
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    induction_services = []

    try:
        for index, row in df_mainloops.iterrows():
            if row[2] in outstations[0]:
                induction_services.append(int(row[0]))
        # print(f"Found {len(induction_services)} matching outstation services.")
        print("Induction Services IDs:", induction_services)
    except Exception as e:
        print(f"Error while checking outstation services: {e}")

    #-----------------------------------------------------------------------------------------------------------------------------------------------

    stabling_services = []
    try:
        for index, row in df_mainloops.iterrows():
            if row[4] in outstations[0]:
                stabling_services.append(int(row[0]))
        # print(f"Found {len(stabling_services)} matching outstation services.")
        print("Stabling Services IDs:", stabling_services)
    except Exception as e:
        print(f"Error while checking outstation services: {e}")

    #-----------------------------------------------------------------------------------------------------------------------------------------------

    invalid_initial_sevices = []

    #check above pandas dataframe which has row[2] == 'RI', save these row[0] in temp_ri_services list. Now find in this df having row[2] == 'RI', in which the time value difference of row[3] of (n+1)th row - row[3] of nth row is more than 120 minutes
    # Find services with row[2] == 'RI'
    temp_ri_services = []
    temp_nbaa_services = []
    try:
        ri_df = df_mainloops[df_mainloops[2] == 'RI']
        temp_ri_services = ri_df[0].tolist()
        temp_ri_services = [int(x) for x in temp_ri_services if pd.notna(x)]
        # print("Temp Initial RI services: ",temp_ri_services)

        # Check for time differences > 120 minutes
        if len(ri_df) > 1:
            for i in range(len(ri_df)-1):
                time1 = pd.to_datetime(ri_df.iloc[i][3])
                time2 = pd.to_datetime(ri_df.iloc[i+1][3])
                if (time2 - time1).total_seconds() / 60 > 120:
                    # print(f"Time difference > 120 minutes between services: {ri_df.iloc[i][0]} and {ri_df.iloc[i+1][0]}")
                    valid_ri_initial_sevice = int(ri_df.iloc[i][0])
                    break
        invalid_ri_initial_services = [int(x) for x in temp_ri_services if x != valid_ri_initial_sevice]
        # print("Invalid Initial RI services: ", invalid_ri_initial_services)


        nbaa_df = df_mainloops[df_mainloops[2] == 'NBAA']
        temp_nbaa_services = nbaa_df[0].tolist()
        temp_nbaa_services = [int(x) for x in temp_nbaa_services if pd.notna(x)]
        # if len(nbaa_df) > 1:
        #     for i in range(len(nbaa_df)-1):
        #         time1 = pd.to_datetime(nbaa_df.iloc[i][3])
        #         time2 = pd.to_datetime(nbaa_df.iloc[i+1][3])
        #         if (time2 - time1).total_seconds() / 60 > 120:
        #             print(f"Time difference > 120 minutes between services: {nbaa_df.iloc[i][0]} and {nbaa_df.iloc[i+1][0]}")
        #             valid_nbaa_initial_sevice = int(nbaa_df.iloc[i][0])
        #             break
        invalid_nbaa_initial_services = temp_nbaa_services
        # print("Invalid Initial NBAA services: ", invalid_nbaa_initial_services)

        invalid_initial_sevices = invalid_ri_initial_services + invalid_nbaa_initial_services
        print("Invalid Initial services: ", invalid_initial_sevices)
                
    except Exception as e:
        print(f"No step back start found while processing services: {e}")
        
    #-----------------------------------------------------------------------------------------------------------------------------------------------

    invalid_signoff_services = []

    nbaa_df = df_mainloops[df_mainloops[4] == 'NBAA']
    temp_nbaa_services = nbaa_df[0].tolist()
    temp_nbaa_services = [int(x) for x in temp_nbaa_services if pd.notna(x)]
    invalid_nbaa_signoff_services = temp_nbaa_services
    # print("Invalid NBAA signoff services: ", invalid_nbaa_signoff_services)

    ri_df = df_mainloops[df_mainloops[4] == 'RI']
    temp_ri_services = ri_df[0].tolist()
    temp_ri_services = [int(x) for x in temp_ri_services if pd.notna(x)]
    try:
        if len(ri_df) > 1:
            for i in range(len(ri_df)-1):
                time1 = pd.to_datetime(ri_df.iloc[i][3])
                time2 = pd.to_datetime(ri_df.iloc[i+1][3])
                if (time2 - time1).total_seconds() / 60 > 120:
                    # print(f"Time difference > 120 minutes between services: {ri_df.iloc[i][0]} and {ri_df.iloc[i+1][0]}")
                    valid_ri_signoff_service = int(ri_df.iloc[i+1][0])
                    break
        invalid_ri_signoff_services = [int(x) for x in temp_ri_services if x != valid_ri_signoff_service]
        # print("Invalid RI signoff services: ", invalid_ri_signoff_services)
    except Exception as e:
        print(f"No step back signoff found while processing services: {e}")

    invalid_signoff_services = invalid_nbaa_signoff_services + invalid_ri_signoff_services
    print("Invalid signoff services: ", invalid_signoff_services)
    #-----------------------------------------------------------------------------------------------------------------------------------------------
    # Return all the required lists
    return induction_services, stabling_services, invalid_initial_sevices, invalid_signoff_services


output = []
count = 1
class Services:
    def __init__(self, attrs):
        """object denotinig the a trip from one station to other station"""
        self.servNum = int(attrs[0]) # we give this number; 0 to 927
        self.trainNum = int(attrs[1]) # 701 to 736
        self.startStn = str(attrs[2])
        self.startTime = hhmm2mins(attrs[3]) # from hh:mm to min
        self.endStn = str(attrs[4])
        self.endTime = hhmm2mins(attrs[5]) # # from hh:mm to min
        self.dir = str(attrs[6]) # up or down (up means towards MKPR)
        self.servDur = int(attrs[7]) # minutes
        try:
            self.stepbackTrainNum = int(attrs[9])
        except ValueError:
            self.stepbackTrainNum = attrs[9] 
        self.servAdded = False # not added YET into any duty
        self.breakDur = 0 # in int minutes
        self.tripDur = 0 # in int minutes

def log(msg):
    print(f"[{get_kolkata_time()}] {msg}", flush = True)

def get_kolkata_time():
    return datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H-%M-%S")

def min2hhmm(mins):
    """ changes the time from minutes to hh:mm
        gives hh:mm string and takes integer minutes 0 to 1440"""
    if True:
        h = mins//60
        mins = mins - (h*60)
        if len(str(h)) == 1: h = "0" + str(h)
        if len(str(mins)) == 1: mins = "0" + str(mins)
        return str(h) + ":" + str(mins)

def hhmm2mins(hhmm):
    """ changes the time from hh:mm to minutes
        take hh:mm string and gives integers minutes 0 to 1440"""
    if True:
        hrs = hhmm[:2]
        min = hhmm[-2:]
        mins = int(hrs)*60 + int(min)
        return mins

def fetchData(data = inputFileLocation):
    """take the file generated from pre-processing as input and read the data
       and store it as a object for further processing"""
    servicesLst = []
    tempService = []
    with open(data, "r") as output:
        reader = csv.reader(output)
        for i,row in enumerate(reader):
           if i == 0: continue # ignore header
           tempService.append(row)
        # # 4th and 6th (starting from 1st) need to go from hh:mm to mins
        for i in range(0, len(tempService)):
            temp = (Services(tempService[i])) # create Service object with Service number and a list of its attributes
            toAppendTF = temp.trainNum in range(301,311) # for debugging..
            toAppendTF = True # comment this for selective appending (for debugging, etc..)
            if toAppendTF: servicesLst.append(temp) # a list of all Services
    return servicesLst


def canAppend2(lst, service2, services):
    #THESE LINES EXPLICITLY CHECKS FOR TRAIN 324 AND 353 AND 398 AND 399 DUT TO TIMETALBE AND OCC REQUIREMENTS ELSE ITS NOT REQUIRED

    # if( (lst[-1].stepbackTrainNum == 324 and lst[-1].endStn == 'DW DN' and service2.trainNum == 324 and service2.endStn == 'NFD') or (lst[-1].stepbackTrainNum == 353 and lst[-1].endStn == 'DW DN' and service2.trainNum == 353 and service2.endStn == 'NFD') ):
    #     return False
    # elif (lst[-1].trainNum == 398 and lst[-1].endStn == 'YB DN' and not(service2.trainNum == 398 and service2.startStn == 'YB DN') ) or ( not(lst[-1].trainNum == 398 and lst[-1].endStn == 'YB DN') and service2.trainNum == 398 and service2.startStn == 'YB DN' ) or (lst[-1].trainNum == 399 and lst[-1].endStn == 'YB DN' and not(service2.trainNum == 399 and service2.startStn == 'YB DN') ) or ( not(lst[-1].trainNum == 399 and lst[-1].endStn == 'YB DN') and service2.trainNum == 399 and service2.startStn == 'YB DN'):
    #     return False
    # elif(lst[-1].trainNum == 398 and lst[-1].endStn == 'NECC' and not(service2.trainNum == 398 and service2.startStn == 'NECC') ) or ( not(lst[-1].trainNum == 398 and lst[-1].endStn == 'NECC') and service2.trainNum == 398 and service2.startStn == 'NECC') or (lst[-1].trainNum == 399 and lst[-1].endStn == 'NECC' and not(service2.trainNum == 399 and service2.startStn == 'NECC') ) or ( not(lst[-1].trainNum == 399 and lst[-1].endStn == 'NECC') and service2.trainNum == 399 and service2.startStn == 'NECC'):
    #     return False
    # elif( (lst[-1].trainNum == 398 and lst[-1].endStn == 'YB UP' and service2.trainNum == 398 and service2.startStn == 'YB UP') or (lst[-1].trainNum == 399 and lst[-1].endStn == 'YB UP' and service2.trainNum == 399 and service2.startStn == 'YB UP') ):
    #     return False
    # elif (lst[-1].trainNum == 398 and lst[-1].endStn == 'DW UP' and service2.trainNum == 398 and service2.startStn == 'DW UP') or (lst[-1].trainNum == 399 and lst[-1].endStn == 'DW UP' and service2.trainNum == 399 and service2.startStn == 'DW UP'):
    #     return False
    # elif(lst[-1].trainNum == 398 and lst[-1].endStn == 'DSTO' and not(service2.trainNum == 398 and service2.startStn == 'DSTO') ) or ( not(lst[-1].trainNum == 398 and lst[-1].endStn == 'DSTO') and service2.trainNum == 398 and service2.startStn == 'DSTO') or (lst[-1].trainNum == 399 and lst[-1].endStn == 'DSTO' and not(service2.trainNum == 399 and service2.startStn == 'DSTO') ) or ( not(lst[-1].trainNum == 399 and lst[-1].endStn == 'DSTO') and service2.trainNum == 399 and service2.startStn == 'DSTO'):
    #     return False
    # elif ((lst[-1].trainNum == 398 and lst[-1].endStn == 'DW DN' and service2.trainNum == 398 and service2.startStn == 'DW DN') or (lst[-1].trainNum == 399 and lst[-1].endStn == 'DW DN' and service2.trainNum == 399 and service2.startStn == 'DW DN') ):
    #     return False
    # elif(lst[-1].trainNum == 398 and lst[-1].endStn == 'DW UP' and not(service2.trainNum == 398 and service2.startStn == 'DW DN') ) or ( not(lst[-1].trainNum == 398 and lst[-1].endStn == 'DW UP') and service2.trainNum == 398 and service2.startStn == 'DW DN') or (lst[-1].trainNum == 399 and lst[-1].endStn == 'DW UP' and not(service2.trainNum == 399 and service2.startStn == 'DW DN') ) or ( not(lst[-1].trainNum == 399 and lst[-1].endStn == 'DW UP') and service2.trainNum == 399 and service2.startStn == 'DW DN'):
    #     return False
    # else:
        
        """this function checks whether a service can be append in the current duty
        or not and it also checks that the constraints should be followed"""
        startEndStnTF = lst[-1].endStn == service2.startStn # checks duty end station and serv start station
        startEndTimeTF = 0 <= (service2.startTime - lst[-1].endTime) <= 40
        startEndStnTFafterBreak = lst[-1].endStn[:2] == service2.startStn[:2] and (lst[-1].servNum not in stabling_services) and (service2.servNum not in induction_services)  #chechks only station, without cosidering direction
        # if (lst[-1].endStn == 'YB UP' and lst[-1].trainNum == 398) or (lst[-1].endStn == 'YB UP' and lst[-1].trainNum == 399):
        #         startEndTimeWithin = 65 <= (service2.startTime - lst[-1].endTime) <= 120
        # elif(lst[-1].endStn == 'DW DN' and lst[-1].trainNum == 398) or (lst[-1].endStn == 'DW DN' and lst[-1].trainNum == 399):
        #     startEndTimeWithin = 80 <= (service2.startTime - lst[-1].endTime) <= 120
        # else:
        startEndTimeWithin = short_break <= (service2.startTime - lst[-1].endTime) <= 150
        #startEndStnTFafterBreak = newDuty.dutyEndStn[:4] == service.startStn[:4] #chechks only station, without cosidering direction
        if lst[-1].stepbackTrainNum == "No StepBack":
            startEndRakeTF = int(lst[-1].trainNum) == int(service2.trainNum) # checks if same rake or not
        else:
            startEndRakeTF = int(lst[-1].stepbackTrainNum) == int(service2.trainNum)


        contTimeDur = 0
        timeDur = 0
        if startEndRakeTF:
            if startEndStnTF and startEndTimeTF:
                return True
                timeDur = service2.endTime - lst[0].startTime  #Duty HRS
                trainNum = service2.trainNum
                for service in reversed(lst):
                    if service.stepbackTrainNum == "No StepBack":
                        if service.trainNum == trainNum:
                            trainNum = service.trainNum
                            contTimeDur = service2.endTime - service.startTime
                    elif int(service.stepbackTrainNum) == trainNum:
                        trainNum = service.trainNum
                        contTimeDur = service2.endTime - service.startTime
                    else:
                        break
                    # for service in lst:
                    #     if (service.trainNum == service2.trainNum):

                    #         contTimeDur = service2.endTime - service.startTime
                    #         break
                if contTimeDur <= Continuous_Driving_time and timeDur <= (Duty_hours - 25):
                    return True
                else: return False
            else: return False

        elif startEndTimeWithin and lst[-1].endStn in crewControl and service2.startStn in crewControl:
            if startEndStnTFafterBreak:
                return True
            else: return False

        else: return False


def allotService(services, start , result):
    global count
    global can_append_dict

    """this function take the list of services as input and start making all the
       possible combinations of duties, after a duty set is made it will only print that
       duty which follows all the constraints"""
    #output = []

    if start == len(services):
        if result:
            if (result[-1].servNum in invalid_signoff_services):
                return
            if not (" " in result[-1].endStn or result[-1].endStn in step_back_location or result[-1].endStn in other_outstations or result[-1].endStn in outstations[0]):
                return
            if (result[0].startStn in cc1 and result[-1].endStn in cc1) or (result[0].startStn in cc2 and result[-1].endStn in cc2):
            # output.append(result)
                BreakDur = []
                tripsDur = []
                breakInSameJur,morningDriveDur,firstBreak = False,False,False
                for i in range(len(result)-1):
                    if (result[i+1].startTime - result[i].endTime) >=short_break and result[i+1].startStn in crewControl:
                        trip_time = (result[i].endTime - result[0].startTime-sum(tripsDur) - sum(BreakDur))
                        if trip_time <= Continuous_Driving_time:
                            tripsDur.append(trip_time)
                        else:
                            return
                        BreakDur.append(result[i+1].startTime - result[i].endTime)
                        if not firstBreak:
                            firstBreak = True
                            if (result[i].endTime - result[0].startTime) >= 30:
                                morningDriveDur = True
                            else:
                                return
                        if ((result[0].startStn in cc1 and result[i].endStn in cc1) or (result[0].startStn in cc2 and result[i].endStn in cc2)) and not breakInSameJur:
                            breakInSameJur = True
                if not breakInSameJur:
                    return
                tripsDur.append(result[-1].endTime - result[0].startTime - sum(BreakDur) - sum(tripsDur))

                if tripsDur[-1] > Continuous_Driving_time:
                    return
                
                if len(BreakDur) >= 3:
                    if BreakDur[0] >= long_break or BreakDur[1] >= long_break:
                        pass
                    else:
                        return


                longBreak = False
                for brake in BreakDur:
                    if brake >= long_break:
                        longBreak = True
                if not longBreak:
                    return
                

                
                # for i in range(len(tripsDur)-1):
                #     if tripsDur[i] >= 120 :
                #         if BreakDur[i] >= long_break:
                #              break
                #         else:
                #             return
                

                

                #----------Logic to find out first break >=30 but <50 mins, and test its justification with the current service duration > 135 min---
                # finding the first long break
                # for i in range(len(BreakDur)):
                #     if (40 <= BreakDur[i]):
                #         end_serv_index_long = i
                #         if i == 0:
                #             initial_serv_index_long = i
                #         else:
                #             initial_serv_index_long = i
                #             for j in range(i-1,-1,-1):
                #                 if (result[j].trainNum == result[j+1].trainNum or result[j].stepbackTrainNum == result[j+1].trainNum) and (result[j+1].startTime - result[j].endTime <= 15):
                #                     initial_serv_index_long = j
                #                 else: break
                #         break
                # # Check if end_serv_index_long was set; if not, return
                # if 'end_serv_index_long' not in locals():
                #     return
                # required_service_duration_long = result[end_serv_index_long].endTime - result[initial_serv_index_long].startTime
                

                # # finding the first short break
                # for i in range(len(BreakDur)):
                #     if (30 <= BreakDur[i] < 40):
                #         end_serv_index_short = i
                #         if i == 0:
                #             initial_serv_index_short = i
                #         else:
                #             initial_serv_index_short = i
                #             for j in range(i-1,-1,-1):
                #                 if (result[j].trainNum == result[j+1].trainNum or result[j].stepbackTrainNum == result[j+1].trainNum) and (result[j+1].startTime - result[j].endTime <= 15):
                #                     initial_serv_index_short = j
                #                 else: break
                #         break
                # # Check if end_serv_index_long was set; if not, return

                # if 'end_serv_index_short' in locals():    
                
                #     #---conditions for justification of long break-----
                    
                #     required_service_duration_short = result[end_serv_index_short].endTime - result[initial_serv_index_short].startTime
                    
                #     if required_service_duration_long < 120 and required_service_duration_short < 120:
                #         Justified_LongBreak = True
                #     elif required_service_duration_long >= 120 and required_service_duration_short >= 120:
                #         if end_serv_index_long < end_serv_index_short:
                #             Justified_LongBreak = True
                #         else: Justified_LongBreak = False
                #     elif required_service_duration_long >= 120:
                #         Justified_LongBreak = True

                #     else: Justified_LongBreak = False


                #     #----if first break is given just after inducion from NFD to DW. It is considered false-------
                #     if end_serv_index_long < end_serv_index_short:
                #         if required_service_duration_long <= 30:
                #             Justified_LongBreak = False
                #     else:
                #         if required_service_duration_short <= 30:
                #             Justified_LongBreak = False
                # else:
                #     if required_service_duration_long <= 30:
                #         Justified_LongBreak = False
                #     else:
                #         Justified_LongBreak = True

                    


                #-----------------------------------------------------------------------------------------------------
                    
                dutyDur = (result[-1].endTime - result[0].startTime)
                if (result[0].servNum in induction_services) and (result[-1].servNum in stabling_services): # if duty starts before 6:15 or ends after 11:30
                    dutyDurTF = dutyDur <= (Duty_hours - 45)
                    s_on_time = result[0].startTime - 25
                    s_off_time = result[-1].endTime + 20
                elif (result[0].servNum in induction_services) and (result[-1].servNum not in stabling_services):
                    dutyDurTF = dutyDur <= (Duty_hours - 35)
                    s_on_time = result[0].startTime - 25
                    s_off_time = result[-1].endTime + 10
                elif (result[0].servNum not in induction_services) and (result[-1].servNum in stabling_services):
                    dutyDurTF = dutyDur <= (Duty_hours - 35)
                    s_on_time = result[0].startTime - 15
                    s_off_time = result[-1].endTime + 20
                elif (result[0].servNum not in induction_services) and (result[-1].servNum not in stabling_services):
                    dutyDurTF = dutyDur <= (Duty_hours - 25)
                    s_on_time = result[0].startTime - 15
                    s_off_time = result[-1].endTime + 10
                else:
                    dutyDurTF = dutyDur <= (Duty_hours - 25)
                    s_on_time = result[0].startTime - 15
                    s_off_time = result[-1].endTime + 10
                    print("There is some error in dutyDurTF\n", result[0].servNum,'\n', result[-1].servNum)
                
                if not dutyDurTF:
                    return


                drivingDur = (result[-1].endTime - result[0].startTime - sum(BreakDur))
                # if 1410 <= s_off_time:
                #     drivingDurTF = drivingDur <= (Driving_duration )
                # elif s_on_time <= 360:
                #     drivingDurTF = drivingDur <= (Driving_duration )
                # else:
                drivingDurTF = drivingDur <= Driving_duration

                if not drivingDurTF:
                    return
                

                # if drivingDur <= 180:
                #     totalBreakDur = long_break <= sum(BreakDur) <= 120
                # else: totalBreakDur = (long_break + short_break) <= sum(BreakDur) <= 120
                # if not totalBreakDur:
                #     return
                

                if len(BreakDur) == 1:
                    totalBreakDur = long_break <= sum(BreakDur) <= 120
                else: totalBreakDur = (short_break + long_break) <= sum(BreakDur) <= 120
                if not totalBreakDur:
                    return

                #dutyDurTF = result[-1].endTime - result[0].startTime
                # if dutyDur <= 150:
                #     longBreak = True #If duty hours les than 2 1/2 hrs, no requirement of break
                #if (dutyDur <= 120 or (120 < dutyDur <= 300 and totalBreakDur >= 35) or (dutyDur >= 300 and totalBreakDur >= 50)) and totalBreakDur <= 60:
                if (
                    breakInSameJur and 
                    dutyDurTF and 
                    morningDriveDur and 
                    drivingDurTF and 
                    longBreak and 
                    totalBreakDur
                    ):
                    #output.append(result[::])
                    tempOutput = []
                    global output
                    for i in result:
                        tempOutput.append(i.servNum)
                    # with open(tempoutput_file, 'a', newline= '') as f:
                        # writer = csv.writer(f)
                        # writer.writerow(tempOutput)
                    output.append(tempOutput)
                    
                    
                    
                    return
                    #print()
                return
            return
        return

    #services.sort(key=lambda serv: serv.startTime)
    if not result:
        if ( services[start].servNum in invalid_initial_services):
            log(f"{services[start].servNum} service is done. Now finding next. count = {count}")
            if count >= count_diff:
                sys.exit()
            count += 1
        elif not (" " in services[start].startStn or services[start].startStn in step_back_location or services[start].startStn in other_outstations or services[start].startStn in outstations[0]):
            log(f"{services[start].servNum} service is done. Now finding next. count = {count}")
            if count >= count_diff:
                sys.exit()
            count += 1
        else:
            result.append(services[start])
            #print(services[start])
            # if result[0].startTime <= 1200: # for all signon before 19:00
            allotService(services,start+1,result)
            log(f"{result[0].servNum} service is done. Now finding next. count = {count}")

            if count :#% 5 == 0 and count != 0:
                with open(tempoutput_file, 'a', newline= '') as f:
                    writer = csv.writer(f)
                    for row in output:
                        writer.writerow(row)
                output = []
            if count >= count_diff:
                sys.exit()
            
            count += 1
            result.pop()
            # else: result.pop()

    else:
        if (services[start].endTime - result[0].startTime) >= (Duty_hours + 60 - 25): #515 = 480(8hrs) - 25(10S/on+15S/off) + 60(extra margin for .endTime)
            start = len(services) - 1

        elif ((services[start].startTime - result[-1].endTime) <= 120):
            if services[start] in can_append_dict.get(result[-1], []):
                if len(result) <= 12:
                    result.append(services[start])
                    allotService(services, start + 1, result)
                    result.pop()
                else:
                    start = len(services) - 1
        else: start = len(services) - 1

    allotService(services,start+1,result)

    return


servicesLstOrig = fetchData()
servicesLstOrig.sort(key=lambda serv: serv.startTime)
result = []
initial_start = args.initial_start
final_end = args.final_end
count_diff = final_end - initial_start
# read Mainloops.csv into a pandas DataFrame
# read outstation.csv using csv.reader

outstation_path = os.path.join(home_path, f"{new_location}/USEFUL OUTPUT_{member_id}/Outstations.csv")
try:
    with open(outstation_path, newline='') as f:
        reader = csv.reader(f)
        outstations = [row for row in reader]
    # print(f"Read Outstations.csv with {len(outstations)} rows")
except Exception as e:
    # print(f"Failed to read {outstation_path}: {e}")
    outstations = []

l1, l2, l3, l4 = find_specific_services(inputFileLocation, outstation_path)
induction_services = l1
stabling_services = l2
invalid_initial_services = l3
invalid_signoff_services = l4

tempoutput_file = home_path + f"/{new_location}/USEFUL OUTPUT_{member_id}/TEMP_OUTPUT_FILES/temp_output_new_{initial_start}_{final_end}.csv"
open(tempoutput_file, 'w').close()

print("Building the services graph dictionary....")
can_append_dict = {}
for numi, i in enumerate(servicesLstOrig):
    can_append_dict[i] = []
    for numj, j in enumerate(servicesLstOrig):
        if numj > numi and canAppend2([i], j, servicesLstOrig):
            can_append_dict[i].append(j)

print("Finished building the services graph dictionary.")

allotService(servicesLstOrig, initial_start, result)  # change start value for
