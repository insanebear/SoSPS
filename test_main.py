import json_handle
from policy_op import rand_gen_policies
import policy_op


# Test module
policy_list = json_handle.read_policy("./archivedPolicy.json")

new_policies = rand_gen_policies(10)

index = list()
for i in range(0, 18):
    index.append(i)

print(index)

for p in policy_list:
    print(p)
    # json_handle.write_policy(p)
print("New Policy")
for p in new_policies:
    print(p)
    json_handle.write_policy(p)

# for policy in policy_list:
#     if policy_op.check_policy(policy):
#         print("yay")
#     else:
#         print("-_-")