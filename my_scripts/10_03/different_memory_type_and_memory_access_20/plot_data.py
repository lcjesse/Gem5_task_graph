import matplotlib.pyplot as plt

# read two result.txt
dir_path = "/home/wj/test/Gem5_task_graph/my_STATS/test_0930/different_memory_type_and_memory_access_20/"
test_path = dir_path+"results.txt"
fig_path = dir_path+"figs/"
link_result_path = dir_path+"LINK_RESULT/"
log_path = dir_path + "log"

with open(test_path) as input_file:
    input_data = input_file.readlines()

# use dict to store info {name: [...]}
input_data_dict = {}

for i in range(1, len(input_data)):
    input_data_dict[input_data[i].split()[0]] = input_data[i].strip().split()[1:]

########### Five parameters_vs_Iters ##########
# five apps with different iterations
mem_type = ['DDR', 'DDR2', 'DDR3', 'DDR4']
ete_delay = {}
flits = {}
hops = {}
latency = {}
network_latency = {}
queueing_latency = {}
for app_num in range(1,6):
    app_name = "App_0" + str(app_num)
    ete_delay[app_name] = []
    flits[app_name] = []
    hops[app_name] = []
    latency[app_name] = []
    network_latency[app_name] = []
    queueing_latency[app_name] = []
    for mt in mem_type:
        filename = "Application_0" + str(app_num) + "_Memory_Type_" + mt
        ete_delay[app_name].append(input_data_dict[filename][5])
        flits[app_name].append(input_data_dict[filename][0])
        hops[app_name].append(input_data_dict[filename][1])
        latency[app_name].append(input_data_dict[filename][2])
        network_latency[app_name].append(input_data_dict[filename][3])
        queueing_latency[app_name].append(input_data_dict[filename][4])
# print(latency)


######################## plot ete delay ########################
line_type = ['-x', '-*', '-^', '-o', '-s']
legend_list = [] #
plt_ptrs = []
i = 0
plt.cla()
for app_num in range(1,6):
    app_name = "App_0" + str(app_num)
    legend_list.append(app_name)
    # Note ! add comma! if not, return a list with one object, else return the required object.
    plt_ptr, = plt.plot([int(x) for x in ete_delay[app_name]], line_type[i])
    plt_ptrs.append(plt_ptr)
    i += 1

plt.title("Average ETE Delay vs. Memory Type")
plt.xlabel("Memory Type", fontsize=12)
plt.ylabel("Average ETE Delay", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3])
ax.set_xticklabels(mem_type)
plt.tight_layout()      # avoid incomplete display
plt.savefig(fig_path + 'Average_ETE_Delay_vs_Memory_Type.jpg')


######################## plot flits received ########################
line_type = ['-x', '-*', '-^', '-o', '-s']
legend_list = []
plt_ptrs = []
i = 0
plt.cla()
for app_num in range(1,6):
    app_name = "App_0" + str(app_num)
    legend_list.append(app_name)
    # Note ! add comma! if not, return a list with one object, else return the required object.
    plt_ptr, = plt.plot([int(x) for x in flits[app_name]], line_type[i])
    plt_ptrs.append(plt_ptr)
    i += 1

plt.title("Flits Received vs. Memory Type")
plt.xlabel("Memory Type", fontsize=12)
plt.ylabel("Flits Received", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3])
ax.set_xticklabels(mem_type)
plt.savefig(fig_path + 'Flits_vs_Memory_Type.jpg')


######################## plot hops ########################
line_type = ['-x', '-*', '-^', '-o', '-s']
legend_list = []
plt_ptrs = []
i = 0
plt.cla()
for app_num in range(1,6):
    app_name = "App_0" + str(app_num)
    legend_list.append(app_name)
    # Note ! add comma! if not, return a list with one object, else return the required object.
    plt_ptr, = plt.plot([float(x) for x in hops[app_name]], line_type[i])
    plt_ptrs.append(plt_ptr)
    i += 1

plt.title("Average Flit Hops vs. Memory Type")
plt.xlabel("Memory Type", fontsize=12)
plt.ylabel("Average Flit Hops", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3])
ax.set_xticklabels(mem_type)
plt.tight_layout()
plt.savefig(fig_path + 'Hops_vs_Memory_Type.jpg')

plt.clf()

# plot latency
line_type = ['-x', '-*', '-^', '-o', '-s']
legend_list = []
plt_ptrs = []
i = 0
for app_num in range(1,6):
    app_name = "App_0" + str(app_num)
    legend_list.append(app_name)
    # Note ! add comma! if not, return a list with one object, else return the required object.
    plt_ptr, = plt.plot([float(x) for x in latency[app_name]], line_type[i])
    plt_ptrs.append(plt_ptr)
    i += 1

plt.title("Average Flit Latency vs. Memory Type")
plt.xlabel("Memory Type", fontsize=12)
plt.ylabel("Average Flit Latency (Cycle)", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3])
ax.set_xticklabels(mem_type)
plt.tight_layout()
plt.savefig(fig_path + 'Latency_vs_Memory_Type.jpg')


######################## plot network latency ########################
line_type = ['-x', '-*', '-^', '-o', '-s']
legend_list = []
plt_ptrs = []
i = 0
plt.cla()
for app_num in range(1,6):
    app_name = "App_0" + str(app_num)
    legend_list.append(app_name)
    # Note ! add comma! if not, return a list with one object, else return the required object.
    plt_ptr, = plt.plot([float(x) for x in network_latency[app_name]], line_type[i])
    plt_ptrs.append(plt_ptr)
    i += 1

plt.title("Average Flit Network Latency vs. Memory Type")
plt.xlabel("Memory Type", fontsize=12)
plt.ylabel("Average Flit Network Latency (Cycle)", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3])
ax.set_xticklabels(mem_type)
plt.tight_layout()
plt.savefig(fig_path + 'Network_Latency_vs_Memory_Type.jpg')


######################## plot queueing latency ########################
line_type = ['-x', '-*', '-^', '-o', '-s']
legend_list = []
plt_ptrs = []
i = 0
plt.cla()
for app_num in range(1,6):
    app_name = "App_0" + str(app_num)
    legend_list.append(app_name)
    # Note ! add comma! if not, return a list with one object, else return the required object.
    plt_ptr, = plt.plot([float(x) for x in queueing_latency[app_name]], line_type[i])
    plt_ptrs.append(plt_ptr)
    i += 1

plt.title("Average Flit Queueing Latency vs. Memory Type")
plt.xlabel("Memory Type", fontsize=12)
plt.ylabel("Average Flit Queueing Latency (Cycle)", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3])
ax.set_xticklabels(mem_type)
plt.tight_layout()
plt.savefig(fig_path + 'Queueing_Latency_vs_Memory_Type.jpg')

plt.clf()
######################## plot link utilization for each app ########################
for app_num in range(1,6):
    plt_ptrs = []
    legend_list = []
    line_type = ['-x', '-*', '-^', '-o']
    j = 0
    plt.cla()       #clear plt
    for mt in mem_type:
        legend_list.append("mem_type_" + mt)
        link_file_path = link_result_path + "link_record_App_0" + str(app_num) + "_Memory_Type_" + mt + ".txt"
        with open(link_file_path) as input_file:
            input_data = input_file.readlines()
        link_utilization = []
        for i in range(1,len(input_data)):
            this_line = input_data[i].split()
            link_utilization.append(int(this_line[1]))
        plt_ptr, = plt.plot([int(x) for x in link_utilization], line_type[j])
        plt_ptrs.append(plt_ptr)
        j += 1
    plt.title("Link Utilization in Each Router for App_0"+ str(app_num))
    plt.xlabel("Router ID", fontsize=12)
    plt.ylabel("Link Utilization", fontsize=12)
    plt.legend(plt_ptrs, legend_list)
    ax = plt.gca()
    ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11])
    plt.tight_layout()      # avoid incomplete display
    plt.savefig(fig_path + 'Link_Util_App_0' + str(app_num) +'.jpg')

'''
######################## plot ETE delay for each router ########################
ete_file_path = dir_path + "APP_ETE_delay.txt"
with open(ete_file_path) as input_file:
    ete_data = input_file.readlines()
legend_list = []
line_type = ['-x', '-*', '-^', '-o', '-s']
plt.cla()
for i in range(1, len(ete_data)):
    this_line = ete_data[i].split()
    app_name = this_line[0]
    legend_list.append(app_name)
    ETE_delay = []
    for j in range(1, len(this_line)):
        ETE_delay.append(this_line[j])
    plt_ptr, = plt.plot([int(x) for x in ETE_delay], line_type[i-1])
    plt_ptrs.append(plt_ptr)
plt.title("ETE Delay vs. Memory Type")
plt.xlabel("Memory Type", fontsize=12)
plt.ylabel("ETE Delay (cycle)", fontsize=12)
plt.legend(plt_ptrs, legend_list)
ax = plt.gca()
ax.set_xticks([0,1,2,3,4,5])
ax.set_xticklabels(iters)
plt.tight_layout()      # avoid incomplete display
plt.savefig(fig_path + 'ETE_Delay_vs_Iters.jpg')

'''
######################## plot link utilization for each app ########################
for app_num in range(1,6):
    plt_ptrs = []
    legend_list = []
    line_type = ['-x', '-*', '-^', '-o', '-s', '-D']
    j = 0
    plt.cla()       #clear plt
    for mt in mem_type:
        legend_list.append("mem_type_" + mt)
        link_file_path =link_result_path + "link_record_App_0" + str(app_num) + "_Memory_Type_" + mt + ".txt"
        with open(link_file_path) as input_file:
            input_data = input_file.readlines()
        link_utilization_ratio = []
        total_link_util = 0
        for i in range(1,len(input_data)):
            this_line = input_data[i].split()
            total_link_util += (int(this_line[1]))
        for i in range(1,len(input_data)):
            this_line = input_data[i].split()
            link_utilization_ratio.append(int(this_line[1])/total_link_util)
        plt_ptr, = plt.plot([float(x) for x in link_utilization_ratio], line_type[j])
        plt_ptrs.append(plt_ptr)
        j += 1
    plt.title("Link Utilization Ratio in Each Router for App_0"+ str(app_num))
    plt.xlabel("Router ID", fontsize=12)
    plt.ylabel("Link Utilization Ratio", fontsize=12)
    plt.legend(plt_ptrs, legend_list)
    ax = plt.gca()
    ax.set_xticks([0,1,2,3,4,5,6,7,8,9,10,11])
    plt.tight_layout()      # avoid incomplete display
    plt.savefig(fig_path + 'Link_Util_Ratio_App_0' + str(app_num) +'.jpg')

# plt.clf()
# ################### PIE
for app_num in range(1,6):
    plt.cla()
    link_file_path =link_result_path + "link_record_App_0" + str(app_num) + "_iters_100.txt"
    legend_list = ['HQM', 'Core-0', 'PE-1 PE-2', 'DDR-0', 'PE-3 PE-4 PE-5', 'PE-13', 'Core-1', \
        'Core-2', 'PE-6 PE-7 PE-8', 'DDR-1', 'PE-9 PE-10 PE-11 PE-12', 'Core-3']
    with open(link_file_path) as input_file:
        input_data = input_file.readlines()
    link_utilization = [int(input_data[i].strip().split()[1]) for i in range(1, len(input_data))]
    explode = [0.01] * 12
    plt.pie(link_utilization, explode=explode, labels=legend_list)
    plt.title("Link Utilization for App_0"+ str(app_num))
    plt.tight_layout()
    plt.savefig(fig_path + 'pie_Link_Util_Ratio_App_0' + str(app_num) +'.jpg')

# ### Note Here!!
# plt.clf()
# ##################### plot ete delay with iters in one simulation #####################
# current_iter = 100
# with open(log_path) as log_file:
#     log_data = log_file.readlines()

log_data_dict = {}
average_delay_time = {}
for app_num in range(1,6):
    key_word = "Application_0"+str(app_num)+"_Iters_"+str(current_iter)
    start_idx = -1
    for i in range(len(log_data)):
        if key_word in log_data[i]:
            start_idx = i + 3
            break
    assert(start_idx != -1)

    each_iter_data = []
    aver_data = []
    total_delay = 0
    assert(log_data[start_idx+current_iter-1].strip().split()[1] == str(current_iter-1))
    for i in range(start_idx, start_idx+current_iter):
        delay = log_data[i].strip().split()[-1]
        total_delay += int(delay)
        each_iter_data.append(delay)
        aver_data.append(total_delay/(i-start_idx+1))

    app_name = "App_0" + str(app_num)
    log_data_dict[app_name] = each_iter_data
    average_delay_time[app_name] = aver_data


### ete delay for each iteration
line_type = ['-x', '-*', '-^', '-o', '-s']
legend_list = []
plt_ptrs = []
i = 0
plt.cla()
for app_num in range(1,6):
    app_name = "App_0" + str(app_num)
    legend_list.append(app_name)
    # Note ! add comma! if not, return a list with one object, else return the required object.
    plt_ptr, = plt.plot([int(x) for x in log_data_dict[app_name]], line_type[i])
    plt_ptrs.append(plt_ptr)
    i += 1

# plt.title("ETE Delay vs. Memory Type")
# plt.xlabel("Memory Type", fontsize=12)
# plt.ylabel("ETE Delay", fontsize=12)
# plt.legend(plt_ptrs, legend_list)
# ax = plt.gca()
# iters = ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
# ax.set_xticks([i*10 for i in range(1,11)])
# ax.set_xticklabels(iters)
# plt.tight_layout()      # avoid incomplete display
# plt.savefig(fig_path + 'ETE_Delay_vs_Iters.jpg')

# ### average ete delay for current iterations
# line_type = ['-x', '-*', '-^', '-o', '-s']
# legend_list = []
# plt_ptrs = []
# i = 0
# plt.cla()
# for app_num in range(1,6):
#     app_name = "App_0" + str(app_num)
#     legend_list.append(app_name)
#     # Note ! add comma! if not, return a list with one object, else return the required object.
#     plt_ptr, = plt.plot([int(x) for x in average_delay_time[app_name]], line_type[i])
#     plt_ptrs.append(plt_ptr)
#     i += 1

# plt.title("Average ETE Delay vs. Memory Type")
# plt.xlabel("Memory Type", fontsize=12)
# plt.ylabel("ETE Delay", fontsize=12)
# plt.legend(plt_ptrs, legend_list)
# ax = plt.gca()
# iters = ['10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
# ax.set_xticks([i*10 for i in range(1,11)])
# ax.set_xticklabels(iters)
# plt.tight_layout()      # avoid incomplete display
# plt.savefig(fig_path + 'Average_ETE_Delay_vs_Current_Iters.jpg')
