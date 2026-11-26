import pyomo.environ as pyo
from pyomo.core import ConcreteModel
from pyomo.opt import SolverFactory
import csv
import pandas as pd
import os
import argparse
import shutil
import sys


NEED_SON_BETWEEN_TIME = False
NEED_SON_START_TIME = "09:15"
NEED_SON_END_TIME = "10:15"
NEED_SON_BETWEEN_TIME_DUTIES = 5
if NEED_SON_BETWEEN_TIME:
    print("NEED S/ON between time : ", NEED_SON_START_TIME, " and ", NEED_SON_END_TIME)



DUTIES_IN_INTERVAL_REQ = False
SERVICES_IN_INTERVAL_REQ = [
    482, 92, 91, 94, 483, 96, 97, 98, 484, 99, 101, 102, 485, 105, 103, 106,
    486, 109, 108, 110, 487, 112, 113, 114, 488, 117, 115, 118, 489, 121, 120, 122
]


# --------------------------------------------- PARSE Command Line Input -----------------------------------------------
parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
parser.add_argument("gap_percent", type=str, help="Provide the objective gap percentage.")
parser.add_argument("line_no", type=str, help="Line no.")
args = parser.parse_args()
member_id = args.member_id
obj_gap = float(args.gap_percent)
line_no = args.line_no

new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"
solver_file = os.path.join(os.getcwd(), "mbnb.exe")
inputFileLocation = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/Mainloops.csv"
tempLocation = os.path.dirname(os.path.abspath(__file__)) + f"/{new_location}/USEFUL OUTPUT_{member_id}/"
outputLocation = tempLocation + "SOLUTION 1/"
os.makedirs(outputLocation, exist_ok=True)

def log(*args):
    for arg in args:
        print(arg, flush=True)


def hhmm2mins(hhmm):
    """ changes the time from hh:mm to minutes
        take hh:mm string and gives integers minutes 0 to 1440"""
    if True:
        hrs = hhmm[:2]
        min = hhmm[-2:]
        mins = int(hrs)*60 + int(min)
        return int(mins)
    
df = pd.read_csv(inputFileLocation)

services = [df.iloc[i,0] for i in range(len(df)) ]



#--------------------------------
#dutiesDF = pd.read_csv("/home/22m1513/fileforModel.csv")

service_assignments = {}



# Create an empty dictionary with keys and empty lists
servicesInPath = {key: [] for key in services}

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
    log("="*100)
    log("Processing SetOfDuties.csv to create service assignments and services in path")
    log("="*100)
    for index, row in enumerate(reader):
        # Filter out NULL values (assuming NULL is represented as the string 'NULL')
        filtered_row = [int(value) for value in row if value != 'NULL' and value != '']
        #filtered_row = [int(value) if value != '' else None for value in row if value != 'NULL']


        
        # if 3 <= len(filtered_row) <= 6:
        #     prob = random.random() < 0.1
        # else: prob = True
        # #Store the filtered row in the dictionary if it's not empty
        # if filtered_row and prob:
        if filtered_row:
            for ii in filtered_row:

                servicesInPath[ii].append(index)
                
            # if len(filtered_row) > 1:
                service_assignments[index] = filtered_row
        if index % 100000 == 0:
            log(f"Processed {index} rows of SetOfDuties.csv for service assignments and services in path")

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
    log("="*100)
    log("Checking if all services are present in the duties")
    log("="*100)
    
    for index,services1 in service_assignments.items():
        for service in services1:
            if service not in servicesInDuties:
                servicesInDuties.append(service)
        if index % 100000 == 0:
            log(f"Checked {index} rows of service assignments for missing services.")
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
        with open(f"{tempLocation}SOLUTION 1/logfiles/missingServices.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for ser in missingService:
                writer.writerow([ser])
        if not found: log("No service is missing")
        sys.exit(0)
    log("All services are present in the duties")
    log("="*100)
    log("Creating Mathematical Model")
    log("="*100)
    log("Setting up decision variables")
    scsMathModel = ConcreteModel()
    scsMathModel.fPath = pyo.Var([path for path in service_assignments.keys()], domain=pyo.Binary) #Reals, bounds=(0,1))

    def objectiveRule(model):
        minimumPath = sum(model.fPath[path] for path in service_assignments.keys())
        return minimumPath 

    scsMathModel.OBJ = pyo.Objective(rule=objectiveRule, sense=pyo.minimize)

    log("Adding Constraints to the model")
    scsMathModel.ConsList = pyo.ConstraintList()
    for edgeService,edgepaths in servicesInPath.items():
        scsMathModel.ConsList.add(sum(scsMathModel.fPath[pathId] for pathId in edgepaths) ==  1)
    # scsMathModel.write(f"{tempLocation}Model.nl", format = 'nl')


    #----------------------------- Adding constraint to ensure atleast 1 duty is selected for S/ON at YBCC after 18:20 and before 19:00 --------------------------------------
    if DUTIES_IN_INTERVAL_REQ:
        required_services = SERVICES_IN_INTERVAL_REQ # for line1 duties between 09:00 and 09:30
        scsMathModel.ConsList.add(
            sum(
                scsMathModel.fPath[idx]
                for idx in scsMathModel.fPath
                if service_assignments[idx][0] in required_services
            ) >= 5
        )



    #---------------------------------TO FORCE SOME DUTIES ARE BETWEEN START AND END TIME--------------------------------------------------------
    if NEED_SON_BETWEEN_TIME:
        # Create a proper time column called "Start Time"
        df_1 = df.copy()
        df_1["Start Time"] = df_1["Start Time"].apply(hhmm2mins)
        # print(df_1)
        # Filter rows where Start Time < 07:15
        mask = (df_1["Start Time"] >= hhmm2mins(NEED_SON_START_TIME)) & (df_1["Start Time"] <= hhmm2mins(NEED_SON_END_TIME) & (df_1["Start Station"] == "SHD UP" or df_1["Start Station"] == "SHD DN"))
        # Extract values from column 0
        required_son_services = df_1.loc[mask, df_1.columns[0]].tolist()
        # print(values_list)


        scsMathModel.ConsList.add(
            sum(
                scsMathModel.fPath[idx]
                for idx in scsMathModel.fPath
                if service_assignments[idx][0] in required_son_services
            ) >= NEED_SON_BETWEEN_TIME_DUTIES
        )



    log("="*100)
    log("Solving Model")
    log("="*100)
    # opt=SolverFactory("gurobi_direct")
    # result=opt.solve(scsMathModel)
    optSolver = SolverFactory('bnb', executable = solver_file)
    #optSolver.options['--time_limit'] = 15000
    optSolver.options['--branch_dir'] = 1
    optSolver.options['--threads'] = 4
    optSolver.options['--brancher'] = 'maxvio'
    optSolver.options['--set_lp_method'] = 0
    optSolver.options['--sppheur'] = 1
    optSolver.options['--log_level'] = 3
    optSolver.options['--obj_gap_percent'] = obj_gap
    log("="*100)
    log("Solver Started")
    log("="*100)
    result = optSolver.solve(scsMathModel, tee=True, logfile=f"{tempLocation}SOLUTION 1/logfiles/BNB_solver_{member_id}.log")

    log('Solver status:', result.solver.status)
    log('Solver termination condition:',result.solver.termination_condition)


    if result.solver.termination_condition != "infeasible":
    #     pass
        varVal = []
        totalDuties = 0

        with open(f"{outputLocation}solution_{member_id}.csv", 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for variable in scsMathModel.fPath:
                #log(str(variable),scsMathModel.fPath[variable].value)
                if abs(scsMathModel.fPath[variable].value-1) <= 1e-6:
                    writer.writerow(service_assignments[int(variable)])
                    #log(scsMathModel.fPath[variable],'=', service_assignments[int(variable)-1])
                    totalDuties += 1
    #     #     #log(scsMathModel.fPath[variable],'=',int(scsMathModel.fPath[variable].value))
        log("Total Duties: ",totalDuties)

        shutil.copy(f"{outputLocation}solution_{member_id}.csv", f"{tempLocation}solution_{member_id}.csv")
    else:
        log("Infeasible solution found in iteration:")
