import traceback
import sys

""" Representation of a policy
        ------------------------------------------------------------------------
        [0]     [1]     [2]     [3]     [4]     [5]     [6]     [7]     [8]
        ------------------------------------------------------------------------
        Policy |MCI   |Damage |Story  |Time   |Role   |Select  |Stage  |Load
        Type   |Level |Type   |       |       |       |        |       |
        ------------------------------------------------------------------------
        [9]     [10]    [11]    [12]    [13]    [14]    [15]    [16]    [17]
        ------------------------------------------------------------------------
        Deliver|Return|Wait   |Treat  |Operate|Release|Method  |Compli |Enforce
        To     |To    |*      |       |       |*      |value   |ance   |
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
    17: "Enforce",
}

# Category
policy_element = {
    "policyType": 0,
    "conditions": [1, 2, 3, 4],
    "role": 5,
    "action": [6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
    "minCompliance": 16,
    "enforce": 17,
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
# policy type - compliance/enforce check (Index-Index)
# type_compliance_map = {
#     1: [16, 17],
#     2: [16, 17],
# }


class PolicyError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return self.value


def check_policy(policy):
    try:
        # check policy type
        policy_type = policy[0]
        if policy_type == -1:
            PolicyError("PolicyType Error: " + str(policy[0]))
            return False
        else:
            if policy_type not in value_map[0]:
                PolicyError("PolicyType Error: " + str(policy[0]))
                return False

        # check role
        role = policy[5]
        if role == -1:
            PolicyError("Role Error: " + str(policy[5]))
            return False
        else:
            if role not in value_map[5]:
                PolicyError("Role Error: " + str(policy[5]))
                return False

        # check conditions
        conditions = policy[1:5]
        if conditions.count(-1) == len(conditions):     # no condition is activated
            PolicyError("Condition Error: " + str(policy[1:5]))
            return False
        else:
            cond_indices = policy_element["conditions"]
            role_cond_indices = role_cond_map[role]
            for cond_idx in cond_indices:   # check if it is role-related condition
                if policy[cond_idx] != -1 and cond_idx not in role_cond_indices:
                    # there is condition but not related to a role
                    PolicyError("Condition Error: " + str(policy[1:5]))
                    return False

            for cond_idx in role_cond_indices:  # check if a role condition has proper value
                if policy[cond_idx] not in value_map[cond_idx]:
                    # find if value belongs to a value list
                    PolicyError("Condition Error: " + str(policy[1:5]))
                    return False

        # check actions
        actions = policy[6:15]  # except method value due to optional
        if actions.count(-1) != len(actions)-1:       # action should exist one
            PolicyError("Action Error: " + str(policy[6:15]))
            return False
        else:
            actions_indices = role_action_map[role]
            if policy_type == 1:
                for action_idx in actions_indices:
                    if policy[action_idx] != -1 and policy[action_idx] not in value_map[action_idx]:
                        PolicyError("Action Error: " + str(policy[6:15]))
                        return False
            elif policy_type == 2:
                for action_idx in actions_indices:
                    if policy[action_idx] not in (-1,0):
                        PolicyError("Action Error: " + str(policy[6:15]))
                        return False

        # check compliance
        if policy_type == 1 and policy[16] != -1:
            PolicyError("Compliance Error: " + str(policy[16]))
            return False
        elif policy_type == 2 and policy[16] == -1:
            PolicyError("Compliance Error: " + str(policy[16]))
            return False
        # check enforce
        if policy_type == 1 and policy[17] == -1:
            PolicyError("Enforce Error: " + str(policy[16]))
            return False

    except PolicyError as e:
        print(policy)
        print(e)
        print(traceback.format_exc())
        print(sys.exc_info())
    return True


def if_contains_all(value, t_list):
    return all(i == value for i in t_list)


def if_contains_any(value, t_list):
    return any(i == value for i in t_list)


def if_contains_all_list(v_list, t_list):
    return all(i in v_list for i in t_list)


def non_related_indices(role):
    cond_elements = policy_element["conditions"]
    role_conds = role_cond_map[role]
    result = list()
    for elem in cond_elements:
        if elem not in role_conds:
            result.append(elem)
    return result


def get_policy_val_list(idx_list, policy):
    result = list()
    for i in idx_list:
        result.append(policy[i])
    return result


def check_full_description(policy, policy_elem):
    for idx in policy_elem:
        if policy[idx] == -1:
            return False
    return True

def check_one_description(policy, policy_elem):
    condition = list()
    for idx in policy_elem:
        if policy[idx] != -1:
            condition.append(idx)

    if len(condition) != 1:
        return False
    return True