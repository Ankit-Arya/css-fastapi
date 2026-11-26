import argparse
import csv
import os
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime

import pytz


parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the member ID.")
parser.add_argument("line_no", type=str, help="Provide the line number.")
parser.add_argument("max_processes", type=int, help="Maximum number of concurrent processes.")
parser.add_argument("short_break", type=int, help="Duration of short breaks.")
parser.add_argument("long_break", type=int, help="Duration of long breaks.")
parser.add_argument("duty_hours", type=int, help="Total duty hours.")
parser.add_argument("continuous_drive", type=int, help="Maximum continuous driving time.")
parser.add_argument("driving_hours", type=int, help="Maximum driving duration in a duty.")
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


script_dir = os.path.dirname(os.path.abspath(__file__))
new_location = os.path.join("ALL_USER_TT", f"LINE{line_no}_{member_id}")
logs_dir = os.path.join(script_dir, "WATCHER_LOGS")
os.makedirs(logs_dir, exist_ok=True)


def get_kolkata_time():
    return datetime.now(pytz.timezone("Asia/Kolkata")).strftime(
        "%Y-%m-%d %H:%M:%S"
    )


def log(msg):
    print(f"[{get_kolkata_time()}] {msg}", flush=True)


class ProcessWatcher:
    def __init__(self, start=0, max_processes=8, gap=5, max_final_end=1342):
        self.max_processes = max_processes
        self.gap = gap
        self.max_final_end = max_final_end
        # pid -> (Popen object, range tuple, open log handle, log path)
        self.running_processes = {}
        self.completed_ranges = set()
        self.next_start = start
        self.should_stop = False

        self.base_dir = os.path.join(script_dir, "WATCHER_PROCESSES")
        self.logs_dir = logs_dir
        self.dirs = {
            "logs": os.path.join(self.logs_dir, f"process_logs_{member_id}"),
            "pids": os.path.join(self.logs_dir, f"process_pids_{member_id}"),
            "scripts": os.path.join(self.logs_dir, f"process_scripts_{member_id}"),
        }

        for dir_path in self.dirs.values():
            os.makedirs(dir_path, exist_ok=True)

    def get_next_range(self):
        """Preserve the original sequential ranges and gap size."""
        if self.next_start < self.max_final_end:
            final_end = min(self.next_start + self.gap, self.max_final_end)
            range_tuple = (self.next_start, final_end)
            self.next_start = final_end
            return range_tuple
        return None

    def get_worker_script(self):
        """Return the worker script for the selected line."""
        if line_no == "1":
            filename = "duty_pool_generator_line1.py"
        elif line_no == "34":
            filename = "duty_pool_generator_line34.py"
        else:
            raise ValueError(f"Unsupported line number: {line_no}")

        python_script = os.path.join(self.base_dir, filename)
        if not os.path.isfile(python_script):
            raise FileNotFoundError(f"Worker script not found: {python_script}")
        return python_script

    def start_process(self, initial_start, final_end):
        """Launch one Python worker directly and capture stdout + stderr."""
        python_script = self.get_worker_script()

        log_filename = f"process_log_{initial_start}_{final_end}.txt"

        log_file = os.path.join(self.dirs["logs"], log_filename)
        pid_file = os.path.join(
            self.dirs["pids"], f"pid_{initial_start}_{final_end}.txt"
        )

        command = [
            sys.executable,
            python_script,
            "--member_id", str(member_id),
            "--initial_start", str(initial_start),
            "--final_end", str(final_end),
            "--short_break", str(watcher_short_break),
            "--long_break", str(watcher_long_break),
            "--duty_hours", str(watcher_duty_hours),
            "--continuous_drive", str(watcher_continuous_drive),
            "--driving_duration", str(watcher_driving_duration),
            "--juris_conflict", str(juris_conflict),
        ]

        log_handle = open(
            log_file, "w", encoding="utf-8", buffering=1
        )

        try:
            process = subprocess.Popen(
                command,
                cwd=self.base_dir,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
        except Exception:
            log_handle.close()
            raise

        try:
            with open(pid_file, "w", encoding="utf-8") as f:
                f.write(str(process.pid))
        except Exception:
            # Do not leave a worker running if its PID file cannot be written.
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            log_handle.close()
            raise

        self.running_processes[process.pid] = (
            process,
            (initial_start, final_end),
            log_handle,
            log_file,
        )

        log(
            f"Started Python worker PID {process.pid} "
            f"for range {initial_start}-{final_end}"
        )
        log(f"Worker output and errors are logged to: {log_file}")

    def _remove_pid_file(self, range_tuple):
        pid_file = os.path.join(
            self.dirs["pids"],
            f"pid_{range_tuple[0]}_{range_tuple[1]}.txt",
        )
        try:
            os.remove(pid_file)
        except FileNotFoundError:
            pass
        except OSError as exc:
            log(f"Could not remove PID file {pid_file}: {exc}")

    def check_processes(self):
        """Check actual Python worker exit codes and start replacement work."""
        for pid, (process, range_tuple, log_handle, log_file) in list(
            self.running_processes.items()
        ):
            return_code = process.poll()

            # None means the worker is still running.
            if return_code is None:
                continue

            self.running_processes.pop(pid, None)

            try:
                log_handle.close()
            except Exception:
                pass

            self._remove_pid_file(range_tuple)

            if return_code != 0:
                log(
                    f"ERROR: Worker PID {pid} failed for range {range_tuple}; "
                    f"exit code={return_code}. Check log: {log_file}"
                )
                self.should_stop = True
                self.stop_all_processes()
                raise RuntimeError(
                    f"Worker failed for range {range_tuple}; "
                    f"exit code={return_code}. Log: {log_file}"
                )

            log(f"Worker PID {pid} exited successfully for range {range_tuple}")
            self.completed_ranges.add(range_tuple)

            if (
                len(self.running_processes) < self.max_processes
                and not self.should_stop
            ):
                next_range = self.get_next_range()
                if next_range is not None:
                    self.start_process(*next_range)

    def stop_all_processes(self):
        """Stop tracked Python workers safely on Windows."""
        log("Stopping all tracked workers...")
        self.should_stop = True

        for pid, (process, range_tuple, log_handle, log_file) in list(
            self.running_processes.items()
        ):
            try:
                if process.poll() is None:
                    log(f"Terminating worker PID {pid}, range {range_tuple}")
                    process.terminate()
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        log(f"Worker PID {pid} did not stop; forcing kill")
                        process.kill()
                        process.wait(timeout=5)
            except Exception as exc:
                log(f"Error stopping worker PID {pid}: {exc}")
            finally:
                try:
                    log_handle.close()
                except Exception:
                    pass
                self._remove_pid_file(range_tuple)

        self.running_processes.clear()
        log("All tracked workers stopped")

    def run(self):
        """Start the initial batch and monitor until all ranges finish."""
        def signal_handler(signum, frame):
            log(f"Received shutdown signal {signum}")
            self.stop_all_processes()
            raise SystemExit(0)

        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, "SIGTERM"):
            signal.signal(signal.SIGTERM, signal_handler)

        log("Starting Process Watcher")
        log("Press Ctrl+C to stop all workers")
        log(f"Process logs directory: {self.dirs['logs']}")
        log(f"Process PIDs directory: {self.dirs['pids']}")

        try:
            # Start the initial batch, up to max_processes.
            for _ in range(self.max_processes):
                if self.should_stop:
                    break
                next_range = self.get_next_range()
                if next_range is None:
                    break
                self.start_process(*next_range)

            # Continue until all work has been assigned and all workers exit.
            while self.running_processes and not self.should_stop:
                self.check_processes()
                time.sleep(1)

            if not self.should_stop:
                log("All processes completed normally")
        except KeyboardInterrupt:
            log("Received keyboard interrupt")
            self.stop_all_processes()
        except Exception as exc:
            log(f"Error in watcher main loop: {exc}")
            self.stop_all_processes()
            raise


if __name__ == "__main__":
    if watcher_max_process < 1:
        raise ValueError("max_processes must be at least 1")

    tempoutput_file = os.path.join(
        script_dir,
        new_location,
        f"USEFUL OUTPUT_{member_id}",
        "TEMP_OUTPUT_FILES",
    )

    if os.path.exists(tempoutput_file):
        shutil.rmtree(tempoutput_file)
    os.makedirs(tempoutput_file, exist_ok=True)

    mainloop_file = os.path.join(
        script_dir,
        new_location,
        f"USEFUL OUTPUT_{member_id}",
        "Mainloops.csv",
    )

    with open(mainloop_file, "r", newline="", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        row_count = sum(1 for _ in reader)

    log(f"Mainloop file: {mainloop_file}")
    log(f"Mainloop row count: {row_count}")

    watcher = ProcessWatcher(
        start=0,
        max_processes=watcher_max_process,
        gap=5,
        max_final_end=row_count - 1,
    )

    try:
        watcher.run()
    finally:
        # Close any remaining log handles if execution exits unexpectedly.
        for entry in list(watcher.running_processes.values()):
            try:
                entry[2].close()
            except Exception:
                pass

    # Preserve the original cleanup behaviour: remove PID and script folders,
    # but retain worker logs for troubleshooting.
    for dir_path in list(watcher.dirs.values())[1:]:
        shutil.rmtree(dir_path, ignore_errors=True)
