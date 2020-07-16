import matplotlib.pyplot as plt

# read two result.txt
dir_path = "/home/wj/Study/gem5/my_STATS/test_20200616/"
test_msg_size_path = dir_path+"test_msg_size/results.txt"

with open(test_msg_size_path) as msg_file:
    msg_data = msg_file.readlines()

# use dict to store info {name: [...]}
msg_data_dict = {}
for i in range(1, len(msg_data)):
    msg_data_dict[msg_data[i].split()[0]] = msg_data[i].split()[1:]

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
        msg_delay[app_name].append(msg_data_dict[filename][3])
# print(msg_data_dict)
# print(msg_delay)

# plot
line_type = ['-x', '-*', '-^', '-o', '-s']
legend_list = []
plt_ptrs = []
for app_num in range(1,6):
    app_name = "Application_0" + str(app_num)
    legend_list.append(app_name)
    plt_ptr, = plt.plot([float(x) for x in msg_delay[app_name]], line_type[app_num-1])
    plt_ptrs.append(plt_ptr)

plt.title("Average Flit Network Latency vs. Message Size (Iters=50)", fontsize=11)
plt.xlabel("Message Size Set (bit)", fontsize=12)
plt.ylabel("Average Flit Network Latency (Cycle)", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3,4])
ax.set_xticklabels(msg_size)
plt.savefig('Network_Latency_vs_Msg_Size_50.jpg')
plt.show()

