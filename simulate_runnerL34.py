

import subprocess
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def main():

    import sys
    import json
    from helpers import update_status
    print(f"simulate_runner.py started!")
    print(f"Received args: {sys.argv}")
    # CLI args: python3 simulate_runner.py <execution_id> <file_path> <stepping_back_json>
    execution_id = sys.argv[1]
    file_path = sys.argv[2]
    print('FILE PATH==',file_path)
    stepping_back_raw = sys.argv[3]  # Passed as JSON string
    timetable_type = sys.argv[4]

    # Try loading the JSON safely
    default_stepping_back = [
        {"station": "SBC1", "start": "08:00", "end": "10:00"},
        {"station": "SBC2", "start": "09:00", "end": "11:00"},
        {"station": "SBC3", "start": "17:00", "end": "19:00"},
    ]

    # Parse user input safely
    try:
        user_stepping_back = json.loads(stepping_back_raw)
    except Exception as e:
        print("⚠️ Invalid stepping_back data, defaulting to empty list.")
        print("Error detail:", e)
        user_stepping_back = []

    # Merge user input with defaults
    stepping_back_merged = []
    for default in default_stepping_back:
        # Check if user provided this station
        user_entry = next((u for u in user_stepping_back if u.get("station") == default["station"]), None)
        if user_entry:
            # Merge user values with defaults
            stepping_back_merged.append({
                "station": default["station"],
                "start": user_entry.get("start", default["start"]),
                "end": user_entry.get("end", default["end"]),
            })
        else:
            # Use default if user didn't provide
            stepping_back_merged.append(default)


    # Helper function to safely parse time
    def safe_parse_time(time_str, fallback_hour=None, fallback_minute=None):
        try:
            parts = str(time_str).strip().split(":")
            if len(parts) == 1:
                hour = int(parts[0])
                minute = 0
            else:
                hour = int(parts[0])
                minute = int(parts[1])
            hour = max(0, min(23, hour))
            minute = max(0, min(59, minute))
            return hour, minute
        except Exception as e:
            print(f"⚠️ Failed to parse time '{time_str}':", e)
            hour = fallback_hour if fallback_hour is not None else random.randint(0, 23)
            minute = fallback_minute if fallback_minute is not None else random.randint(0, 59)
            return hour, minute


    # Process merged list and set globals
    stepping_back_saved = []

    for entry in stepping_back_merged:
        station_name = entry["station"].strip()

        start_hour, start_minute = safe_parse_time(entry.get("start", "00:00"))
        end_hour, end_minute = safe_parse_time(entry.get("end", "23:59"))

        stepping_back_saved.append({
            "station": station_name,
            "start": f"{start_hour:02}:{start_minute:02}",
            "end": f"{end_hour:02}:{end_minute:02}",
        })

        # Set globals
        globals()[f"{station_name}startHour"] = int(start_hour)
        globals()[f"{station_name}startMinute"] = int(start_minute)
        globals()[f"{station_name}endHour"] = int(end_hour)
        globals()[f"{station_name}endMinute"] = int(end_minute)


    # Debug output
    print("\n=== Stepping Back Configurations ===")
    for entry in stepping_back_saved:
        station = entry["station"]
        start_hour = globals()[f"{station}startHour"]
        start_minute = globals()[f"{station}startMinute"]
        end_hour = globals()[f"{station}endHour"]
        end_minute = globals()[f"{station}endMinute"]

        print(f"{station}: {start_hour:02}:{start_minute:02} -> {end_hour:02}:{end_minute:02}")
        print(f"  ├─ {station}startHour ({type(start_hour).__name__}) = {start_hour}")
        print(f"  ├─ {station}startMinute ({type(start_minute).__name__}) = {start_minute}")
        print(f"  ├─ {station}endHour ({type(end_hour).__name__}) = {end_hour}")
        print(f"  └─ {station}endMinute ({type(end_minute).__name__}) = {end_minute}")
        print("------------------------------------") 
        
            
    try:
        print('-------------INSIDE CODE--------------')
        print(f"SBC1endHour -- {SBC1endHour}")
        print(f"SBC1startHour -- {SBC1startHour}")
        print(f"SBC2endMinute -- {SBC2endMinute}")
        print(f"SBC1endMinute -- {SBC1endMinute}")
        print("------------------------------------")         
        import csv
        import math
        import copy
        import matplotlib.pyplot as plt
        import sys
        import time
        import matplotlib
        import matplotlib.pyplot as plt
        # import plotly.express as px
        # import plotly.graph_objects as go
        import matplotlib.dates as mdates
        import argparse
        import pandas as pd
        import numpy as np
        import datetime
        import random
        import warnings
        warnings.filterwarnings('ignore')
        warnings.simplefilter(action='ignore',category=FutureWarning)
        update_status(execution_id, f"Save your UID for future ref - {execution_id}","WIP")
        time.sleep(2)
        update_status(execution_id, "Pre-Processing Time Table","WIP")
        df1 = pd.read_csv(file_path, index_col=0,header=None)
        df1.columns = df1.iloc[0]
        ids = df1.loc['TRAIN NO'].unique()
        ids = [i for i in ids if str(i) != 'nan' ]
        print(f"NO. of Trains: {len(ids)}")
        print(ids)
        df1.drop('TRAIN NO',axis=0,inplace=True)
        rail = {}
        for i in range(len(ids)):
            rail[i] = df1.filter(like=ids[i])
            rail[i] = rail[i].reset_index()
            rail[i].rename(columns={0:'TRAIN NO'},inplace=True)
            rail[i] = pd.melt(rail[i],id_vars='TRAIN NO',value_name='TIME',var_name='trainId')
            rail[i].drop(columns='trainId',inplace=True)
            rail[i].rename(columns={'TRAIN NO': 'CheckPoints'},inplace=True)
            rail[i].set_index('CheckPoints',inplace=True)
            rail[i].dropna(inplace=True)
            rail[i]['TIME'] = pd.to_datetime(rail[i]['TIME'],infer_datetime_format=True,errors = 'coerce')
            rail[i]['TIME'] += pd.to_timedelta((rail[i]['TIME'].diff() < pd.Timedelta(0)).cumsum(), unit='d')

        for i in rail:
            rail[i].dropna(inplace=True)
            
            for j in range(rail[i].shape[0]):
                if rail[i].iloc[j,0] < rail[i].iloc[0,0]: #time less than induction time 
                    rail[i].iloc[j,0] = rail[i].iloc[j,0] + pd.to_timedelta('1 day')

            if (rail[i]['TIME'].diff() < pd.Timedelta(0)).any():
                bool_series = rail[i]['TIME'].diff() < pd.Timedelta(0)
                print(f"Check Train ID: {ids[i]}, Location: {rail[i].loc[bool_series].index[0]}, Time: {rail[i].loc[bool_series].iloc[0,0].time()}\n") 
                step_name = f"Issue in Train {ids[i]}"
                message = f"Location: {rail[i].loc[bool_series].index[0]}, Time: {rail[i].loc[bool_series].iloc[0,0].time()}"
                update_status(execution_id, step_name, "error", message)
        #My Edited
        # SBC1 DSTO # StepBack Timimng at DSTO 7:45 to 22:00
        # SBC2 VASI # StepBack Timimng at VASI 7:00 to 22:00
        # SBC3 NECC  # StepBack Timimng at NECC 7:15 to 22:00

        def departure():
            for a in range(j+1):
                print('DATA DETAILS--j--a--index',j,a,rail[x].index[a])
                if (rail[x].index[a] not in {'YBDN','YBUP','DWDN','DWUP','SBC1','SBC2','SBC3'}) & (a == 0):
                    route.update({'INDUCTION' : rail[x].index[a],'INDUCTION-TIME' : rail[x].iloc[a, 0],'INDUCTION-VIA' :rail[x].index[a+1],'SERVICE-TIME' : rail[x].iloc[a+1, 0]})
                    continue
                if a ==rail[x].shape[0] - 1:
                    route.update({'STABLING' : rail[x].index[a],'STABLING-TIME' : rail[x].iloc[a, 0], 'STABLING-VIA' : rail[x].index[a-1]})
                    continue
                    
                if rail[x].index[a] == 'SBC1' and rail[x].index[a+1] != 'SBC1':
                    route.update({'DSTO-DN': rail[x].iloc[a, 0]})
                    continue
                if rail[x].index[a] in (['SBC2']) and rail[x].index[a+1] in (['SBC2']):
                    route.update({'VASI-DN': rail[x].iloc[a, 0]})
                    continue
                if rail[x].index[a] in (['SBC3']) and rail[x].index[a+1] in (['SBC3']):
                    route.update({'NECC-DN': rail[x].iloc[a, 0]})
                    continue
                if rail[x].index[a] == 'YBDN':
                    route.update({'YB-DN': rail[x].iloc[a, 0]})
                    continue
                if rail[x].index[a] == 'DWDN':
                    route.update({'DW-DN': rail[x].iloc[a, 0]})
                    continue
                if rail[x].index[a] == 'DWUP':
                    route.update({'DW-UP': rail[x].iloc[a, 0]})
                    continue
                if rail[x].index[a] == 'YBUP':
                    route.update({'YB-UP': rail[x].iloc[a, 0]})
                    continue
                if rail[x].index[a] in (['SBC1']) and rail[x].index[a+1] in (['SBC1']):
                    route.update({'DSTO-UP': rail[x].iloc[a, 0]})
                    continue
                if rail[x].index[a] in (['SBC2']) and rail[x].index[a+1] not in (['SBC2']):
                    route.update({'VASI-UP': rail[x].iloc[a, 0]})
                    continue
                if rail[x].index[a] in (['SBC3']) and rail[x].index[a+1] not in (['SBC3']):
                    route.update({'NECC-UP': rail[x].iloc[a, 0]})
                    continue
                # if rail[x].index[a] == 'NBAA UP':
                #     route.update({'NBAA-UP': rail[x].iloc[a, 0]})
                #     continue
                

        k = 0
        duty2 = pd.DataFrame()
        departure_chart = pd.DataFrame()
        trips = pd.DataFrame(columns=['Train_No', 'LocationPick', 'Trip_Start', 'LocationRelieve', 'Trip_End', 'Trip_Duration'])
        trips['Trip_Start'] = pd.to_datetime(trips['Trip_Start'])
        trips['Trip_End'] = pd.to_datetime(trips['Trip_End'])
        trips['Trip_Duration'] = pd.to_datetime(trips['Trip_Duration'])
        trips['Train_No'] = pd.to_numeric(trips['Train_No']).astype(int)
        while True:
            countnum = 0
            alldone = 0
            for checksize in rail.keys():
                if rail[checksize].size == 0:
                    countnum = countnum + 1
                if countnum == len(ids):
                    print('All Done')
                    alldone = 1
                    break
            if alldone == 1:
                break
            temp = []
            for dum in rail.keys():
                if rail[dum].size != 0:
                    temp.append(rail[dum].iloc[0, 0])
            temp1 = sorted(temp)
            route = {} 
            for item in temp1:
                for x in rail.keys():
                    if rail[x].size != 0:
                        if rail[x].iloc[0, 0] == item:
                            break
                        else:
                            continue
                    
                if rail[x].size != 0:
                    print('Checking for :-', ids[x])
                    print('From', rail[x].iloc[0])
        #             departure_chart = departure_chart.append(route,ignore_index=True)
                    i = 0
                    j = 0
        #             if rail[x].index[i] not in {'CCDN','CCUP','SBC1','SBC2'}:
        #                 route.update({'INDUCTION' : rail[x].index[i],'INDUCTION-TIME' : rail[x].iloc[i, 0] })
        #                 departure()
                    
                    ###STEP-BACK FOR SBC1###
                    #SBC1
                    if (rail[x].index[i] == 'SBC1'):
                        while ((rail[x].iloc[j, 0] - rail[x].iloc[i, 0]) <= datetime.timedelta(hours=2, minutes=30)) & (
                            j < (rail[x].shape[0] - 1)):
                            
        #                     #SBC1 > CCDN > CCUP
        #                     if (rail[x].index[j] == 'CCDN') & (j != i) & (rail[x].index[j + 1] == 'CCUP'):
        #                         print('SBC1-CCDN>CCUP',rail[x].index[j])
        # #                         rail[x].reset_index(inplace=True)
        # #                         rail[x].set_index('CheckPoints', inplace=True)
        #                         data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
        #                                 'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
        #                                 'Trip_Duration': rail[x].iloc[j+1, 0] - rail[x].iloc[i, 0]}
        #                         departure()
        #                         data.update(route)
        #                         trips = trips.append(data, ignore_index=True)
        #                         rail[x].iloc[j+1,0] = rail[x].iloc[j,0] + datetime.timedelta(seconds=1)
        #                         del data
        #                         rail[x].reset_index(inplace=True)
        #                         rail[x].drop(rail[x].index[i:j + 1], inplace=True)
        #                         rail[x].set_index('CheckPoints', inplace=True)
        #                         j = i = 0
        #                         break
                            
                            #SBC1 > DWUP | DWDN
                            if (rail[x].index[j] == 'DWUP') | (rail[x].index[j] == 'DWDN') | (j == (rail[x].shape[0] - 1)):
                                print('-------------------------------------------------SBC1-CCDN-OR-CCUP',rail[x].index[j])
                                data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                        'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                        'Trip_Duration': rail[x].iloc[j, 0] - rail[x].iloc[i, 0]}
                                departure()
                                data.update(route)
                                trips = trips.append(data, ignore_index=True)
                                del data
                                rail[x].reset_index(inplace=True)
                                rail[x].drop(rail[x].index[i:j], inplace=True)
                                rail[x].set_index('CheckPoints', inplace=True)
                                j = 0
                                break
                            j = j + 1
                            
                    ###STEP-BACK FOR SBC2###
                    #SBC2
                    if (rail[x].index[i] == 'SBC2'):
                        while ((rail[x].iloc[j, 0] - rail[x].iloc[i, 0]) <= datetime.timedelta(hours=2, minutes=35)) & ((j < (rail[x].shape[0] - 1))):
                            
                            #SBC2 > CCUP | CCDN
                            if ((rail[x].index[j] == 'YBUP') | (rail[x].index[j] == 'YBDN')) :
                                data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                        'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                        'Trip_Duration': rail[x].iloc[j, 0] - rail[x].iloc[i, 0]}
                                departure()
                                data.update(route)
                                trips = trips.append(data, ignore_index=True)
                                del data
                                rail[x].reset_index(inplace=True)
                                rail[x].drop(rail[x].index[i:j], inplace=True)
                                rail[x].set_index('CheckPoints', inplace=True)
                                j = 0
                                break
                            j = j + 1

                    
                    ###STEP-BACK FOR SBC2###
                    #SBC3
                    if (rail[x].index[i] == 'SBC3'):
                        while ((rail[x].iloc[j, 0] - rail[x].iloc[i, 0]) <= datetime.timedelta(hours=2, minutes=35)) & ((j < (rail[x].shape[0] - 1))):
                            
                            #SBC2 > CCUP | CCDN
                            if ((rail[x].index[j] == 'YBUP') | (rail[x].index[j] == 'YBDN')) :
                                data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                        'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                        'Trip_Duration': rail[x].iloc[j, 0] - rail[x].iloc[i, 0]}
                                departure()
                                data.update(route)
                                trips = trips.append(data, ignore_index=True)
                                del data
                                rail[x].reset_index(inplace=True)
                                rail[x].drop(rail[x].index[i:j], inplace=True)
                                rail[x].set_index('CheckPoints', inplace=True)
                                j = 0
                                break
                            j = j + 1

                    
                    route = {}
                    while ((rail[x].iloc[j, 0] - rail[x].iloc[i, 0]) <= datetime.timedelta(hours=2, minutes=25)) & (
                            j < (rail[x].shape[0] - 1)):
                        
                        # StepBack Timimng at DSTO 7:45 to 22:00
                        #SBC1 > SBC1
                        if (rail[x].index[j] == 'SBC1') & (rail[x].index[j + 1] == 'SBC1') & (rail[x].iloc[j, 0].hour >= SBC1startHour) & (
                            rail[x].iloc[j, 0].hour < SBC1endHour) & ((rail[x].iloc[j, 0].minute >= SBC1startMinute if (rail[x].iloc[j, 0].hour == SBC1startHour) else True)) & (
                            ids[x] not in ['399','398']):
                            data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                    'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                    'Trip_Duration': rail[x].iloc[j, 0] - rail[x].iloc[i, 0]}
                            departure()
                            data.update(route)
                            trips = trips.append(data, ignore_index=True)
                            del data
                            rail[x].reset_index(inplace=True)
                            rail[x].drop(rail[x].index[i:j + 1], inplace=True)
                            rail[x].set_index('CheckPoints', inplace=True)
                            j = 0
                            break

                        # StepBack Timimng at VASI 7:00 to 22:00
                        #SBC2 > SBC2
                        if (rail[x].index[j] == 'SBC2') & (rail[x].index[j + 1] == 'SBC2') & ((rail[x].iloc[j, 0].hour >= SBC2startHour)) & (
                            (rail[x].iloc[j, 0].minute >= SBC2startMinute if (rail[x].iloc[j, 0].hour == SBC2startHour) else True)) & (
                            rail[x].iloc[j, 0].hour < SBC2endHour) & (ids[x] not in ['399','398']):
                            data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                    'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                    'Trip_Duration': rail[x].iloc[j, 0] - rail[x].iloc[i, 0]}
                            departure()
                            data.update(route)
                            trips = trips.append(data, ignore_index=True)
                            del data
                            rail[x].reset_index(inplace=True)
                            rail[x].drop(rail[x].index[i:j + 1], inplace=True)
                            rail[x].set_index('CheckPoints', inplace=True)
                            j = 0
                            break

                        # StepBack Timimng at NECC 7:15 to 22:00
                        #SBC3 > SBC3
                        if (rail[x].index[j] == 'SBC3') & (rail[x].index[j + 1] == 'SBC3') & ((rail[x].iloc[j, 0].hour >= SBC3startHour)) & (
                            (rail[x].iloc[j, 0].minute >= SBC3startMinute if (rail[x].iloc[j, 0].hour == SBC3startHour) else True)) & (
                            rail[x].iloc[j, 0].hour < SBC3endHour) & (ids[x] not in ['399','398']):
                            data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                    'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                    'Trip_Duration': rail[x].iloc[j, 0] - rail[x].iloc[i, 0]}
                            departure()
                            data.update(route)
                            trips = trips.append(data, ignore_index=True)
                            del data
                            rail[x].reset_index(inplace=True)
                            rail[x].drop(rail[x].index[i:j + 1], inplace=True)
                            rail[x].set_index('CheckPoints', inplace=True)
                            j = 0
                            break

                        # DWUP > DWDN
                        # I've added 'LocationRelieve': 'DWT' on 10july2025 , previously it was 'LocationRelieve': rail[x].index[j]
                        # Done so that we can give 40 min break since TO need to ensure TO's boarding
                        if (rail[x].index[j] == 'DWUP') & (j != i) & (rail[x].index[j + 1] == 'DWDN'):
                            data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                    'LocationRelieve': 'DWT', 'Trip_End': rail[x].iloc[j, 0],
                                    'Trip_Duration': rail[x].iloc[j+1, 0] - rail[x].iloc[i, 0]}
                            departure()
                            data.update(route)
                            trips = trips.append(data, ignore_index=True)
                            rail[x].iloc[j+1,0] = rail[x].iloc[j,0] + datetime.timedelta(seconds=1)
                            del data
                            rail[x].reset_index(inplace=True)
                            rail[x].drop(rail[x].index[i:j + 1], inplace=True)
                            rail[x].set_index('CheckPoints', inplace=True)
                            j = 0
                            break

                        # DWUP | DWDN
                        if ((rail[x].index[j] == 'DWUP') | (rail[x].index[j] == 'DWDN')) & (j != 0):
                            data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                    'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                    'Trip_Duration': rail[x].iloc[j, 0] - rail[x].iloc[i, 0]}
                            departure()
                            data.update(route)
                            trips = trips.append(data, ignore_index=True)
                            del data
                            rail[x].reset_index(inplace=True)
                            rail[x].drop(rail[x].index[i:j], inplace=True)
                            rail[x].set_index('CheckPoints', inplace=True)
                            j = 0
                            break

                        # YBUP | YBDN
                        if ((rail[x].index[j] == 'YBUP') | (rail[x].index[j] == 'YBDN')) & (j != 0):
                            data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                    'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                    'Trip_Duration': rail[x].iloc[j, 0] - rail[x].iloc[i, 0]}
                            departure()
                            data.update(route)
                            trips = trips.append(data, ignore_index=True)
                            del data
                            rail[x].reset_index(inplace=True)
                            rail[x].drop(rail[x].index[i:j], inplace=True)
                            rail[x].set_index('CheckPoints', inplace=True)
                            j = 0
                            break
                        j = j + 1 #within while loop
                        
                    if j == 0: #Outside while loop
                        break
                        
                    route = {}
                    if j == rail[x].shape[0] - 1: #Outside while loop
                        data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                'Trip_Duration': rail[x].iloc[j, 0] - rail[x].iloc[i, 0]}
                        departure()
                        data.update(route)
                        trips = trips.append(data, ignore_index=True)
                        del data
                        rail[x].reset_index(inplace=True)
                        rail[x].drop(rail[x].index, inplace=True)
                        departure_chart = departure_chart.append(route,ignore_index=True)
                        break

                    j = j - 1
                else:
                    print('ELSE STATEMENT')
                    break

        # Step Back trips integration at SBC1, SBC2. SBC3
        comptrip = pd.DataFrame(
            columns=['Train_No', 'LocationPick', 'Trip_Start', 'LocationRelieve', 'Trip_End', 'Trip_Duration'])
        dumtrips = trips.copy()
        dumtrips.sort_values(['Trip_Start'], inplace=True)
        dumtrips.reset_index(drop=True, inplace=True)

        while (dumtrips.size != 0):
            print('Total_Trips:', len(comptrip.index))
            comptrip = pd.DataFrame(columns=['Train_No', 'LocationPick', 'Trip_Start', 'LocationRelieve', 'Trip_End', 'Trip_Duration'])
            dumtrips = trips.copy()
            dumtrips.sort_values(['Trip_Start'], inplace=True)
            dumtrips.reset_index(drop=True, inplace=True)
            x = 0
            y = 0
            z = 0
            
            while x < len(dumtrips.index):
                print('Starting From:', dumtrips['Trip_Start'][x],dumtrips['Train_No'][x])
                trip = dumtrips.iloc[x].copy()
                trip['TrainSBC1'] = '0'
                trip['TrainSBC2'] = '0'
                trip['TrainSBC3'] = '0'
                dumtrips.drop(dumtrips.index[x], inplace=True)
                dumtrips.sort_values(['Trip_Start'], inplace=True)
                dumtrips.reset_index(drop=True, inplace=True)
                y = 0
                while y < len(dumtrips.index):
                    breaked = 0
                    ###Randomly Breaking Trips###
                    if ((
                            trip['Trip_Duration'] > datetime.timedelta(hours=0,minutes=1)) & (trip['LocationRelieve'] in ( 'DWDN','YBDN','DWUP','YBUP'))):
                        breaked = 1
                        break
                    if breaked == 1:
                        break

                    ass = 0

                    ###FOR CC INCOMING TRAIN###
                    # if ((dumtrips['Train_No'][y] == trip['Train_No']) | (dumtrips['Train_No'][y] == trip['TrainSBC1']) | (dumtrips['Train_No'][y] == trip['TrainSBC2']) | (
                    #         dumtrips['Train_No'][y] == trip['TrainSBC3'])) & (
                    #         dumtrips['Trip_Start'][y] == trip['Trip_End']) & (
                    #         dumtrips['Trip_End'][y] - trip['Trip_Start'] <= (datetime.timedelta(hours=2, minutes=30))) & (dumtrips['LocationPick'][y] == trip['LocationRelieve']):
                    #     trip['Trip_End'] = dumtrips['Trip_End'][y]
                    #     trip['Trip_Duration'] = dumtrips['Trip_End'][y] - trip['Trip_Start']
                    #     trip['LocationRelieve'] = dumtrips['LocationRelieve'][y]
                    #     dumtrips.drop(dumtrips.index[y], inplace=True)
                    #     dumtrips.sort_values(['Trip_Start'], inplace=True)
                    #     dumtrips.reset_index(drop=True, inplace=True)
                    #     ass = 1


                    if (len(dumtrips.index) == 0) | (y == len(dumtrips.index)):
                        break
                        
                    #Trips Joining at SBC1: DSTO
                    if (trip['LocationRelieve'] == 'SBC1') & (trip['TrainSBC1'] == '0') & (ass == 0):
                        z = 0
                        ass = 0
                        dumtrips.sort_values(['Trip_End'],ascending=True, inplace=True)
                        dumtrips.reset_index(drop=True, inplace=True)
                        while z < len(dumtrips.index):
                            if (dumtrips['Trip_Start'][z] - trip['Trip_End'] >= datetime.timedelta(minutes=2)) & (
                                    trip['Train_No'] != dumtrips['Train_No'][z]) & (dumtrips['LocationPick'][z] == 'SBC1') & (trip['Trip_Duration'] + dumtrips['Trip_Duration'][z] <= datetime.timedelta(hours=2,minutes=35) ):
                                print('DSTO-->',trip['Trip_End'],trip['Train_No'],'-=-',dumtrips['Train_No'][z],dumtrips['Trip_Start'][z])
                                trip['TrainSBC1'] = dumtrips['Train_No'][z]
                                trip['Trip_End'] = dumtrips['Trip_End'][z]
                                trip['Trip_Duration'] = dumtrips['Trip_End'][z] - trip['Trip_Start']
                                trip['LocationRelieve'] = dumtrips['LocationRelieve'][z]
                                
                                trip['INDUCTION'] = trip['INDUCTION'] if pd.isnull(dumtrips['INDUCTION'][z]) else dumtrips['INDUCTION'][z]
                                trip['INDUCTION-VIA'] = trip['INDUCTION-VIA'] if pd.isnull(dumtrips['INDUCTION-VIA'][z]) else dumtrips['INDUCTION-VIA'][z]
                                trip['SERVICE-TIME'] = trip['SERVICE-TIME'] if pd.isnull(dumtrips['SERVICE-TIME'][z]) else dumtrips['SERVICE-TIME'][z]
                                trip['INDUCTION-TIME'] = trip['INDUCTION-TIME'] if pd.isnull(dumtrips['INDUCTION-TIME'][z]) else dumtrips['INDUCTION-TIME'][z]
                                
                                trip['DW-DN'] = trip['DW-DN'] if pd.isnull(dumtrips['DW-DN'][z]) else dumtrips['DW-DN'][z]
                                trip['DW-UP'] = trip['DW-UP'] if  pd.isnull(dumtrips['DW-UP'][z]) else dumtrips['DWU-P'][z]
                                trip['YB-DN'] = trip['YB-DN'] if pd.isnull(dumtrips['YB-DN'][z]) else dumtrips['YB-DN'][z]
                                trip['YB-UP'] = trip['YB-UP'] if pd.isnull(dumtrips['YB-UP'][z]) else dumtrips['YB-UP'][z]
                                trip['DSTO-DN'] = trip['DSTO-DN'] if pd.isnull(dumtrips['DSTO-DN'][z]) else dumtrips['DSTO-DN'][z]
                                trip['DSTO-UP'] = trip['DSTO-UP'] if pd.isnull(dumtrips['DSTO-UP'][z]) else dumtrips['DSTO-UP'][z]
                                trip['VASI-DN'] = trip['VASI-DN'] if pd.isnull(dumtrips['VASI-DN'][z]) else dumtrips['VASI-DN'][z]
                                trip['VASI-UP'] = trip['VASI-UP'] if pd.isnull(dumtrips['VASI-UP'][z]) else dumtrips['VASI-UP'][z]
                                trip['NECC-UP'] = trip['NECC-UP'] if pd.isnull(dumtrips['NECC-UP'][z]) else dumtrips['NECC-UP'][z]
                                trip['NECC-DN'] = trip['NECC-DN'] if pd.isnull(dumtrips['NECC-DN'][z]) else dumtrips['NECC-DN'][z]

                                trip['STABLING'] = trip['STABLING'] if pd.isnull(dumtrips['STABLING'][z]) else dumtrips['STABLING'][z]
                                trip['STABLING-TIME'] = trip['STABLING-TIME'] if pd.isnull(dumtrips['STABLING-TIME'][z]) else dumtrips['STABLING-TIME'][z]
                                trip['STABLING-VIA'] = trip['STABLING-VIA'] if pd.isnull(dumtrips['STABLING-VIA'][z]) else dumtrips['STABLING-VIA'][z]


                                dumtrips.drop(dumtrips.index[z], inplace=True)
                                dumtrips.sort_values(['Trip_Start'], inplace=True)
                                dumtrips.reset_index(drop=True, inplace=True)
                                ass = 1
                                break
                            z = z + 1

                    #Trips Joining at SBC2: VASI
                    if (trip['LocationRelieve'] == 'SBC2') & (trip['TrainSBC2'] == '0') & (ass == 0) :
                        z = 0
                        ass = 0
                        dumtrips.sort_values(['Trip_Start'], inplace=True)
                        dumtrips.reset_index(drop=True, inplace=True)
                        while z < len(dumtrips.index):
                            if (dumtrips['Trip_Start'][z] - trip['Trip_End'] >= datetime.timedelta(minutes=2)) & (
                                    (dumtrips['Train_No'][z] != trip['Train_No']) & (
                                    dumtrips['Train_No'][z] != trip['TrainSBC1']) & (
                                    dumtrips['Train_No'][z] != trip['TrainSBC3'])) & (
                                    dumtrips['LocationPick'][z] == 'SBC2') :
                                print('VASI-->',trip['Trip_End'],trip['Train_No'],'-=-',dumtrips['Train_No'][z],dumtrips['Trip_Start'][z])
                                trip['TrainSBC2'] = dumtrips['Train_No'][z]
                                trip['Trip_End'] = dumtrips['Trip_End'][z]
                                trip['Trip_Duration'] = dumtrips['Trip_End'][z] - trip['Trip_Start']
                                trip['LocationRelieve'] = dumtrips['LocationRelieve'][z]

                                trip['INDUCTION'] = trip['INDUCTION'] if pd.isnull(dumtrips['INDUCTION'][z]) else dumtrips['INDUCTION'][z]
                                trip['INDUCTION-VIA'] = trip['INDUCTION-VIA'] if pd.isnull(dumtrips['INDUCTION-VIA'][z]) else dumtrips['INDUCTION-VIA'][z]
                                trip['SERVICE-TIME'] = trip['SERVICE-TIME'] if pd.isnull(dumtrips['SERVICE-TIME'][z]) else dumtrips['SERVICE-TIME'][z]
                                trip['INDUCTION-TIME'] = trip['INDUCTION-TIME'] if pd.isnull(dumtrips['INDUCTION-TIME'][z]) else dumtrips['INDUCTION-TIME'][z]
                                                        
                                trip['DW-DN'] = trip['DW-DN'] if pd.isnull(dumtrips['DW-DN'][z]) else dumtrips['DW-DN'][z]
                                trip['DW-UP'] = trip['DW-UP'] if  pd.isnull(dumtrips['DW-UP'][z]) else dumtrips['DW-UP'][z]
                                trip['YB-DN'] = trip['YB-DN'] if pd.isnull(dumtrips['YB-DN'][z]) else dumtrips['YB-DN'][z]
                                trip['YB-UP'] = trip['YB-UP'] if pd.isnull(dumtrips['YB-UP'][z]) else dumtrips['YB-UP'][z]
                                trip['DSTO-DN'] = trip['DSTO-DN'] if pd.isnull(dumtrips['DSTO-DN'][z]) else dumtrips['DSTO-DN'][z]
                                trip['DSTO-UP'] = trip['DSTO-UP'] if pd.isnull(dumtrips['DSTO-UP'][z]) else dumtrips['DSTO-UP'][z]
                                trip['VASI-DN'] = trip['VASI-DN'] if pd.isnull(dumtrips['VASI-DN'][z]) else dumtrips['VASI-DN'][z]
                                trip['VASI-UP'] = trip['VASI-UP'] if pd.isnull(dumtrips['VASI-UP'][z]) else dumtrips['VASI-UP'][z]
                                trip['NECC-UP'] = trip['NECC-UP'] if pd.isnull(dumtrips['NECC-UP'][z]) else dumtrips['NECC-UP'][z]
                                trip['NECC-DN'] = trip['NECC-DN'] if pd.isnull(dumtrips['NECC-DN'][z]) else dumtrips['NECC-DN'][z]

                                trip['STABLING'] = trip['STABLING'] if pd.isnull(dumtrips['STABLING'][z]) else dumtrips['STABLING'][z]
                                trip['STABLING-TIME'] = trip['STABLING-TIME'] if pd.isnull(dumtrips['STABLING-TIME'][z]) else dumtrips['STABLING-TIME'][z]
                                trip['STABLING-VIA'] = trip['STABLING-VIA'] if pd.isnull(dumtrips['STABLING-VIA'][z]) else dumtrips['STABLING-VIA'][z]

                                dumtrips.drop(dumtrips.index[z], inplace=True)
                                dumtrips.sort_values(['Trip_Start'], inplace=True)
                                dumtrips.reset_index(drop=True, inplace=True)
                                ass = 1
                                break
                            z = z + 1

                    #Trips Joining at SBC3: NECC
                    if (trip['LocationRelieve'] == 'SBC3') & (trip['TrainSBC3'] == '0') & (ass == 0) :
                        z = 0
                        ass = 0
                        dumtrips.sort_values(['Trip_Start'], inplace=True)
                        dumtrips.reset_index(drop=True, inplace=True)
                        while z < len(dumtrips.index):
                            if (dumtrips['Trip_Start'][z] - trip['Trip_End'] >= datetime.timedelta(minutes=2)) & (
                                (dumtrips['Train_No'][z] != trip['Train_No']) & (
                                dumtrips['Train_No'][z] != trip['TrainSBC1']) & (
                                dumtrips['Train_No'][z] != trip['TrainSBC2'])) & (dumtrips['LocationPick'][z] == 'SBC3'):
                                print('NECC-->',trip['Trip_End'],trip['Train_No'],'-=-',dumtrips['Train_No'][z],dumtrips['Trip_Start'][z])
                                trip['TrainSBC3'] = dumtrips['Train_No'][z]
                                trip['Trip_End'] = dumtrips['Trip_End'][z]
                                trip['Trip_Duration'] = dumtrips['Trip_End'][z] - trip['Trip_Start']
                                trip['LocationRelieve'] = dumtrips['LocationRelieve'][z]

                                trip['INDUCTION'] = trip['INDUCTION'] if pd.isnull(dumtrips['INDUCTION'][z]) else dumtrips['INDUCTION'][z]
                                trip['INDUCTION-VIA'] = trip['INDUCTION-VIA'] if pd.isnull(dumtrips['INDUCTION-VIA'][z]) else dumtrips['INDUCTION-VIA'][z]
                                trip['SERVICE-TIME'] = trip['SERVICE-TIME'] if pd.isnull(dumtrips['SERVICE-TIME'][z]) else dumtrips['SERVICE-TIME'][z]
                                trip['INDUCTION-TIME'] = trip['INDUCTION-TIME'] if pd.isnull(dumtrips['INDUCTION-TIME'][z]) else dumtrips['INDUCTION-TIME'][z]
                                
                                trip['DW-DN'] = trip['DW-DN'] if pd.isnull(dumtrips['DW-DN'][z]) else dumtrips['DW-DN'][z]
                                trip['DW-UP'] = trip['DW-UP'] if  pd.isnull(dumtrips['DW-UP'][z]) else dumtrips['DW-UP'][z]
                                trip['YB-DN'] = trip['YB-DN'] if pd.isnull(dumtrips['YB-DN'][z]) else dumtrips['YB-DN'][z]
                                trip['YB-UP'] = trip['YB-UP'] if pd.isnull(dumtrips['YB-UP'][z]) else dumtrips['YB-UP'][z]
                                trip['DSTO-DN'] = trip['DSTO-DN'] if pd.isnull(dumtrips['DSTO-DN'][z]) else dumtrips['DSTO-DN'][z]
                                trip['DSTO-UP'] = trip['DSTO-UP'] if pd.isnull(dumtrips['DSTO-UP'][z]) else dumtrips['DSTO-UP'][z]
                                trip['VASI-DN'] = trip['VASI-DN'] if pd.isnull(dumtrips['VASI-DN'][z]) else dumtrips['VASI-DN'][z]
                                trip['VASI-UP'] = trip['VASI-UP'] if pd.isnull(dumtrips['VASI-UP'][z]) else dumtrips['VASI-UP'][z]
                                trip['NECC-UP'] = trip['NECC-UP'] if pd.isnull(dumtrips['NECC-UP'][z]) else dumtrips['NECC-UP'][z]
                                trip['NECC-DN'] = trip['NECC-DN'] if pd.isnull(dumtrips['NECC-DN'][z]) else dumtrips['NECC-DN'][z]

                                trip['STABLING'] = trip['STABLING'] if pd.isnull(dumtrips['STABLING'][z]) else dumtrips['STABLING'][z]
                                trip['STABLING-TIME'] = trip['STABLING-TIME'] if pd.isnull(dumtrips['STABLING-TIME'][z]) else dumtrips['STABLING-TIME'][z]
                                trip['STABLING-VIA'] = trip['STABLING-VIA'] if pd.isnull(dumtrips['STABLING-VIA'][z]) else dumtrips['STABLING-VIA'][z]

                                dumtrips.drop(dumtrips.index[z], inplace=True)
                                dumtrips.sort_values(['Trip_Start'], inplace=True)
                                dumtrips.reset_index(drop=True, inplace=True)
                                ass = 1
                                break
                            z = z + 1

                    y = (y + 1) if ass == 0 else 0
                comptrip = comptrip.append(trip)
                dumtrips.sort_values(['Trip_Start'], inplace=True)
                dumtrips.reset_index(drop=True, inplace=True)
                x = 0
        #########################################################################################    
        print('The_End')
        print('Total_Trips:', len(comptrip.index))

        comptrip = comptrip.reindex(columns= ['Train_No', 'LocationPick', 'Trip_Start', 'LocationRelieve', 'Trip_End',
                                'Trip_Duration', 'TrainSBC1', 'TrainSBC2','TrainSBC3','INDUCTION','INDUCTION-TIME', 
                                    'INDUCTION-VIA','SERVICE-TIME', 'DSTO-DN', 'DSTO-UP', 'DW-DN', 'DW-UP',  'NECC-DN', 'NECC-UP', 'VASI-DN', 
                                    'VASI-UP', 'YB-DN', 'YB-UP','STABLING', 'STABLING-TIME', 'STABLING-VIA'])

        # comptrip.to_excel(r"comptrips-10-7-2025.xlsx")
        comptrip.reset_index(drop=True, inplace=True)
        YB_Jurisdiction = ['DYB','SDG-YB',  'YBSDG',  'SBC2', 'NESY', 'YBUP', 'YBDN', 'NSST/KSHI',  'SBC3', 'NECCSDG',  'VASIO/S']
        DW_Jurisdiction = ['NFD', 'KNR', 'DWDN','DWUP', 'DW3RD', 'JPW','DSTOSDG','SBC1','DWT']
        comptrip.to_excel(f"temp_files/{execution_id}comptrip.xlsx")
        update_status(execution_id, "Pre=Processing and analysis complete", "completed")
        # Formatting trips in IITB input Format
        if 'level_0' in comptrip.columns:
            comptrip.drop(columns=['level_0'], inplace=True)
        comptrip.reset_index(inplace=True)

        df = pd.DataFrame(comptrip)
        print('....1')
        df['Trip_Start'] = pd.to_datetime(df['Trip_Start'])
        df['Trip_End'] = pd.to_datetime(df['Trip_End'])
        print('....2')

        df['Service_time_minutes'] = (df['Trip_End'] - df['Trip_Start']).dt.total_seconds() / 60
        df['Service_time'] = df['Service_time_minutes'].round().astype(int) 
        print('....3')

        df['Start_Time'] = df['Trip_Start'].dt.strftime('%H:%M')
        df['End_Time'] = df['Trip_End'].dt.strftime('%H:%M')

        def adjust_time(time_str):
            hours, minutes = map(int, time_str.split(':'))
            if hours == 0:
                hours = 24
            elif hours == 1:
                hours = 25
            elif hours == 2:
                hours = 26
            return f"{hours:02}:{minutes:02}"

        print('....4')

        df['Start_Time'] = df['Start_Time'].apply(adjust_time)
        df['End_Time'] = df['End_Time'].apply(adjust_time)

        for index, row in df.iterrows():
            # df.at[index, 'Same Jurisdiction'] = 'yes'
            if (df.at[index, 'LocationPick'] in YB_Jurisdiction) & (df.at[index, 'LocationRelieve'] in YB_Jurisdiction):
                df.at[index, 'Same Jurisdiction'] = 'yes'
                # print(f"{df.at[index, 'LocationPick']}, {df.at[index, 'LocationRelieve']}, {df.at[index, 'Same Jurisdiction']}")
            if (df.at[index, 'LocationPick'] in DW_Jurisdiction) & (df.at[index, 'LocationRelieve'] in DW_Jurisdiction):
                df.at[index, 'Same Jurisdiction'] = 'yes'
                # print(f"{df.at[index, 'LocationPick']}, {df.at[index, 'LocationRelieve']}, {df.at[index, 'Same Jurisdiction']}")
            if (df.at[index, 'LocationPick'] in YB_Jurisdiction) & (df.at[index, 'LocationRelieve'] in DW_Jurisdiction):
                df.at[index, 'Same Jurisdiction'] = 'no'
                # print(f"{df.at[index, 'LocationPick']}, {df.at[index, 'LocationRelieve']}, {df.at[index, 'Same Jurisdiction']}")
            if (df.at[index, 'LocationPick'] in DW_Jurisdiction) & (df.at[index, 'LocationRelieve'] in YB_Jurisdiction):
                df.at[index, 'Same Jurisdiction'] = 'no'
                # print(f"{df.at[index, 'LocationPick']}, {df.at[index, 'LocationRelieve']}, {df.at[index, 'Same Jurisdiction']}")
            
            if pd.notna(df.at[index, 'TrainSBC1']) and df.at[index, 'TrainSBC1'] != '0':
                df.at[index, 'Step Back Rake'] = df.at[index, 'TrainSBC1']
                df.at[index, 'Step Back Location'] = 'DSTO'
            elif pd.notna(df.at[index, 'TrainSBC2']) and df.at[index, 'TrainSBC2'] != '0':
                df.at[index, 'Step Back Rake'] = df.at[index, 'TrainSBC2']
                df.at[index, 'Step Back Location'] = 'VASI'
            elif pd.notna(df.at[index, 'TrainSBC3']) and df.at[index, 'TrainSBC3'] != '0':
                df.at[index, 'Step Back Rake'] = df.at[index, 'TrainSBC3']
                df.at[index, 'Step Back Location'] = 'NECC'
            else:
                df.at[index, 'Step Back Rake'] = 'No StepBack'
                df.at[index, 'Step Back Location'] = 'No StepBack'
                
            if df.at[index, 'LocationPick'] in ('YBDN','YBUP','DWDN','DWUP'):
                df.at[index, 'Direction'] = 'DN' if df.at[index, 'LocationPick'] in ['YBDN','DWDN'] else 'UP' 
            else:
                df.at[index, 'Direction'] = 'DN' if df.at[index, 'LocationRelieve'] in ['YBDN', 'DWDN'] else 'UP'
            

        df_final = df[['Train_No', 'LocationPick', 'Start_Time', 'LocationRelieve', 'End_Time', 'Direction', 'Service_time', 'Same Jurisdiction', 'Step Back Rake', 'Step Back Location']]
        df_final.columns = ['Rake Num', 'Start Station', 'Start Time', 'End Station', 'End Time', 'Direction', 'Service time', 'Same Jurisdiction', 'Step Back Rake', 'Step Back Location']

        print(df_final.tail(10))
        df_final.reset_index(drop=True,inplace=True)
        df_final.reset_index(inplace=True)
        df_final.to_csv(f"temp_files/{execution_id}redefinedinputparameters.csv", index=False)
        update_status(execution_id, "Creating duty dataset to be optimized - This might take some time", "WIP")


        print("Preprocessing complete. Starting parallel duty generation...")

        # Call the multiprocessing script and wait for it to finish
        subprocess.run(["python", "multiprocessing_duty_generator.py", execution_id,timetable_type], check=True)
        update_status(execution_id, f"Dataset Generation successfull", "completed")

        print("Parallel duty generation finished. Continue with postprocessing...")

        update_status(execution_id, f"Starting Optimization Process - This will take time - Sit tight", "WIP")

        import os
        import sys
        import logging
        import pandas as pd
        import csv
        from io import StringIO
        from pyomo.environ import (
            ConcreteModel, Var, Objective, ConstraintList,
            Binary, minimize, value, SolverFactory
        )
        from pyomo.opt import TerminationCondition


        # ------------------ LOGGING (flush immediately) ------------------
        class FlushHandler(logging.StreamHandler):
            def emit(self, record):
                super().emit(record)
                self.flush()


        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[FlushHandler(sys.stdout)],
            force=True
        )


        def log_divider(msg):
            """Print a clear visual divider for major steps."""
            logging.info("=" * 80)
            logging.info(msg)
            logging.info("=" * 80)


        # ------------------ FILE LOCATIONS ------------------
        # execution_id = globals().get("execution_id", "")  # optional prefix
        BASE_DIR = "temp_files"

        INPUT_FILE_LOCATION = os.path.join(BASE_DIR, f"{execution_id}redefinedinputparameters.csv")
        DUTIES_FILE = os.path.join(BASE_DIR, f"{execution_id}generated_duties_graph.csv")
        SOLUTION_FILE = os.path.join(BASE_DIR, f"{execution_id}solution.csv")

        PRIMARY_SOLVER = globals().get("PRIMARY_SOLVER", "cbc")
        LOCAL_SOLVERS = globals().get("LOCAL_SOLVERS", ["glpk", "cbc"])


        # ------------------ HELPER: validate file existence ------------------
        def check_file_exists(path, description):
            if not os.path.exists(path):
                logging.error(f"❌ Missing {description} file: {path}")
                logging.error("   → Make sure the file exists and is not locked by another process.")
                raise FileNotFoundError(f"{description} file not found: {path}")
            else:
                logging.info(f"✅ Found {description} file: {path}")


        # ------------------ LOAD INPUTS ------------------
        log_divider("STEP 1: Loading Input Services")

        try:
            check_file_exists(INPUT_FILE_LOCATION, "input services")
            df = pd.read_csv(INPUT_FILE_LOCATION)

            if df.empty:
                raise ValueError("Input services file is empty!")

            services = [df.iloc[i, 0] for i in range(len(df))]
            logging.info(f"Loaded {len(services)} services from input.")
        except Exception as e:
            logging.error("❌ Failed to load input services file.", exc_info=True)
            logging.error("   → Check file format, encoding, and content (must have at least one column).")
            sys.exit(1)


        # ------------------ LOAD DUTIES ------------------
        log_divider("STEP 2: Loading Duty Assignments")

        service_assignments = {}
        servicesInPath = {key: [] for key in services}

        try:
            check_file_exists(DUTIES_FILE, "duties")

            with open(DUTIES_FILE, "rb") as file:
                raw = file.read()
                content = raw.replace(b"\x00", b"").decode("utf-8", errors="ignore")
                reader = csv.reader(StringIO(content))

                header_skipped = False
                for index, row in enumerate(reader):
                    if not header_skipped:
                        header_skipped = True
                        continue

                    if not row or len(row) < 2:
                        logging.warning(f"Duty row {index} skipped (empty or malformed).")
                        continue

                    try:
                        filtered = [int(v) for v in row[1:] if v not in ("NULL", "", None)]
                    except ValueError:
                        logging.warning(f"⚠️ Non-numeric data found in row {index}: {row}")
                        continue

                    valid_services = [s for s in filtered if s in services]
                    if not valid_services:
                        logging.warning(f"Duty {index} skipped — no valid service IDs found.")
                        continue

                    duty_id = index - 1
                    service_assignments[duty_id] = valid_services
                    for service in valid_services:
                        servicesInPath[service].append(duty_id)

            if not service_assignments:
                raise ValueError("No valid duties found in file.")

            logging.info(f"✅ Loaded {len(service_assignments)} valid duty assignments.")
        except Exception as e:
            logging.error("❌ Failed to load duties file.", exc_info=True)
            logging.error("   → Ensure CSV format is valid and IDs match the services list.")
            sys.exit(1)


        # ------------------ BUILD MODEL ------------------
        log_divider("STEP 3: Building Optimization Model")

        try:
            model = ConcreteModel()
            model.fPath = Var(service_assignments.keys(), domain=Binary)
            model.OBJ = Objective(expr=sum(model.fPath[path] for path in service_assignments), sense=minimize)
            model.ConsList = ConstraintList()

            for service, path_ids in servicesInPath.items():
                if path_ids:
                    model.ConsList.add(sum(model.fPath[path_id] for path_id in path_ids) == 1)
                else:
                    logging.warning(f"⚠️ Service {service} not found in any duty — may cause infeasibility.")

            logging.info("✅ Pyomo model successfully built.")
        except Exception as e:
            logging.error("❌ Error while building Pyomo model.", exc_info=True)
            sys.exit(1)


        # ------------------ SOLVE MODEL ------------------
        log_divider("STEP 4: Solving Model")

        def try_solve(solver_name, model, time_limit=3600, gap_percent=5):
            try:
                if not solver_name:
                    return None

                logging.info(f"Attempting solver: {solver_name.upper()}")

                solver = SolverFactory(solver_name)
                if not solver.available(False):
                    logging.warning(f"Solver '{solver_name}' is not available on this system.")
                    return None

                # Apply solver-specific options
                if solver_name.lower() == "cbc":
                    solver.options["seconds"] = time_limit
                    solver.options["ratioGap"] = gap_percent / 100.0
                elif solver_name.lower() == "glpk":
                    solver.options["tmlim"] = time_limit
                elif solver_name.lower() == "neos":
                    solver = SolverFactory("neos")
                    result = solver.solve(model, opt="bonmin", tee=True)
                    return result

                result = solver.solve(model, tee=True)
                sys.stdout.flush()
                return result

            except Exception as e:
                logging.warning(f"Solver {solver_name.upper()} failed: {e}", exc_info=True)
                return None


        results = try_solve(PRIMARY_SOLVER, model)
        for solver_name in LOCAL_SOLVERS:
            if results is None or not hasattr(results, "solver") or getattr(results.solver, "status", None) is None:
                results = try_solve(solver_name, model)
            else:
                break

        if results is None or not hasattr(results, "solver"):
            logging.critical("❌ All solver attempts failed.")
            logging.critical("   → Ensure CBC or GLPK is installed and available in system PATH.")
            sys.exit(1)

        logging.info(f"Solver status: {getattr(results.solver, 'status', 'UNKNOWN')}")
        logging.info(f"Termination condition: {getattr(results.solver, 'termination_condition', 'UNKNOWN')}")


        # ------------------ PROCESS RESULTS ------------------
        log_divider("STEP 5: Writing Solution")

        try:
            if getattr(results.solver, "termination_condition", None) == TerminationCondition.infeasible:
                logging.warning("⚠️ Model infeasible — some services not covered by any duty.")
            else:
                total_duties = 0
                with open(SOLUTION_FILE, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    for path_var in model.fPath:
                        val = value(model.fPath[path_var])
                        if abs(val - 1) <= 1e-6:
                            writer.writerow(service_assignments[path_var])
                            total_duties += 1
                logging.info(f"✅ Solution written to: {SOLUTION_FILE}")
                logging.info(f"✅ Total duties selected: {total_duties}")
        except Exception as e:
            logging.error("❌ Error writing solution file.", exc_info=True)
            logging.error("   → Check write permissions or file locks.")
            sys.exit(1)


        # ------------------ COMPLETION ------------------
        log_divider("✅ EXECUTION COMPLETE")
        logging.info("Script finished successfully.")
        update_status(execution_id, f"Success ! Optimization Complete", "completed")
        update_status(execution_id, f"Creating Trip Chart Format", "WIP")

        import csv
        import math
        import copy
        # from datetime import datetime, timedelta
        import matplotlib.pyplot as plt
        # import seaborn as sns
        import sys
        import time
        import matplotlib
        import matplotlib.pyplot as plt
        # import plotly.express as px
        # import plotly.graph_objects as go
        import matplotlib.dates as mdates
        import argparse

        import pandas as pd
        import numpy as np
        import datetime
        import random
        import warnings
        warnings.filterwarnings('ignore')
        warnings.simplefilter(action='ignore',category=FutureWarning)

        # df_final = pd.read_csv(r"redefinedinputparameters.csv")
        df_final = pd.read_csv(f"temp_files/{execution_id}redefinedinputparameters.csv")
        if 'index' in df_final.columns:
            df_final.drop(columns= ['index'], inplace=True)

        if 'Unnamed: 0' in df_final.columns:
            df_final.drop(columns= ['Unnamed: 0'], inplace=True)

        df_final

        import pandas as pd

        # Read file line by line and convert each row to a list of integers

        with open(f"temp_files/{execution_id}solution.csv", 'r') as file:
        # with open('solution.csv', 'r') as file:
            duties_list = [
                [int(item) for item in line.strip().split(',') if item.strip().isdigit()]
                for line in file if line.strip()
            ]

        # Create DataFrame with 'Duties' column
        df = pd.DataFrame({'Duties': duties_list})

        # Final result
        final_result = df

        # Preview
        print(final_result.head())

        import ast  # Abstract Syntax Trees (safe parser for literals like lists)

        duty = pd.DataFrame()
        duty_no = 1

        for index, TripIndexList in enumerate(final_result['Duties']):
            try:
                # Convert stringified list to actual list
                TripIndexList = ast.literal_eval(TripIndexList) if isinstance(TripIndexList, str) else TripIndexList
            except Exception as e:
                print(f"Error parsing TripIndexList at row {index}: {e}")
                continue

            print(f"\nProcessing Duty No: {duty_no}")
            for TripIndex in TripIndexList:
                try:
                    TripIndex = int(TripIndex)
                    trip = df_final.iloc[TripIndex].copy()
                    trip['Duty_No'] = duty_no
                    duty = pd.concat([duty, trip.to_frame().T], ignore_index=True)
                except Exception as e:
                    print(f"Error with TripIndex {TripIndex}: {e}")
            duty_no += 1

        print("\n✅ Duty assignment complete.")
        print(duty.head())

        duty = duty.reindex(columns= ['Duty_No','Rake Num', 'Start Station', 'Start Time', 'End Station', 'End Time',
            'Direction', 'Service time', 'Same Jurisdiction', 'Step Back Rake',
            'Step Back Location','ROUTE-VIA',])

        duty.reset_index(drop=True, inplace=True)

        # Check duty1 dataframe here
        duty1 = duty.copy()
        # duty1 = df_final.copy()
        duty1 = duty1.rename(columns = {
                            'Rake Num' : 'Train_No',
                            'Start Station' : 'LocationPick',
                            'End Station' : 'LocationRelieve',
                            'Start Time' : 'Trip_Start',
                            'End Time' : 'Trip_End',
                                })

        def min2hhmm(mins):
            """ changes the time from minutes to hh:mm
                gives hh:mm string and takes integer minutes 0 to 1440"""
            if True:
                h = mins//60
                mins = mins - (h*60)
                if len(str(h)) == 1: h = "0" + str(h)
                if len(str(mins)) == 1: mins = "0" + str(mins)
                return str(h) + ":" + str(mins) + ":" + "00"
                
        duty1['Trip_Duration'] = duty1['Service time'].apply(min2hhmm)
        duty1['Trip_Duration'] = duty1['Trip_Duration'].apply(pd.Timedelta)

        # DC_FILL1[column] = DC_FILL1[column].replace(r'(\d{2}:\d{2}):\d{2}',r'\1', regex=True)
        duty1['Trip_Start'] = duty1['Trip_Start'].replace(r'(\d{2}:\d{2}):\d{2}',r'\1', regex=True)
        duty1['Trip_End'] = duty1['Trip_End'].replace(r'(\d{2}:\d{2}):\d{2}',r'\1', regex=True)

        def adjust_time(time_str):
            hours, minutes = map(int, time_str.split(':'))
            if hours == 24:
                hours = 0
            elif hours == 25:
                hours = 1
            elif hours == 26:
                hours = 2
            return f"{hours:02}:{minutes:02}"

        duty1['Trip_Start'] = duty1['Trip_Start'].apply(adjust_time)
        duty1['Trip_End'] = duty1['Trip_End'].apply(adjust_time)

        duty1 = duty1.reindex(columns= ['Duty_No', 'Sign_On', 'SignOn_Location', 'Sign_Off', 'SignOff_Location', 'ACTUAL_DUTYHOURS','Train_No', 
                                        'LocationPick', 'Trip_Start', 'LocationRelieve','Trip_End','Trip_Duration','Service time', 'breaks','Single_Run',
                                        'Total_Run','Step Back Rake','Step Back Location','ROUTE-VIA'])

        duty1.reset_index(drop=True, inplace=True)

        duty1['Trip_Start'] = pd.to_datetime(duty1['Trip_Start'],errors='coerce')
        duty1['Trip_End'] = pd.to_datetime(duty1['Trip_End'],errors='coerce')

        duty2 = pd.DataFrame(columns=['Duty_No','Sign_On', 'SignOn_Location', 'Sign_Off',
            'SignOff_Location', 'ACTUAL_DUTYHOURS', 'Train_No','LocationPick', 'Trip_Start',
            'LocationRelieve', 'Trip_End', 'Trip_Duration','Service time', 'breaks', 'Single_Run',
            'Total_Run', 'Step Back Rake',
            'Step Back Location','ROUTE-VIA'])

        duty2['Trip_Start'] = pd.to_datetime(duty2['Trip_Start'],errors='coerce')
        duty2['Trip_End'] = pd.to_datetime(duty2['Trip_End'],errors='coerce')

        # For Line3 & 4 only
        for x in duty1['Duty_No'].unique():
            # if x == 3:
                duty_temp = duty1[duty1['Duty_No']==x].copy()
                # print(duty_temp.dtypes)
                duty_temp.reset_index(drop=True, inplace=True)
                duty_temp.loc[0,'SignOn_Location'] = duty_temp.loc[0,'LocationPick']
                # Check Sign ON Time 
                duty_temp.loc[0,'Sign_On'] = duty_temp.loc[0,'Trip_Start'] - datetime.timedelta(minutes=15) if (duty_temp.loc[0,'SignOn_Location'] in {'DWDN','DWUP','YBUP','YBDN','DWT'}) else duty_temp.loc[0,'Trip_Start'] - datetime.timedelta(minutes=25)
                duty_temp.loc[0,'SignOff_Location'] = duty_temp.iloc[-1]['LocationRelieve']
                # Check Sign OFF Time 
                duty_temp.loc[0,'Sign_Off'] = duty_temp.iloc[-1]['Trip_End'] + datetime.timedelta(minutes=10) if (duty_temp.loc[0,'SignOff_Location'] in {'DWDN','DWUP','YBUP','YBDN','DWT'}) else duty_temp.iloc[-1]['Trip_End'] + datetime.timedelta(minutes=20)
                duty_temp.loc[0,'ACTUAL_DUTYHOURS'] = duty_temp.loc[0,'Sign_Off'] - duty_temp.loc[0,'Sign_On']
                duty_temp.loc[0,'Total_Run'] = duty_temp['Trip_Duration'].sum()
                
                for index in range(0, duty_temp.shape[0] - 1 ):
                    duty_temp.loc[index,'breaks'] = duty_temp.loc[index + 1,'Trip_Start'] - duty_temp.loc[index,'Trip_End']
                duty_temp.loc[duty_temp.shape[0] - 1 ,'breaks'] = pd.Timedelta("0 days")
                
                initial_index = 0
                for index, value in enumerate(duty_temp['breaks']):
                    # print(f"index: {index}, value: {value}")
                    if (index != duty_temp.index[-1]) & (value != pd.Timedelta("0 days")):
                        # print(f"index: {index}")
                        duty_temp.loc[initial_index,'Single_Run'] = duty_temp['Trip_Duration'][initial_index : index + 1].sum()
                        initial_index = index + 1
                    if  index == duty_temp.index[-1]:
                        # print(index)
                        duty_temp.loc[initial_index,'Single_Run'] = duty_temp['Trip_Duration'][initial_index : index + 1].sum()
                        
                # print(duty_temp[['Trip_Start', 'Trip_End','Trip_Duration', 'breaks', 'Single_Run', 'Total_Run']])
                # print(duty_temp)
                duty2 = duty2.append(duty_temp)

        duty2.reset_index(drop=True, inplace=True)

        duty2.replace('SBC1','DSTO',regex=True,inplace=True)
        duty2.replace('SBC2','VASI',regex=True,inplace=True)
        duty2.replace('SBC3','NEC',regex=True,inplace=True)

        duty2['ACTUAL_DUTYHOURS'] = pd.to_timedelta(duty2['ACTUAL_DUTYHOURS'], errors='coerce')

        duty2['ACTUAL_DUTYHOURS'] = (duty2['ACTUAL_DUTYHOURS'] % pd.Timedelta(days=1))

        duty2.to_excel(f"temp_files/trip_chart_{execution_id}.xlsx")

        import pandas as pd
        import datetime

        # ── 1) FILES ────────────────────────────────────────────────────────────────
        INPUT_FILE  = f'temp_files/trip_chart_{execution_id}.xlsx'   # 🔁 adjust if needed
        OUTPUT_FILE = f'temp_files/duty_trip_break_summary_{execution_id}.xlsx'

        # ── 2) JURISDICTION HELPERS ─────────────────────────────────────────────────
        yb_jurisdiction = {
            'SDG-YB','DYB', 'YBSDG', 'SBC2', 'NESY', 'YBUP', 'YBDN', 'NSST/KSHI', 'SBC3', 'NECCSDG', 'VASIO/S'
        }
        dw_jurisdiction = {
            'NFD', 'KNR', 'DWDN', 'DWUP', 'DW3RD', 'JPW', 'DSTOSDG', 'SBC1', 'DWT'
        }
        def get_jurisdiction(loc):
            if loc in yb_jurisdiction: return 'YB'
            if loc in dw_jurisdiction: return 'DW'
            return 'UNKNOWN'

        # ── 3) DURATION → STRING CONVERTER ──────────────────────────────────────────
        def floatday_to_hhmm(f):
            """Convert a float-of-day to 'HH:MM'. Drops zero or NaN to ''. """
            if pd.isna(f) or f == 0:
                return ''
            td = pd.to_timedelta(f, unit='D')
            total_secs = int(round(td.total_seconds()))
            h, rem = divmod(total_secs, 3600)
            m, _   = divmod(rem, 60)
            return f"{h:02d}:{m:02d}"

        # ── 4) LOAD & CLEAN ─────────────────────────────────────────────────────────
        df = pd.read_excel(INPUT_FILE)
        # normalize headers
        df.columns = [c.strip().replace('\n','_') for c in df.columns]
        # carry Duty_No down through detail rows
        df['Duty_No'] = df['Duty_No'].fillna(method='ffill')

        # ── 4.1) COERCE any time/timedelta→float fraction of day ───────────────────
        def to_floatday(x):
            """Keep NaN; convert ints/floats unchanged; turn time/timedelta into float-of-day."""
            if pd.isna(x):
                return x
            if isinstance(x, (int, float)):
                return float(x)
            if isinstance(x, datetime.time):
                secs = x.hour*3600 + x.minute*60 + x.second
                return secs / (24*3600)
            if isinstance(x, pd.Timedelta):
                return x.total_seconds() / (24*3600)
            # fallback: try float conversion
            return float(x)

        # apply to both columns
        df['Single_Run'] = df['Single_Run'].apply(to_floatday)
        df['breaks']     = df['breaks'].apply(to_floatday)

        # ── 5) BUILD SUMMARY ────────────────────────────────────────────────────────
        output_rows = []

        for duty_no, grp in df.groupby('Duty_No', sort=False):
            g = grp.reset_index(drop=True)
            first = g.iloc[0]

            # Base columns: duty number, sign-on/off with juris
            base = [
                duty_no,
                first['Sign_On'],
                first['SignOn_Location'],
                get_jurisdiction(first['SignOn_Location']),
                first['Sign_Off'],
                first['SignOff_Location'],
                get_jurisdiction(first['SignOff_Location']),
            ]

            # collect every trip-duration > 0
            trips = [
                float(r['Single_Run'])
                for _, r in g.iterrows()
                if pd.notna(r['Single_Run']) and r['Single_Run'] > 0
            ]

            # collect every break-duration > 0, paired with its jurisdiction
            breaks = []
            for _, r in g.iterrows():
                b = r['breaks']
                if pd.notna(b) and b > 0:
                    loc = r.get('LocationRelieve')
                    if pd.isna(loc):
                        loc = r.get('SignOff_Location')
                    breaks.append((float(b), get_jurisdiction(loc)))

            # assemble up to five [trip, break, break_jurisdiction] blocks
            blocks = []
            for i in range(5):
                # trip
                if i < len(trips):
                    t_str = floatday_to_hhmm(trips[i])
                else:
                    t_str = ''
                # break
                if i < len(breaks):
                    b_val, jur = breaks[i]
                    b_str = floatday_to_hhmm(b_val)
                else:
                    b_str, jur = '', ''
                blocks += [t_str, b_str, jur]

            output_rows.append(base + blocks)

        # ── 6) ASSEMBLE + DUMP ──────────────────────────────────────────────────────
        base_cols = [
            'Duty_No',
            'Sign_On','SignOn_Location','SignOn_Jurisdiction',
            'Sign_Off','SignOff_Location','SignOff_Jurisdiction'
        ]
        tb_cols = []
        for i in range(1, 6):
            tb_cols += [
                f'trip_{i}_duration',
                f'break_{i}_duration',
                f'break_{i}_jurisdiction'
            ]

        final_cols = base_cols + tb_cols

        out_df = pd.DataFrame(output_rows, columns=final_cols)
        out_df.to_excel(OUTPUT_FILE, index=False)

        print(f"✅ Done! Open “{OUTPUT_FILE}” – every trip & break now shows exact HH:MM.")




    except Exception as e:
        update_status(execution_id, "Pipeline Broke--", "error", str(e))

if __name__ == "__main__":
    print('WE GOT HERE AGAIN')
    main()