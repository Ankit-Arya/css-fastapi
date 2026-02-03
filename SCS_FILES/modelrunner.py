import subprocess
import argparse
import os


parser = argparse.ArgumentParser()
parser.add_argument("member_id", type=str, help="Provide the current time.")
parser.add_argument("gap_percent", type=str, help="Provide the objective gap percentage.")
parser.add_argument("line_no", type=str, help="Line no.")
args = parser.parse_args()
member_id = args.member_id
obj_gap = float(args.gap_percent)
line_no = args.line_no

cwd = os.getcwd()
new_location = f"ALL_USER_TT/LINE{line_no}_{member_id}"

cmd = [
        "python3", "-u", "MathematicalModelBNB.py", member_id, str(obj_gap), line_no
    ]
log_file = f"{cwd}/{new_location}/USEFUL OUTPUT_{member_id}/logfiles/logBNB_{member_id}.txt"

with open(log_file, "w") as f:
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="")   # optional: echo to console
        f.write(line)

    process.wait()

print(f"Model Runner Process finished with return code {process.returncode}")
