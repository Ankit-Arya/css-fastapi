import csv
from collections import defaultdict
import os
import concurrent.futures
import sys

# Parameters
Duty_hours = 440
Driving_duration = 360
Continuous_Driving_time = 180
long_break = 50
short_break = 30
execution_id = sys.argv[1]
timetable_type = sys.argv[2]
print('ARGS IN PARALLEL FILE', execution_id)

crewControl = ['CCDN', 'CCUP']
final_op = []

# ---- Definitions, Classes, Helpers ----

def hhmm_to_minutes(hhmm: str) -> int:
    h, m = map(int, hhmm.split(":"))
    return h * 60 + m



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
        duties = generate_duties_from_service(i, global_graph, global_services)
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
    print("Starting pre-processing...", flush=True)

    print("Loading services...", flush=True)
    services = fetchData(f'temp_files/{execution_id}redefinedinputparameters.csv')
    print(f"Total services loaded: {len(services)}")

    print("Building graph...", flush=True)
    graph = build_graph(services)

    print("Generating duty pool (parallel)...", flush=True)
    duty_pool = parallel_generate_duties_and_return()

    print("Saving duties to CSV...", flush=True)
    save_duties_to_csv(duty_pool)
    print(" Done.", flush=True)