import subprocess
import time
import os
import signal
import sys
from datetime import datetime
import pytz
from zoneinfo import ZoneInfo
import os
import argparse
import shutil
import csv

parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
parser.add_argument("line_no", type=str, help="Provide the line no.")
parser.add_argument("max_processes", type=int, default=4, help="Maximum number of concurrent processes.")
parser.add_argument("short_break", type=int, default=30, help="Duration of short breaks.")
parser.add_argument("long_break", type=int, default=50, help="Duration of long breaks.")
parser.add_argument("duty_hours", type=int, default=8*60, help="Total duty hours.")
parser.add_argument("continuous_drive", type=int, default=3*60, help="Maximum continuous driving time.")
parser.add_argument("driving_hours", type=int, default=6*60, help="Maximum driving duration in a duty.")
parser.add_argument("juris_conflict", type=int, help="Jurisdiction conflict count.")
args = parser.parse_args()
member_id = args.member_id
line_no = args.line_no
watcher_max_process = args.max_processes
watcher_short_break = args.short_break
watcher_long_break = args.long_break
watcher_duty_hours = args.duty_hours
watcher_continuous_drive = args.continuous_drive
watcher_driving_duration = args.driving_hours
juris_conflict = args.juris_conflict

new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"
logs_dir = os.path.dirname(os.path.abspath(__file__)) + "/WATCHER_LOGS"
os.makedirs(logs_dir, exist_ok=True)

def get_kolkata_time():
    return datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H-%M-%S")

def log(msg):
    print(f"[{get_kolkata_time()}] {msg}", flush=True)

class ProcessWatcher:
    def __init__(self, start = 0, max_processes=8, gap=5, max_final_end = 1342):

        self.max_processes = max_processes
        self.gap = gap
        self.max_final_end = max_final_end
        self.running_processes = {}  # Dictionary to store process and its range
        self.completed_ranges = set()  # Set to store completed ranges
        self.next_start = start  # Start from start
        self.should_stop = False
        
        # Create directory structure
        self.base_dir = os.path.dirname(os.path.abspath(__file__)) + "/WATCHER_PROCESSES"
        self.logs_dir = logs_dir
        self.dirs = {
            'logs': os.path.join(self.logs_dir, f"process_logs_{member_id}"),
            'pids': os.path.join(self.logs_dir, f"process_pids_{member_id}"),
            'scripts': os.path.join(self.logs_dir, f"process_scripts_{member_id}"),
            # 'output': os.path.join(self.base_dir, f"process_output_{member_id}"),
            # 'temp': os.path.join(self.base_dir, f"process_temp_{member_id}")
        }
        
        # Create all directories
        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
    def get_next_range(self):
        """Get the next range, allowing overlap at the boundary."""
        if self.next_start < self.max_final_end:
            final_end = min(self.next_start + self.gap, self.max_final_end)
            range_tuple = (self.next_start, final_end)
            self.next_start = final_end
            return range_tuple
        return None

    def start_process(self, initial_start, final_end):
        """Start a new process with given range"""
        # Create log file for this instance
        log_file = os.path.join(self.dirs['logs'], f"process_log_{initial_start}_{final_end}.txt")
        
        # Create a shell script to run the process
        script_path = os.path.join(self.dirs['scripts'], f"run_process_{initial_start}_{final_end}.sh")
        if line_no == '7':
            with open(script_path, 'w') as f:
                f.write(f'''#!/bin/bash
                cd "{self.base_dir}"
                nohup python3 duty_pool_generator_circular_line{line_no}.py --member_id {member_id} --initial_start {initial_start} --final_end {final_end} --short_break {watcher_short_break} --long_break {watcher_long_break} --duty_hours {watcher_duty_hours} --continuous_drive {watcher_continuous_drive} --driving_duration {watcher_driving_duration} --juris_conflict {juris_conflict} > "{log_file}" 2>&1 &
                echo $! > "{os.path.join(self.dirs['pids'], f'pid_{initial_start}_{final_end}.txt')}"
                ''')
        elif line_no == '7N':
            with open(script_path, 'w') as f:
                f.write(f'''#!/bin/bash
                cd "{self.base_dir}"
                nohup python3 duty_pool_generator_line{line_no}.py --member_id {member_id} --initial_start {initial_start} --final_end {final_end} --short_break {watcher_short_break} --long_break {watcher_long_break} --duty_hours {watcher_duty_hours} --continuous_drive {watcher_continuous_drive} --driving_duration {watcher_driving_duration} --juris_conflict {juris_conflict} > "{log_file}" 2>&1 &
                echo $! > "{os.path.join(self.dirs['pids'], f'pid_{initial_start}_{final_end}.txt')}"
                ''')
        else:
            with open(script_path, 'w') as f:
                f.write(f'''#!/bin/bash
                cd "{self.base_dir}"
                nohup python3 duty_pool_generator_line{line_no}.py --member_id {member_id} --initial_start {initial_start} --final_end {final_end} --short_break {watcher_short_break} --long_break {watcher_long_break} --duty_hours {watcher_duty_hours} --continuous_drive {watcher_continuous_drive} --driving_duration {watcher_driving_duration} --juris_conflict {juris_conflict}  > "{log_file}" 2>&1 &
                echo $! > "{os.path.join(self.dirs['pids'], f'pid_{initial_start}_{final_end}.txt')}"
                ''')
        
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Run the script
        process = subprocess.Popen(
            ['bash', script_path],
            env={**os.environ, "PYTHONUNBUFFERED": "1"}
        )
        
        # Wait a moment for the process to start and write its PID
        time.sleep(1)
        
        # Read the PID from the file
        try:
            with open(os.path.join(self.dirs['pids'], f"pid_{initial_start}_{final_end}.txt"), 'r') as f:
                pid = int(f.read().strip())
            self.running_processes[pid] = (initial_start, final_end)
            log(f"Started process {pid} with range {initial_start}-{final_end}")
            log(f"Process output being logged to: {log_file}")
        except Exception as e:
            log(f"Error starting process: {str(e)}")
            raise

    def check_processes(self):
        """Check status of running processes and start new ones if needed"""
        for pid in list(self.running_processes.keys()):
            try:
                # Check if process is still running
                os.kill(pid, 0)
            except OSError:
                # Process is not running
                range_tuple = self.running_processes.pop(pid)
                self.completed_ranges.add(range_tuple)
                log(f"Process {pid} completed range {range_tuple}")
                
                # Clean up PID file
                try:
                    os.remove(os.path.join(self.dirs['pids'], f"pid_{range_tuple[0]}_{range_tuple[1]}.txt"))
                except:
                    pass
                
                # Start new process if we haven't reached max_final_end
                if len(self.running_processes) < self.max_processes and not self.should_stop:
                    next_range = self.get_next_range()
                    if next_range:
                        self.start_process(*next_range)

    def stop_all_processes(self):
        """Stop all running processes"""
        log("Stopping all processes...")
        self.should_stop = True
        
        for pid in list(self.running_processes.keys()):
            try:
                log(f"Terminating process {pid}")
                os.kill(pid, signal.SIGTERM)
                time.sleep(1)  # Give process time to terminate
                
                # Check if process is still running
                try:
                    os.kill(pid, 0)
                    log(f"Process {pid} did not terminate gracefully, forcing kill")
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass  # Process already terminated
                    
            except Exception as e:
                log(f"Error stopping process {pid}: {str(e)}")
            
            # Clean up PID file
            try:
                range_tuple = self.running_processes[pid]
                os.remove(os.path.join(self.dirs['pids'], f"pid_{range_tuple[0]}_{range_tuple[1]}.txt"))
            except:
                pass
        
        self.running_processes.clear()
        log("All processes stopped")

    def run(self):
        """Main run loop"""
        # Set up signal handler
        def signal_handler(signum, frame):
            log("Received shutdown signal")
            self.stop_all_processes()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        log("Starting Process Watcher")
        log("Press Ctrl+C to stop all processes")
        log(f"Process logs directory: {self.dirs['logs']}")
        log(f"Process PIDs directory: {self.dirs['pids']}")
        log(f"Process scripts directory: {self.dirs['scripts']}")
        # log(f"Process output directory: {self.dirs['output']}")
        # log(f"Process temp directory: {self.dirs['temp']}")
        
        try:
            # Start initial batch of processes
            for _ in range(self.max_processes):
                if self.should_stop:
                    break
                next_range = self.get_next_range()
                if next_range:
                    self.start_process(*next_range)
                else:
                    break

            # Main monitoring loop
            while self.running_processes and not self.should_stop:
                self.check_processes()
                time.sleep(1)  # Check every second

            if not self.should_stop:
                log("All processes completed normally")
            else:
                log("Processes stopped by user")

        except KeyboardInterrupt:
            log("Received keyboard interrupt")
            self.stop_all_processes()
        except Exception as e:
            log(f"Error in main loop: {str(e)}")
            self.stop_all_processes()
            raise

if __name__ == "__main__":
    tempoutput_file = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/TEMP_OUTPUT_FILES"
    if os.path.exists(tempoutput_file):
        shutil.rmtree(tempoutput_file)
    os.makedirs(tempoutput_file, exist_ok=True)
    mainloop_file = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/Mainloops.csv"
    with open(mainloop_file,'r') as f:
        reader = csv.reader(f)
        row_count = sum(1 for row in reader)


    watcher = ProcessWatcher(start=0, max_processes= watcher_max_process, gap=5, max_final_end = row_count -1)
    watcher.run()
    #delete all folders created for watcher after completion
    for dir_path in list(watcher.dirs.values())[:]:
        shutil.rmtree(dir_path)