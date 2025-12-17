import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')


def main():
    import sys
    import json
    import shutil
    import random
    import time
    from helpers import update_status

    # ------------------------------------------------------------------
    # CBC check
    # ------------------------------------------------------------------
    cbc_path = shutil.which("cbc")
    if not cbc_path:
        print("CBC solver not found in PATH!")
        print("Please install CBC: https://github.com/coin-or/Cbc/releases")
        sys.exit(1)

    print(f"CBC solver detected at: {cbc_path}")
    print("simulate_runnerL5.py started!")
    print("Received args:", sys.argv)

    # ------------------------------------------------------------------
    # CLI ARGS (from process_fileL5)
    # ------------------------------------------------------------------
    execution_id = sys.argv[1]
    file_path = sys.argv[2]
    stepping_back_raw = sys.argv[3]     # JSON dict
    timetable_type = sys.argv[4]
    single_run_max = sys.argv[5]
    break_small = int(sys.argv[6])
    break_large = int(sys.argv[7])

    print("Timetable Type:", timetable_type)
    print(f"single_run_max={single_run_max}, break_small={break_small}, break_large={break_large}")

    # ------------------------------------------------------------------
    # DEFAULTS (IMPORTANT: always exist)
    # ------------------------------------------------------------------
    SBC1startHour = 0
    SBC1startMinute = 0
    SBC1endHour = 23
    SBC1endMinute = 59

    SBC2startHour = 0
    SBC2startMinute = 0
    SBC2endHour = 23
    SBC2endMinute = 59

    # ------------------------------------------------------------------
    # Load stepping back configuration
    # ------------------------------------------------------------------
    try:
        stepping_back = json.loads(stepping_back_raw)
        if not isinstance(stepping_back, dict):
            raise ValueError("stepping_back is not a dict")
    except Exception as e:
        print("⚠️ Invalid stepping_back data, defaulting to empty config")
        print("Error detail:", e)
        stepping_back = {}

    # Ensure structure
    for station in ("SBC1", "SBC2"):
        stepping_back.setdefault(
            station,
            {"enabled": False, "start": "00:00", "end": "23:59"}
        )

    # ------------------------------------------------------------------
    # Helper: safe time parsing
    # ------------------------------------------------------------------
    def safe_parse_time(time_str, default="00:00"):
        try:
            hh, mm = str(time_str or default).split(":")
            return max(0, min(23, int(hh))), max(0, min(59, int(mm)))
        except Exception:
            hh, mm = default.split(":")
            return int(hh), int(mm)

    # ------------------------------------------------------------------
    # Apply stepping-back configuration
    # ------------------------------------------------------------------
    if stepping_back["SBC1"]["enabled"]:
        SBC1startHour, SBC1startMinute = safe_parse_time(stepping_back["SBC1"]["start"])
        SBC1endHour, SBC1endMinute = safe_parse_time(stepping_back["SBC1"]["end"])
        print(f"SBC1 ACTIVE: {SBC1startHour:02}:{SBC1startMinute:02} → {SBC1endHour:02}:{SBC1endMinute:02}")
    else:
        print("SBC1 is disabled")

    if stepping_back["SBC2"]["enabled"]:
        SBC2startHour, SBC2startMinute = safe_parse_time(stepping_back["SBC2"]["start"])
        SBC2endHour, SBC2endMinute = safe_parse_time(stepping_back["SBC2"]["end"])
        print(f"SBC2 ACTIVE: {SBC2startHour:02}:{SBC2startMinute:02} → {SBC2endHour:02}:{SBC2endMinute:02}")
    else:
        print("SBC2 is disabled")

    # ------------------------------------------------------------------
    # FINAL DEBUG (guaranteed safe)
    # ------------------------------------------------------------------
    print("\n=== FINAL STEPPING BACK VALUES ===")
    print("SBC1:", SBC1startHour, SBC1startMinute, SBC1endHour, SBC1endMinute)
    print("SBC2:", SBC2startHour, SBC2startMinute, SBC2endHour, SBC2endMinute)

    print("\nTRY PRINTING SBC1 VARIABLES")
    time.sleep(1)
    print(
        f"SBC1startHour={SBC1startHour}, "
        f"SBC1startMinute={SBC1startMinute}, "
        f"SBC1endHour={SBC1endHour}, "
        f"SBC1endMinute={SBC1endMinute}"
    )


    try:
        print('TRY PRINTING SBC1Hour')
        time.sleep(2)
        print(f'SBC1startHour {SBC1startHour} SBC1startMinute {SBC1startMinute} SBC2startHour {SBC2startHour}')

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
        update_status(execution_id, "STAGE 1 of 4 in progress","WIP")
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
                    try:
                        if (rail[x].index[a] not in {'CCDN','CCUP','SBC1','SBC2'}) & (a == 0):
                            route.update({'INDUCTION' : rail[x].index[a],'INDUCTION-TIME' : rail[x].iloc[a, 0],'INDUCTION_STATION' :rail[x].index[a+1],'SERVICE-TIME' : rail[x].iloc[a+1, 0]})
                            continue
                        if a ==rail[x].shape[0] - 1:
                            route.update({'STABLING' : rail[x].index[a],'STABLING-TIME' : rail[x].iloc[a, 0] })
                            continue
                            
                        if rail[x].index[a] == 'CIPK' and rail[x].index[a+1] == 'CIPK':
                            route.update({'CIPK-DN': rail[x].iloc[a, 0]})
                            continue
                        if rail[x].index[a] == 'CIPK' and rail[x].index[a+1] != 'CIPK':
                            route.update({'CIPK-UP': rail[x].iloc[a, 0]})
                            continue
                            
                        if rail[x].index[a] in (['ILOK','SBC1']) and rail[x].index[a+1] not in (['ILOK','SBC1']):
                            route.update({'ILOK-DN': rail[x].iloc[a, 0]})
                            continue
                        if rail[x].index[a] in (['KTNR','SBC2']) and rail[x].index[a+1] in (['KTNR','SBC2']):
                            route.update({'KTNR-UP': rail[x].iloc[a, 0]})
                            continue
                        if rail[x].index[a] == 'CCDN':
                            route.update({'MUDK-DN': rail[x].iloc[a, 0]})
                            continue
                        if rail[x].index[a] in (['KTNR','SBC2']) and rail[x].index[a+1] not in (['KTNR','SBC2']):
                            route.update({'KTNR-DN': rail[x].iloc[a, 0]})
                            continue
                        if rail[x].index[a] == 'CCUP':
                            route.update({'MUDK-UP': rail[x].iloc[a, 0]})
                            continue
                        if rail[x].index[a] in (['ILOK','SBC1']) and rail[x].index[a+1] in (['ILOK','SBC1']):
                            route.update({'ILOK-UP': rail[x].iloc[a, 0]})
                            continue
                    except:
                        print('Reached exception')
                        pass
                    

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
                    while ((rail[x].iloc[j, 0] - rail[x].iloc[i, 0]) <= datetime.timedelta(hours=2, minutes=25)) & (
                            j < (rail[x].shape[0] - 1)):
                        # SBC1 step-back timmings
                                        ## SBC1 Timmings
                        # if (rail[x].index[j] == 'SBC1') & (rail[x].index[j + 1] == 'SBC1') & (rail[x].iloc[j, 0].hour >= 7) & (rail[x].iloc[j, 0].hour < 21) & ((rail[x].iloc[j, 0].minute >= 25 if (rail[x].iloc[j, 0].hour == 7) else True)):
                        if (rail[x].index[j] == 'SBC1') & (rail[x].index[j + 1] == 'SBC1') & (rail[x].iloc[j, 0].hour >= SBC1startHour) & (rail[x].iloc[j, 0].hour <= SBC1endHour) & (
                            rail[x].iloc[j, 0].minute >= SBC1startMinute if (rail[x].iloc[j, 0].hour == SBC1startHour) else True) & (
                            rail[x].iloc[j, 0].minute <= SBC1endMinute if (rail[x].iloc[j, 0].hour == SBC1endHour) else True):
                        # if (rail[x].index[j] == 'SBC1') & (rail[x].index[j + 1] == 'SBC1') & (rail[x].iloc[j, 0].hour >= 7) & (rail[x].iloc[j, 0].hour < 11) & ((rail[x].iloc[j, 0].minute >= 20 if (rail[x].iloc[j, 0].hour == 7) else True)) & ((rail[x].iloc[j, 0].minute <= 40 if (rail[x].iloc[j, 0].hour == 11) else True)):
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
                        # SBC2 step-back timmings
                        # if (rail[x].index[j] == 'SBC2') & (rail[x].index[j + 1] == 'SBC2') & ((rail[x].iloc[j, 0].hour >= 7)) & ((rail[x].iloc[j, 0].minute >= 20 if (rail[x].iloc[j, 0].hour == 7) else True)) & (rail[x].iloc[j, 0].hour < 21):
                        # if (rail[x].index[j] == 'SBC2') & (rail[x].index[j + 1] == 'SBC2') & (rail[x].iloc[j, 0].hour >= 7) & (rail[x].iloc[j, 0].hour <= 11) & (
                        #     rail[x].iloc[j, 0].minute >= 30 if (rail[x].iloc[j, 0].hour == 7) else True) & (
                        #     rail[x].iloc[j, 0].minute <= 00 if (rail[x].iloc[j, 0].hour == 11) else True):  

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
        dumtrips.sort_values(['Trip_End'], inplace=True)
        dumtrips.reset_index(drop=True, inplace=True)
        while (dumtrips.size != 0):
            print('Total_Trips:', len(comptrip.index))
            comptrip = pd.DataFrame(
                columns=['Train_No', 'LocationPick', 'Trip_Start', 'LocationRelieve', 'Trip_End', 'Trip_Duration'])
            dumtrips = trips.copy()
            dumtrips.sort_values(['Trip_End'], inplace=True)
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
                dumtrips.sort_values(['Trip_End'], inplace=True)
                dumtrips.reset_index(drop=True, inplace=True)
                y = 0
                while y < len(dumtrips.index):
                    breaked = 0
                    ###Randomly Breaking Trips###
                    if ((
                            trip['Trip_Duration'] > datetime.timedelta(hours=0,minutes=1)) & (trip['LocationRelieve'] in ( 'CCUP','CCDN'))):
                        breaked = 1
                        break
                    if breaked == 1:
                        break

                    ass = 0

                    ###FOR CC INCOMING TRAIN###
                    if ((dumtrips['Train_No'][y] == trip['Train_No']) | (dumtrips['Train_No'][y] == trip['TrainSBC1']) | (
                            dumtrips['Train_No'][y] == trip['TrainSBC2'])) & (
                            dumtrips['Trip_Start'][y] == trip['Trip_End']) & (
                            dumtrips['Trip_End'][y] - trip['Trip_Start'] <= (datetime.timedelta(hours=2, minutes=30))) & (dumtrips['LocationPick'][y] == trip['LocationRelieve']):
                        trip['Trip_End'] = dumtrips['Trip_End'][y]
                        trip['Trip_Duration'] = dumtrips['Trip_End'][y] - trip['Trip_Start']
                        trip['LocationRelieve'] = dumtrips['LocationRelieve'][y]
                        dumtrips.drop(dumtrips.index[y], inplace=True)
                        dumtrips.sort_values(['Trip_End'], inplace=True)
                        dumtrips.reset_index(drop=True, inplace=True)
                        ass = 1


                    if (len(dumtrips.index) == 0) | (y == len(dumtrips.index)):
                        break
                    if (trip['LocationRelieve'] == 'SBC1') & (trip['TrainSBC1'] == '0') & (ass == 0):
                        z = 0
                        ass = 0
        #                 skip = 0
                        while z < len(dumtrips.index):
                            if (dumtrips['Trip_Start'][z] - trip['Trip_End'] >= datetime.timedelta(minutes=5)) & (
                                    trip['Train_No'] != dumtrips['Train_No'][z]) & (dumtrips['LocationPick'][z] == 'SBC1') & (trip['Trip_Duration'] + dumtrips['Trip_Duration'][z] <= datetime.timedelta(hours=2,minutes=35) ):
        #                         if (skip == 0) :
        #                             print('SKIP',dumtrips['Train_No'][z],dumtrips['Trip_Start'][z],trip['Trip_End'],dumtrips['LocationPick'][z],trip['Train_No'])
        #                             skip = 1 
        #                             z=z+1
        #                             continue
                                print(dumtrips['Train_No'][z],dumtrips['Trip_Start'][z],trip['Trip_End'],trip['Train_No'])
                                trip['TrainSBC1'] = dumtrips['Train_No'][z]
                                trip['Trip_End'] = dumtrips['Trip_End'][z]
                                trip['Trip_Duration'] = dumtrips['Trip_End'][z] - trip['Trip_Start']
                                trip['LocationRelieve'] = dumtrips['LocationRelieve'][z]
                                trip['MUDK-DN'] = trip['MUDK-DN'] if pd.isnull(dumtrips['MUDK-DN'][z]) else dumtrips['MUDK-DN'][z]
                                trip['MUDK-UP'] = trip['MUDK-UP'] if  pd.isnull(dumtrips['MUDK-UP'][z]) else dumtrips['MUDK-UP'][z]
                                trip['ILOK-DN'] = trip['ILOK-DN'] if pd.isnull(dumtrips['ILOK-DN'][z]) else dumtrips['ILOK-DN'][z]
                                trip['ILOK-UP'] = trip['ILOK-UP'] if pd.isnull(dumtrips['ILOK-UP'][z]) else dumtrips['ILOK-UP'][z]
                                trip['KTNR-DN'] = trip['KTNR-DN'] if pd.isnull(dumtrips['KTNR-DN'][z]) else dumtrips['KTNR-DN'][z]
                                trip['KTNR-UP'] = trip['KTNR-UP'] if pd.isnull(dumtrips['KTNR-UP'][z]) else dumtrips['KTNR-UP'][z]
                                trip['CIPK-DN'] = trip['CIPK-DN'] if pd.isnull(dumtrips['CIPK-DN'][z]) else dumtrips['CIPK-DN'][z]
                                trip['CIPK-UP'] = trip['CIPK-UP'] if pd.isnull(dumtrips['CIPK-UP'][z]) else dumtrips['CIPK-UP'][z]

                                dumtrips.drop(dumtrips.index[z], inplace=True)
                                dumtrips.sort_values(['Trip_End'], inplace=True)
                                dumtrips.reset_index(drop=True, inplace=True)
                                ass = 1
                                break
                            z = z + 1

                    if (trip['LocationRelieve'] == 'SBC2') & (trip['TrainSBC2'] == '0') & (ass == 0) :
        #DELETED CONDITION & (trip['Trip_Duration'] <= datetime.timedelta(hours=2))
                        z = 0
                        ass = 0
                        RISBCASSIGNED = (dumtrips[(dumtrips['Train_No'] == trip['Train_No']) & (dumtrips['LocationPick']=='SBC2')]['Trip_Start'].min()) if RISBCASSIGNED == '0' else RISBCASSIGNED
        #                 print('SBC',trip['Trip_Start'],RISBCASSIGNED,trip['Train_No'])
                        while z < len(dumtrips.index):
                            if (dumtrips['Trip_Start'][z] - trip['Trip_End'] > datetime.timedelta(minutes=5)) & (
                                (dumtrips['Train_No'][z] != trip['Train_No']) & (
                                dumtrips['Train_No'][z] != trip['TrainSBC1']) & (
                                dumtrips['Train_No'][z] != trip['TrainSBC2'])) & (
                                dumtrips['LocationPick'][z] == 'SBC2') & (dumtrips['Trip_Start'][z] != RISBCASSIGNED):
                                trip['TrainSBC2'] = dumtrips['Train_No'][z]
                                trip['Trip_End'] = dumtrips['Trip_End'][z]
                                trip['Trip_Duration'] = dumtrips['Trip_End'][z] - trip['Trip_Start']
                                trip['LocationRelieve'] = dumtrips['LocationRelieve'][z]
                                trip['MUDK-DN'] = trip['MUDK-DN'] if pd.isnull(dumtrips['MUDK-DN'][z]) else dumtrips['MUDK-DN'][z]
                                trip['MUDK-UP'] = trip['MUDK-UP'] if  pd.isnull(dumtrips['MUDK-UP'][z]) else dumtrips['MUDK-UP'][z]
                                trip['ILOK-DN'] = trip['ILOK-DN'] if pd.isnull(dumtrips['ILOK-DN'][z]) else dumtrips['ILOK-DN'][z]
                                trip['ILOK-UP'] = trip['ILOK-UP'] if pd.isnull(dumtrips['ILOK-UP'][z]) else dumtrips['ILOK-UP'][z]
                                trip['KTNR-DN'] = trip['KTNR-DN'] if pd.isnull(dumtrips['KTNR-DN'][z]) else dumtrips['KTNR-DN'][z]
                                trip['KTNR-UP'] = trip['KTNR-UP'] if pd.isnull(dumtrips['KTNR-UP'][z]) else dumtrips['KTNR-UP'][z]
                                trip['CIPK-DN'] = trip['CIPK-DN'] if pd.isnull(dumtrips['CIPK-DN'][z]) else dumtrips['CIPK-DN'][z]
                                trip['CIPK-UP'] = trip['CIPK-UP'] if pd.isnull(dumtrips['CIPK-UP'][z]) else dumtrips['CIPK-UP'][z]
                                
                                dumtrips.drop(dumtrips.index[z], inplace=True)
                                dumtrips.sort_values(['Trip_End'], inplace=True)
                                dumtrips.reset_index(drop=True, inplace=True)
                                ass = 1
                                break
                            z = z + 1

        #             if (ass == 1) & (trip['Trip_Duration'] > datetime.timedelta(minutes=30)):
        #                 break
                    y = (y + 1) if ass == 0 else 0
                comptrip = comptrip.append(trip)
                dumtrips.sort_values(['Trip_End'], inplace=True)
                dumtrips.reset_index(drop=True, inplace=True)
                x = 0

        comptrip.sort_values(['Trip_Start'],inplace=True)  
        comptrip.reset_index(drop=True, inplace=True)
        print('The_End')
        print('Total_Trips:', len(comptrip.index))

        # comptrip.to_excel(r'comptrip.xlsx')

        comptrip.reset_index(drop= True, inplace= True)
        trips1 = comptrip.copy()

        # For KTNR reversal train put time in ILOK column blank
        for i in range(len(trips1)):
            if pd.notnull(trips1.iloc[i]['KTNR-DN']) | pd.notnull(trips1.iloc[i]['KTNR-UP']):
                trips1.loc[i,'ILOK-DN'] = pd.NaT

        comptrip.to_excel(f"temp_files/{execution_id}comptrip.xlsx")
        update_status(execution_id, "STAGE 1 complete", "completed")
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
                df.at[index, 'Step Back Location'] = 'ILOK'
            elif pd.notna(df.at[index, 'TrainSBC2']) and df.at[index, 'TrainSBC2'] != '0':
                df.at[index, 'Step Back Rake'] = df.at[index, 'TrainSBC2']
                df.at[index, 'Step Back Location'] = 'KTNR'
            else:
                df.at[index, 'Step Back Rake'] = 'No StepBack'
                df.at[index, 'Step Back Location'] = 'No StepBack'
            if df.at[index, 'LocationPick'] in ('CCDN','CCUP'):
                df.at[index, 'Direction'] = 'DN' if df.at[index, 'LocationPick'] == 'CCDN' else 'UP' 
            else:
                df.at[index, 'Direction'] = 'DN' if df.at[index, 'LocationRelieve'] == 'CCDN' else 'UP'

        cols = ['MUDK-UP', 'ILOK-DN','KTNR-DN', 'KTNR-UP', 'ILOK-UP', 'MUDK-DN', 'CIPK-UP', 'CIPK-DN']
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
                    if df.loc[i, 'Step Back Location'] == "ILOK":
                        SB_location = "ILOK-UP"
                    if df.loc[i, 'Step Back Location'] == "KTNR":
                        SB_location = "KTNR-UP"
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

        update_status(execution_id, "STAGE 2 of 4 in progress", "WIP")
        import csv
        from collections import defaultdict
        import os

        def hhmm_to_minutes(hhmm: str) -> int:
            h, m = map(int, hhmm.split(":"))
            return h * 60 + m

        # Parameters
        Duty_hours = 460
        # Duty_hours = hhmm_to_minutes(duty_hours)
        Driving_duration = 375
        # Driving_duration = hhmm_to_minutes(running_hours)
        # Continuous_Driving_time = 180
        Continuous_Driving_time = hhmm_to_minutes(single_run_max)
        # long_break = 50
        long_break = int(break_large)
        # short_break = 30
        short_break = int(break_small)

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
        update_status(execution_id, f"STAGE 2 complete", "completed")
        print("Done!")

        update_status(execution_id, f"STAGE 3 of 4 in progress", "WIP")
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
                logging.error(f"Missing {description} file: {path}")
                logging.error("Make sure the file exists and is not locked by another process.")
                raise FileNotFoundError(f"{description} file not found: {path}")
            else:
                logging.info(f"Found {description} file: {path}")


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
            logging.error("Failed to load input services file.", exc_info=True)
            logging.error("Check file format, encoding, and content (must have at least one column).")
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
                        logging.warning(f"Non-numeric data found in row {index}: {row}")
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

            logging.info(f"Loaded {len(service_assignments)} valid duty assignments.")
        except Exception as e:
            logging.error("Failed to load duties file.", exc_info=True)
            logging.error("Ensure CSV format is valid and IDs match the services list.")
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

            logging.info("Pyomo model successfully built.")
        except Exception as e:
            logging.error("Error while building Pyomo model.", exc_info=True)
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
            logging.critical("All solver attempts failed.")
            logging.critical("Ensure CBC or GLPK is installed and available in system PATH.")
            sys.exit(1)

        logging.info(f"Solver status: {getattr(results.solver, 'status', 'UNKNOWN')}")
        logging.info(f"Termination condition: {getattr(results.solver, 'termination_condition', 'UNKNOWN')}")


        # ------------------ PROCESS RESULTS ------------------
        log_divider("STEP 5: Writing Solution")

        try:
            if getattr(results.solver, "termination_condition", None) == TerminationCondition.infeasible:
                logging.warning("Model infeasible — some services not covered by any duty.")
            else:
                total_duties = 0
                with open(SOLUTION_FILE, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    for path_var in model.fPath:
                        val = value(model.fPath[path_var])
                        if abs(val - 1) <= 1e-6:
                            writer.writerow(service_assignments[path_var])
                            total_duties += 1
                logging.info(f"Solution written to: {SOLUTION_FILE}")
                logging.info(f"Total duties selected: {total_duties}")
        except Exception as e:
            logging.error("Error writing solution file.", exc_info=True)
            logging.error("Check write permissions or file locks.")
            sys.exit(1)


        # ------------------ COMPLETION ------------------
        log_divider("EXECUTION COMPLETE")
        logging.info("Script finished successfully.")

        # Example status updates
        update_status(execution_id, "STAGE 3 Complete", "completed")
        update_status(execution_id, "STAGE 4 of 4 in progress", "WIP")

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

        print("\n Duty assignment complete.")
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

        duty2.replace('CCUP','MUDK-UP',regex=True,inplace=True)
        duty2.replace('CCDN','MUDK-DN',regex=True,inplace=True)

        duty2.replace('SBC1','ILOK',regex=True,inplace=True)
        duty2.replace('SBC2','KTNR',regex=True,inplace=True)

        duty2['ACTUAL_DUTYHOURS'] = pd.to_timedelta(duty2['ACTUAL_DUTYHOURS'], errors='coerce')

        duty2['ACTUAL_DUTYHOURS'] = (duty2['ACTUAL_DUTYHOURS'] % pd.Timedelta(days=1))


        duty2.to_excel(f"temp_files/trip_chart_{execution_id}.xlsx")

        # --------------Generate DC


    except Exception as e:
        update_status(execution_id, "Pipeline Broke--", "error", str(e))

if __name__ == "__main__":
    print('WE GOT HERE AGAIN')
    main()