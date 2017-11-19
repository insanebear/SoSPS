import random
from json_handle import read_policy
import itertools

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
    15: range(0, 5),
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
action_cond_map = {
    # value: indices
    6: [1, 2, 3],  # Select
    7: [1, 2, 3],  # Stage
    8: [1, 2],  # Load
    9: [1, 2],  # DeliverTo
    10: [1, 2],  # ReturnTo
    11: [1, 2],  # Wait
    12: [1, 2],  # Treat
    13: [1, 2],  # Operate
    14: [1, 2, 4],  # Release

}

action_cond_map2 = {        # TODO Add compliance policy condition
    # value: indices
    6: [1, 3],  # Select
    7: [1, 3],  # Stage
    8: [1],  # Load
    9: [1],  # DeliverTo
    10: [1],  # ReturnTo
    11: [1],  # Wait
    12: [1],  # Treat
    13: [1],  # Operate
    14: [1, 4],  # Release

}
# role_cond_map = {
#     # value: indices
#     1: [1, 2, 3],  # Rescue
#     2: [1, 2, 4],  # Transport
#     3: [1, 2, 4],  # Treatment
# }
# policy type - compliance/enforce check (Index-Index)
type_compliance_map = {
    1: [16, 17],
    2: [16, 17],
}


def my_initRepeat(container, func):
    return container(func())


def get_prev_policy(container, filename):
    return container(read_policy(filename))


def make_combination(action):
    conditions = list()
    for i in list(action_cond_map[action]):
        conditions.append(value_map[i])
    return list(itertools.product(*conditions))


def gen_individual_ack():
    policy_set = list()
    # action policies
    for role in value_map[5]:  # role = 1, 2, 3
        policy_type = 1
        for action in role_action_map[role]:
            combinations = make_combination(action)
            for combination in combinations:
                policy = [None] * 18
                policy[0] = policy_type
                policy[5] = role
                policy[17] = 0
                policy[action] = select_value_by_idx(action)  # set action method on action name
                # condition
                for cond, cond_value in zip(action_cond_map[action], combination):
                    policy[cond] = cond_value
                # method value
                if policy[11] is not None or policy[14] is not None:
                    policy[15] = select_value_by_idx(15)
                # make rest of indices to invalid(-1)
                for pol_idx in range(0, len(policy)):
                    if policy[pol_idx] is None:
                        policy[pol_idx] = -1
                # print(policy)
                policy_set.append(policy)

    # compliance policies
    for role in value_map[5]:
        policy_type = 2
        for action in role_action_map[role]:
            policy = [None] * 18
            policy[0] = policy_type
            policy[5] = role
            policy[16] = select_value_by_idx(16)  # compliance value
            policy[action] = 0  # mark on action
            for cond_value in value_map[1]:  # MCI level condition
                policy[1] = cond_value

                # make the rest of indices to invalid (-1)
                for pol_idx in range(0, len(policy)):
                    if policy[pol_idx] is None:
                        policy[pol_idx] = -1
                policy_set.append(policy)
    return policy_set


def gen_individual_multi():   #
    policy_set = list()
    # action policies
    for role in value_map[5]:   # role = 1, 2, 3
        policy_type = 1
        for action in role_action_map[role]:
            combinations = make_combination(action)
            for combination in combinations:
                policy = [None] * 18
                policy[0] = policy_type
                policy[5] = role
                policy[17] = select_value_by_idx(17)    # enforce or not
                policy[action] = select_value_by_idx(action)    # set action method on action name
                # condition
                for cond, cond_value in zip(action_cond_map[action], combination):
                    policy[cond] = cond_value
                # method value
                if policy[11] is not None or policy[14] is not None:
                    policy[15] = select_value_by_idx(15)
                # make rest of indices to invalid(-1)
                for pol_idx in range(0, len(policy)):
                    if policy[pol_idx] is None:
                        policy[pol_idx] = -1
                # print(policy)
                policy_set.append(policy)
    # compliance policies
    for role in value_map[5]:
        policy_type = 2
        for action in role_action_map[role]:
            policy = [None] * 18
            policy[0] = policy_type
            policy[5] = role
            policy[16] = select_value_by_idx(16)        # compliance value
            policy[action] = 0      # mark on action
            for cond_value in value_map[1]:            # MCI level condition
                policy[1] = cond_value

            # make the rest of indices to invalid (-1)
                for pol_idx in range(0, len(policy)):
                    if policy[pol_idx] is None:
                        policy[pol_idx] = -1
                policy_set.append(policy)

    # for role in value_map[5]:
    #     policy_type = 2
    #     for action in role_action_map[role]:
    #         combinations = make_combination(action)
    #         for combination in combinations:
    #             policy = [None] * 18
    #             policy[0] = policy_type
    #             policy[5] = role
    #             policy[16] = select_value_by_idx(16)
    #
    #             # mark on action name
    #             policy[action] = 0
    #             for cond, cond_value in zip(action_cond_map[action], combination):
    #                 policy[cond] = cond_value
    #             # make rest of indices to invalid(-1)
    #             for pol_idx in range(0, len(policy)):
    #                 if policy[pol_idx] is None:
    #                     policy[pol_idx] = -1
    #                 # print(policy)
    #             policy_set.append(policy)
    # print("Generated Set of Policies", len(policy_set))
    return policy_set


def gen_individual_directed():
    policy_set = list()
    # action policies
    for role in value_map[5]:  # role = 1, 2, 3
        policy_type = 1
        for action in role_action_map[role]:
            combinations = make_combination(action)
            for combination in combinations:
                policy = [None] * 18
                policy[0] = policy_type
                policy[5] = role
                policy[17] = 1
                # set action method on action name
                policy[action] = select_value_by_idx(action)
                for cond, cond_value in zip(action_cond_map[action], combination):
                    policy[cond] = cond_value
                # method value
                if policy[11] is not None or policy[14] is not None:
                    policy[15] = select_value_by_idx(15)
                # make rest of indices to invalid(-1)
                for pol_idx in range(0, len(policy)):
                    if policy[pol_idx] is None:
                        policy[pol_idx] = -1
                # print(policy)
                policy_set.append(policy)
    # print("Generated Set of Policies", len(policy_set))
    return policy_set


def mut_policy_ack(policy_set, m_portion):
    # in some probability, a policy is mutated by deletion, addition, or modification

    idx_list = list()
    for i in range(0, len(policy_set)-1):
        idx_list.append(i)

    to_be_mutated_idx = list()
    for i in range(0, int(len(policy_set)*m_portion)):
        num = random.randint(0, len(idx_list)-1)
        to_be_mutated_idx.append(idx_list[num])
        del idx_list[num]

    for mut_idx in to_be_mutated_idx:
        policy = policy_set[mut_idx]
        if policy[0] == 1:      # action policy
            role = policy[5]
            choice = random.randint(0, 1)
            if choice == 0:
                if policy[11] != -1 or policy[14] != -1:
                    policy[15] = select_value_by_idx(15)
                    continue
            elif choice == 1:
                action_list = role_action_map[role]
                for action in action_list:
                    if policy[action] != -1:
                        act_method = select_value_by_idx(action)
                        policy[action] = act_method
                        break
        elif policy[0] == 2:    # compliance policy
            new_compliance = select_value_by_idx(16)
            while policy[16] == new_compliance:
                new_compliance = select_value_by_idx(16)
            policy[16] = new_compliance

    return policy_set,


def mut_policy_multi(policy_set, m_portion):
    # in some probability, a policy is mutated by deletion, addition, or modification

    idx_list = list()
    for i in range(0, len(policy_set)-1):
        idx_list.append(i)

    to_be_mutated_idx = list()
    for i in range(0, int(len(policy_set)*m_portion)):
        num = random.randint(0, len(idx_list)-1)
        to_be_mutated_idx.append(idx_list[num])
        del idx_list[num]

    for mut_idx in to_be_mutated_idx:
        policy = policy_set[mut_idx]
        if policy[0] == 1:      # action policy
            role = policy[5]
            choice = random.randint(0, 2)
            if choice == 0:
                if policy[11] != -1 or policy[14] != -1:
                    policy[15] = select_value_by_idx(15)
                    continue
            elif choice == 1:
                if policy[17] == 1:     # Enforce
                    policy[17] = 0
                else:
                    policy[17] = 1
            elif choice == 2:
                action_list = role_action_map[role]
                for action in action_list:
                    if policy[action] != -1:
                        act_method = select_value_by_idx(action)
                        policy[action] = act_method
                        break

        elif policy[0] == 2:    # compliance policy
            new_compliance = select_value_by_idx(16)
            while policy[16] == new_compliance:
                new_compliance = select_value_by_idx(16)
            policy[16] = new_compliance

    return policy_set,


def mut_policy_directed(policy_set, m_portion):
    # in some probability, a policy is mutated by deletion, addition, or modification

    idx_list = list()
    for i in range(0, len(policy_set) - 1):
        idx_list.append(i)

    to_be_mutated_idx = list()
    for i in range(0, int(len(policy_set) * m_portion)):
        num = random.randint(0, len(idx_list) - 1)
        to_be_mutated_idx.append(idx_list[num])
        del idx_list[num]

    for mut_idx in to_be_mutated_idx:
        policy = policy_set[mut_idx]
        if policy[0] == 1:      # action policy
            role = policy[5]
            choice = random.randint(0, 1)
            if choice == 0:
                if policy[11] != -1 or policy[14] != -1:
                    policy[15] = select_value_by_idx(15)
                    continue
            elif choice == 1:
                action_list = role_action_map[role]
                for action in action_list:
                    if policy[action] != -1:
                        act_method = select_value_by_idx(action)
                        policy[action] = act_method
                        break
    return policy_set,


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


def check_policy_set(policy):
    # each condition has one direction of action...
    pass

#
# policies = gen_individual_all()
# make_policy_json("all_policies.json", policies)
# print(len(policies))


# def mut_policy(policy_set, m_portion):
#     # in some probability, a policy is mutated by deletion, addition, or modification
#
#     idx_list = list()
#     for i in range(0, len(policy_set)-1):
#         idx_list.append(i)
#
#     to_be_mutated_idx = list()
#     for i in range(0, int(len(policy_set)*m_portion)):
#         num = random.randint(0, len(idx_list)-1)
#         to_be_mutated_idx.append(idx_list[num])
#         del idx_list[num]
#
#     for mut_idx in to_be_mutated_idx:
#         policy = policy_set[mut_idx]
#         if policy[0] == 1:      # action policy
#             role = policy[5]
#             if policy[11] != -1 or policy[14] != -1:
#                 if bool(random.getrandbits(1)):
#                     policy[15] = select_value_by_idx(15)
#                     continue
#
#             action_list = role_action_map[role]
#             for action in action_list:
#                 if policy[action] != -1:
#                     act_method = select_value_by_idx(action)
#                     policy[action] = act_method
#                     break
#
#             # if policy[17] == 1:     # Enforce
#             #     policy[17] = 0
#             # else:
#             #     policy[17] = 1
#         elif policy[0] == 2:    # compliance policy
#             new_compliance = select_value_by_idx(16)
#             while policy[16] == new_compliance:
#                 new_compliance = select_value_by_idx(16)
#             policy[16] = new_compliance
#
#     return policy_set,

