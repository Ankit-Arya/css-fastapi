import pyomo.environ as pyo
from pyomo.core import ConcreteModel
from pyomo.opt import SolverFactory
import csv
import pandas as pd
import os
import argparse
import sys


parser = argparse.ArgumentParser()
parser.add_argument("execution_id", type=str, help="Provide the current time.")
parser.add_argument("gap_percent", type=str, help="Provide the objective gap percentage.")
args = parser.parse_args()
obj_gap = float(args.gap_percent)
execution_id = args.execution_id

BASE_DIR = "temp_files"

INPUT_FILE_LOCATION = os.path.join(BASE_DIR, f"{execution_id}redefinedinputparameters.csv")
DUTIES_FILE = os.path.join(BASE_DIR, f"{execution_id}generated_duties_graph.csv")
SOLUTION_FILE = os.path.join(BASE_DIR, f"{execution_id}solution.csv")

df = pd.read_csv(INPUT_FILE_LOCATION)

services = [df.iloc[i,0] for i in range(len(df)) ]



#--------------------------------
#dutiesDF = pd.read_csv("/home/22m1513/fileforModel.csv")

service_assignments = {}

def log(*args):
    for s in args:
        print(s, flush=True, end=' ')

# Create an empty dictionary with keys and empty lists
servicesInPath = {key: [] for key in services}

# Open the CSV file in binary mode
with open(DUTIES_FILE, 'rb') as file:
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
        if index == 0:
            continue
        # Filter out NULL values (assuming NULL is represented as the string 'NULL')
        filtered_row = [int(value) for value in row if value != 'NULL' and value != '']
        filtered_row = filtered_row[1:]  # Exclude the first element which is duty ID
        # print(filtered_row)
        #filtered_row = [int(value) if value != '' else None for value in row if value != 'NULL']


        
        # if 3 <= len(filtered_row) <= 6:
        #     prob = random.random() < 0.1
        # else: prob = True
        # #Store the filtered row in the dictionary if it's not empty
        # if filtered_row and prob:
        if filtered_row:
            for ii in filtered_row:

                servicesInPath[ii].append(index-1)
                
            # if len(filtered_row) > 1:
                service_assignments[index-1] = filtered_row

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
        with open(f"{BASE_DIR}/missingServices.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for ser in missingService:
                writer.writerow([ser])
        if not found: log("No service is missing")
        sys.exit(0)

    scsMathModel = ConcreteModel()
    scsMathModel.fPath = pyo.Var([path for path in service_assignments.keys()], domain=pyo.Binary) #Reals, bounds=(0,1))
    scsMathModel.fServ = pyo.Var([ser for ser in services], domain=pyo.Reals, bounds=(0,1))

    def objectiveRule(model):
        minimumPath = sum(model.fPath[path] for path in service_assignments.keys())
        return minimumPath 

    scsMathModel.OBJ = pyo.Objective(rule=objectiveRule, sense=pyo.minimize)
    scsMathModel.ConsList = pyo.ConstraintList()
    for ser in services:
        scsMathModel.ConsList.add(scsMathModel.fServ[ser] == 1)


    for edgeService,edgepaths in servicesInPath.items():
        scsMathModel.ConsList.add(sum(scsMathModel.fPath[pathId] for pathId in edgepaths) ==  scsMathModel.fServ[edgeService])

    log("Solving Model")
    # opt=SolverFactory("gurobi_direct")
    # result=opt.solve(scsMathModel)
    optSolver = SolverFactory('bnb', executable="bnb")
    #optSolver.options['--time_limit'] = 15000
    optSolver.options['--branch_dir'] = 1
    optSolver.options['--threads'] = 4
    optSolver.options['--brancher'] = 'maxvio'
    optSolver.options['--set_lp_method'] = 0
    optSolver.options['--sppheur'] = 1
    optSolver.options['--log_level'] = 3
    optSolver.options['--obj_gap_percent'] = obj_gap
    result = optSolver.solve(scsMathModel, tee=True)

    log('Solver status:', result.solver.status)
    log('Solver termination condition:',result.solver.termination_condition)


    if result.solver.termination_condition != "infeasible":
    #     pass
        varVal = []
        totalDuties = 0

        with open(SOLUTION_FILE, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for variable in scsMathModel.fPath:
                #log(str(variable),scsMathModel.fPath[variable].value)
                if abs(scsMathModel.fPath[variable].value-1) <= 1e-6:
                    writer.writerow(service_assignments[int(variable)])
                    #log(scsMathModel.fPath[variable],'=', service_assignments[int(variable)-1])
                    totalDuties += 1
    #     #     #log(scsMathModel.fPath[variable],'=',int(scsMathModel.fPath[variable].value))
        log("Total Duties: ",totalDuties)
    else:
        log("Infeasible solution found in iteration:")
