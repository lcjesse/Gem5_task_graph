import matplotlib.pyplot as plt

# read result.txt
dir_path = "/home/wj/Study/gem5/my_STATS/Ring_bottleneck_exploration_0622/test_num_cpus/"
test_injection_rate_path = dir_path+"results.txt"

with open(test_injection_rate_path) as injection_rate_file:
    inj_data = injection_rate_file.readlines()

# use dict to store info {name: [...]}
inj_data_dict = {}
for i in range(1, len(inj_data)):
    inj_data_dict[inj_data[i].split()[0]] = inj_data[i].strip().split()[1:]
# print(inj_data_dict)

########### Latency_vs_Injection Rate ##########
# four size ring with different injection rate
injection_rate = []
for i in range(1,10):
    injection_rate.append(".0"+str(i))
for i in range(1,10):
    injection_rate.append("."+str(i)+"0")

inj_delay = {}
inj_flits_received = {}
inj_average_hops = {}
for num_cpus in ['8', '16', '32', '64']:
    inj_delay[num_cpus] = []
    inj_average_hops[num_cpus] = []
    inj_flits_received[num_cpus] = []
    for inj in injection_rate:
        filename = "Ring_Uniform_" + num_cpus + "_InjectionRate_" + inj + "_SimCycles_1000000"
        if len(inj_data_dict[filename]) != 0:
            inj_delay[num_cpus].append(inj_data_dict[filename][2])
            inj_average_hops[num_cpus].append(inj_data_dict[filename][1])
            inj_flits_received[num_cpus].append(inj_data_dict[filename][0])
        # else:
            # inj_delay[num_cpus].append(0)
            # inj_average_hops[num_cpus].append(0)
            # inj_flits_received[num_cpus].append(0)

# print(inj_delay)
# print(inj_average_hops)
# print(inj_flits_received)
performance = {}
performance['Average Flit Latency'] = inj_delay
performance['Average Hops'] = inj_average_hops
performance['Flits Received'] = inj_flits_received

# plot
line_type = ['-x', '-*', '-^', '-o']
for k,v in performance.items():
    legend_list = []
    plt_ptrs = []
    i = 0
    for num_cpus in ['8', '16', '32', '64']:
        legend_list.append(num_cpus + "cores")
        # Note ! add comma! if not, return a list with one object, else return the required object.
        plt_ptr, = plt.plot([float(x) for x in v[num_cpus]], line_type[i])
        plt_ptrs.append(plt_ptr)
        i += 1

    plt.title(k + " vs. Injection Rate", fontsize=10)
    plt.xlabel("Injection Rate", fontsize=12)
    plt.ylabel(k, fontsize=12)
    plt.legend(plt_ptrs, legend_list)
    ax = plt.gca()
    ax.set_xticks([i for i in range(len(injection_rate))])
    ax.set_xticklabels(injection_rate)
    # plt.savefig(k + '_vs_Injection_Rate.png')
    plt.show()
