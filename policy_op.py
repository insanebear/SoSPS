import random
from json_handle import read_policy

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
type_compliance_map = {
    1: [16, 17],
    2: [16, 17],
}


def my_initRepeat(container, func, max_size):
    ind_size = random.randint(2, max_size)
    return container(func(ind_size))


def get_prev_policy(container, filename):
    return container(read_policy(filename))


def gen_individual(ind_size):
    # individual means a set of policies
    policy_set = list()
    for i in range(0, ind_size):
        policy = gen_policy()
        while not check_policy(policy):
            policy = gen_policy()
            if check_policy(policy):
                break
        policy_set.append(policy)
    return policy_set


def gen_policy():
    # initialize policy element with fixed length
    policy = [None] * 18

    # select a policy type
    policy_type = sel_rand_val(0)
    policy[0] = policy_type
    # select a role
    role = sel_rand_val(5)
    policy[5] = role
    # select an action according to the selected role
    action_list = role_action_map[role]
    action_name = action_list[sel_rand_idx(action_list)]

    if policy_type == 1:    # action policy
        action_method = sel_rand_val(action_name)
        policy[action_name] = action_method
        policy[17] = sel_rand_val(17)
    elif policy_type == 2:  # compliance policy
        policy[action_name] = 0                 # 0 as a check sign
        policy[16] = sel_rand_val(16)  # minimum compliance

    candid_cond_list = role_cond_map[role]
    num_cond = random.randint(1, len(candid_cond_list))     # how many conditions?

    for i in range(0, num_cond-1):
        copied_list = list(candid_cond_list)

        cond_name = copied_list[sel_rand_idx(copied_list)]
        copied_list.remove(cond_name)
        policy[cond_name] = sel_rand_val(cond_name)

    # make rest of indices to invalid(-1
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


def mut_policy(policy_set, indpb):
    # in some probability, a policy is mutated by deletion, addition, or modification
    mut_type_prob = random.random()

    if mut_type_prob < 0.2:
        # mutation by addition
        policy = gen_policy()
        while not check_policy(policy):
            policy = gen_policy()
            if check_policy(policy):
                break
        policy_set.append(policy)
    elif mut_type_prob < 0.4:
        if len(policy_set) > 2:
            del_idx = random.randint(0, len(policy_set)-1)
            del policy_set[del_idx]
    elif mut_type_prob < 1.0:
        for policy in policy_set:
            if random.random() < indpb:
                # print("Before", policy)
                mut_by_modify(policy)
                # print("After", policy)

    return policy_set,


def mut_by_modify(policy):
    # Pick random numbers of policies from the individual.
    # Change values in contents based on relationships.
    change_content = ""

    if policy[0] == 1:        # action policy
        change_category = ['role', 'condition', 'actionName', 'actionMethod', 'actionValue', 'enforce']
        change_idx = sel_rand_idx(change_category)
        if change_idx == 4:
            while policy[11] == -1 and policy[14] == -1:
                change_idx = sel_rand_idx(change_category)
        change_content = change_category[change_idx]
    elif policy[0] == 2:      # compliance policy
        change_category = ['role', 'condition', 'actionName', 'compliance']
        change_idx = random.randint(0, len(change_category)-1)
        change_content = change_category[change_idx]

    role = policy[5]
    if change_content == "role":
        role_list = value_map[5]
        cur_role = role
        candid_roles = list()
        for role_idx in role_list:
            if role_idx == cur_role:
                continue
            candid_roles.append(role_idx)
        # set a new role
        new_role = candid_roles[random.randint(0, len(candid_roles)-1)]
        policy[5] = new_role
        for action in list(policy_element["action"]):
            policy[action] = -1     # reset actions

        # select a new action name according to a new role
        candid_actions = role_action_map[new_role]
        new_action_idx = sel_rand_idx(candid_actions)
        new_action = candid_actions[new_action_idx]
        if policy[0] == 1:       # if policy type is action,
            # select a new method
            policy[new_action] = sel_rand_val(new_action)
        elif policy[0] == 2:     # else if policy type is compliance,
            # mark on the action
            policy[new_action] = 0
    elif change_content == "condition":     # TODO refactoring here
        # change only once!
        cond_by_role = role_cond_map[role]
        prob = random.random()
        if not check_full_description(policy, cond_by_role):
            candid_cond = list()
            if prob < 0.2:
                # add new a condition
                for cond in cond_by_role:
                    if policy[cond] != -1:
                        continue
                    candid_cond.append(cond)    # select candidate conditions
                change_cond_idx = sel_rand_idx(candid_cond)
                policy[change_cond_idx] = sel_rand_val(change_cond_idx)
            elif prob < 0.4:
                # delete a condition
                candid_cond = list()
                for cond_idx in cond_by_role:
                    # find conditions which have its value
                    if policy[cond_idx] != -1:
                        candid_cond.append(cond_idx)
                if len(candid_cond) > 1:
                    target_idx = sel_rand_idx(candid_cond)
                    policy[target_idx] = -1     # delete the value
            elif prob < 1.0:
                # change an original condition
                candid_cond = list()
                for cond_idx in cond_by_role:
                    # find conditions which have its value
                    if policy[cond_idx] != -1:
                        candid_cond.append(cond_idx)
                target_idx = sel_rand_idx(candid_cond)
                new_cond_val = sel_rand_val(target_idx)
                policy[target_idx] = new_cond_val
        else:
            if prob < 0.5:      # delete a condition
                candid_cond = list()
                for cond_idx in cond_by_role:
                    # find conditions which have its value
                    if policy[cond_idx] != -1:
                        candid_cond.append(cond_idx)
                if len(candid_cond) > 1:
                    target_idx = sel_rand_idx(candid_cond)
                    policy[target_idx] = -1  # delete the value
            elif prob < 1.0:    # change an original condition
                # change an original condition
                candid_cond = list()
                for cond_idx in cond_by_role:
                    # find conditions which have its value
                    if policy[cond_idx] != -1:
                        candid_cond.append(cond_idx)
                target_idx = sel_rand_idx(candid_cond)
                new_cond_val = sel_rand_val(target_idx)
                policy[target_idx] = new_cond_val
    elif change_content == "actionName":
        action_list = role_action_map[role]
        candid_actions = list()
        # make candid list except current action
        for action in action_list:
            if policy[action] == -1:
                candid_actions.append(action)
            else:
                policy[action] = -1
        # select a new action
        new_action_idx = sel_rand_idx(candid_actions)
        new_action = candid_actions[new_action_idx]
        if policy[0] == 1:       # if policy type is action,
            # select a new method
            act_method = sel_rand_val(new_action)
            policy[new_action] = act_method
        elif policy[0] == 2:     # else if policy type is compliance,
            # mark on the action
            policy[new_action] = 0
    elif change_content == "actionMethod":
        if policy[0] == 1:  # double check if the policy is for action.
            action_list = role_action_map[role]
            for action in action_list:
                if policy[action] != -1:
                    act_method = sel_rand_val(action)
                    policy[action] = act_method
                    break
    elif change_content == "actionValue":
        candid_action = list()
        for action in (11, 14):
            if policy[action] != -1:
                candid_action.append(action)
        target_idx = sel_rand_idx(candid_action)
        policy[15] = sel_rand_val(target_idx)
    elif change_content == "compliance":
        new_compliance = float(random.randint(0, 9)/10)
        while policy[16] == new_compliance:
            new_compliance = float(random.randint(0, 9) / 10)
        policy[16] = new_compliance
    elif change_content == "enforce":
        if policy[17] == 1:
            policy[17] = 0
        else:
            policy[17] = 1

    return policy


def check_full_description(policy, policy_elem):
    for idx in policy_elem:
        if policy[idx] == -1:
            return False
    return True


def sel_rand_idx(candid_list):
    return random.randint(0, len(candid_list) - 1)


def sel_rand_val(idx):
    val_list = value_map[idx]
    val_idx = random.randint(0, len(val_list) - 1)
    return val_list[val_idx]


def check_policy_set():
    pass
