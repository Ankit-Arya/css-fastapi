# import time
# import pandas as pd
# import os
# from helpers import update_status

# def process_file(execution_id: str, file_path: str, user_id: str, user_name: str, stepping_back: list):
#     try:
#         update_status(execution_id, "Reading File", "running")
#         time.sleep(1)  # Simulate delay
#         df = pd.read_csv(file_path)
#         update_status(execution_id, "Reading File", "completed")

#         # Create intermediate Excel files
#         for i in range(1, 4):
#             step_name = f"Creating Reference File {i}"
#             update_status(execution_id, step_name, "running")
#             time.sleep(1)  # Simulate processing
#             excel_path = f"temp_files/{execution_id}_ref_{i}.xlsx"
#             df.to_excel(excel_path, index=False)
#             update_status(execution_id, step_name, "completed")

#         # Create final output CSV
#         update_status(execution_id, "Generating Final Output CSV", "running")
#         time.sleep(1)
#         output_csv_path = f"temp_files/{execution_id}_final_output.csv"
#         df.to_csv(output_csv_path, index=False)
#         update_status(execution_id, "Generating Final Output CSV", "completed")

#         update_status(execution_id, "All Tasks", "completed")

#     except Exception as e:
#         update_status(execution_id, "All Tasks", "error", str(e))
import time
import pandas as pd
import os
from helpers import update_status

def process_file(
    execution_id: str, 
    file_path: str, 
    user_id: str, 
    user_name: str, 
    stepping_back: list
):
    try:
        update_status(execution_id, "Reading File", "running")
        time.sleep(1)  # Simulate delay
        df = pd.read_excel(file_path) if file_path.endswith(".xlsx") else pd.read_csv(file_path)
        update_status(execution_id, "Reading File", "completed")

        # Log stepping back entries for debug
        print(f"Stepping back entries for {execution_id}: {stepping_back}")

        # Create intermediate Excel files
        for i in range(1, 4):
            step_name = f"Creating Reference File {i}"
            update_status(execution_id, step_name, "running")
            time.sleep(1)  # Simulate processing
            excel_path = f"temp_files/{execution_id}_ref_{i}.xlsx"
            df.to_excel(excel_path, index=False)
            update_status(execution_id, step_name, "completed")

        # Create final output CSV
        update_status(execution_id, "Generating Final Output CSV", "running")
        time.sleep(1)
        output_csv_path = f"temp_files/trip_chart_{execution_id}.csv"
        df.to_csv(output_csv_path, index=False)
        update_status(execution_id, "Generating Final Output CSV", "completed")

        update_status(execution_id, "All Tasks", "completed")

    except Exception as e:
        update_status(execution_id, "All Tasks", "error", str(e))
