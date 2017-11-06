import random
from json_handle import read_policy
from policy_check import check_policy, if_contains_all

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
    policy_type = select_value_by_idx(0)
    policy[0] = policy_type
    # select a role
    role = select_value_by_idx(5)
    policy[5] = role
    # select an action according to the selected role
    action_list = role_action_map[role]
    idx = select_idx(action_list)
    action_idx = action_list[idx]

    if policy_type == 1:    # action policy
        # action method
        action_method = select_value_by_idx(action_idx)
        policy[action_idx] = action_method
        # enforce
        policy[17] = select_value_by_idx(17)
    elif policy_type == 2:  # compliance policy
        # action name mark
        policy[action_idx] = 0
        # minimum compliance
        policy[16] = select_value_by_idx(16)

    # select conditions
    candid_cond_list = role_cond_map[role]
    num_cond = random.randint(1, len(candid_cond_list))     # how many conditions?
    copied_list = list(candid_cond_list)

    for i in range(0, num_cond):
        idx = select_idx(copied_list)
        cond_idx = copied_list[idx]
        policy[cond_idx] = select_value_by_idx(cond_idx)
        del copied_list[idx]

    # make rest of indices to invalid(-1)
    for pol_idx in range(0, len(policy)):
        if policy[pol_idx] is None:
            policy[pol_idx] = -1

    return policy


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
        for idx in range(0, len(policy_set)-1):
            if random.random() < indpb:
                copied_policy = list(policy_set[idx])
                copied_policy = mut_by_modify(copied_policy)
                while not check_policy(copied_policy):
                    copied_policy = list(policy_set[idx])
                    copied_policy = mut_by_modify(copied_policy)
                policy_set[idx] = copied_policy
    return policy_set,


def mut_by_modify(policy):
    # Pick random numbers of policies from the individual.
    # Change values in contents based on relationships.
    change_category = ""

    # gather categories according to policy type
    # select a category to change
    if policy[0] == 1:        # action policy
        change_list = ['role', 'condition', 'actionName', 'actionMethod', 'methodValue', 'enforce']
        if policy[11] == -1 and policy[14] == -1:   # otherwise 11, 14, except action value
            change_list.remove("methodValue")
        change_idx = select_idx(change_list)
        change_category = change_list[change_idx]
    elif policy[0] == 2:      # compliance policy
        change_list = ['role', 'condition', 'actionName', 'compliance']
        change_idx = select_idx(change_list)
        change_category = change_list[change_idx]

    role = policy[5]
    if change_category == "role":
        # If you change role, all other elements should be changed too.
        # select a new role
        cur_role = role
        candid_roles = list()
        for role_idx in value_map[5]:
            if role_idx == cur_role:
                continue
            candid_roles.append(role_idx)
        new_role = candid_roles[select_idx(candid_roles)]
        # set a new role
        policy[5] = new_role

        # reset if role-dependent condition exists
        role_cond_indices = role_cond_map[role]
        condition_indices = list(policy_element['conditions'])
        for idx in condition_indices:
            if idx not in role_cond_indices and policy[idx] != 1:
                policy[idx] = -1

        # If there is no condition after resetting role-dependent conditions,
        # (but do nothing if at least one condition)
        cond_values = get_policy_val_list(role_cond_indices, policy)
        if if_contains_all(-1, cond_values):
            # Conditions are all empty.
            candid_cond_list = role_cond_map[role]
            num_cond = random.randint(1, len(candid_cond_list))  # how many conditions?
            copied_list = list(candid_cond_list)

            for i in range(0, num_cond):
                idx = select_idx(copied_list)
                cond_idx = copied_list[idx]
                policy[cond_idx] = select_value_by_idx(cond_idx)
                del copied_list[idx]

        # select a new action name according to a new role
        for action in list(policy_element["action"]):
            policy[action] = -1  # reset actions
        candid_actions = role_action_map[new_role]
        new_action_idx = select_idx(candid_actions)
        new_action = candid_actions[new_action_idx]
        if policy[0] == 1:       # if policy type is action,
            # select and set a new method
            policy[new_action] = select_value_by_idx(new_action)
        elif policy[0] == 2:     # else if policy type is compliance,
            # select and mark on the action
            policy[new_action] = 0
    elif change_category == "condition":     # TODO refactoring here
        # change only once!
        condition_indices = role_cond_map[role]

        mutate_categories = ['add', 'delete', 'modify']
        if check_full_description(policy, condition_indices):       # if all conditions are activated,
            mutate_categories.remove('add')
        elif check_one_description(policy, condition_indices):
            mutate_categories.remove('delete')
        mutate_category = mutate_categories[select_idx(mutate_categories)]

        candid_cond = list()
        if mutate_category == "add":
            for cond in condition_indices:
                if policy[cond] != -1:
                    continue
                candid_cond.append(cond)  # select candidate conditions
            add_cond_idx = select_idx(candid_cond)
            policy[add_cond_idx] = select_value_by_idx(add_cond_idx)
        elif mutate_category == "delete":
            for cond in condition_indices:
                # find conditions which have its value
                if policy[cond] != -1:
                    candid_cond.append(cond)
                del_cond_idx = select_idx(candid_cond)
                policy[del_cond_idx] = -1  # delete the value
        elif mutate_category == "modify":
            for cond in condition_indices:
                # find conditions which have its value
                if policy[cond] != -1:
                    candid_cond.append(cond)
            modi_cond_idx = select_idx(candid_cond)
            new_cond_val = select_value_by_idx(modi_cond_idx)
            policy[modi_cond_idx] = new_cond_val
    elif change_category == "actionName":
        action_list = role_action_map[role]
        candid_actions = list()
        # make candid list except current action
        for action in action_list:
            if policy[action] == -1:           # gather candidate actionNames
                candid_actions.append(action)
            else:                              # reset original actionName
                policy[action] = -1
        # select a new action
        new_action_idx = select_idx(candid_actions)
        new_action = candid_actions[new_action_idx]
        if policy[0] == 1:       # if policy type is action,
            # select a new method
            act_method = select_value_by_idx(new_action)
            policy[new_action] = act_method
        elif policy[0] == 2:     # else if policy type is compliance,
            # mark on the action
            policy[new_action] = 0
    elif change_category == "actionMethod":
        if policy[0] == 1:  # double check if the policy is for action.
            action_list = role_action_map[role]
            for action in action_list:
                if policy[action] != -1:
                    act_method = select_value_by_idx(action)
                    policy[action] = act_method
                    break
    elif change_category == "methodValue":
        if policy[11] != -1 or policy[14] != -1:
            policy[15] = random.randint(1, 5)
    elif change_category == "compliance":
        new_compliance = select_value_by_idx(16)
        while policy[16] == new_compliance:
            new_compliance = select_value_by_idx(16)
        policy[16] = new_compliance
    elif change_category == "enforce":
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


def check_one_description(policy, policy_elem):
    condition = list()
    for idx in policy_elem:
        if policy[idx] != -1:
            condition.append(idx)

    if len(condition) != 1:
        return False
    return True


def select_idx(candid_list):
    return random.randint(0, len(candid_list) - 1)


def select_value_by_idx(idx):
    val_list = value_map[idx]
    val_idx = random.randint(0, len(val_list) - 1)
    return val_list[val_idx]


def get_policy_val_list(idx_list, policy):
    result = list()
    for i in idx_list:
        result.append(policy[i])
    return result


def check_policy_set():
    pass
