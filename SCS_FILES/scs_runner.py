from datetime import datetime
import json
import subprocess
import os
import sys
import time
import sys
import json
from helpers import update_status
import shutil


def main():
    try:
        # --------------------------------------------- PARSE Command Line Input -----------------------------------------------
        
        print(f"scs_runner.py started!")
        print(f"Received args: {sys.argv}")
        # CLI args: python3 simulate_runner.py <execution_id> <file_path> <stepping_back_json>
        member_id = sys.argv[1]
        excel_file = sys.argv[2]
        print('FILE PATH==',excel_file)
        stepping_back_raw = sys.argv[3]  # Passed as JSON string
        timetable_type = sys.argv[4]
        line_no = sys.argv[5]
        max_processes = '20'
        gap_percent = '5'
        json_file = os.path.abspath(f"parameters_{line_no}.json")
        with open(json_file, "r") as f:
            json_params = json.load(f)
        # Run each script with its arguments
        # current_time = datetime.now().strftime('%d%m%y%H%M%S')
        # Get current working directory and convert for WSL
        cwd = os.getcwd()
        wsl_cwd = cwd.replace("\\", "/").replace("E:", "/mnt/e").replace("D:", "/mnt/d").replace("C:", "/mnt/c").replace("F:", "/mnt/f")
        new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"
        os.makedirs(f"{new_location}/USEFUL OUTPUT_{member_id}/logfiles", exist_ok=True)
        
        #1--------------------------------------------------------------------------------------------------------------
        #send_progress_json(line_no, progress)
        update_status(member_id, f"Save your UID for future ref - {member_id}","WIP")
        time.sleep(2)
        update_status(member_id, "STAGE 1 of 4 in progress","WIP")
        update_status(member_id, "Pre-Processing Time Table","WIP")
        try:
            if line_no == '7':
                try:
                    subprocess.run(["python", f"initial_timetable_read_1_circular_line{line_no}.py", member_id, excel_file], check=True)
                    subprocess.run(["python", f"initial_timetable_read_2_circular_line{line_no}.py", member_id, excel_file], check=True)
                    subprocess.run(["python", f"initial_timetable_read_3_circular_line{line_no}.py", member_id], check=True)
                    print("Processing the Time Table with Circular Line7")
                except subprocess.CalledProcessError as e:
                    shutil.rmtree(f"{new_location}")
                    line_no = '7N'
                    new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"
                    os.makedirs(f"{new_location}/USEFUL OUTPUT_{member_id}/logfiles", exist_ok=True)
                    print("Processing the Time Table with Normal Line7")
                    subprocess.run(["python", f"initial_timetable_read_line{line_no}.py", member_id, excel_file], check=True)
            else:
                subprocess.run(["python", f"initial_timetable_read_line{line_no}.py", member_id, excel_file], check=True)
        except subprocess.CalledProcessError as e:
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            print("There is some error in Initial Time Table reading process. Please contact SCS Administrator.")
            step_name = "Pre-Processing Time Table"
            message = "Error in Initial Time Table reading process."
            update_status(member_id, step_name, "error", message)
            sys.exit(1)

        update_status(member_id, "Pre=Processing and analysis complete", "completed")

        #2--------------------------------------------------------------------------------------------------------------
        if line_no == '6':
            crew_control = ['BAPB']
            depots = ['AJDD']
        elif line_no == '34':
            crew_control = ['DW', 'YB']
            depots = ['NFD', 'YBD', 'NESY']
        elif line_no == '1':
            crew_control = ['SHD']
            depots = ['SPKD']
        elif line_no == '5':
            crew_control = ['MUDK']
            depots = ['MDD', 'BGZD']
        elif line_no == '7' or line_no == '7N':
            crew_control = ['PBGW', 'KKDA']
            depots = ['MKPD', 'VND']
            svvrRakes = ['1111', '2222']
        elif line_no == '9':
            crew_control = ['DW']
            depots = ['DEPOT']
        elif line_no == 'AEL':
            crew_control = ['DSTO']
            depots = ['DWD']
        else: 
            print("There is error in crew_control or depots naming.")
            sys.exit(1)


        data = { "crew_control" : crew_control, "depots" : depots}
        try:
            result = subprocess.run(["python", "jurisdiction_extraction.py", member_id, line_no , json.dumps(data)], check=True, capture_output=True, text=True)
            # print("Output:", result.stdout)
        except subprocess.CalledProcessError as e:
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            print("Return Code:", e.returncode)
            print("There is some error in Loops Formation. Please contact SCS Administrator.")
            step_name = "Jurisdiction Extraction"
            message = "Error in Jurisdiction Extraction process."
            update_status(member_id, step_name, "error", message)
            sys.exit(1)

        # Capture the three lists from the stdout of jurisdiction_extraction.py
        output_lines = result.stdout.strip().split('\n')
        if len(output_lines) >= 3:
            normal_stations = eval(output_lines[0])
            outstations = eval(output_lines[1])
            crew_control_list = eval(output_lines[2])
            # print(type(normal_stations), type(outstations), type(crew_control_list))
        else:
            print("Expected at least 3 lines of output from jurisdiction_extraction.py")
            step_name = "Jurisdiction Extraction"
            message = "Insufficient output from Jurisdiction Extraction process."
            update_status(member_id, step_name, "error", message)
            sys.exit(1)


        #update_progress(5)
        #send_progress_json(line_no, progress)


        # ##send_progress_json(line_no, progress)(progress_json)


        #--------------------------------------------------------------------------------------------------------------
        update_status(member_id, "Initial Services are being checked","WIP")

        try:
            result = subprocess.run(["python", f"CheckInitialServices.py", member_id, line_no], check= True, capture_output=True, text=True)
            output_lines = result.stdout.strip().split('\n')
            if len(output_lines) >= 6:
                cc1_mismatch = eval(output_lines[0])
                cc2_mismatch = eval(output_lines[1])
                sameTrainTimeConflicts = eval(output_lines[2])
                timeConflicts = eval(output_lines[3])
                stationConflicts = eval(output_lines[4])
                ind_stb_Conflicts = eval(output_lines[5])
            else:
                raise ValueError("Expected at least 3 lines of output from CheckInitialServices.py")
        except:
            print("There is some error in Initial Services Check. Please contact SCS Administrator.")
            step_name = "Initial Services Check"
            message = "Error in Initial Services Check process."
            update_status(member_id, step_name, "error", message)
            sys.exit(1)

        if int(cc1_mismatch) + int(cc2_mismatch) != 0 or int(sameTrainTimeConflicts) + int(timeConflicts) + int(stationConflicts) + int(ind_stb_Conflicts) != 0:
            print("Initial Services check failed. Please resolve the issues and try again.")
            step_name = "Initial Services Check"
            message = f"CC1 Mismatches: {cc1_mismatch}, CC2 Mismatches: {cc2_mismatch}, Same Train Time Conflicts: {sameTrainTimeConflicts}, Time Conflicts: {timeConflicts}, Station Conflicts: {stationConflicts}, Ind STB Conflicts: {ind_stb_Conflicts}"
            update_status(member_id, step_name, "error", message)
            sys.exit(1)
        juris_conflict = int(abs(cc1_mismatch))
        print(f"Jurisdiction Conflicts: {juris_conflict}")

        update_status(member_id, f"Initial Services check completed and found ok", "completed")
        update_status(member_id, f"STAGE 1 complete", "completed")

        #3--------------------------------------------------------------------------------------------------------------
        update_status(member_id, "Creating duty loops with reversal parameters", "WIP")
        try:
            if line_no == '7':
                data1 = { "svvrRakes" : svvrRakes}
                subprocess.run(["python", f"loops_formation_circular_line{line_no}.py", member_id, json.dumps(data1)], check=True)
            elif line_no == '7N':
                data1 = { "svvrRakes" : svvrRakes}
                subprocess.run(["python", f"loops_formation_line{line_no}.py", member_id, json.dumps(data1)], check=True)
            else:
                subprocess.run(["python", f"loops_formation_line{line_no}.py", member_id], check=True)
        except subprocess.CalledProcessError as e:
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            print("Return Code:", e.returncode)
            print("There is some error in Loops Formation. Please contact SCS Administrator.")
            step_name = "Loops Formation"
            message = "Error in Loops Formation process."
            update_status(member_id, step_name, "error", message)
            sys.exit(1)

        update_status(member_id, f"STAGE 2 complete", "completed")

        #4--------------------------------------------------------------------------------------------------------------

        solution_path = f"{new_location}/USEFUL OUTPUT_{member_id}/SOLUTION 1/solution_{member_id}.csv"
        log_path = f"{cwd}/{new_location}/USEFUL OUTPUT_{member_id}/logfiles/logWatcher_{member_id}.txt"
        log_path_bnb = f"{cwd}/{new_location}/USEFUL OUTPUT_{member_id}/logfiles/logBNB_{member_id}.txt"
        bnb_error_path = f"{cwd}/{new_location}/USEFUL OUTPUT_{member_id}/logfiles/missingServices.csv"
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        if juris_conflict == 0:
            update_status(member_id, "Creating duty dataset to be optimized - This might take some time", "WIP")
            try:
                
                cmd = [
                    "wsl", "bash", "-c",
                    f"/home/yogesh_189/miniconda3/bin/conda run -n pyomo_env python3 -u duty_pool_watcher.py "
                    f"{member_id} {line_no} {max_processes} "
                    f"{json_params['short_break']} {json_params['long_break']} {json_params['duty_hours']} "
                    f"{json_params['continuous_drive']} {json_params['driving_hours']} {juris_conflict}"
                ]

                with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc, \
                        open(log_path, "w") as log_file:
                    for line in proc.stdout:
                        # print(line, end="")        # real-time console output
                        log_file.write(line)       # real-time file write
                        log_file.flush()           # flush immediately

                proc.wait()
            except Exception as e:
                print("There is some error in Duty Pool Generation. Please contact SCS Administrator.")
                step_name = "Duty Pool Generation"
                message = "Error in Duty Pool Generation process."
                update_status(member_id, step_name, "error", message)
                print(str(e))
                sys.exit(1)
            try:
                subprocess.run(["python", "MergeTempOutputFiles.py", member_id, line_no], check=True)
                update_status(member_id, f"Dataset Generation successfull", "completed")
            except subprocess.CalledProcessError as e:
                print("STDOUT:", e.stdout)
                print("STDERR:", e.stderr)
                print("Return Code:", e.returncode)
                print("There is some error in Merging Temp Output Files. Please contact SCS Administrator.")
                step_name = "Merging Temp Output Files"
                message = "Error in Merging Temp Output Files process."
                update_status(member_id, step_name, "error", message)
                sys.exit(1)
            
            try:
                update_status(member_id, f"Starting Optimization Process - This will take time - Sit tight", "WIP")
                subprocess.run(
                    [
                        "wsl", "bash", "-c",
                        f"/home/yogesh_189/miniconda3/bin/conda run -n pyomo_env "
                        f"python3 -u modelrunner.py {member_id} {gap_percent} {line_no} "
                        f"> '{wsl_cwd}/{new_location}/USEFUL OUTPUT_{member_id}/logfiles/logRunnerBNB_{member_id}.txt' 2>&1"
                    ],
                    check=True
                )
            except subprocess.CalledProcessError as e:
                print("STDOUT:", e.stdout)
                print("STDERR:", e.stderr)
                print("Return Code:", e.returncode)
                print("There is some error in Mathematical Model. Please contact SCS Administrator.")
                step_name = "Mathematical Model"
                message = "Error in Mathematical Model process."
                update_status(member_id, step_name, "error", message)
                sys.exit(1)
            if not os.path.exists(solution_path) and (line_no == '7' or line_no == '7N' or line_no == '34') and not os.path.exists(bnb_error_path):
                for juris_con in range(1,6):
                    print(f"Solution not found with normal duties.")
                    print("Trying with different jurisdiction sign on/off...")
                    print(f"Retrying with jurisdiction conflict {juris_con}...")
                    if juris_con == 1:
                        try:
                            cmd = [
                                "wsl", "bash", "-c",
                                f"/home/yogesh_189/miniconda3/bin/conda run -n pyomo_env python3 -u duty_pool_watcher.py "
                                f"{member_id} {line_no} {max_processes} "
                                f"{json_params['short_break']} {json_params['long_break']} {json_params['duty_hours']} "
                                f"{json_params['continuous_drive']} {json_params['driving_hours']} {juris_con}"
                            ]

                            with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc, \
                                    open(log_path, "w") as log_file:
                                for line in proc.stdout:
                                    # print(line, end="")        # real-time console output
                                    log_file.write(line)       # real-time file write
                                    log_file.flush()           # flush immediately

                            proc.wait()
                        except:
                            print("There is some error in Duty Pool Generation. Please contact SCS Administrator.")
                            step_name = "Duty Pool Generation"
                            message = "Error in Duty Pool Generation process."
                            update_status(member_id, step_name, "error", message)
                            sys.exit(1)
                        try:
                            subprocess.run(["python", "MergeTempOutputFiles.py", member_id, line_no], check=True)
                        except subprocess.CalledProcessError as e:
                            print("STDOUT:", e.stdout)
                            print("STDERR:", e.stderr)
                            print("Return Code:", e.returncode)
                            print("There is some error in Merging Temp Output Files. Please contact SCS Administrator.")
                            step_name = "Merging Temp Output Files"
                            message = "Error in Merging Temp Output Files process."
                            update_status(member_id, step_name, "error", message)
                            sys.exit(1)

                    try:
                        subprocess.run(
                            [
                                "wsl", "bash", "-c",
                                f"/home/yogesh_189/miniconda3/bin/conda run -n pyomo_env "
                                f"python3 -u modelrunner_01.py {member_id} {gap_percent} {line_no} {juris_con} "
                                f"> '{wsl_cwd}/{new_location}/USEFUL OUTPUT_{member_id}/logfiles/logRunnerBNB_01_{member_id}.txt' 2>&1"
                            ],
                            check=True
                        )
                
                    except subprocess.CalledProcessError as e:
                        print("STDOUT:", e.stdout)
                        print("STDERR:", e.stderr)
                        print("Return Code:", e.returncode)
                        print("There is some error in Mathematical Model. Please contact SCS Administrator.")
                        step_name = "Mathematical Model"
                        message = "Error in Mathematical Model process."
                        update_status(member_id, step_name, "error", message)
                        sys.exit(1)
                    
                    if os.path.exists(solution_path):
                        print(f"Solution found with jurisdiction conflict {juris_con}.")
                        break
                    else:
                        if juris_con == 5:
                            print("No solution found with jurisdiction conflict 5. Exiting...")
                            sys.exit(1)
                        print(f"No solution found with jurisdiction conflict {juris_con}. Retrying...")

        else:
            update_status(member_id, "Creating duty dataset to be optimized - This might take some time", "WIP")
            try:
                cmd = [
                    "wsl", "bash", "-c",
                    f"/home/yogesh_189/miniconda3/bin/conda run -n pyomo_env python3 -u duty_pool_watcher.py "
                    f"{member_id} {line_no} {max_processes} "
                    f"{json_params['short_break']} {json_params['long_break']} {json_params['duty_hours']} "
                    f"{json_params['continuous_drive']} {json_params['driving_hours']} {juris_conflict}"
                ]

                with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as proc, \
                        open(log_path, "w") as log_file:
                    for line in proc.stdout:
                        # print(line, end="")        # real-time console output
                        log_file.write(line)       # real-time file write
                        log_file.flush()           # flush immediately

                proc.wait()
            except Exception as e:
                print("There is some error in Duty Pool Generation. Please contact SCS Administrator.")
                step_name = "Duty Pool Generation"
                message = "Error in Duty Pool Generation process."
                update_status(member_id, step_name, "error", message)
                print(str(e))
                sys.exit(1)
            try:
                subprocess.run(["python", "MergeTempOutputFiles.py", member_id,line_no], check=True)
                update_status(member_id, f"Dataset Generation successfull", "completed")
            except subprocess.CalledProcessError as e:
                print("STDOUT:", e.stdout)
                print("STDERR:", e.stderr)
                print("Return Code:", e.returncode)
                print("There is some error in Merging Temp Output Files. Please contact SCS Administrator.")
                step_name = "Merging Temp Output Files"
                message = "Error in Merging Temp Output Files process."
                update_status(member_id, step_name, "error", message)
                sys.exit(1)
            update_status(member_id, f"Dataset Generation successfull", "completed")
            time.sleep(2)
            update_status(member_id, f"Starting Optimization Process - This will take time - Sit tight", "WIP")
            for juris_con in range(1,6):
                try:
                    if juris_con == 1:
                        juris_con = juris_conflict
                    elif juris_con == juris_conflict:
                        continue
                    subprocess.run(
                        [
                            "wsl", "bash", "-c",
                            f"/home/yogesh_189/miniconda3/bin/conda run -n pyomo_env "
                            f"python3 -u modelrunner_01.py {member_id} {gap_percent} {line_no} {juris_con} "
                            f"> '{wsl_cwd}/{new_location}/USEFUL OUTPUT_{member_id}/logfiles/logRunnerBNB_01_{member_id}.txt' 2>&1"
                        ],
                        check=True
                    )
                except subprocess.CalledProcessError as e:
                    print("STDOUT:", e.stdout)
                    print("STDERR:", e.stderr)
                    print("Return Code:", e.returncode)
                    print("There is some error in Mathematical Model. Please contact SCS Administrator.")
                    step_name = "Mathematical Model"
                    message = "Error in Mathematical Model process."
                    update_status(member_id, step_name, "error", message)
                    sys.exit(1)
                
                if os.path.exists(solution_path):
                    print(f"Solution found with jurisdiction conflict {juris_con}.")
                    break
                elif os.path.exists(bnb_error_path):
                    print(f"Missing services found. Check {bnb_error_path} for details.")
                    break
                else:
                    if juris_con == 5:
                        print("No solution found with jurisdiction conflict 5. Exiting...")
                        sys.exit(1)
                    print(f"No solution found with jurisdiction conflict {juris_con}. Retrying...")

        if not os.path.exists(solution_path):
            print("No solution found. Exiting...")
            sys.exit(1)
        update_status(member_id, f"Success ! Optimization Complete", "completed")
        #7--------------------------------------------------------------------------------------------------------------
        time.sleep(2)
        update_status(member_id, f"Creating Trip Chart Format", "WIP")
        try:
            subprocess.run(["python", "solToRoster.py", member_id, line_no, json.dumps(data)], check=True)
            #update_progress(10)
            #send_progress_json(line_no, progress)
            print("All scripts executed successfully!")
        except subprocess.CalledProcessError as e:
            print("STDOUT:", e.stdout)
            print("STDERR:", e.stderr)
            print("Return Code:", e.returncode)
            print("There is some error in Solution to Roster conversion. Please contact SCS Administrator.")
            step_name = "Solution to Roster Conversion"
            message = "Error in Solution to Roster conversion process."
            update_status(member_id, step_name, "error", message)
            sys.exit(1)
        update_status(member_id, f"Trip Chart Formatting completed", "completed")
        update_status(member_id, "STAGE 4 Complete", "completed")

    except Exception as e:
        update_status(member_id, "Pipeline Broke--", "error", str(e))


if __name__ == "__main__":
    print('INSIDE SCS 1.0 RUNNER')
    main()