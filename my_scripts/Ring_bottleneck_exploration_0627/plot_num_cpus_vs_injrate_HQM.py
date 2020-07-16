import matplotlib.pyplot as plt

# read result.txt
dir_path = "/home/wj/Study/gem5/my_STATS/Ring_bottleneck_exploration_0627/Uniform_different_num_cores_with_HQM_vs_different_inj_rate/"
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
for i in range(1,9):
    injection_rate.append(".0"+str(i))
for i in range(10,15):
    injection_rate.append("."+str(i))

inj_delay = {}
inj_network_delay = {}
inj_vnet0_delay = {}
inj_vnet1_delay = {}
inj_vnet2_delay = {}
inj_flits_received = {}
inj_average_hops = {}
for num_cpus in ['8', '16', '32', '64', '128', '256']:
    inj_delay[num_cpus] = []
    inj_average_hops[num_cpus] = []
    inj_flits_received[num_cpus] = []
    inj_network_delay[num_cpus] = []
    inj_vnet0_delay[num_cpus] = []
    inj_vnet1_delay[num_cpus] = []
    inj_vnet2_delay[num_cpus] = []
    for inj in injection_rate:
        filename = "Ring_Uniform_" + num_cpus + "_InjectionRate_" + inj + "_SimCycles_1000000"
        if len(inj_data_dict[filename]) != 0:
            inj_delay[num_cpus].append(inj_data_dict[filename][2])
            inj_average_hops[num_cpus].append(inj_data_dict[filename][1])
            inj_flits_received[num_cpus].append(inj_data_dict[filename][0])
            inj_network_delay[num_cpus].append(inj_data_dict[filename][3])
            inj_vnet0_delay[num_cpus].append(inj_data_dict[filename][4])
            inj_vnet1_delay[num_cpus].append(inj_data_dict[filename][5])
            inj_vnet2_delay[num_cpus].append(inj_data_dict[filename][6])
        # else:
            # inj_delay[num_cpus].append(0)
            # inj_average_hops[num_cpus].append(0)
            # inj_flits_received[num_cpus].append(0)

# print(inj_delay)
# print(inj_average_hops)
# print(inj_flits_received)
performance = {}
performance['Average_Flit_Latency'] = inj_delay
performance['Average_Hops'] = inj_average_hops
performance['Flits_Received'] = inj_flits_received
performance['Average_Flit_Network_Latency'] = inj_network_delay
performance['Average_Flit_Vnet0_latency'] = inj_vnet0_delay
performance['Average_Flit_Vnet1_latency'] = inj_vnet1_delay
performance['Average_Flit_Vnet2_latency'] = inj_vnet2_delay

# plot
line_type = ['-x', '-*', '-^', '-o', '-D', '-p']
for k,v in performance.items():
    legend_list = []
    plt_ptrs = []
    i = 0
    for num_cpus in ['8', '16', '32', '64', '128', '256']:
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
    plt.savefig(k + '_vs_Injection_Rate_HQM.png')
    plt.show()
