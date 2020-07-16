import matplotlib.pyplot as plt

# read two result.txt
dir_path = "/home/wj/Study/gem5/my_STATS/test_20200616/"
test_iters_path = dir_path+"test_iters/results.txt"
test_msg_size_path = dir_path+"test_msg_size/results.txt"

with open(test_iters_path) as iters_file:
    iters_data = iters_file.readlines()

with open(test_msg_size_path) as msg_file:
    msg_data = msg_file.readlines()

# use dict to store info {name: [...]}
iters_data_dict = {}
msg_data_dict = {}
for i in range(1, len(iters_data)):
    iters_data_dict[iters_data[i].split()[0]] = iters_data[i].strip().split()[1:]
# print(iters_data_dict)
for i in range(1, len(msg_data)):
    msg_data_dict[msg_data[i].split()[0]] = msg_data[i].split()[1:]

########### Latency_vs_Iters ##########
# five apps with different iterations
iters = ['1', '10', '20', '30', '40', '50']
iters_delay = {}
for app_num in range(1,6):
    app_name = "Application_0" + str(app_num)
    iters_delay[app_name] = []
    for iter in iters:
        filename = "Application_0" + str(app_num) + "_iters" + iter
        iters_delay[app_name].append(iters_data_dict[filename][2])
# print(iters_delay)

# plot
line_type = ['-x', '-*', '-^', '-o', '-s']
legend_list = []
plt_ptrs = []
i = 0
for app_num in range(1,6):
    app_name = "Application_0" + str(app_num)
    legend_list.append(app_name)
    # Note ! add comma! if not, return a list with one object, else return the required object.
    plt_ptr, = plt.plot([float(x) for x in iters_delay[app_name]], line_type[i])
    plt_ptrs.append(plt_ptr)
    i += 1

plt.title("Average Flit Latency vs. Execution Iterations (Msg Size 256-512-512)")
plt.xlabel("Execution Iterations", fontsize=12)
plt.ylabel("Average Flit Latency (Cycle)", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3,4,5])
ax.set_xticklabels(iters)
plt.savefig('Latency_vs_Iters_256_512_512.jpg')
plt.show()

########## Latency_vs_Msg_size ##########
# five apps with different message size
msg_size=['256_512_512', '256_1600_512', '256_5120_512', '256_12288_512', '512_12288_512']
iters_msg = 50
msg_delay = {}
for app_num in range(1, 6):
    app_name = "Application_0" + str(app_num)
    msg_delay[app_name] = []
    for i in range(len(msg_size)):
        filename = "Application_0" + str(app_num) + "_iters" + str(iters_msg) + "_msg_" + msg_size[i]
        msg_delay[app_name].append(msg_data_dict[filename][2])
# print(msg_data_dict)
# print(msg_delay)

# plot
legend_list = []
plt_ptrs = []
for app_num in range(1,6):
    app_name = "Application_0" + str(app_num)
    legend_list.append(app_name)
    plt_ptr, = plt.plot([float(x) for x in msg_delay[app_name]], line_type[app_num-1])
    plt_ptrs.append(plt_ptr)

plt.title("Average Flit Latency vs. Message Size (Iters=50)")
plt.xlabel("Message Size Set (bit)", fontsize=12)
plt.ylabel("Average Flit Latency (Cycle)", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3,4])
ax.set_xticklabels(msg_size)
plt.savefig('Latency_vs_Msg_Size_50.jpg')
plt.show()

