import json

""" Representation of a policy
        ------------------------------------------------------------------------
        [0]     [1]     [2]     [3]     [4]     [5]     [6]     [7]     [8]
        ------------------------------------------------------------------------
        Policy |MCI   |Damage |Story  |Time   |Role   |Select  |Stage  |Load
        Type   |Level |Type   |       |       |       |        |       |
        ------------------------------------------------------------------------
        [9]     [10]    [11]    [12]    [13]    [14]    [15]    [16]    [17]
        ------------------------------------------------------------------------
        Deliver|Return|Wait   |Treat  |Operate|Release|Method  |Compli |Enforced
        To     |To    |       |       |       |       |value   |ance   |
        ------------------------------------------------------------------------

        This module reads json and translate domain-specific strings into numbers or vice versa.
"""

translate_map = {
    "policyType": {
        "Action": 1,
        "Compliance": 2,
    },
    "DamageType": {
        "Fire": 1,
        "Collapse": 2,
    },
    "role": {
        "RESCUE": 1,
        "TRANSPORT": 2,
        "TREATMENT": 3,
    },
    "Select": {
        "Distance": 1,
        "Severity": 2,
        "InjuryType": 3,
        "": 0,
    },
    "Stage": {
        "MeanRandom": 1,
        "MCSlot": 2,
        "": 0,
    },
    "Load": {
        "Distance": 1,
        "Severity": 2,
        "InjuryType": 3,
        "": 0,
    },
    "DeliverTo": {
        "Distance": 1,
        "Vacancy": 2,
        "Rate": 3,
        "": 0,
    },
    "ReturnTo": {
        "MeanRandom": 1,
        "MCSlot": 2,
        "Original": 3,
        "": 0,
    },
    "Wait": {
        "Stay": 1,
        "": 0,
    },
    "Treat": {
        "Severity": 1,
        "": 0,
    },
    "Operate": {
        "Severity": 1,
        "ArriveTime": 2,
        "InjuryType": 3,
        "": 0,
    },
    "Release": {
        "Strength": 1,
        "Time": 2,
        "": 0,
    },
}

rev_translate_map = {
    "policyType": {
        1: "Action",
        2: "Compliance",
    },
    "DamageType": {
        1: "Fire",
        2: "Collapse",
        -1: "",
    },
    "role": {
        1: "RESCUE",
        2: "TRANSPORT",
        3: "TREATMENT",
    },
    "Select": {
        1: "Distance",
        2: "Severity",
        3: "InjuryType",
        4: "Random",
        0: "",
    },
    "Stage": {
        1: "MeanRandom",
        2: "MCSlot",
        3: "Random",
        0: "",
    },
    "Load": {
        1: "Distance",
        2: "Severity",
        3: "InjuryType",
        4: "Random",
        0: "",
    },
    "DeliverTo": {
        1: "Distance",
        2: "Vacancy",
        3: "Rate",
        4: "Random",
        0: "",
    },
    "ReturnTo": {
        1: "MeanRandom",
        2: "MCSlot",
        3: "Original",
        4: "Random",
        0: "",
    },
    "Wait": {
        1: "Stay",
        0: "",
    },
    "Treat": {
        1: "Severity",
        2: "Random",
        0: "",
    },
    "Operate": {
        1: "Severity",
        2: "ArriveTime",
        3: "InjuryType",
        4: "Random",
        0: "",
    },
    "Release": {
        1: "Strength",
        2: "Time",
        0: "",
    },
}

index_map = {
    0: "policyType",
    1: "MCILevel",
    2: "DamageType",
    3: "Story",
    4: "Time",
    5: "role",
    6: "Select",
    7: "Stage",
    8: "Load",
    9: "DeliverTo",
    10: "ReturnTo",
    11: "Wait",
    12: "Treat",
    13: "Operate",
    14: "Release",
    15: "MethodValue",
    16: "Compliance",
    17: "Enforced",
}


def read_policy(filename):
    policy_set = list()
    with open(filename) as f:
        for line in f:
            while True:
                try:
                    policies = json.loads(line)
                    for policy in policies:
                        prev_policy = [None] * 18

                        # policy type
                        policy_type = policy['policyType']
                        prev_policy[0] = translate_map['policyType'][policy_type]

                        # conditions
                        conditions = policy['conditions']
                        for condition in conditions:
                            if condition['variable'] == "MCILevel":
                                prev_policy[1] = int(condition['value'][0])
                            elif condition['variable'] == "DamageType":
                                cond_val = condition['value']
                                prev_policy[2] = translate_map["DamageType"][cond_val]
                            elif condition['variable'] == "Story":
                                prev_policy[3] = int(condition['value'][0])
                            elif condition['variable'] == "Time":
                                prev_policy[4] = int(condition['value'][0])

                        # role
                        role = policy['role']
                        prev_policy[5] = translate_map['role'][role]

                        # action
                        action = policy['action']
                        action_name = action['actionName']
                        action_method = action['actionMethod']
                        if action_name == "Select":
                            prev_policy[6] = translate_map["Select"][action_method]
                        elif action_name == "Stage":
                            prev_policy[7] = translate_map["Stage"][action_method]
                        elif action_name == "Load":
                            prev_policy[8] = translate_map["Load"][action_method]
                        elif action_name == "DeliverTo":
                            prev_policy[9] = translate_map["DeliverTo"][action_method]
                        elif action_name == "ReturnTo":
                            prev_policy[10] = translate_map["ReturnTo"][action_method]
                        elif action_name == "Wait":
                            prev_policy[11] = translate_map["Wait"][action_method]
                        elif action_name == "Treat":
                            prev_policy[12] = translate_map["Treat"][action_method]
                        elif action_name == "Operate":
                            prev_policy[13] = translate_map["Operate"][action_method]
                        elif action_name == "Release":
                            prev_policy[14] = translate_map["Release"][action_method]

                        # method value
                        if action['methodValue'] == "":
                            prev_policy[15] = -1
                        else:
                            prev_policy[15] = int(action['methodValue'])

                        # minCompliance and enforce
                        if prev_policy[0] == 1:     # action policy
                            prev_policy[16] = -1    # do not use min_compliance
                            # if str_to_bool(policy['enforce']):
                            if policy['enforce'] == "true":
                                prev_policy[17] = 1
                            else:
                                prev_policy[17] = 0
                        elif prev_policy[0] == 2:   # compliance policy
                            prev_policy[16] = float(policy['minCompliance'])

                        # fill -1 into rest of irrelevant indices
                        for idx in range(0, len(prev_policy)):
                            if prev_policy[idx] is None:
                                prev_policy[idx] = -1
                        policy_set.append(prev_policy)
                    break
                except ValueError:
                    # Not yet a complete JSON value
                    line += next(f)

    return policy_set


def poli_to_dict(numeric_policy):

    policy = dict()
    # "policyType"
    idx_mean = index_map[0]
    value = numeric_policy[0]
    mci_str = rev_translate_map[idx_mean][value]
    policy['policyType'] = mci_str

    # "conditions"
    conditions = list()
    for idx in range(1, 5):
        idx_mean = index_map[idx]
        value = numeric_policy[idx]

        if value == -1:
            continue
        else:
            condition = dict()
            condition['variable'] = index_map[idx]
            condition['operator'] = "=="
            if idx in {1, 3, 4}:
                condition['value'] = str(value)
            elif idx == 2:
                mci_str = rev_translate_map[idx_mean][value]
                condition['value'] = mci_str
            conditions.append(condition)

    policy['conditions'] = conditions

    # "role"
    idx_mean = index_map[5]
    value = numeric_policy[5]
    mci_str = rev_translate_map[idx_mean][value]
    policy['role'] = mci_str

    # "action"
    action = dict()
    for idx in range(6, 16):
        idx_mean = index_map[idx]
        value = numeric_policy[idx]
        if value == -1:
            action['methodValue'] = ""
            continue
        else:
            if idx == 15:
                action['methodValue'] = str(value)
            else:
                mci_str = rev_translate_map[idx_mean][value]
                action['actionName'] = idx_mean
                action['actionMethod'] = mci_str
    policy['action'] = action

    # "minCompliance"
    policy['minCompliance'] = numeric_policy[16]

    # "enforced"
    policy['enforce'] = val_to_bool(numeric_policy[17])

    return policy


def make_policy_json(filename, individual):
    policy_set = list()

    for policy in individual:
        policy_dict = poli_to_dict(policy)
        policy_set.append(policy_dict)

    dir_path = "./json/candidates/"
    file_path = dir_path+filename
    with open(file_path, 'w') as f:
        f.write(json.dumps(policy_set, indent=4))


def val_to_bool(v):
    if v is 1:
        return "true"
    return "false"

