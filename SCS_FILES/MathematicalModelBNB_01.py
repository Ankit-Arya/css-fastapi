from datetime import datetime
import pyomo.environ as pyo
from pyomo.core import ConcreteModel
from pyomo.opt import SolverFactory
import csv
import pandas as pd
import os
import argparse
import pytz
import shutil
import sys


def get_kolkata_time():
    return datetime.now(pytz.timezone("Asia/Kolkata")).strftime("%Y-%m-%d %H-%M-%S")

def log(*args):
    for arg in args:
        print(arg, flush=True)

parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
parser.add_argument("gap_percent", type=str, help="Provide the objective gap percentage.")
parser.add_argument("line_no", type=str, help="Line no.")
parser.add_argument("juris_conflict", type=int, help="Jurisdiction conflict")
args = parser.parse_args()
member_id = args.member_id
obj_gap = float(args.gap_percent)
line_no = args.line_no
juris_conflict = args.juris_conflict

new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"

inputFileLocation = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/Mainloops.csv"
tempLocation = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/"
outputLocation = tempLocation + "SOLUTION 1/"
os.makedirs(outputLocation, exist_ok=True)

df = pd.read_csv(inputFileLocation)

services = [df.iloc[i,0] for i in range(len(df)) ]

# services.remove(671)

#------------------Temporary code FOR WEEKDAYS SHORT SERVICE SAKP/3RD EVENING INDUCTION TO MKPR OFF----------------------
# value = 651
# if value in services:
#     services.remove(value)
#     log(f"Service {value} removed from the list of services.")



#--------------------------------
#dutiesDF = pd.read_csv("/home/22m1513/fileforModel.csv")

service_assignments = {}




# Create an empty dictionary with keys and empty lists
servicesInPath = {key: [] for key in services}

# Dictionary to store the binary indicator (0/1) for each duty
duty_binary_indicators = {}

# Open the CSV file in binary mode
with open(f"{tempLocation}SetOfDuties.csv", 'rb') as file:
    # Read the file content as bytes
    file_content = file.read()
    
    # Replace null bytes with an empty string
    file_content = file_content.replace(b'\x00', b'')
    
    # Convert the modified content back to a string
    file_content = file_content.decode('utf-8')
    
    # Use StringIO to create a file-like object for csv.reader
    from io import StringIO
    file_like_object = StringIO(file_content)
    
    # Create a CSV reader
    reader = csv.reader(file_like_object)
    
    # Iterate over each row and filter out NULL values
    for index, row in enumerate(reader):
        # Filter out NULL values (assuming NULL is represented as the string 'NULL')
        filtered_row = [int(value) for value in row if value != 'NULL' and value != '']
        #filtered_row = [int(value) if value != '' else None for value in row if value != 'NULL']

        if filtered_row:
            # Extract the binary indicator (last element)
            binary_indicator = filtered_row[-1]
            # Remove the binary indicator from the services list
            services_in_duty = filtered_row[:-1]
            
            # Store the binary indicator for this duty
            duty_binary_indicators[index] = binary_indicator
            
            for ii in services_in_duty:
                servicesInPath[ii].append(index)
                
            service_assignments[index] = services_in_duty

x = len(service_assignments)
"""
for i in services:
    # randomServicesAssignments[x] = [i] 
    service_assignments[x] = [i]
    servicesInPath[i].append(x)
    x += 1
"""
num_services = len(services)
num_drivers = len(service_assignments)
log(num_drivers)
#service_assignments - key:duty_number, value:set of service numbers in this duty
for xyz in range(1):
    servicesInDuties = []
    for index,services1 in service_assignments.items():
        for service in services1:
            if service not in servicesInDuties:
                servicesInDuties.append(service)
        if len(servicesInDuties) == num_services: 
            break
    if num_services != len(servicesInDuties):
        log(f"Total No. of services are not appended in iteration, total number of services:{num_services},number of services appended:{len(servicesInDuties)}")
        servicesInDuties.sort()
        # log(servicesInDuties)
        found = False
        missingService = []
        for checkser in services:
            if checkser not in servicesInDuties:
                log(checkser, '\n')
                missingService.append(checkser)
                found  = True
        with open(f"{tempLocation}logfiles/missingServices.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for ser in missingService:
                writer.writerow([ser])
        if not found: log("No service is missing")
        sys.exit(0)

    scsMathModel = ConcreteModel()
    scsMathModel.fPath = pyo.Var([path for path in service_assignments.keys()], domain=pyo.Binary) 
    scsMathModel.fServ = pyo.Var([ser for ser in services], domain=pyo.Reals, bounds=(0,1)) #Reals, bounds=(0,1))

    def objectiveRule(model):
        # Primary objective: minimize number of duties
        minimumPath = sum(model.fPath[path] for path in service_assignments.keys())
        
        # Secondary objective: maximize number of 1's (reward for selecting duties with binary indicator = 1)
        # Using a small weight to prioritize duty minimization over 1's maximization
        # reward_for_ones = -0.1 * sum(model.fPath[path] * duty_binary_indicators[path] for path in service_assignments.keys())
        
        return minimumPath #+ reward_for_ones

    # Add constraint for minimum percentage of 1's in the solution
    # You can modify this percentage as needed (e.g., 0.3 for 30%, 0.5 for 50%, etc.)
    # min_percentage_ones = 0.99  # 99% minimum of selected duties should have binary indicator = 1

    # Count total duties with binary indicator = 1
    total_ones_available = sum(1 for indicator in duty_binary_indicators.values() if indicator == 1)
    total_zeros_available = sum(1 for indicator in duty_binary_indicators.values() if indicator == 0)
    
    log(f"Total duties with binary indicator 1: {total_ones_available}")
    log(f"Total duties with binary indicator 0: {total_zeros_available}")
    # log(f"Target minimum percentage of 1's: {min_percentage_ones * 100}%")


    scsMathModel.OBJ = pyo.Objective(rule=objectiveRule, sense=pyo.minimize)
    scsMathModel.ConsList = pyo.ConstraintList()
    for ser in services:
        scsMathModel.ConsList.add(scsMathModel.fServ[ser] == 1)
    

    
    # Constraint: At least min_percentage_ones of selected duties should have binary indicator = 1
    # sum(selected duties with indicator = 1) >= min_percentage_ones * sum(all selected duties)
    # This can be rewritten as: sum(selected duties with indicator = 1) - min_percentage_ones * sum(all selected duties) >= 0
    scsMathModel.ConsList.add(
        (sum(scsMathModel.fPath[path] for path in service_assignments.keys()) - sum(scsMathModel.fPath[path] * duty_binary_indicators[path] for path in service_assignments.keys())) == juris_conflict
    )

# for edge in services:
#       pathIdsContainingServ = []
#       for path in service_assignments.keys():
#         for ee in service_assignments[path]:
#           if ee==edge:
#             pathIdsContainingServ.append(path)
#             log(path)
#       scsMathModel.ConsList.add(sum(scsMathModel.fPath[pathId] for pathId in pathIdsContainingServ) == scsMathModel.fServ[edge])

    for edgeService,edgepaths in servicesInPath.items():
        scsMathModel.ConsList.add(sum(scsMathModel.fPath[pathId] for pathId in edgepaths) ==  scsMathModel.fServ[edgeService])
    # scsMathModel.write(f"{tempLocation}Model.nl", format = 'nl')

    log("Solving Model")
    # opt=SolverFactory("gurobi_direct")
    # result=opt.solve(scsMathModel)
    optSolver = SolverFactory('bnb', executable="bnb")
    #optSolver.options['--time_limit'] = 15000
    optSolver.options['--branch_dir'] = 1
    # optSolver.options['--threads'] = 4
    optSolver.options['--brancher'] = 'maxvio'
    optSolver.options['--set_lp_method'] = 0
    optSolver.options['--sppheur'] = 1
    # optSolver.options['--sol_limit'] = 1
    optSolver.options['--threads'] = 4
    optSolver.options['--log_level'] = 3
    optSolver.options['--obj_gap_percent'] = obj_gap
    
    result = optSolver.solve(scsMathModel, tee=True)

    log(f'Solver status: {result.solver.status}')
    log(f'Solver termination condition: {result.solver.termination_condition}')


    if result.solver.termination_condition != "infeasible":
    #     pass
        varVal = []
        totalDuties = 0
        selected_ones = 0
        selected_zeros = 0
        
        with open(f"{outputLocation}solution_{member_id}.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for variable in scsMathModel.fPath:
                #log(str(variable),scsMathModel.fPath[variable].value)
                if abs(scsMathModel.fPath[variable].value-1) <= 1e-6:
                    writer.writerow(service_assignments[int(variable)])
                    #log(scsMathModel.fPath[variable],'=', service_assignments[int(variable)-1])
                    totalDuties += 1
                    
                    # Count 1's and 0's in selected duties
                    if duty_binary_indicators[int(variable)] == 1:
                        selected_ones += 1
                    else:
                        selected_zeros += 1
    #     #     #log(scsMathModel.fPath[variable],'=',int(scsMathModel.fPath[variable].value))
        shutil.copy(f"{outputLocation}solution_{member_id}.csv", f"{tempLocation}solution_{member_id}.csv")
        
        log(f"Total Duties: {totalDuties}")
        log(f"Selected duties with binary indicator 1: {selected_ones}")
        log(f"Selected duties with binary indicator 0: {selected_zeros}")
        
        # Calculate and log the actual percentage of 1's achieved
        if totalDuties > 0:
            actual_percentage_ones = (selected_ones / totalDuties) * 100
            log(f"Actual percentage of 1's achieved: {actual_percentage_ones:.2f}%")
        else:
            log("No duties selected")

    else:
        log("Infeasible solution found in iteration:")
