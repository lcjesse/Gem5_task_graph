import matplotlib.pyplot as plt

# read two result.txt
dir_path = "/home/wj/Study/gem5/my_STATS/test_20200616/"
test_iters_path = dir_path+"test_iters_512_12288_512/results.txt"

with open(test_iters_path) as iters_file:
    iters_data = iters_file.readlines()

# use dict to store info {name: [...]}
iters_data_dict = {}
for i in range(1, len(iters_data)):
    iters_data_dict[iters_data[i].split()[0]] = iters_data[i].strip().split()[1:]
# print(iters_data_dict)

########### Latency_vs_Iters ##########
# five apps with different iterations
iters = ['1', '10', '20', '30', '40', '50']
iters_delay = {}
for app_num in range(1,6):
    app_name = "Application_0" + str(app_num)
    iters_delay[app_name] = []
    for iter in iters:
        filename = "Application_0" + str(app_num) + "_iters" + iter
        iters_delay[app_name].append(iters_data_dict[filename][3])
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

plt.title("Average Flit Network Latency vs. Execution Iterations (Msg Size 512_12288_512)", fontsize=10)
plt.xlabel("Execution Iterations", fontsize=12)
plt.ylabel("Average Flit Network Latency (Cycle)", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3,4,5])
ax.set_xticklabels(iters)
plt.savefig('Network_Latency_vs_Iters_512_12288_512.jpg')
plt.show()
