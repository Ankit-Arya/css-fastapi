import pandas as pd
import argparse
import os

parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
args = parser.parse_args()
member_id = args.member_id


new_location = f"ALL_USER_TT/LINE7_{member_id}"
# Read the two CSV files
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
folder_name = f"{member_id}"
outputFileLocation = os.path.join(current_dir, f"{new_location}/USEFUL OUTPUT_{folder_name}/")
df1 = pd.read_csv(f"{outputFileLocation}InitialServices_up.csv")
df2 = pd.read_csv(f"{outputFileLocation}InitialServices_dn.csv")

# Concatenate the dataframes
df = pd.concat([df1, df2], ignore_index=True)

# Sort the dataframe by 'Start Time'
df_sorted = df.sort_values(by='Start Time')

# Optional: Reset index if needed
df_sorted = df_sorted.reset_index(drop=True)
# print(df_sorted)
# Display or use df_sorted as needed
df_sorted.iloc[:, 0] = range(len(df_sorted))
df_sorted.columns = ['', *df_sorted.columns[1:]]
# print(df_sorted)
df_sorted.to_csv(f"{outputFileLocation}InitialServices.csv", index=False)