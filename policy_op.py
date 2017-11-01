import random

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
        This module contains policy-related operations
        including (random) generation, checking a policy and checking a policy set.
"""
# Index
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

# Category
policy_element = {
    "policyType": 1,
    "conditions": [1, 2, 3, 4],
    "role": 5,
    "action": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "minCompliance": 16,
    "enforced": 17,
}

# Values
value_map = {
    0: [1, 2],
    1: [1, 2, 3, 4, 5],  # MCI level
    2: [1, 2],  # Damage type
    3: [1, 2, 3, 4],  # Story
    4: [1, 2, 3, 4, 5],  # Time
    5: [1, 2, 3], # role
    6: [1, 2, 3],  # select: [distance, severity, injuryType]
    7: [1, 2],  # stage: [meanRandom, MCSlot]
    8: [1, 2, 3],  # load: [distance, severity, injuryType]
    9: [1, 2, 3],  # deliverTo: [distance, vacancy, rate]
    10: [1, 2, 3],  # returnTo: [MeanRandom, MCSlot, original]
    11: [1],  # wait: [stay]
    12: [1],  # treat: [severity]
    13: [1, 2, 3],  # operate: [severity, arriveTime, injuryType]
    14: [1, 2],  # release: [strength, time]
    15: range(0, ),
    16: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9],
    17: [0, 1]
}


# Relationship
role_action_map = {
    # value: indices
    1: [6, 7],  # Rescue: [select, stage]
    2: [8, 9, 10, 11],  # Transport: [load, deliverTo, returnTo, wait]
    3: [12, 13, 14],  # Treatment: [treat, operate, release]
}
role_cond_map = {
    # value: indices
    1: [1, 2, 3],  # Rescue
    2: [1, 2, 4],  # Transport
    3: [1, 2, 4],  # Treatment
}

# role_cond_excp_map = {
#     1: 4,  # Rescue
#     2: 3,  # Transport
#     3: 3,  # Treatment
# }



# policy type - compliance/enforce check (Index-Index)
type_compliance_map = {
    1: [16, 17],
    2: [16, 17],
}


def rand_gen_policies(indiv_size):
    policy_set = list()
    while indiv_size != len(policy_set):
        policy = gen_policy()
        if check_policy(policy):
            print("Generated policy", policy)
            policy_set.append(policy)

    return policy_set


def gen_policy():
    # initialize policy element with fixed length
    policy = [None] * 18

    # select a policy type
    policy_type = random.randint(1, 2)
    policy[0] = policy_type
    # select a role
    role = random.randint(1, 3)
    policy[5] = role
    # select an action according to the selected role
    action_list = role_action_map[role]
    action_name = action_list[random.randint(0, len(action_list) - 1)]

    if policy_type == 1:    # action policy
        method_list = value_map[action_name]
        action_method = method_list[random.randint(0, len(method_list) - 1)]
        policy[action_name] = action_method
        policy[17] = random.randint(0, 1)
    elif policy_type == 2:  # compliance policy
        policy[action_name] = 0                 # 0 as a check sign
        policy[16] = random.randint(0, 9) / 10  # minimum compliance

    # TODO condition
    # MCI level
    cond_name = 1
    cond_val_list = value_map[cond_name]
    val_idx = random.randint(0, len(cond_val_list) - 1)
    policy[cond_name] = cond_val_list[val_idx]

    for pol_idx in range(0, len(policy)):
        if policy[pol_idx] is None:
            policy[pol_idx] = -1

    return policy


def check_policy(policy):
    # check role (by value) - A policy must contain role-value.
    check_value(5, policy)
    # check conditions (by value) - A policy must contain at least 1 condition.
    cond_idx = list(policy_element['conditions'])
    first_idx = cond_idx[0]
    cond_list = policy[first_idx : first_idx+len(cond_idx)]
    if if_contains_all(-1, cond_list):
        # if conditions are all deactivated, (have -1)
        return False
    # check action by role
    if not check_by_role(policy):
        return False
    # check action by policy type
    if not check_by_policy_type(policy):
        return False
    # check values in array
    for p_idx in range(0, len(policy)):
        if policy[p_idx] in [-1, 0] or p_idx == 15:
            continue
        else:
            if not check_value(p_idx, policy):
                return False
    return True


def check_by_policy_type(policy):
    # action_list = policy[6:15]
    action_idx = policy_element['action']
    first_idx = action_idx[0]
    action_list = policy[first_idx:first_idx+len(action_idx)-1]   # method_val is not primary.
    policy_type = policy[0]
    if policy_type == 1:  # 'Action'
        # check action indices
        if if_contains_any(0, action_list):
            # 0 should not be in action policy.
            return False
        if if_contains_all(-1, action_list):
            # At least one action should be described.
            return False

        # check min_compliance
        if policy[16] != -1:
            return False
        # check enforced
        if policy[17] not in {0, 1}:
            return False

    elif policy_type == 2:    # 'Compliance'
        if not if_contains_any(0, action_list):
            # values should have at least one of 0
            print(11)
            return False
        if not if_contains_all_list([0, -1], action_list):
            # values should have 0 or -1
            return False
        if 0 > policy[16] or policy[16] >= 1:
            # compliance value should be in between 0 and 1
            return False
        if policy[17] != -1:
            # enforce value should be -1
            return False
    else:
        return False

    return True


def check_by_role(policy):
    role = policy[5]
    candid_act_idx = role_action_map[role]
    first_idx = candid_act_idx[0]
    action_elem = policy[first_idx:first_idx+len(candid_act_idx)]
    if if_contains_all(-1, action_elem):
        return False
    else:
        return True


def check_value(idx, policy):
    if policy[idx] not in value_map[idx]:
        return False
    else:
        return True


def if_contains_all(value, t_list):
    return all(i == value for i in t_list)


def if_contains_any(value, t_list):
    return any(i == value for i in t_list)


def if_contains_all_list(v_list, t_list):
    return all(i in v_list for i in t_list)










def check_policy_set():
    pass


# def check_policy(policy):
#     # check if factors came out in a wrong way
#     # role is in charge of some condition variables and actions (also the action controls methods)
#     # 반드시 나와야 하는 것, 반드시 나오면 안되는 것.
#
#     # check role and conditions
#     role = policy[5]
#     unavail_idx = role_cond_excp_map[role]
#     avail_idx = role_cond_map[role]
#
#     conditions = list()
#     conditions.append(policy_element['conditions'])
#
#     # check if there is an unavailable value
#     for idx in conditions:
#         if idx in unavail_idx & policy[idx] != -1:
#             raise PolicyWrongError()
#     # check if there is a missing value
#     values = list()
#     for idx in avail_idx:
#         values.append(policy[idx])
#     if -1 in values:
#         raise PolicyMissingError()
#
# def check_cond(role, values):
#     pass
