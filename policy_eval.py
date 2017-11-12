import os
import logging
import subprocess
from json_handle import make_policy_json

number = 0

SIMUL_LOG = 'simulation.log'

# def evaluate(indiv_poli_set):
def evaluate(indiv_poli_set, file_num, gen_num):
    # java simulator combine
    # one file --> execution --> result value
    # result = [file1, file2, ... file_#population]
    # compare current best solution

    logging.basicConfig(filename=SIMUL_LOG, level=logging.DEBUG)

    command = "java -jar SIMVASoS-MCI.jar ./json/candidates/"
    # file_name = "cand_poli_set.json"
    file_name = str(gen_num)+"_cand_poli_set" + str(file_num) + ".json"
    # file_name = "archivedPolicy.json
    total_command = command+file_name

    make_policy_json(file_name, indiv_poli_set)

    try:
        # run SIMVA-SoS MCI (Java Program)
        proc = subprocess.run(total_command.split(), stdout=subprocess.PIPE)
        for line in proc.stdout.splitlines():
            logging.debug(line.decode('utf-8'))
            # print(line.decode('utf-8'))
    except subprocess.CalledProcessError as e:
        print(e.output)

    # read the result file
    eval_result = 0.0
    with open("Sim_Result.txt") as f:
        while True:
            line = f.read().strip()
            if not line:
                break
            eval_result = float(line)
    print("Simulation Result: ", eval_result)
    return eval_result,




