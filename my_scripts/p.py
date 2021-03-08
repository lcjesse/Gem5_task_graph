### Custom Plot Function ###
import matplotlib.pyplot as plt
from matplotlib.pyplot import legend, plot, xticks
import numpy as np

class PlotFunction():
    """Make Data visualization Easier !"""
    def __init__(self, y_data, x_label, y_label, x_ticklabels=[], x_ticks=[], title=''):
        self.y_data=y_data
        self.x_label=x_label
        self.y_label=y_label
        self.x_ticklabels=x_ticklabels
        self.x_ticks=x_ticks
        if title == '':
            self.title=self.y_label+" vs. "+self.x_label
        else:
            self.title=self.y_label+" vs. "+self.x_label+title

    def plot_figs(self):
        plt.clf()
        legend_list = []
        line_type=['', '', '-x', '-*', '-^', '-o', '-s', '-<', '-v', '-D']
        plt_ptrs = []
        i = 0
        default_xticks_len = 0
        for key, value in self.y_data.items():
            legend_list.append(key)
            assert(i < len(line_type)) # aviod over the range of line_type
            plt_ptr, = plt.plot([int(x) for x in value], line_type[i], markersize=4)
            plt_ptrs.append(plt_ptr)
            i += 1

            if default_xticks_len == 0:
                default_xticks_len = len(value)

        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.legend(plt_ptrs, legend_list)
        ax = plt.gca()

        if self.x_ticklabels != []:
            ax.set_xticklabels(self.x_ticklabels)
        else:
            ax.set_xticklabels([str(x) for x in range(default_xticks_len)])

        if self.x_ticks != []:
            ax.set_xticks(self.x_ticks)
        else:
            ax.set_xticks([x for x in range(default_xticks_len)])

        plt.tight_layout()

    def save_figs(self, dir, filename=''):
        self.plot_figs()
        name=''
        if filename != '':
            name = filename + '.png'
        else:
            name =  self.title + '.png'

        plt.savefig(dir + name, dpi=600)

    def plot_pie(self, dir='./', title='', legend_list=[], if_save=True):
        plt.clf()

        if legend_list == []:
            legend_list = ['HQM', 'Core-0', 'PE-1 PE-2', 'DDR-0', 'PE-3 PE-4 PE-5', 'PE-13', 'Core-1', \
                'Core-2', 'PE-6 PE-7 PE-8', 'DDR-1', 'PE-9 PE-10 PE-11 PE-12', 'Core-3']

        explode = [0.01] * len(self.y_data)
        plt.pie(self.y_data, explode=explode, labels=legend_list)
        plt.title(title)
        plt.tight_layout()
        if if_save:
            plt.savefig(dir+title+'.jpg')

############################################################################################################
##################################### Top Parameters Settings  #############################################
if_throughput = False
if_plot_all = True
if_compare = False
if_plot_network_performance = False
if_plot_other_metrics = False
iterations = 1000
############################################################################################################

############################################################################################################
########################## Plot throughput for all applications (1-5)  ######################################
############################################################################################################

if if_throughput:
    dir_path = "/home/wj/Gem5_task_graph/my_STATS/02_24_11_59/"
    print("Work Directory is Now at :", dir_path)
    print("Plot throughput")
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"

    # Parameter Setting
    app=[1, 2, 3, 4]
    # app=[1]
    applicaton=[str(i) for i in app]
    iters=[20]
    mem_access=[20]
    mem_type = ['DDR3']

    throughput = {}
    time_ = {}
    c_t_ = {}
    for app in applicaton:
        app_name = "Application_0" + app
        time=[]
        completed=[]
        c_t = {}
        dir_name = app_name +"_Ring"
        log_path = dir_path + dir_name + "/data"
        with open(log_path) as log_file:
            log_data = log_file.readlines()

        for i in range(len(log_data)):
            line=log_data[i]
            time.append(float(line.strip().split()[0]))
            completed.append(float(line.strip().split()[1]))
            c_t[float(line.strip().split()[1])] = float(line.strip().split()[0])

        app_throughput=[]
        for i in range(len(log_data)):
            app_throughput.append(completed[i]*1e9/time[i])

        time_[app_name] = time
        throughput[app_name] = app_throughput
        c_t_[app_name] = c_t

    for app in applicaton:
        data = {}
        app_name = "Application_0" + app
        data[app_name] = throughput[app_name]
        # 20 get one point
        x = int(len(time_[app_name]) / 40)

        x_ticks=[i*40 for i in range(x)]
        x_ticklabels=[str(time_[app_name][i]) for i in x_ticks]
        p = PlotFunction(data, "Simulation Time (cycle)", "Throughput(pps)", x_ticklabels, x_ticks, ' for_App_0'+str(app))
        p.save_figs(fig_path, p.title)


############################################################################################################
########################## Plot ete delay for all applications (1-5)  ######################################
############################################################################################################

if if_plot_all:

    dir_path = "/home/wj/Gem5_task_graph/my_STATS/02_25_02_05/"
    print("Work Directory is Now at :", dir_path)
    print("Plot ete delay")
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"

    # Parameter Setting
    app=[1, 2, 3, 4]
    # app=[1]
    applicaton=[str(i) for i in app]
    iters=[20]
    mem_access=[20]
    mem_type = ['DDR3']

    ete_delay = {}
    for app in applicaton:
        app_name = "Application_0" + app
        each_iter_data = []
        dir_name = app_name +"_Ring"
        log_path = dir_path + dir_name + "/application_delay_running_info.log"
        with open(log_path) as log_file:
            log_data = log_file.readlines()

        for i in range(1, iterations+1):
            delay = log_data[i].strip().split()[-1]
            each_iter_data.append(delay)

        ete_delay[app_name] = each_iter_data

    x_ticks=[i*100 for i in range(1,(int(iterations/100)+1))]
    x_ticklabels=[str(i) for i in x_ticks]

    for app in applicaton:
        data = {}
        app_name = "Application_0" + app
        data[app_name] = ete_delay[app_name]
        p = PlotFunction(data, "Execution Iterations", "ETE Delay", x_ticklabels, x_ticks, ' for_App_0'+str(app))
        p.save_figs(fig_path, p.title)


############################################################################################################
#################### Compare ete delay with other version for same application #############################
############################################################################################################

if if_compare:

    a=[1, 2, 3, 4, 5]
    # a=[1]
    applicaton=[str(i) for i in a]
    iters=[20]
    mem_access=[20]
    mem_type = ['DDR3']

    dir_path = "/home/wj/gem5_multiapp/Gem5_task_graph/my_STATS/01_28_05_57_pe_7_1_cyc_1000_outmem_10/"
    print("Compare ete delay with other version")
    print("Work Directory is Now at :", dir_path)

    old_ete_delay = {}
    for app in applicaton:
        app_name = "Application_0" + app
        each_iter_data = []
        dir_name = app_name +"_Ring"
        log_path = dir_path + dir_name + "/application_delay_running_info.log"
        with open(log_path) as log_file:
            log_data = log_file.readlines()

        for i in range(1, iterations+1):
            delay = log_data[i].strip().split()[-1]
            each_iter_data.append(delay)

        old_ete_delay[app_name] = each_iter_data

    dir_path = "/home/wj/gem5_multiapp/Gem5_task_graph/my_STATS/01_28_07_09_pe_7_1_cyc_1000_outmem_10/"
    print("Work Directory is Now at :", dir_path)
    result_path = dir_path+"results.txt"
    ## plot in the new
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"

    new_ete_delay = {}
    for app in applicaton:
        app_name = "Application_0" + app
        each_iter_data = []
        dir_name = app_name +"_Ring"
        log_path = dir_path + dir_name + "/application_delay_running_info.log"
        with open(log_path) as log_file:
            log_data = log_file.readlines()

        for i in range(1, iterations+1):
            delay = log_data[i].strip().split()[-1]
            each_iter_data.append(delay)

        new_ete_delay[app_name] = each_iter_data

    x_ticks=[i*100 for i in range(1,(int(iterations/100)+1))]
    x_ticklabels=[str(i) for i in x_ticks]


    for app in applicaton:
        data = {}
        app_name = "Application_0" + app
        data["old"] = old_ete_delay[app_name]
        data["new"] = new_ete_delay[app_name]
        p = PlotFunction(data, "Execution Iterations", "ETE Delay", x_ticklabels, x_ticks, ' for_App_0'+str(app)+'_compare')
        p.save_figs(fig_path, p.title)


############################################################################################################
########################## Plot network performance metrics for all applications (1-5)  ####################
############################################################################################################
if if_plot_network_performance:

    dir_path = "/home/wj/gem5_multiapp/Gem5_task_graph/my_STATS/01_04_01/"
    print("Work Directory is Now at :", dir_path)
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"
    log_path = dir_path + "log"

    ## Parameter Setting
    app=[1, 2, 3, 4, 5]
    mem_access=[20]
    mem_type = ['DDR3']
    para = ["Flits_received", "Average_hops", "Average_flit_latency", \
        "Average_network_flit_latency", "Average_flit_queueing_latency"]

    with open(result_path) as results_file:
        result_data = results_file.readlines()

    result = {}
    for line in range(1, 6):
        info = result_data[line].strip().split()
        result[info[0]] = info[1:]

    for idx, param in enumerate(para):
        y_data = []
        app_name_ = []
        for app in range(1,6):
            app_name = "Application_0" + str(app)
            dir_name = "Application_0"+str(app)+"_Ring"
            y_data.append(float(result[dir_name][idx]))
            app_name_.append(app_name)

        plt.clf()
        plt.bar(range(len(y_data)), y_data, width=0.5, align="center", tick_label=app_name_, alpha=0.5)

        xlabel = "Different Application"
        plt.xlabel(xlabel)
        plt.ylabel(param)
        plt.tight_layout()
        title = xlabel + " vs. " + param
        plt.title(title)
        plt.tight_layout()
        plt.savefig(fig_path+title+".jpg")


############################################################################################################
########################## Plot other performance metrics for all applications (1-5)  ######################
############################################################################################################
if if_plot_other_metrics:

    dir_path = "/home/wj/gem5_multiapp/Gem5_task_graph/my_STATS/11_11/multi_app/"
    print("Work Directory is Now at :", dir_path)
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"

    ## Parameter Setting
    app=[1, 2, 3, 4, 5, 7]
    iters=[20]
    mem_access=[20]
    mem_type = ['DDR3']

    task_waiting = {}
    for app in app:
        app_name = "Application_0" + str(app)
        kk = "Total_Task_Waiting_Time"
        each_iter_data = []
        for iter in iters:
            for mc in mem_access:
                for mt in mem_type:
                    key_word = 'Application_0' + str(app) + '_Iters_' + str(iter) + '_Memory_Access_' +\
                        str(mc) + '_Memory_Type_' + str(mt)
                    log_path = dir_path + key_word + "/task_waiting_time_info.log"
                    with open(log_path) as log_file:
                        log_data = log_file.readlines()

                    start_idx = -1
                    for i in range(len(log_data)):
                        if kk in log_data[i]:
                            start_idx = i + 2
                            break
                    assert(start_idx != -1)

                    for i in range(start_idx, start_idx+20):
                        delay = log_data[i].strip().split()[-1]
                        each_iter_data.append(delay)
                    if app == 7:
                        each_iter_data[12] = 300000
                    else:
                        each_iter_data[12]=10000

        task_waiting[app_name] = each_iter_data

    x_ticklabels=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
    x_ticks=[i for i in range(0,20)]

    for app in range(1, 7):
        data = {}
        if app == 6:
            app=7
        app_name = "Application_0" + str(app)
        data["App"] = task_waiting[app_name]
        p = PlotFunction(data, "Core Id", "task_waiting time", x_ticklabels, x_ticks, ' for_App_0'+str(app))
        p.save_figs(fig_path, p.title)


# dir_path = "/home/wj/test/Gem5_task_graph/my_STATS/10_03/different_memory_type_and_memory_access_20/"
# result_path = dir_path+"results.txt"
# fig_path = dir_path+"FIGS/"
# link_result_path = dir_path+"LINK_RESULT/"
# log_path = dir_path + "log"

# ## Parameter Setting
# app=[1, 2, 3, 4, 5]
# iters=[100]
# mem_access=[20]
# mem_type = ['DDR3']

# ## Read File -> log
# with open(log_path) as log_file:
#     log_data = log_file.readlines()

# old_ete_delay = {}
# for app in app:
#     app_name = "Application_0" + str(app)
#     each_iter_data = []
#     for iter in iters:
#         for mc in mem_access:
#             for mt in mem_type:
#                 key_word = 'Application_0' + str(app) + '_Iters_' + str(iter) + '_Memory_Access_' +\
#                     str(mc) + '_Memory_Type_' + str(mt)
#                 start_idx = -1
#                 for i in range(len(log_data)):
#                     if key_word in log_data[i]:
#                         start_idx = i + 3
#                         break
#                 assert(start_idx != -1)

#                 assert(log_data[start_idx+iter-1].strip().split()[1] == str(iter-1))
#                 for i in range(start_idx, start_idx+iter):
#                     delay = log_data[i].strip().split()[-1]
#                     each_iter_data.append(delay)

#     old_ete_delay[app_name] = each_iter_data
