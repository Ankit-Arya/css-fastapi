import csv
from collections import defaultdict
import os
import concurrent.futures
import sys

# Parameters
Duty_hours = 460
Driving_duration = 375
Continuous_Driving_time = 180
long_break = 50
short_break = 30
execution_id = sys.argv[1]
timetable_type = sys.argv[2]
print('ARGS IN PARALLEL FILE', execution_id)

crewControl = ['CCDN', 'CCUP']
final_op = []


# =================[ MAIN EXECUTION BLOCK ]=================

if __name__ == '__main__':
    print("Starting pre-processing...", flush=True)

    print("Loading services...", flush=True)
    services = fetchData(f'temp_files/{execution_id}redefinedinputparameters.csv')
    print(f"Total services loaded: {len(services)}")

    print("Building graph...")
    graph = build_graph(services)

    print("Generating duty pool (parallel)...")
    duty_pool = parallel_generate_duties_and_return()

    print("Saving duties to CSV...")
    save_duties_to_csv(duty_pool)
    print(" Done.")