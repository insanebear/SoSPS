import os
import subprocess
from json_handle import make_policy_json

def evaluate(indiv_poli_set):
    # java simulator combine
    # one file --> execution --> result value
    # result = [file1, file2, ... file_#population]
    # compare current best solution

    command = "java -jar SIMVASoS-MCI.jar ./json/"
    file_name = "cand_poli_set.json"
    # file_name = "archivedPolicy.json"
    total_command = command+file_name

    make_policy_json(file_name, indiv_poli_set)

    # run SIMVA-SoS MCI (Java Program)
    subprocess.run(total_command.split(), stdout=subprocess.PIPE)
    eval_result = 0.0

    with open("Sim_Result.txt") as f:
        while True:
            line = f.read().strip()
            if not line:
                break
            eval_result = float(line)
    print(eval_result)
    return eval_result,
