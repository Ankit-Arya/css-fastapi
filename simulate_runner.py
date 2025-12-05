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
        # update_status(execution_id, f"Your execution ID is {execution_id}","WIP")
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

        # update_status(execution_id, f"Unique Train IDs: {ids}", "WIP")
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
                break

        def departure():
                for a in range(j+1):
                    print('DATA DETAILS--j--a--index',j,a,rail[x].index[a])
                    if (rail[x].index[a] not in {'CCDN','CCUP','SBC1','SBC2'}) & (a == 0):
                        route.update({'INDUCTION' : rail[x].index[a],'INDUCTION-TIME' : rail[x].iloc[a, 0],'INDUCTION_STATION' :rail[x].index[a+1],'SERVICE-TIME' : rail[x].iloc[a+1, 0]})
                        continue
                    if a ==rail[x].shape[0] - 1:
                        route.update({'STABLING' : rail[x].index[a],'STABLING-TIME' : rail[x].iloc[a, 0] })
                        continue
                    if rail[x].index[a] == 'NBAA' and rail[x].index[a+1] != 'NBAA':
                        route.update({'NBAA-DN': rail[x].iloc[a, 0]})
                        continue
                    if rail[x].index[a] == 'SBC1' and rail[x].index[a+1] == 'JLML':
                        route.update({'DSG-DN': rail[x].iloc[a, 0]})
                        continue
                    if rail[x].index[a] in (['RI','SBC2']) and rail[x].index[a+1] in (['RI','SBC2']):
                        route.update({'RI-DN': rail[x].iloc[a, 0]})
                        continue
                    if rail[x].index[a] == 'CCDN':
                        route.update({'SHD-DN': rail[x].iloc[a, 0]})
                        continue
                    if rail[x].index[a] in (['RI','SBC2']) and rail[x].index[a+1] not in (['RI','SBC2']):
                        route.update({'RI-UP': rail[x].iloc[a, 0]})
                        continue
                    if rail[x].index[a] == 'CCUP':
                        route.update({'SHD-UP': rail[x].iloc[a, 0]})
                        continue
                    if rail[x].index[a] == 'SBC1' and rail[x].index[a-1] == 'JLML':
                        route.update({'DSG-UP': rail[x].iloc[a, 0]})
                        continue
                    if rail[x].index[a] == 'NBAA' and rail[x].index[a+1] == 'NBAA':
                        route.update({'NBAA-UP': rail[x].iloc[a, 0]})
                        continue


                    

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
                    if (rail[x].index[i] == 'SBC1'):
                        while ((rail[x].iloc[j, 0] - rail[x].iloc[i, 0]) <= datetime.timedelta(hours=2, minutes=30)) & (
                            j < (rail[x].shape[0] - 1)):
                            if (rail[x].index[j] == 'CCDN') & (j != i) & (rail[x].index[j + 1] == 'CCUP'):
                                print('SBC1-CCDN>CCUP',rail[x].index[j])
        #                         rail[x].reset_index(inplace=True)
        #                         rail[x].set_index('CheckPoints', inplace=True)
                                data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                        'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
                                        'Trip_Duration': rail[x].iloc[j+1, 0] - rail[x].iloc[i, 0]}
                                departure()
                                data.update(route)
                                trips = trips.append(data, ignore_index=True)
                                rail[x].iloc[j+1,0] = rail[x].iloc[j,0] + datetime.timedelta(seconds=1)
                                del data
                                rail[x].reset_index(inplace=True)
                                rail[x].drop(rail[x].index[i:j + 1], inplace=True)
                                rail[x].set_index('CheckPoints', inplace=True)
                                j = i = 0
                                break
                            if (rail[x].index[j] == 'CCUP') | (rail[x].index[j] == 'CCDN') | (j == (rail[x].shape[0] - 1)):
                                print('SBC1-CCDN-OR-CCUP',rail[x].index[j])
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
                                j = i = 0
                                break
                            j = j + 1
                            
                        ###STEP-BACK FOR SBC2###
                    if (rail[x].index[i] == 'SBC2'):
                        while ((rail[x].iloc[j, 0] - rail[x].iloc[i, 0]) <= datetime.timedelta(hours=2, minutes=35)) & ((j < (rail[x].shape[0] - 1))):
                            if ((rail[x].index[j] == 'CCUP') | (rail[x].index[j] == 'CCDN')) :
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
                    while ((rail[x].iloc[j, 0] - rail[x].iloc[i, 0]) <= datetime.timedelta(hours=2, minutes=50)) & (
                            j < (rail[x].shape[0] - 1)):
                        
                        # SBC1 Timmings
                        if (rail[x].index[j] == 'SBC1') & (rail[x].index[j + 1] == 'SBC1') & (rail[x].iloc[j, 0].hour >= SBC1startHour) & (rail[x].iloc[j, 0].hour <= SBC1endHour) & (
                            rail[x].iloc[j, 0].minute >= SBC1startMinute if (rail[x].iloc[j, 0].hour == SBC1startHour) else True) & (
                            rail[x].iloc[j, 0].minute <= SBC1endMinute if (rail[x].iloc[j, 0].hour == SBC1endHour) else True):
              
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

                        # SBC2 Timings
                        if (rail[x].index[j] == 'SBC2') & (rail[x].index[j + 1] == 'SBC2') & (rail[x].iloc[j, 0].hour >= SBC2startHour) & (rail[x].iloc[j, 0].hour <= SBC2endHour) & (
                            rail[x].iloc[j, 0].minute >= SBC2startMinute if (rail[x].iloc[j, 0].hour == SBC2startHour) else True) & (
                            rail[x].iloc[j, 0].minute <= SBC2endMinute if (rail[x].iloc[j, 0].hour == SBC2endHour) else True):
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

                        
                        # if (rail[x].index[j] == 'CCUP') & (j != i) & (rail[x].index[j + 1] == 'CCDN'):
                        #     data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                        #             'LocationRelieve': rail[x].index[j+1], 'Trip_End': rail[x].iloc[j+1, 0],
                        #             'Trip_Duration': rail[x].iloc[j+1, 0] - rail[x].iloc[i, 0]}
                        #     departure()
                        #     data.update(route)
                        #     trips = trips.append(data, ignore_index=True)
                        #     # rail[x].iloc[j+1,0] = rail[x].iloc[j,0] 
                        #     del data
                        #     rail[x].reset_index(inplace=True)
                        #     rail[x].drop(rail[x].index[i:j + 1], inplace=True)
                        #     rail[x].set_index('CheckPoints', inplace=True)
                        #     j = 0
                        #     break
                        if (rail[x].index[j] == 'CCDN') & (j != i) & (rail[x].index[j + 1] == 'CCUP'):
                            data = {'Train_No': ids[x], 'LocationPick': rail[x].index[i], 'Trip_Start': rail[x].iloc[i, 0],
                                    'LocationRelieve': rail[x].index[j], 'Trip_End': rail[x].iloc[j, 0],
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
                        
                        if ((rail[x].index[j] == 'CCUP') | (rail[x].index[j] == 'CCDN')) & (j != 0):
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
                    if j == 0:
                        break
                        
                    route = {}
                    if j == rail[x].shape[0] - 1:
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

        # update_status(execution_id, "Trip Analysis Complete", "WIP")

        skip = 0
        RISBCASSIGNED = trips[trips['LocationPick']=='SBC2']['Trip_Start'].min()
        DSGSBCASSIGNED = trips[trips['LocationPick']=='SBC1']['Trip_Start'].min()
        comptrip = pd.DataFrame(
            columns=['Train_No', 'LocationPick', 'Trip_Start', 'LocationRelieve', 'Trip_End', 'Trip_Duration'])
        dumtrips = trips.copy()
        dumtrips.sort_values(['LocationPick','Trip_Start'], inplace=True)
        dumtrips.reset_index(drop=True, inplace=True)
        while (dumtrips.size != 0):
            print('Total_Trips:', len(comptrip.index))
            comptrip = pd.DataFrame(
                columns=['Train_No', 'LocationPick', 'Trip_Start', 'LocationRelieve', 'Trip_End', 'Trip_Duration'])
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
                dumtrips.drop(dumtrips.index[x], inplace=True)
                dumtrips.sort_values(['Trip_Start'], inplace=True)
                dumtrips.reset_index(drop=True, inplace=True)
                y = 0
                while y < len(dumtrips.index):
                    breaked = 0
                    ###Randomly Breaking Trips###
                    if ((
                            trip['Trip_Duration'] > datetime.timedelta(hours=0,minutes=10)) & (trip['LocationRelieve'] in ( 'CCUP','CCDN')) & (trip['LocationPick'] in ( 'CCUP','CCDN'))):
                        breaked = 1
                        break
                    if breaked == 1:
                        break

                    ass = 0


                    if (len(dumtrips.index) == 0) | (y == len(dumtrips.index)):
                        break
                    if (trip['LocationRelieve'] == 'SBC1') & (trip['TrainSBC1'] == '0') & (ass == 0):
                        z = 0
                        ass = 0
                        dumtrips.sort_values(['Trip_End'],ascending=True, inplace=True)
                        dumtrips.reset_index(drop=True, inplace=True)
                        while z < len(dumtrips.index):
                            if (dumtrips['Trip_Start'][z] - trip['Trip_End'] >= datetime.timedelta(minutes=5)) & (
                                    trip['Train_No'] != dumtrips['Train_No'][z]) & (dumtrips['LocationPick'][z] == 'SBC1') & (trip['Trip_Duration'] + dumtrips['Trip_Duration'][z] <= datetime.timedelta(hours=2,minutes=35) ):

                                print('DSG-SBC',dumtrips['Train_No'][z],dumtrips['Trip_Start'][z],trip['Trip_End'],trip['Train_No'])
                                trip['TrainSBC1'] = dumtrips['Train_No'][z]
                                trip['Trip_End'] = dumtrips['Trip_End'][z]
                                trip['Trip_Duration'] = dumtrips['Trip_End'][z] - trip['Trip_Start']
                                trip['LocationRelieve'] = dumtrips['LocationRelieve'][z]
                                trip['INDUCTION'] = trip['INDUCTION'] if pd.isnull(dumtrips['INDUCTION'][z]) else dumtrips['INDUCTION'][z]
                                trip['INDUCTION_STATION'] = trip['INDUCTION_STATION'] if pd.isnull(dumtrips['INDUCTION_STATION'][z]) else dumtrips['INDUCTION_STATION'][z]
                                trip['SERVICE-TIME'] = trip['SERVICE-TIME'] if pd.isnull(dumtrips['SERVICE-TIME'][z]) else dumtrips['SERVICE-TIME'][z]
                                trip['INDUCTION-TIME'] = trip['INDUCTION-TIME'] if pd.isnull(dumtrips['INDUCTION-TIME'][z]) else dumtrips['INDUCTION-TIME'][z]
                                trip['SHD-DN'] = trip['SHD-DN'] if pd.isnull(dumtrips['SHD-DN'][z]) else dumtrips['SHD-DN'][z]
                                trip['SHD-UP'] = trip['SHD-UP'] if  pd.isnull(dumtrips['SHD-UP'][z]) else dumtrips['SHD-UP'][z]
                                trip['RI-DN'] = trip['RI-DN'] if pd.isnull(dumtrips['RI-DN'][z]) else dumtrips['RI-DN'][z]
                                trip['RI-UP'] = trip['RI-UP'] if pd.isnull(dumtrips['RI-UP'][z]) else dumtrips['RI-UP'][z]
                                trip['DSG-DN'] = trip['DSG-DN'] if pd.isnull(dumtrips['DSG-DN'][z]) else dumtrips['DSG-DN'][z]
                                trip['DSG-UP'] = trip['DSG-UP'] if pd.isnull(dumtrips['DSG-UP'][z]) else dumtrips['DSG-UP'][z]
                                trip['NBAA-DN'] = trip['NBAA-DN'] if pd.isnull(dumtrips['NBAA-DN'][z]) else dumtrips['NBAA-DN'][z]
                                trip['NBAA-UP'] = trip['NBAA-UP'] if pd.isnull(dumtrips['NBAA-UP'][z]) else dumtrips['NBAA-UP'][z]
                                trip['STABLING'] = trip['STABLING'] if pd.isnull(dumtrips['STABLING'][z]) else dumtrips['STABLING'][z]
                                trip['STABLING-TIME'] = trip['STABLING-TIME'] if pd.isnull(dumtrips['STABLING-TIME'][z]) else dumtrips['STABLING-TIME'][z]

                                dumtrips.drop(dumtrips.index[z], inplace=True)
                                dumtrips.sort_values(['Trip_End'],ascending=True, inplace=True)
                                dumtrips.reset_index(drop=True, inplace=True)
                                ass = 1
                                break
                            z = z + 1

                    if (trip['LocationRelieve'] == 'SBC2') & (trip['TrainSBC2'] == '0') & (ass == 0) :
                    #DELETED CONDITION & (trip['Trip_Duration'] <= datetime.timedelta(hours=2))
                        z = 0
                        ass = 0
                        dumtrips.sort_values(['Trip_Start'],ascending=True, inplace=True)
                        dumtrips.reset_index(drop=True, inplace=True)
                        while z < len(dumtrips.index):
                            if (dumtrips['Trip_Start'][z] - trip['Trip_End'] > datetime.timedelta(minutes=5)) & (
                                    (dumtrips['Train_No'][z] != trip['Train_No']) & (
                                    dumtrips['Train_No'][z] != trip['TrainSBC1']) & (
                                            dumtrips['Train_No'][z] != trip['TrainSBC2'])) & (
                                    dumtrips['LocationPick'][z] == 'SBC2') & (dumtrips['Trip_Start'][z] != RISBCASSIGNED):
                                print('RI-SBC',dumtrips['Train_No'][z],dumtrips['Trip_Start'][z],trip['Trip_End'],trip['Train_No'])
                                trip['TrainSBC2'] = dumtrips['Train_No'][z]
                                trip['Trip_End'] = dumtrips['Trip_End'][z]
                                trip['Trip_Duration'] = dumtrips['Trip_End'][z] - trip['Trip_Start']
                                trip['LocationRelieve'] = dumtrips['LocationRelieve'][z]
                                trip['INDUCTION'] = trip['INDUCTION'] if pd.isnull(dumtrips['INDUCTION'][z]) else dumtrips['INDUCTION'][z]
                                trip['INDUCTION_STATION'] = trip['INDUCTION_STATION'] if pd.isnull(dumtrips['INDUCTION_STATION'][z]) else dumtrips['INDUCTION_STATION'][z]
                                trip['SERVICE-TIME'] = trip['SERVICE-TIME'] if pd.isnull(dumtrips['SERVICE-TIME'][z]) else dumtrips['SERVICE-TIME'][z]
                                trip['INDUCTION-TIME'] = trip['INDUCTION-TIME'] if pd.isnull(dumtrips['INDUCTION-TIME'][z]) else dumtrips['INDUCTION-TIME'][z]
                                trip['SHD-DN'] = trip['SHD-DN'] if pd.isnull(dumtrips['SHD-DN'][z]) else dumtrips['SHD-DN'][z]
                                trip['SHD-UP'] = trip['SHD-UP'] if  pd.isnull(dumtrips['SHD-UP'][z]) else dumtrips['SHD-UP'][z]
                                trip['RI-DN'] = trip['RI-DN'] if pd.isnull(dumtrips['RI-DN'][z]) else dumtrips['RI-DN'][z]
                                trip['RI-UP'] = trip['RI-UP'] if pd.isnull(dumtrips['RI-UP'][z]) else dumtrips['RI-UP'][z]
                                trip['DSG-DN'] = trip['DSG-DN'] if pd.isnull(dumtrips['DSG-DN'][z]) else dumtrips['DSG-DN'][z]
                                trip['DSG-UP'] = trip['DSG-UP'] if pd.isnull(dumtrips['DSG-UP'][z]) else dumtrips['DSG-UP'][z]
                                trip['NBAA-DN'] = trip['NBAA-DN'] if pd.isnull(dumtrips['NBAA-DN'][z]) else dumtrips['NBAA-DN'][z]
                                trip['NBAA-UP'] = trip['NBAA-UP'] if pd.isnull(dumtrips['NBAA-UP'][z]) else dumtrips['NBAA-UP'][z]
                                trip['STABLING'] = trip['STABLING'] if pd.isnull(dumtrips['STABLING'][z]) else dumtrips['STABLING'][z]
                                trip['STABLING-TIME'] = trip['STABLING-TIME'] if pd.isnull(dumtrips['STABLING-TIME'][z]) else dumtrips['STABLING-TIME'][z]

                                dumtrips.drop(dumtrips.index[z], inplace=True)
                                dumtrips.sort_values(['Trip_Start'],ascending=True, inplace=True)
                                dumtrips.reset_index(drop=True, inplace=True)
                                ass = 1
                                break
                            z = z + 1

                    y = (y + 1) if ass == 0 else 0
                comptrip = comptrip.append(trip)
                dumtrips.sort_values(['Trip_Start'], inplace=True)
                dumtrips.reset_index(drop=True, inplace=True)
                x = 0
                
        print('The_End')
        print('Total_Trips:', len(comptrip.index))

        comptrip = comptrip.reindex(columns= ['Train_No', 'LocationPick', 'Trip_Start', 'LocationRelieve', 'Trip_End','Trip_Duration',
                                            'TrainSBC1', 'TrainSBC2','NBAA-DN', 'DSG-DN','SHD-DN','RI-DN','RI-UP','SHD-UP', 'DSG-UP','NBAA-UP',
                                            'INDUCTION', 'INDUCTION-TIME','INDUCTION_STATION','SERVICE-TIME','STABLING', 'STABLING-TIME'])
        comptrip = comptrip.sort_values('Trip_Start', ascending= True)
        comptrip.reset_index(drop= True, inplace=True)

        comptrip.to_excel(f"temp_files/{execution_id}comptrip.xlsx")
        update_status(execution_id, "Pre=Processing and analysis complete", "completed")
        if 'level_0' in comptrip.columns:
            comptrip.drop(columns=['level_0'], inplace=True)
        comptrip.reset_index(inplace=True)

        df = pd.DataFrame(comptrip)

        df['Trip_Start'] = pd.to_datetime(df['Trip_Start'])
        df['Trip_End'] = pd.to_datetime(df['Trip_End'])

        df['Service_time_minutes'] = (df['Trip_End'] - df['Trip_Start']).dt.total_seconds() / 60
        df['Service time'] = df['Service_time_minutes'].round().astype(int) 

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

        df['Start_Time'] = df['Start_Time'].apply(adjust_time)
        df['End_Time'] = df['End_Time'].apply(adjust_time)

        for index, row in df.iterrows():
            df.at[index, 'Same Jurisdiction'] = 'yes'
            if pd.notna(df.at[index, 'TrainSBC1']) and df.at[index, 'TrainSBC1'] != '0':
                df.at[index, 'Step Back Rake'] = df.at[index, 'TrainSBC1']
                df.at[index, 'Step Back Location'] = 'DSG'
            elif pd.notna(df.at[index, 'TrainSBC2']) and df.at[index, 'TrainSBC2'] != '0':
                df.at[index, 'Step Back Rake'] = df.at[index, 'TrainSBC2']
                df.at[index, 'Step Back Location'] = 'RI'
            else:
                df.at[index, 'Step Back Rake'] = 'No StepBack'
                df.at[index, 'Step Back Location'] = 'No StepBack'
            if df.at[index, 'LocationPick'] in ('CCDN','CCUP'):
                df.at[index, 'Direction'] = 'DN' if df.at[index, 'LocationPick'] == 'CCDN' else 'UP' 
            else:
                df.at[index, 'Direction'] = 'DN' if df.at[index, 'LocationRelieve'] == 'CCDN' else 'UP'

        cols = ['NBAA-DN','DSG-DN', 'SHD-DN', 'RI-DN', 'RI-UP', 'SHD-UP', 'DSG-UP', 'NBAA-UP']
        route = ''

        for i in range(len(df)):   
            trip_dict = {}
            sorted_trip_dict = {}
            for col in cols:
                if pd.notnull(df.loc[i, col]):
                    trip_dict[col] = df.loc[i, col]
                
                sorted_trip_dict = dict(sorted(trip_dict.items(), key= lambda pair: pair[1]))
                
            if len(sorted_trip_dict) > 1: # Ignore single station time value in route column
                route += 'Train_No/' + str(df.loc[i, 'Train_No']) + " -- "
                for key, value in sorted_trip_dict.items():
                    if df.loc[i, 'Step Back Location'] == "RI":
                        SB_location = "RI-DN"
                    if df.loc[i, 'Step Back Location'] == "DSG":
                        SB_location = "DSG-UP"
                    if df.loc[i, 'Step Back Location'] == "No StepBack":
                        SB_location = "No StepBack"
                    
                    if SB_location in str(key):
                        route +=  str(key) + '/' + value.strftime("%H:%M") + " -- "
                        route +=  'SB_Train_No/' + str(df.loc[i, 'Step Back Rake']) + " -- "
                    else:
                        route +=  str(key) + '/' + value.strftime("%H:%M") + " -- "
            df.loc[i, 'ROUTE-VIA'] = route
            route = ''

        df = df.reindex(columns= ['Train_No', 'LocationPick','Start_Time', 'LocationRelieve','End_Time','Direction','Service time',
                                'Same Jurisdiction','Step Back Rake','Step Back Location','ROUTE-VIA'])

        df_final = df.rename(columns= { 'Train_No' : 'Rake Num',
                                    'LocationPick' : 'Start Station',
                                    'Start_Time' : 'Start Time',
                                    'LocationRelieve' : 'End Station',
                                    'End_Time' : 'End Time',})

        df_final.reset_index(drop=True,inplace=True)
        df_final.reset_index(inplace=True)

        df_final.to_csv(f"temp_files/{execution_id}redefinedinputparameters.csv", index=False)

        update_status(execution_id, "Creating duty dataset to be optimized - This might take some time", "WIP")
        import csv
        from collections import defaultdict
        import os

        # Parameters
        Duty_hours = 440
        Driving_duration = 360
        Continuous_Driving_time = 170
        long_break = 50
        short_break = 30

        crewControl = ['CCDN', 'CCUP']
        final_op = []

        class Services:
            def __init__(self, attrs):
                self.servNum = attrs[0]
                self.trainNum = int(attrs[1])
                self.startStn = attrs[2]
                self.startTime = hhmm2mins(attrs[3])
                self.endStn = attrs[4]
                self.endTime = hhmm2mins(attrs[5])
                self.dir = attrs[6]
                self.servDur = int(attrs[7])
                self.stepbackTrainNum = attrs[9]
                self.servAdded = False
                self.breakDur = 0
                self.tripDur = 0

        def min2hhmm(mins):
            h = mins // 60
            mins = mins - (h * 60)
            if len(str(h)) == 1:
                h = "0" + str(h)
            if len(str(mins)) == 1:
                mins = "0" + str(mins)
            return str(h) + ":" + str(mins)

        def hhmm2mins(hhmm):
            parts = hhmm.split(":")
            if len(parts) == 2:
                hrs, mins = int(parts[0]), int(parts[1])
            elif len(parts) == 3:
                hrs, mins = int(parts[0]), int(parts[1])
            else:
                raise ValueError(f"Invalid time format: {hhmm}")
            print(hhmm, hrs, mins)
            return hrs * 60 + mins

        def fetchData(csv_file=f"temp_files/{execution_id}redefinedinputparameters.csv"):
            servicesLst = []
            with open(csv_file) as output:
                reader = csv.reader(output)
                next(reader)  # Skip header
                for row in reader:
                    servicesLst.append(Services(row))
            return servicesLst

        def canAppend2(service1, service2):
            """Check if service2 can follow service1 based on your original logic"""
            
            # Case 1: Same station, same time (immediate connection)
            startEndStnTF = service1.endStn == service2.startStn
            startEndTimeTF = service2.startTime == service1.endTime  # No technical break
            
            # Case 2: Short break at crew control station
            startEndStnTFafterBreak = service1.endStn[:2] == service2.startStn[:2]
            startEndTimeWithin = short_break <= (service2.startTime - service1.endTime) <= (120 if timetable_type == 'large' else 150)
            
            # Rake matching logic
            if service1.stepbackTrainNum == "No StepBack":
                startEndRakeTF = int(service1.trainNum) == int(service2.trainNum)
            else:
                startEndRakeTF = int(service1.stepbackTrainNum) == int(service2.trainNum)
            
            # Case 1: Direct rake connection
            if startEndRakeTF and startEndStnTF and startEndTimeTF:
                return True
            
            # Case 2: Break at crew control station
            elif startEndTimeWithin and service1.endStn[:4] in crewControl and startEndStnTFafterBreak:
                return True
            
            return False

        def build_graph(services):
            """Build adjacency graph of services that can follow each other"""
            graph = defaultdict(list)
            
            for i, service1 in enumerate(services):
                for j, service2 in enumerate(services):
                    if i != j and canAppend2(service1, service2):
                        graph[i].append(j)
            
            return graph

        def calculate_continuous_driving_time(path, services):
            """Calculate continuous driving time for a path, respecting rake changes"""
            if not path:
                return 0
            
            max_continuous = 0
            current_continuous = services[path[0]].servDur
            current_train = services[path[0]].trainNum
            
            for i in range(1, len(path)):
                prev_service = services[path[i-1]]
                curr_service = services[path[i]]
                
                # Check if same rake continues
                if prev_service.stepbackTrainNum == "No StepBack":
                    rake_continues = (prev_service.trainNum == curr_service.trainNum)
                else:
                    rake_continues = (int(prev_service.stepbackTrainNum) == curr_service.trainNum)
                
                gap = curr_service.startTime - prev_service.endTime
                
                if rake_continues and gap == 0:  # Continuous driving
                    current_continuous += curr_service.servDur
                else:  # Break in continuity
                    max_continuous = max(max_continuous, current_continuous)
                    current_continuous = curr_service.servDur
            
            max_continuous = max(max_continuous, current_continuous)
            return max_continuous

        def is_valid_duty(path, services):
            """Check if a path forms a valid duty based on your original constraints"""
            if len(path) < 1:
                return False
            
            # Calculate duty duration and breaks
            duty_start = services[path[0]].startTime
            duty_end = services[path[-1]].endTime
            duty_dur = duty_end - duty_start
            
            # Calculate break durations
            break_durs = []
            for i in range(len(path) - 1):
                break_dur = services[path[i+1]].startTime - services[path[i]].endTime
                break_durs.append(break_dur)
            
            total_break_dur = sum(break_durs)
            driving_dur = duty_dur - total_break_dur
            
            # Check long break requirement
            long_break_exists = any(br >= long_break for br in break_durs)
            
            # Check total break duration constraint
            total_break_dur_valid = long_break <= total_break_dur <= (120 if timetable_type == 'large' else 150) if break_durs else True
            
            # Check continuous driving time
            continuous_driving = calculate_continuous_driving_time(path, services)
            
            # Apply your original validation logic
            valid = (duty_dur <= Duty_hours and 
                    driving_dur <= Driving_duration and 
                    long_break_exists and 
                    total_break_dur_valid and
                    continuous_driving <= Continuous_Driving_time)
            
            return valid

        def generate_duties_from_service(start_idx, graph, services, max_depth=15):
            """Generate all valid duties starting from a given service using DFS"""
            valid_duties = []
            
            def dfs(current_path):
                if len(current_path) > max_depth:
                    return
                
                # Check if current path is a valid duty
                if len(current_path) > 1 and is_valid_duty(current_path, services):
                    valid_duties.append(current_path[:])
                
                # Try to extend the path
                current_service_idx = current_path[-1]
                for next_service_idx in graph[current_service_idx]:
                    if next_service_idx not in current_path:  # Avoid cycles
                        # Additional check for duty duration before adding
                        test_path = current_path + [next_service_idx]
                        test_duty_dur = services[test_path[-1]].endTime - services[test_path[0]].startTime
                        if test_duty_dur <= Duty_hours:
                            current_path.append(next_service_idx)
                            dfs(current_path)
                            current_path.pop()
            
            dfs([start_idx])
            return valid_duties

        def generate_all_duties(services):
            """Generate all valid duties using graph approach"""
            print("Building connection graph...")
            graph = build_graph(services)
            
            all_duties = []
            
            print("Generating duties...")
            for i, service in enumerate(services):
                duties_from_service = generate_duties_from_service(i, graph, services)
                print(f"[{i+1}/{len(services)}] Service {service.servNum}: {len(duties_from_service)} duties generated.")
                
                # Convert indices back to service numbers
                for duty_indices in duties_from_service:
                    duty_service_nums = [services[idx].servNum for idx in duty_indices]
                    all_duties.append(duty_service_nums)
            
            return all_duties

        def save_duties_to_csv(duties, filename=f"temp_files/{execution_id}generated_duties_graph.csv"):
            """Save duties to CSV file"""
            if not duties:
                print("No duties to save.")
                return
            
            max_length = max(len(duty) for duty in duties)
            
            with open(filename, 'w', newline='') as file:
                writer = csv.writer(file)
                # Write header
                header = ['Duty_ID'] + [f'Service_{i+1}' for i in range(max_length)]
                writer.writerow(header)
                
                # Write duties
                for idx, duty in enumerate(duties):
                    row = [idx] + duty + [''] * (max_length - len(duty))
                    writer.writerow(row)
            
            print(f"Duties saved to {filename}")
            

        # Main execution
        # if __name__ == "__main__":
        print("Loading services...")
        services = fetchData()
        services.sort(key=lambda serv: serv.startTime)
        print(f"Total services loaded: {len(services)}")
        
        print("Generating duties using graph approach...")
        all_duties = generate_all_duties(services)
        
        print(f"Total valid duties generated: {len(all_duties)}")
        
        # Save to CSV
        save_duties_to_csv(all_duties)
        
        # Also store in global variable for compatibility
        final_op = all_duties
        update_status(execution_id, f"Dataset Generation successfull with {len(all_duties)} records", "completed")
        print("Done!")

        update_status(execution_id, f"Starting Optimization Process - This will take time - Sit tight", "WIP")
# ------------------SOLVER----------------

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

        # Example status updates
        update_status(execution_id, "Success! Optimization Complete", "completed")
        update_status(execution_id, "Creating Trip Chart Format", "WIP")

        # ------------------------fIll tc
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
        df_final = pd.read_csv(f"temp_files/{execution_id}redefinedinputparameters.csv")

        if 'index' in df_final.columns:
            df_final.drop(columns= ['index'], inplace=True)

        if 'Unnamed: 0' in df_final.columns:
            df_final.drop(columns= ['Unnamed: 0'], inplace=True)

        df_final

        with open(f"temp_files/{execution_id}solution.csv", 'r') as file:
            duties_list = [
                [int(item) for item in line.strip().split(',') if item.strip().isdigit()]
                for line in file if line.strip()
            ]

        # Create DataFrame with 'Duties' column
        df = pd.DataFrame({'Duties': duties_list})

        # Final result
        final_result = df

        final_result.to_csv(f"temp_files/{execution_id}OutputForDC.csv")

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

        # For all Line except Line9 and Line 3&4
        for x in duty1['Duty_No'].unique():
            # if x == 3:
                duty_temp = duty1[duty1['Duty_No']==x].copy()
                # print(duty_temp.dtypes)
                duty_temp.reset_index(drop=True, inplace=True)
                duty_temp.loc[0,'SignOn_Location'] = duty_temp.loc[0,'LocationPick']
                # Check Sign ON Time 
                duty_temp.loc[0,'Sign_On'] = duty_temp.loc[0,'Trip_Start'] - datetime.timedelta(minutes=15) if (duty_temp.loc[0,'SignOn_Location'] in {'CCDN','CCUP'}) else duty_temp.loc[0,'Trip_Start'] - datetime.timedelta(minutes=25)
                duty_temp.loc[0,'SignOff_Location'] = duty_temp.iloc[-1]['LocationRelieve']
                # Check Sign OFF Time 
                duty_temp.loc[0,'Sign_Off'] = duty_temp.iloc[-1]['Trip_End'] + datetime.timedelta(minutes=10) if (duty_temp.loc[0,'SignOff_Location'] in {'CCDN','CCUP'}) else duty_temp.iloc[-1]['Trip_End'] + datetime.timedelta(minutes=20)
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

                duty2 = duty2.append(duty_temp)

        duty2.reset_index(drop=True, inplace=True)

        duty2.replace('CCUP','SHD-UP',regex=True,inplace=True)
        duty2.replace('CCDN','SHD-DN',regex=True,inplace=True)

        duty2.replace('SBC1','DSG',regex=True,inplace=True)
        duty2.replace('SBC2','RI',regex=True,inplace=True)

        duty2['ACTUAL_DUTYHOURS'] = pd.to_timedelta(duty2['ACTUAL_DUTYHOURS'], errors='coerce')

        duty2['ACTUAL_DUTYHOURS'] = (duty2['ACTUAL_DUTYHOURS'] % pd.Timedelta(days=1))

        duty2.to_excel(f"temp_files/trip_chart_{execution_id}.xlsx")

        # --------------Generate DC

        # df_final = pd.read_excel(r"comptrip-SUN-892025.xlsx")

        # # Adding Last_Train in df_final column for stabling duty filling in Departure Chart

        # df_final['Last_Train'] = df_final['Train_No']
        # for i in range(len(df_final)):
        #     for column in ['TrainSBC1', 'TrainSBC2']:
        #         if df_final.loc[i, column] != 0:
        #             # print(i, column, df_final.loc[i, column])
        #             df_final.loc[i, 'Last_Train'] = df_final.loc[i, column]

        # final_duty = pd.read_csv(r"OutputForDC.csv")

        # #Run for Duty formation

        # duty = pd.DataFrame()
        # duty_no = 1
        # import ast

        # for index, TripIndexList in enumerate(final_duty['Duties']):
        #     # print(f"Index: {index}, TripIndexList: {TripIndexList}")
            
        #     TripIndexList = ast.literal_eval(TripIndexList)
        #     # print(type(TripIndexList))
        #     for TripIndex in TripIndexList:  
        #         TripIndex = int(TripIndex)
        #         trip = df_final.iloc[TripIndex].copy()
        #         trip['Duty_No'] = duty_no
        #         duty = duty.append(trip)      
        #     duty_no =duty_no + 1

        # if 'index' in duty.columns:
        #     duty.drop(columns='index', inplace=True)
        # if 'level_0' in duty.columns:
        #     duty.drop(columns='level_0', inplace=True)
        # if 'Unnamed: 0' in duty.columns:
        #     duty.drop(columns='Unnamed: 0', inplace=True) 
        # duty.reset_index(drop=True, inplace=True)

        # duty1 = duty.copy()
        # duty1 = duty1.rename(columns = {
        #                     # 'Rake Num' : 'Train_No',
        #                     # 'Start Station' : 'LocationPick',
        #                     # 'Start Time' : 'Trip_Start',
        #                     # 'End Station' : 'LocationRelieve',
        #                     # 'End Time' : 'Trip_End',
        # })

        # duty1 = duty1.reindex(columns= ['Duty_No', 'Train_No', 'Sign_On', 'SignOn_Location', 'Sign_Off', 'SignOff_Location', 'ACTUAL_DUTYHOURS',
        #                                 'LocationPick', 'Trip_Start', 'LocationRelieve','Trip_End','Trip_Duration', 'breaks','Single_Run',
        #                                 'Total_Run',
        #                                  'TrainSBC1','TrainSBC2','NBAA-DN','DSG-DN','SHD-DN','RI-DN','RI-UP','SHD-UP','DSG-UP','NBAA-UP', 
        #                                 'INDUCTION', 'INDUCTION-TIME', 'INDUCTION_STATION','SERVICE-TIME','STABLING', 'STABLING-TIME','Last_Train'])

        # duty1.reset_index(drop=True, inplace=True)

        # # Formatting departure_chart

        # departure_chart = duty1[['Duty_No','Train_No','INDUCTION','INDUCTION-TIME','Trip_Start','Trip_End','NBAA-DN','DSG-DN','SHD-DN','RI-DN','RI-UP',
        #                          'SHD-UP','DSG-UP','TrainSBC1','TrainSBC2','NBAA-UP','STABLING','STABLING-TIME','Last_Train']]

        # departure_chart = departure_chart.drop_duplicates()
        # departure_chart.reset_index(drop=True, inplace=True)

        # DC_FILL = pd.read_csv(r'L1-SUN-892025-DC.csv')

        # #Run for Duty formation from OR Tool output
        # # try:
        # DC_FILL = DC_FILL[~DC_FILL.isnull().all(axis=1)]
        # DC_FILL['DEPOT'] = pd.to_datetime(DC_FILL['DEPOT'],errors='coerce')
        # DC_FILL['NBAA-DN'] = pd.to_datetime(DC_FILL['NBAA-DN'],errors='coerce')
        # DC_FILL['DSG-DN'] = pd.to_datetime(DC_FILL['DSG-DN'],errors='coerce')
        # DC_FILL['SHD-DN'] = pd.to_datetime(DC_FILL['SHD-DN'],errors='coerce')
        # DC_FILL['KG-DN'] = pd.to_datetime(DC_FILL['KG-DN'],errors='coerce')
        # DC_FILL['RI-DN'] = pd.to_datetime(DC_FILL['RI-DN'],errors='coerce')
        # DC_FILL['RI-UP'] = pd.to_datetime(DC_FILL['RI-UP'],errors='coerce')
        # DC_FILL['SLAP'] = pd.to_datetime(DC_FILL['SLAP'],errors='coerce')
        # DC_FILL['SHD-UP'] = pd.to_datetime(DC_FILL['SHD-UP'],errors='coerce')
        # DC_FILL['DSG-UP'] = pd.to_datetime(DC_FILL['DSG-UP'],errors='coerce')
        # DC_FILL['NBAA-UP'] = pd.to_datetime(DC_FILL['NBAA-UP'],errors='coerce')
        # DC_FILL['DEPOT.1'] = pd.to_datetime(DC_FILL['DEPOT.1'],errors='coerce')
        # DC_FILL.dtypes
        # # except:
        # #     pass

        # # try:
        # DC_FILL['DEPOT'] = DC_FILL['DEPOT'].dt.time
        # DC_FILL['NBAA-DN'] = DC_FILL['NBAA-DN'].dt.time
        # DC_FILL['DSG-DN'] = DC_FILL['DSG-DN'].dt.time
        # DC_FILL['SHD-DN'] = DC_FILL['SHD-DN'].dt.time
        # DC_FILL['KG-DN'] = DC_FILL['KG-DN'].dt.time
        # DC_FILL['RI-DN'] = DC_FILL['RI-DN'].dt.time
        # DC_FILL['RI-UP'] = DC_FILL['RI-UP'].dt.time
        # DC_FILL['SLAP'] = DC_FILL['SLAP'].dt.time
        # DC_FILL['SHD-UP'] = DC_FILL['SHD-UP'].dt.time
        # DC_FILL['DSG-UP'] = DC_FILL['DSG-UP'].dt.time
        # DC_FILL['NBAA-UP'] = DC_FILL['NBAA-UP'].dt.time
        # DC_FILL['DEPOT.1'] = DC_FILL['DEPOT.1'].dt.time
        # DC_FILL.dtypes
        # # except:
        # #     pass

        # # try:
        # departure_chart['INDUCTION-TIME'] = departure_chart['INDUCTION-TIME'].dt.time
        # departure_chart['Trip_Start'] = departure_chart['Trip_Start'].dt.time
        # departure_chart['Trip_End'] = departure_chart['Trip_End'].dt.time

        # departure_chart['NBAA-DN'] = departure_chart['NBAA-DN'].dt.time
        # departure_chart['DSG-DN'] = departure_chart['DSG-DN'].dt.time
        # departure_chart['SHD-DN'] = departure_chart['SHD-DN'].dt.time
        # departure_chart['RI-DN'] = departure_chart['RI-DN'].dt.time
        # departure_chart['DSG-UP'] = departure_chart['DSG-UP'].dt.time
        # departure_chart['SHD-UP'] = departure_chart['SHD-UP'].dt.time
        # departure_chart['RI-UP'] = departure_chart['RI-UP'].dt.time
        # departure_chart['NBAA-UP'] = departure_chart['NBAA-UP'].dt.time

        # departure_chart['STABLING-TIME'] = departure_chart['STABLING-TIME'].dt.time
        # # except:
        # #     pass

        # #Run for Duty formation from OR Tool outputd
        # departure_chart['Train_No'] = pd.to_numeric(departure_chart['Train_No'])
        # departure_chart['Last_Train'] = pd.to_numeric(departure_chart['Last_Train'])
        # departure_chart['Duty_No'] = pd.to_numeric(departure_chart['Duty_No'])

        # departure_chart['TrainSBC1'] = pd.to_numeric(departure_chart['TrainSBC1'])
        # departure_chart['TrainSBC2'] = pd.to_numeric(departure_chart['TrainSBC2'])

        # #Run for Duty formation from OR Tool output
        # for i in range(len(DC_FILL)):
        #     # try:
        #         if (not pd.isnull(DC_FILL.iloc[i]['SHD-UP'])) & (not pd.isnull(DC_FILL.iloc[i]['DSG-UP'])):
        #             # print(DC_FILL.iloc[i])
        #             DC_FILL.at[i,'SHDUPOUT'] = departure_chart[((departure_chart['Train_No']==int(DC_FILL.iloc[i]['TRAIN NO']))|(departure_chart['TrainSBC1']==int(DC_FILL.iloc[i]['TRAIN NO']))|(departure_chart['TrainSBC2']==int(DC_FILL.iloc[i]['TRAIN NO']))) & (departure_chart['SHD-UP']== DC_FILL.iloc[i]['SHD-UP']) & (departure_chart['SHD-UP'] == departure_chart['Trip_Start'])]['Duty_No']     
        #     #         print(DC_FILL.iloc[i])
        #     # except:
        #     #     pass

        #     # try:
        #         if not pd.isnull(DC_FILL.iloc[i]['RI-UP']):
        #     #         print(DC_FILL.iloc[i])
        #             DC_FILL.at[i,'RI-OUT'] = departure_chart[((departure_chart['Train_No']==int(DC_FILL.loc[i]['TRAIN NO']))|(departure_chart['TrainSBC1']==int(DC_FILL.loc[i]['TRAIN NO']))|(departure_chart['TrainSBC2']==int(DC_FILL.loc[i]['TRAIN NO']))) & (departure_chart['RI-UP']== DC_FILL.loc[i]['RI-UP'])]['Duty_No']     
        #     #         print(DC_FILL.iloc[i])
        #     # except:
        #     #     pass
            
        #     # try:
        #         if not pd.isnull(DC_FILL.iloc[i]['SHD-DN']):
        #             if pd.isnull(DC_FILL.iloc[i]['NBAA-DN']):
        #     #             print(DC_FILL.iloc[i])
        #                 DC_FILL.at[i,'SHDDNOUT'] = departure_chart[((departure_chart['Train_No']==int(DC_FILL.iloc[i]['TRAIN NO']))|(departure_chart['TrainSBC1']==int(DC_FILL.iloc[i]['TRAIN NO']))|(departure_chart['TrainSBC2']==int(DC_FILL.iloc[i]['TRAIN NO']))) & (departure_chart['SHD-DN']== DC_FILL.iloc[i]['SHD-DN']) & (DC_FILL.iloc[i]['SHD-DN'] < departure_chart['Trip_End'])]['Duty_No']     
        #     #             print(DC_FILL.iloc[i])
        #             if not pd.isnull(DC_FILL.iloc[i]['NBAA-DN']):
        #     #             print(DC_FILL.iloc[i])
        #                 DC_FILL.at[i,'SHDDNOUT'] = departure_chart[((departure_chart['Train_No']==int(DC_FILL.iloc[i]['TRAIN NO']))|(departure_chart['TrainSBC1']==int(DC_FILL.iloc[i]['TRAIN NO']))|(departure_chart['TrainSBC2']==int(DC_FILL.iloc[i]['TRAIN NO']))) & (departure_chart['SHD-DN']== DC_FILL.iloc[i]['SHD-DN']) & (departure_chart['SHD-DN'] == departure_chart['Trip_Start'])]['Duty_No']     
        #     #             print(DC_FILL.iloc[i])
        #     # except:
        #     #     pass

        #     # try:
        #         if not pd.isnull(DC_FILL.iloc[i]['DSG-DN']):
        #     #         print(DC_FILL.iloc[i])
        #             DC_FILL.at[i,'DSGDNOUT'] = departure_chart[((departure_chart['Train_No']==int(DC_FILL.iloc[i]['TRAIN NO']))|(departure_chart['TrainSBC1']==int(DC_FILL.iloc[i]['TRAIN NO']))|(departure_chart['TrainSBC2']==int(DC_FILL.iloc[i]['TRAIN NO']))) & (departure_chart['DSG-DN']== DC_FILL.iloc[i]['DSG-DN'])]['Duty_No']     
        #     #         print(DC_FILL.iloc[i])
        #     # except:
        #     #     pass


        # #Run for Duty formation from OR Tool output

        # DC_FILL1 = DC_FILL.copy()
        # DC_FILL1 = DC_FILL1.reindex(columns = ['TRAIN NO','DEPOT', 'INDUCTION', 'INDUCTION-TIME', 'INDUCTION-DUTY','NBAA-DN', 'DSG-DN', 'DSGDNOUT', 
        #                                        'SHD-DN','SHDDNOUT','KG-DN', 'RI-DN', 'RI-UP', 'RI-OUT', 'SLAP', 'SHD-UP', 'SHDUPOUT',
        #                                        'DSG-UP', 'NBAA-UP', 'DEPOT.1','STABLING-DUTY','STABLING', 'STABLING-TIME'])
        # # DC_FILL1['STABLING'] = DC_FILL1['STABLING'].astype(object)

        # df_final['Train_No'] = pd.to_numeric(df_final['Train_No'])
        # df_final['Last_Train'] = pd.to_numeric(df_final['Last_Train'])

        # #Trainwise induction and induction_location detail 
        # df_induction = df_final[df_final['INDUCTION-TIME'].notnull() | df_final['INDUCTION'].notnull()].reindex(columns = ['Train_No','INDUCTION',
        #                                                                                                                    'INDUCTION-TIME'])
        # df_induction = df_induction.dropna(subset=['INDUCTION', 'INDUCTION-TIME'])
        # df_induction.set_index('Train_No', drop = True, inplace=True)
        # df_induction['INDUCTION-TIME'] = df_induction['INDUCTION-TIME'].dt.time

        # df_stabling = df_final[df_final['STABLING'].notnull() | df_final['STABLING-TIME'].notnull()].reindex(columns = ['Last_Train','STABLING','STABLING-TIME'])
        # df_stabling = df_stabling.dropna(subset=['STABLING','STABLING-TIME'])
        # df_stabling.set_index('Last_Train', drop = True, inplace=True)
        # df_stabling['STABLING-TIME'] = df_stabling['STABLING-TIME'].dt.time

        # for train_number in df_induction.index.values:
        #     first_occurance_index = DC_FILL1.loc[DC_FILL1['TRAIN NO'] == train_number].index[0]
        #     DC_FILL1.loc[first_occurance_index,'INDUCTION'] = df_induction.loc[train_number,'INDUCTION']
        #     DC_FILL1.loc[first_occurance_index,'INDUCTION-TIME'] = df_induction.loc[train_number,'INDUCTION-TIME']
            
        # # try:
        # for train_number in df_stabling.index.values:
        #     last_occurance_index = DC_FILL1.loc[DC_FILL1['TRAIN NO'] == train_number].index[-1]
        #     # print(f"Train No: {train_number} Last_Index: {last_occurance_index}")
        #     DC_FILL1.loc[last_occurance_index,'STABLING'] = df_stabling.loc[train_number,'STABLING']
        #     DC_FILL1.loc[last_occurance_index,'STABLING-TIME'] = df_stabling.loc[train_number,'STABLING-TIME']
        # # except:
        # #     pass

        # departure_chart['Train_No'] = pd.to_numeric(departure_chart['Train_No'])
        # departure_chart['Last_Train'] = pd.to_numeric(departure_chart['Last_Train'])

        # induction_duty = departure_chart[departure_chart['INDUCTION'].notnull() | departure_chart['INDUCTION-TIME'].notnull()].reindex(
        #                  columns = ['Train_No', 'Duty_No', 'INDUCTION','INDUCTION-TIME'])
        # induction_duty.set_index('Train_No', drop = True, inplace= True)
        # induction_duty['Duty_No'] = induction_duty['Duty_No'].astype(int)

        # stabling_duty = departure_chart[departure_chart['STABLING'].notnull() | departure_chart['STABLING-TIME'].notnull()].reindex(
        #                 columns = ['Last_Train', 'Duty_No', 'STABLING','STABLING-TIME'])
        # stabling_duty.set_index('Last_Train', drop = True, inplace= True)
        # stabling_duty['Duty_No'] = stabling_duty['Duty_No'].astype(int)

        # for train_number in induction_duty.index.values:
        #     first_index_number = DC_FILL1[DC_FILL1['TRAIN NO'] == train_number].index[0]
        #     DC_FILL1.loc[first_index_number, 'INDUCTION-DUTY'] = induction_duty.loc[train_number, 'Duty_No']

        # for train_number in stabling_duty.index.values:
        #     last_index_number = DC_FILL1[DC_FILL1['TRAIN NO'] == train_number].index[-1]
        #     DC_FILL1.loc[last_index_number, 'STABLING-DUTY'] = stabling_duty.loc[train_number, 'Duty_No']
            
        # for column in ['DEPOT','INDUCTION-TIME', 'NBAA-DN', 'DSG-DN',
        #        'SHD-DN', 'KG-DN','RI-DN', 'RI-UP', 'SLAP',
        #        'SHD-UP', 'DSG-UP', 'NBAA-UP', 'DEPOT.1',
        #        'STABLING-TIME']:
        #     DC_FILL1[column] = DC_FILL1[column].astype(str)
        #     DC_FILL1[column] = DC_FILL1[column].replace(r'(\d{2}:\d{2}):\d{2}',r'\1', regex=True)
        #     DC_FILL1[column] = DC_FILL1[column].replace('nan', '', regex=True)
        #     DC_FILL1[column] = DC_FILL1[column].replace('NaT', '', regex=True)

        # DC_FILL1.replace('SBC1','DSG',regex=True,inplace=True)
        # DC_FILL1.replace('SBC2','RI',regex=True,inplace=True)
        # DC_FILL1.replace('CC','SHD-',regex=True,inplace=True)

        # DC_FILL1.to_excel(r"L1-SUN-892025-DC_FILL1.xlsx")
    except Exception as e:
        update_status(execution_id, "Pipeline Broke--", "error", str(e))

if __name__ == "__main__":
    print('WE GOT HERE AGAIN')
    main()