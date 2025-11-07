# import csv
# from collections import defaultdict
# import os
# import concurrent.futures

# # ---- Definitions, Classes, Helpers (all top level, BEFORE main) ----

# Duty_hours = 440
# Driving_duration = 360
# Continuous_Driving_time = 170
# long_break = 50
# short_break = 30

# YB_Jurisdiction = ['SDG-YB','DYB', 'YBSDG', 'SBC2', 'NESY', 'YBUP', 'YBDN', 'NSST/KSHI', 'SBC3', 'NECCSDG', 'VASIO/S']
# DW_Jurisdiction = ['NFD', 'KNR', 'DWDN', 'DWUP', 'DW3RD', 'JPW', 'DSTOSDG', 'SBC1', 'DWT']
# cc1 = YB_Jurisdiction
# cc2 = DW_Jurisdiction
# crewControl = ['YBDN', 'YBUP', 'DWDN', 'DWUP', 'DWT']
# crewControlSet = set(crewControl)

# def min2hhmm(mins):
#     h = mins // 60
#     mins = mins % 60
#     return f"{h:02d}:{mins:02d}"

# def hhmm2mins(hhmm):
#     parts = hhmm.split(":")
#     if len(parts) == 2:
#         hrs, mins = int(parts[0]), int(parts[1])
#     elif len(parts) == 3:
#         hrs, mins = int(parts[0]), int(parts[1])
#     else:
#         raise ValueError(f"Invalid time format: {hhmm}")
#     return hrs * 60 + mins

# class Services:
#     def __init__(self, attrs):
#         self.servNum = attrs[0]
#         self.trainNum = int(attrs[1])
#         self.startStn = attrs[2]
#         self.startTime = hhmm2mins(attrs[3])
#         self.endStn = attrs[4]
#         self.endTime = hhmm2mins(attrs[5])
#         self.dir = attrs[6]
#         self.servDur = int(attrs[7])
#         self.stepbackTrainNum = attrs[9]
#         self.servAdded = False
#         self.breakDur = 0
#         self.tripDur = 0

# def fetchData(csv_path='redefinedinputparameters.csv'):
#     servicesLst = []
#     with open(csv_path) as output:
#         reader = csv.reader(output)
#         next(reader)
#         for row in reader:
#             servicesLst.append(Services(row))
#     return servicesLst

# def canFollow(s1, s2):
#     if s1.endStn == s2.startStn and s1.endTime == s2.startTime:
#         if s1.stepbackTrainNum == "No StepBack":
#             rake_ok = s1.trainNum == s2.trainNum
#         else:
#             rake_ok = int(s1.stepbackTrainNum) == s2.trainNum
#         if rake_ok:
#             cont_drive = s2.endTime - s1.startTime
#             return cont_drive <= Continuous_Driving_time and (s2.endTime - s1.startTime) <= Duty_hours
#         return False

#     gap = s2.startTime - s1.endTime
#     if short_break <= gap <= 140 and s1.endStn[:4] in crewControlSet:
#         return s1.endStn[:2] == s2.startStn[:2] and (s2.endTime - s1.startTime) <= Duty_hours
#     return False

# def exceeds_continuous_driving(path, limit=Continuous_Driving_time, short_break=30):
#     cont_drive = path[0].endTime - path[0].startTime
#     for i in range(1, len(path)):
#         prev = path[i - 1]
#         curr = path[i]
#         gap = curr.startTime - prev.endTime
#         if gap >= short_break:
#             cont_drive = curr.endTime - curr.startTime
#         else:
#             cont_drive += curr.endTime - prev.endTime
#         if cont_drive > limit:
#             return True
#     return False

# def build_trip_graph(services):
#     graph = defaultdict(list)
#     total = len(services)
#     for i in range(total):
#         s1 = services[i]
#         for j in range(i + 1, total):
#             s2 = services[j]
#             if s2.startTime - s1.endTime > 120:
#                 break
#             if canFollow(s1, s2):
#                 graph[s1.servNum].append(s2)
#     return graph

# def check_additional_constraints(path):
#     for i in range(len(path) - 1):
#         if path[i].endStn == "DWT":
#             gap = path[i + 1].startTime - path[i].endTime
#             if not (40 <= gap <= 49 or gap > 60):
#                 return False

#     cont_drive = path[0].endTime - path[0].startTime
#     for i in range(1, len(path)):
#         gap = path[i].startTime - path[i - 1].endTime
#         if gap >= short_break:
#             if cont_drive >= 140 and gap < 40:
#                 return False
#             break
#         else:
#             cont_drive += path[i].endTime - path[i - 1].endTime

#     return True

# def generate_duties(start_trip, graph, cc1, cc2, max_depth=10):
#     stack = [(start_trip, [start_trip])]
#     valid_duties = []

#     while stack:
#         current, path = stack.pop()
#         start_time = path[0].startTime
#         end_time = path[-1].endTime
#         duty_dur = end_time - start_time
#         if duty_dur > Duty_hours:
#             continue

#         break_dur = 0
#         has_long_break = False
#         jurisdictional_break_found = False
#         invalid_break = False

#         if path[0].startStn in cc1:
#             starting_jurisdiction = cc1
#         elif path[0].startStn in cc2:
#             starting_jurisdiction = cc2
#         else:
#             starting_jurisdiction = None

#         for i in range(len(path) - 1):
#             gap = path[i + 1].startTime - path[i].endTime
#             nxt = path[i+1]
#             if (
#                 nxt.startStn  == "DWDN" and
#                 nxt.endStn    == "NFD"   and
#                 nxt.startTime < 22 * 60 and
#                 gap < short_break
#             ):
#                 invalid_break = True
#                 break

#             break_dur += gap

#             if gap > 140:
#                 invalid_break = True
#                 break

#             if gap >= long_break:
#                 has_long_break = True

#             if gap >= short_break and starting_jurisdiction:
#                 if path[i].endStn in starting_jurisdiction:
#                     jurisdictional_break_found = True

#         if invalid_break:
#             continue

#         driving_dur = duty_dur - break_dur
#         if driving_dur > Driving_duration:
#             continue

#         if exceeds_continuous_driving(path):
#             continue

#         good_duty = break_dur <= 120
#         valid_jurisdiction = (
#             (path[0].startStn in cc1 and path[-1].endStn in cc1) or
#             (path[0].startStn in cc2 and path[-1].endStn in cc2)
#         )
#         if start_time < 6 * 60:
#             total_trip_duration = sum(s.servDur for s in path)
#             if total_trip_duration >= 330:
#                 continue

#         first_break_threshold = 80 if path[0].trainNum in (398, 399, '398','399') else 40

#         continuous_end = path[0].endTime
#         for i in range(1, len(path)):
#             gap = path[i].startTime - path[i-1].endTime
#             if gap < first_break_threshold:
#                 continuous_end = path[i].endTime
#             else:
#                 break

#         initial_cont = continuous_end - path[0].startTime
#         first_cont_trip = (initial_cont <= 30)

#         breaks = []
#         if has_long_break:
#             for i in range(len(path)-1):
#                 gap = path[i+1].startTime - path[i].endTime
#                 if gap > 0:
#                     breaks.append(gap)

#         if has_long_break:
#             first_break_valid = (breaks[0] >= first_break_threshold)
#         else:
#             first_break_valid = False

#         second_break_valid = (breaks[1] >= 40) if (len(breaks) > 1) else False

#         crewcontrolending = (path[-1].endStn in crewControlSet and end_time >= (23*60 + 30))
#         if (
#             len(path) > 1 and
#             has_long_break and
#             valid_jurisdiction and
#             jurisdictional_break_found and
#             good_duty and
#             check_additional_constraints(path) and
#             second_break_valid and
#             first_break_valid and 
#             not first_cont_trip
#         ):
#             valid_duties.append([s.servNum for s in path])

#         if len(path) >= max_depth:
#             continue

#         for next_trip in graph.get(current.servNum, []):
#             if next_trip in path:
#                 continue
#             stack.append((next_trip, path + [next_trip]))

#     return valid_duties

# def chunk_indices(total, chunk_spans):
#     ranges = []
#     start = 0
#     for span in chunk_spans:
#         end = min(start + span, total)
#         ranges.append((start, end))
#         start = end
#         if start >= total:
#             break
#     if start < total:
#         ranges.append((start, total))
#     return ranges

# # --- Multiprocessing block helpers ---
# def process_range(args):
#     start, end = args
#     sub_duties = []
#     for i in range(start, end):
#         duties = generate_duties(services[i], graph, cc1, cc2)
#         print(f"Subprocess [{i+1}/{len(services)}] {services[i].servNum}: {len(duties)} duties")
#         sub_duties.extend(duties)
#     return sub_duties

# def parallel_generate_duties_and_return(chunk_spans=None):
#     total = len(services)
#     if chunk_spans is None:
#         chunk_spans = [50, 50, 100, 200, 300, 300]
#     chunks = chunk_indices(total, chunk_spans)
#     args = [(start, end) for (start, end) in chunks]
#     all_duties = []
#     with concurrent.futures.ProcessPoolExecutor() as executor:
#         results = executor.map(process_range, args)
#         for duty_chunk in results:
#             all_duties.extend(duty_chunk)
#     print(f"\n✅ Total valid duties generated: {len(all_duties)}")
#     return all_duties

# def save_duties_to_csv(duty_pool, filename='generated_dutiesnewcc.csv', max_depth=None):
#     if max_depth is None:
#         max_depth = max(len(duty) for duty in duty_pool) if duty_pool else 0

#     with open(filename, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([''] + list(range(max_depth)))
#         for idx, duty in enumerate(duty_pool):
#             row = [idx] + duty[:max_depth] + [''] * (max_depth - len(duty))
#             writer.writerow(row)

#     print(f"\n✅ Duty pool saved to '{os.path.abspath(filename)}'.")

# # =================[ MAIN EXECUTION BLOCK ]=================

# if __name__ == '__main__':

#     # ---- Code before parallel block (PREVIOUS) ----
#     print("Starting pre-processing...")
#     # [Your earlier processing code can go here]

#     # ---- Data Loading Section ----
#     print("Loading services...")
#     services = fetchData('redefinedinputparameters.csv')
#     print(f"Total services loaded: {len(services)}")

#     print("Building graph...")
#     graph = build_trip_graph(services)

#     # ---- Parallel Duty Generator Section ----
#     print("Generating duty pool (parallel)...")
#     duty_pool = parallel_generate_duties_and_return()

#     # ---- Code after duty pool generation (FURTHER) ----
#     # You can add further processing, analytics, or file saving here:
#     print("Saving duties to CSV...")
#     save_duties_to_csv(duty_pool)
#     print("✅ Done.")

import csv
from collections import defaultdict
import os
import concurrent.futures
import sys
# ---- Definitions, Classes, Helpers ----

Duty_hours = 440
Driving_duration = 360
Continuous_Driving_time = 170
long_break = 50
short_break = 30
execution_id = sys.argv[1]
timetable_type = sys.argv[2]
print('ARGS IN PARALLEL FILE', execution_id)
YB_Jurisdiction = ['SDG-YB','DYB', 'YBSDG', 'SBC2', 'NESY', 'YBUP', 'YBDN', 'NSST/KSHI', 'SBC3', 'NECCSDG', 'VASIO/S']
DW_Jurisdiction = ['NFD', 'KNR', 'DWDN', 'DWUP', 'DW3RD', 'JPW', 'DSTOSDG', 'SBC1', 'DWT']
cc1 = YB_Jurisdiction
cc2 = DW_Jurisdiction
crewControl = ['YBDN', 'YBUP', 'DWDN', 'DWUP', 'DWT']
crewControlSet = set(crewControl)


def min2hhmm(mins):
    h = mins // 60
    mins = mins % 60
    return f"{h:02d}:{mins:02d}"


def hhmm2mins(hhmm):
    parts = hhmm.split(":")
    if len(parts) == 2:
        hrs, mins = int(parts[0]), int(parts[1])
    elif len(parts) == 3:
        hrs, mins = int(parts[0]), int(parts[1])
    else:
        raise ValueError(f"Invalid time format: {hhmm}")
    return hrs * 60 + mins


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

def fetchData(csv_path=f"temp_files/{execution_id}redefinedinputparameters.csv"):
# def fetchData(csv_path='redefinedinputparameters.csv'):
    servicesLst = []
    with open(csv_path) as output:
        reader = csv.reader(output)
        next(reader)
        for row in reader:
            servicesLst.append(Services(row))
    return servicesLst


def canFollow(s1, s2):
    if s1.endStn == s2.startStn and s1.endTime == s2.startTime:
        if s1.stepbackTrainNum == "No StepBack":
            rake_ok = s1.trainNum == s2.trainNum
        else:
            rake_ok = int(s1.stepbackTrainNum) == s2.trainNum
        if rake_ok:
            cont_drive = s2.endTime - s1.startTime
            return cont_drive <= Continuous_Driving_time and (s2.endTime - s1.startTime) <= Duty_hours
        return False

    gap = s2.startTime - s1.endTime
    if short_break <= gap <= (120 if timetable_type == 'large' else 150) and s1.endStn[:4] in crewControlSet:
        return s1.endStn[:2] == s2.startStn[:2] and (s2.endTime - s1.startTime) <= Duty_hours
    return False


def exceeds_continuous_driving(path, limit=Continuous_Driving_time, short_break=30):
    cont_drive = path[0].endTime - path[0].startTime
    for i in range(1, len(path)):
        prev = path[i - 1]
        curr = path[i]
        gap = curr.startTime - prev.endTime
        if gap >= short_break:
            cont_drive = curr.endTime - curr.startTime
        else:
            cont_drive += curr.endTime - prev.endTime
        if cont_drive > limit:
            return True
    return False


def build_trip_graph(services):
    graph = defaultdict(list)
    total = len(services)
    for i in range(total):
        s1 = services[i]
        for j in range(i + 1, total):
            s2 = services[j]
            if s2.startTime - s1.endTime > (120 if timetable_type == 'large' else 150):
                break
            if canFollow(s1, s2):
                graph[s1.servNum].append(s2)
    return graph


def check_additional_constraints(path):
    for i in range(len(path) - 1):
        if path[i].endStn == "DWT":
            gap = path[i + 1].startTime - path[i].endTime
            if not (40 <= gap <= 49 or gap > 60):
                return False

    cont_drive = path[0].endTime - path[0].startTime
    for i in range(1, len(path)):
        gap = path[i].startTime - path[i - 1].endTime
        if gap >= short_break:
            if cont_drive >= 140 and gap < 40:
                return False
            break
        else:
            cont_drive += path[i].endTime - path[i - 1].endTime

    return True


def generate_duties(start_trip, graph, cc1, cc2, max_depth=10):
    stack = [(start_trip, [start_trip])]
    valid_duties = []

    while stack:
        current, path = stack.pop()
        start_time = path[0].startTime
        end_time = path[-1].endTime
        duty_dur = end_time - start_time
        if duty_dur > Duty_hours:
            continue

        break_dur = 0
        has_long_break = False
        jurisdictional_break_found = False
        invalid_break = False

        if path[0].startStn in cc1:
            starting_jurisdiction = cc1
        elif path[0].startStn in cc2:
            starting_jurisdiction = cc2
        else:
            starting_jurisdiction = None

        for i in range(len(path) - 1):
            gap = path[i + 1].startTime - path[i].endTime
            nxt = path[i+1]
            if (
                nxt.startStn  == "DWDN" and
                nxt.endStn    == "NFD"   and
                nxt.startTime < 22 * 60 and
                gap < short_break
            ):
                invalid_break = True
                break

            break_dur += gap

            if gap > 150:
                invalid_break = True
                break

            if gap >= long_break:
                has_long_break = True

            if gap >= short_break and starting_jurisdiction:
                if path[i].endStn in starting_jurisdiction:
                    jurisdictional_break_found = True

        if invalid_break:
            continue

        driving_dur = duty_dur - break_dur
        if driving_dur > Driving_duration:
            continue

        if exceeds_continuous_driving(path):
            continue

        good_duty = 50 < break_dur < (120 if timetable_type == 'large' else 150)

        valid_jurisdiction = (
            (path[0].startStn in cc1 and path[-1].endStn in cc1) or
            (path[0].startStn in cc2 and path[-1].endStn in cc2)
        )
        if start_time < 6 * 60:
            total_trip_duration = sum(s.servDur for s in path)
            if total_trip_duration >= 330:
                continue

        first_break_threshold = 80 if path[0].trainNum in (398, 399, '398','399') else 40

        continuous_end = path[0].endTime
        for i in range(1, len(path)):
            gap = path[i].startTime - path[i-1].endTime
            if gap < first_break_threshold:
                continuous_end = path[i].endTime
            else:
                break

        initial_cont = continuous_end - path[0].startTime
        first_cont_trip = (initial_cont <= 30)

        breaks = []
        if has_long_break:
            for i in range(len(path)-1):
                gap = path[i+1].startTime - path[i].endTime
                if gap > 0:
                    breaks.append(gap)

        if has_long_break:
            first_break_valid = (breaks[0] >= first_break_threshold)
        else:
            first_break_valid = False

        second_break_valid = (breaks[1] >= 40) if (len(breaks) > 1) else False

        crewcontrolending = (path[-1].endStn in crewControlSet and end_time >= (23*60 + 30))
        if (
            len(path) > 1 and
            has_long_break and
            valid_jurisdiction and
            jurisdictional_break_found and
            good_duty and
            check_additional_constraints(path) and
            second_break_valid and
            first_break_valid and 
            not first_cont_trip
        ):
            valid_duties.append([s.servNum for s in path])

        if len(path) >= max_depth:
            continue

        for next_trip in graph.get(current.servNum, []):
            if next_trip in path:
                continue
            stack.append((next_trip, path + [next_trip]))

    return valid_duties


def chunk_indices(total, chunk_spans):
    ranges = []
    start = 0
    for span in chunk_spans:
        end = min(start + span, total)
        ranges.append((start, end))
        start = end
        if start >= total:
            break
    if start < total:
        ranges.append((start, total))
    return ranges


# ---- Multiprocessing Globals + Initializer ----

global_services = None
global_graph = None

def init_worker(shared_services, shared_graph):
    global global_services, global_graph
    global_services = shared_services
    global_graph = shared_graph


def process_range(args):
    start, end = args
    sub_duties = []
    for i in range(start, end):
        duties = generate_duties(global_services[i], global_graph, cc1, cc2)
        print(f"Subprocess [{i+1}/{len(global_services)}] {global_services[i].servNum}: {len(duties)} duties")
        sub_duties.extend(duties)
    return sub_duties


def parallel_generate_duties_and_return(chunk_spans=None):
    total = len(services)
    if chunk_spans is None:
        chunk_spans = [50, 50, 100, 200, 300, 300]
    chunks = chunk_indices(total, chunk_spans)
    args = [(start, end) for (start, end) in chunks]

    all_duties = []
    with concurrent.futures.ProcessPoolExecutor(
        initializer=init_worker,
        initargs=(services, graph)
    ) as executor:
        results = executor.map(process_range, args)
        for duty_chunk in results:
            all_duties.extend(duty_chunk)

    print(f"\n Total valid duties generated: {len(all_duties)}")
    return all_duties


# def save_duties_to_csv(duties, filename=f"temp_files/{execution_id}generated_duties_graph.csv"):
#     if max_depth is None:
#         max_depth = max(len(duty) for duty in duty_pool) if duty_pool else 0

#     with open(filename, mode='w', newline='') as file:
#         writer = csv.writer(file)
#         writer.writerow([''] + list(range(max_depth)))
#         for idx, duty in enumerate(duty_pool):
#             row = [idx] + duty[:max_depth] + [''] * (max_depth - len(duty))
#             writer.writerow(row)

#     print(f"\n Duty pool saved to '{os.path.abspath(filename)}'.")
def save_duties_to_csv(duty_pool, filename=None, max_depth=None):
    if filename is None:
        filename = f"temp_files/{execution_id}generated_duties_graph.csv"

    if max_depth is None:
        max_depth = max((len(duty) for duty in duty_pool), default=0)

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([''] + list(range(max_depth)))
        for idx, duty in enumerate(duty_pool):
            row = [idx] + duty[:max_depth] + [''] * (max_depth - len(duty))
            writer.writerow(row)

    print(f"\n Duty pool saved to '{os.path.abspath(filename)}'.")


# =================[ MAIN EXECUTION BLOCK ]=================

if __name__ == '__main__':
    print("Starting pre-processing...")

    print("Loading services...")
    services = fetchData(f'temp_files/{execution_id}redefinedinputparameters.csv')
    print(f"Total services loaded: {len(services)}")

    print("Building graph...")
    graph = build_trip_graph(services)

    print("Generating duty pool (parallel)...")
    duty_pool = parallel_generate_duties_and_return()

    print("Saving duties to CSV...")
    save_duties_to_csv(duty_pool)
    print(" Done.")
