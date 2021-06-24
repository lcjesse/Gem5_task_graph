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
            self.title=title
            # self.title=self.y_label+" vs. "+self.x_label+title

    def plot_figs(self):
        plt.clf()
        legend_list = []
        line_type=['-1', '-h', '-x', '-*', '-^', '-o', '-s', '-<', '-v', '-D']
        plt_ptrs = []
        i = 0
        default_xticks_len = 0
        for key, value in self.y_data.items():
            legend_list.append(key)
            assert(i < len(line_type)) # aviod over the range of line_type
            plt_ptr, = plt.plot([float(x) for x in value], line_type[i], markersize=4)
            plt_ptrs.append(plt_ptr)
            i += 1

            if default_xticks_len == 0:
                default_xticks_len = len(value)
        
        plt.title(self.title)
        plt.xlabel(self.x_label)
        plt.ylabel(self.y_label)
        plt.legend(plt_ptrs, legend_list)
        ax = plt.gca()
        ax.set_ylim(bottom=0)

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

    def plot_pie(self, dir,  legend_list=[],filename=''):
        plt.clf()

        if legend_list == []:
            legend_list = ['HQM', 'Core-0', 'PE-1 PE-2', 'DDR-0', 'PE-3 PE-4 PE-5', 'PE-13', 'Core-1', \
                'Core-2', 'PE-6 PE-7 PE-8', 'DDR-1', 'PE-9 PE-10 PE-11 PE-12', 'Core-3']

        explode = [0.01] * len(self.y_data)
        plt.pie(self.y_data, explode=explode, labels=legend_list)
        plt.title(self.title)
        plt.tight_layout()
        name=''
        if filename != '':
            name = filename + '.png'
        else:
            name =  self.title + '.png'

        plt.savefig(dir + name, dpi=600)

############################################################################################################
##################################### Top Parameters Settings  #############################################
if_plot_all = True
if_throughput = True
if_compare = False
if_plot_network_performance = False
if_plot_other_metrics = False
if_plot_distribution = False
iterations = 10000
frequency = 1e9
############################################################################################################

############################################################################################################
########################## Plot throughput for all applications (1-4)  ######################################
############################################################################################################
if if_throughput:
    dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_06_24/test_pe/"
    print("Work Directory is Now at :", dir_path)
    print("Plot throughput")
    fig_path = dir_path+"FIGS/"

    # Parameter Setting
    app=[1,2,3,4]
    # app=[1]
    applicaton=[str(i) for i in app]
    iters=[20]
    mem_access=[5]
    mem_type = ['DDR4']
    topology = ['Ring','Mesh']
    evaluation = ['original', 'cost']
    name = ['Ring_original', 'Ring_cost', 'Mesh_cost']
    # name = ['Ring_original', 'Ring_pe']

    interval=100
    all_throughput = {}
    for app in applicaton:
        for access in mem_access:
            for mem in mem_type:
                for TOPO in topology:
                    for EVAL in evaluation:
                        app_name = "Application_0"+app+"_"+TOPO+"_"+EVAL
                        each_throughput_data = []
                        dir_name = "Application_0"+app+"_"+TOPO+"_Memory_Access_"+str(access)+"_Memory_Type_"+mem+"_"+EVAL
                        log_path = dir_path + dir_name + "/application_delay_running_info.log"
                        with open(log_path) as log_file:
                            log_data = log_file.readlines()

                        for i in range(1, len(log_data)):
                            end_time = log_data[i].strip().split()[3]
                            current_tp = float(i)*frequency/float(end_time)/1000000
                            each_throughput_data.append(current_tp)

                        all_throughput[app_name] = each_throughput_data

    x_ticks=[i*1000/interval for i in range(0,(int(10000/1000)+1))]
    x_ticklabels=[str(int(i*interval)) for i in x_ticks]
    # labels = ["Application_02","Application_03","Application_04"]
    labels = ["Application_01","Application_02","Application_03","Application_04"]
    Ring_o_means = []
    Ring_p_means = []
    aRing_p_means = []
    Ring_o_std = []
    Ring_p_std = []
    aRing_p_std = []
    for app in applicaton:
        data = {}
        for NAME in name:
            app_name = "Application_0"+app+"_"+NAME
            data[app_name] = all_throughput[app_name][0:10000:interval]
            vardata = data[app_name][10:]    # get rid of start
            vardata = list(map(float, vardata))
            varofdata = np.var(vardata)     
            stdofdata = np.std(vardata,ddof=1)
            meanofdata = np.mean(vardata)
            if NAME == 'Ring_original':
                Ring_o_means.append(meanofdata)
                Ring_o_std.append(stdofdata)
            elif NAME == 'Ring_cost':
                Ring_p_means.append(meanofdata)
                Ring_p_std.append(stdofdata)
            elif NAME == 'Mesh_cost':
                aRing_p_means.append(meanofdata)
                aRing_p_std.append(stdofdata)
    x = np.arange(len(labels))  # the label locations
    width = 0.2  # the width of the bars
    fig, ax = plt.subplots(figsize=(8, 4.5))
    rects1 = ax.bar(x - width, Ring_o_means, width, yerr=Ring_o_std, label='Ring_original')
    rects2 = ax.bar(x, Ring_p_means, width, yerr=Ring_p_std, label='Ring_cost')
    rects3 = ax.bar(x + width, aRing_p_means, width, yerr=aRing_p_std, label='Mesh_cost')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Throughput(Mpps)')
    ax.set_title('Throughput Before & After Optimization')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    for a,b in zip(x, Ring_o_means): 
        ax.text(a - width, b+0.5, '%0.1f' % b, ha='center', va= 'bottom',fontsize=8) 
    for a,b in zip(x, Ring_p_means): 
        ax.text(a, b+0.5, '%0.1f' % b, ha='center', va= 'bottom',fontsize=8) 
    for a,b in zip(x, aRing_p_means): 
        ax.text(a + width, b+0.5, '%0.1f' % b, ha='center', va= 'bottom',fontsize=8) 

    fig.tight_layout()
    fig.savefig(fig_path+'Throughput vs. Execution Iterations_mapping_cost.png', dpi=200)


############################################################################################################
########################## Plot ete delay for all applications (1-4)  ######################################
############################################################################################################
if if_plot_all:

    dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_06_24/test_pe/"
    print("Work Directory is Now at :", dir_path)
    print("Plot ete delay")
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"

    # Parameter Setting
    app=[1,2,3,4]
    # app=[1]
    applicaton=[str(i) for i in app]
    iters=[20]
    mem_access=[5]
    mem_type = ['DDR4']
    topology = ['Ring','Mesh']
    evaluation = ['original', 'cost']
    name = ['Ring_original', 'Ring_cost', 'Mesh_cost']
    # name = ['Ring_original', 'Ring_pe']

    interval=100
    ete_delay = {}
    for app in applicaton:
        for access in mem_access:
            for mem in mem_type:
                for TOPO in topology:
                    for EVAL in evaluation:
                        # app_name = "Application_0"+app+"_"+TOPO+"_"+EVAL
                        # each_iter_data = []
                        dir_name = "Application_0"+app+"_"+TOPO+"_Memory_Access_"+str(access)+"_Memory_Type_"+mem+"_"+EVAL
                        log_path = dir_path + dir_name + "/application_delay_running_info.log"
                        with open(log_path) as log_file:
                            log_data = log_file.readlines()
                        
                        for i in range(1, len(log_data)):
                            part = log_data[i].strip().split()[0].replace('.stp','')
                            app_name = ''
                            if '6' in part:
                                app_name = "App_0"+app+"_follow_"+TOPO+"_"+EVAL
                            elif '1' in part or '3' in part:
                                app_name = "App_0"+app+"_head_"+TOPO+"_"+EVAL
                            else:
                                app_name = "App_0"+app+"_"+TOPO+"_"+EVAL
                            if app_name not in ete_delay:
                                ete_delay[app_name] = []
                            delay = log_data[i].strip().split()[4]
                            ete_delay[app_name].append(delay)
                                    
                        # ete_delay[app_name] = each_iter_data

    x_ticks=[i*1000/interval for i in range(1,(int(10000/1000)+1))]
    x_ticklabels=[str(int(i*interval)) for i in x_ticks]
    # labels = ["App_01_head","App_01_follow","App_02","App_03_head","App_03_follow","App_04"]
    labels = ["App_01_head","App_01_follow","App_02","App_03_head","App_03_follow","App_04"]
    Ring_o_means = []
    Ring_p_means = []
    aRing_p_means = []
    Ring_o_std = []
    Ring_p_std = []
    aRing_p_std = []
    plt.clf()
    for app in labels:
        data = {}
        for NAME in name:
            app_name = app+"_"+NAME
            data[app_name] = ete_delay[app_name][0:10000:interval]
            vardata = data[app_name][10:]    # get rid of start
            vardata = list(map(int, vardata))
            varofdata = np.var(vardata)     
            stdofdata = np.std(vardata,ddof=1)
            meanofdata = np.mean(vardata)
            print(f"mean of {app_name}: {meanofdata:.2f};    var: {varofdata:.2f};    std: {stdofdata:.2f}")
            if NAME == 'Ring_original':
                Ring_o_means.append(meanofdata)
                Ring_o_std.append(stdofdata)
            elif NAME == 'Ring_cost':
                Ring_p_means.append(meanofdata)
                Ring_p_std.append(stdofdata)
            elif NAME == 'Mesh_cost':
                aRing_p_means.append(meanofdata)
                aRing_p_std.append(stdofdata)

        # p = PlotFunction(data, "Execution Iterations(times)", "ETE Delay(cycles)", x_ticklabels, x_ticks, 'ETE Delay vs. Execution Iterations for App_0'+str(app))
        # p.save_figs(fig_path, p.title)
    x = np.arange(len(labels))  # the label locations
    width = 0.2  # the width of the bars
    fig, ax = plt.subplots(figsize=(8, 4.5))
    rects1 = ax.bar(x - width, Ring_o_means, width, yerr=Ring_o_std, label='Ring_original')
    rects2 = ax.bar(x, Ring_p_means, width, yerr=Ring_p_std, label='Ring_cost')
    rects3 = ax.bar(x + width, aRing_p_means, width, yerr=aRing_p_std, label='Mesh_cost')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('ETE Delay(cycles)')
    ax.set_title('ETE Delay Before & After Optimization')
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()
    for a,b in zip(x, Ring_o_means): 
        ax.text(a - width, b, '%d' % b, ha='center', va= 'bottom',fontsize=8) 
    for a,b in zip(x, Ring_p_means): 
        ax.text(a, b, '%d' % b, ha='center', va= 'bottom',fontsize=8) 
    for a,b in zip(x, aRing_p_means): 
        ax.text(a + width, b, '%d' % b, ha='center', va= 'bottom',fontsize=8) 

    fig.tight_layout()
    fig.savefig(fig_path+'ETE Delay vs. Execution Iterations_mapping_cost.png', dpi=200)


    # plt.clf()
    # labels = ["App_01_head","App_01_follow","App_02","App_03_head","App_03_follow","App_04"]
    # Ring_o_means = [867341, 257049, 482864, 1103833, 328405, 2122344]
    # Ring_p_means = [42410, 15149, 743815, 83445, 24626, 800008]
    # Ring_p_means = [126624, 21063, 42041, 174385, 38980, 165999]

    # x = np.arange(len(labels))  # the label locations
    # width = 0.2  # the width of the bars
    # fig, ax = plt.subplots(figsize=(8, 4.5))
    # rects1 = ax.bar(x - width, Ring_o_means, width, label='Ring_original')
    # rects2 = ax.bar(x, Ring_p_means, width, label='Ring_cost')
    # rects3 = ax.bar(x + width, Ring_p_means, width, label='Ring_pe')

    # # Add some text for labels, title and custom x-axis tick labels, etc.
    # ax.set_ylabel('ETE Delay Jitter(cycle^2)')
    # ax.set_title('ETE Delay Jitter Before & After Optimization')
    # ax.set_xticks(x)
    # ax.set_xticklabels(labels)
    # ax.legend()
    # # for a,b in zip(x, Ring_o_means): 
    # #     ax.text(a - width, b, '%d' % b, ha='center', va= 'bottom',fontsize=8) 
    # # for a,b in zip(x, Ring_p_means): 
    # #     ax.text(a, b, '%d' % b, ha='center', va= 'bottom',fontsize=8) 
    # # for a,b in zip(x, Ring_p_means): 
    # #     ax.text(a + width, b, '%d' % b, ha='center', va= 'bottom',fontsize=8) 

    # fig.tight_layout()
    # fig.savefig(fig_path+'ETE Delay Jitter vs. Execution Iterations_mapping.png', dpi=200)

############################################################################################################
########################## Plot network performance metrics for all applications (1-5)  ####################
############################################################################################################
if if_plot_network_performance:

    dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_06_24/test_pe_unified/"
    print("Work Directory is Now at :", dir_path)
    print("Plot network performance")
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"
    log_path = dir_path + "log"

    # Parameter Setting
    app=[2, 4]
    # app=[1]
    applicaton=[str(i) for i in app]
    mem_access=[5]
    mem_type = ['DDR4']
    topology = ['Ring','Mesh']
    evaluation = ['original', 'cost']
    name = ['Ring_original', 'Ring_cost', 'Mesh_cost']
    # name = ['Ring_original', 'Ring_pe']
    para = ["Average_flit_latency(cycles)", "Average_network_flit_latency(cycles)", "Average_flit_queueing_latency(cycles)", "Flits_received", "Average_hops"]
    para1 = ["Average_flit_latency", "Average_network_flit_latency", "Average_flit_queueing_latency", "Flits_received", "Average_hops"]
    # with open(result_path) as results_file:
    #     result_data = results_file.readlines()
    interval=100
    performance = []
    for idx, param in enumerate(para):
        temp_performance = {}
        for app in applicaton:
            for access in mem_access:
                for mem in mem_type:
                    for TOPO in topology:
                        for EVAL in evaluation:
                            app_name = "Application_0"+app+"_"+TOPO+"_"+EVAL
                            each_iter_data = []
                            dir_name = "Application_0"+app+"_"+TOPO+"_Memory_Access_"+str(access)+"_Memory_Type_"+mem+"_"+EVAL
                            log_path = dir_path + dir_name + "/network_performance.log"
                            with open(log_path) as log_file:
                                log_data = log_file.readlines()
                            
                            for i in range(1, len(log_data)):
                                delay = log_data[i].strip().split()[idx+2]
                                each_iter_data.append(delay)
                                        
                            temp_performance[app_name] = each_iter_data
        performance.append(temp_performance)

    x_ticks=[i*1000/interval for i in range(0,(int(10000/1000)+1))]
    x_ticklabels=[str(int(i*interval)) for i in x_ticks]
    # para1 = ["Average_flit_latency", "Average_network_flit_latency", "Average_flit_queueing_latency", "Flits_received", "Average_hops"]
    for idx, param in enumerate(para):
        for app in applicaton:
            data = {}
            for NAME in name:
                app_name = "Application_0"+app+"_"+NAME
                data[app_name] = performance[idx][app_name][0:10000:interval]
            p = PlotFunction(data, "Execution Iterations(times)", param, x_ticklabels, x_ticks, para1[idx]+' vs. Execution Iterations for App_0'+str(app))
            p.save_figs(fig_path, p.title)


############################################################################################################
########################## Plot network flow distribution for all applications (1-5)  ####################
############################################################################################################
if if_plot_distribution:

    dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_06_24/test_pe_unified/"
    print("Work Directory is Now at :", dir_path)
    print("Plot flow distribution")
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"
    log_path = dir_path + "log"

    # Parameter Setting
    app=[2, 4]
    # app=[1]
    applicaton=[str(i) for i in app]
    mem_access=[5]
    mem_type = ['DDR4']
    # with open(result_path) as results_file:
    #     result_data = results_file.readlines()

    link = {}
    for app in applicaton:
        for access in mem_access:
            for mem in mem_type:
                app_name = "Application_0"+app+"_Memory_Access_"+str(access)
                buffer_read = []
                dir_name = "LINK_RESULT"
                log_path = dir_path + dir_name + "/Link_Record_Application_0"+app+"_Memory_Access_"+str(access)+"_Memory_Type_"+mem+".txt"
                with open(log_path) as log_file:
                    log_data = log_file.readlines()
                
                for i in range(1, 13):
                    data = log_data[i].strip().split()[1]
                    buffer_read.append(int(data))
                            
                link[app_name] = buffer_read
                print(buffer_read)

    x_ticks=[i*1000 for i in range(1,(int(10000/1000)+1))]
    x_ticklabels=[str(int(i)) for i in x_ticks]
    for app in applicaton:
        # data = {}
        app_name = "Application_0"+app+"_Memory_Access_5"
        # data[app_name] = link[app_name]
        # for access in mem_access:
        #     app_name = "Application_0"+app+"_Memory_Access_"+str(access)
        #     data[app_name] = link[app_name]
        p = PlotFunction(link[app_name], "Execution Iterations(times)", "ETE Delay(cycles)", x_ticklabels, x_ticks, 'Link Utilization for App_0'+str(app))
        p.plot_pie(fig_path,[],p.title)





# ############################################################################################################
# ########################## Plot network performance metrics for all applications (1-5)  ####################
# ############################################################################################################
# if if_plot_network_performance:

#     dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_06_24/test_pe_unified/"
#     print("Work Directory is Now at :", dir_path)
#     result_path = dir_path+"results.txt"
#     fig_path = dir_path+"FIGS/"
#     link_result_path = dir_path+"LINK_RESULT/"
#     log_path = dir_path + "log"

#     ## Parameter Setting
#     app=[2, 4, 5]
#     mem_access=[5]
#     mem_type = ['DDR3']
#     para = ["Flits_received", "Average_hops", "Average_flit_latency", \
#         "Average_network_flit_latency", "Average_flit_queueing_latency"]

#     with open(result_path) as results_file:
#         result_data = results_file.readlines()

#     result = {}
#     for line in range(1, 6):
#         info = result_data[line].strip().split()
#         result[info[0]] = info[1:]

#     for idx, param in enumerate(para):
#         y_data = []
#         app_name_ = []
#         for app in range(1,6):
#             app_name = "Application_0" + str(app)
#             dir_name = "Application_0"+str(app)+"_Ring"
#             y_data.append(float(result[dir_name][idx]))
#             app_name_.append(app_name)
            
#         plt.clf()
#         plt.bar(range(len(y_data)), y_data, width=0.5, align="center", tick_label=app_name_, alpha=0.5)

#         xlabel = "Different Application"
#         plt.xlabel(xlabel)
#         plt.ylabel(param)
#         plt.tight_layout()
#         title = xlabel + " vs. " + param
#         plt.title(title)
#         plt.tight_layout()
#         plt.savefig(fig_path+title+".jpg")

# ############################################################################################################
# #################### Compare ete delay with other version for same application #############################
# ############################################################################################################

# if if_compare:

#     a=[2, 4, 5]
#     # a=[1]
#     applicaton=[str(i) for i in a]
#     iters=[20]
#     mem_access=[5]
#     mem_type = ['DDR3']

#     dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/01_28_05_57_pe_7_1_cyc_1000_outmem_10/"
#     print("Compare ete delay with other version")
#     print("Work Directory is Now at :", dir_path)

#     old_ete_delay = {}
#     for app in applicaton:
#         app_name = "Application_0" + app
#         each_iter_data = []
#         dir_name = app_name +"_Ring"
#         log_path = dir_path + dir_name + "/application_delay_running_info.log"
#         with open(log_path) as log_file:
#             log_data = log_file.readlines()
        
#         for i in range(1, len(log_data)):
#             delay = log_data[i].strip().split()[-1]
#             each_iter_data.append(delay)
                    
#         old_ete_delay[app_name] = each_iter_data

#     dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/01_28_07_09_pe_7_1_cyc_1000_outmem_10/"
#     print("Work Directory is Now at :", dir_path)
#     result_path = dir_path+"results.txt"
#     ## plot in the new 
#     fig_path = dir_path+"FIGS/"
#     link_result_path = dir_path+"LINK_RESULT/"

#     new_ete_delay = {}
#     for app in applicaton:
#         app_name = "Application_0" + app
#         each_iter_data = []
#         dir_name = app_name +"_Ring"
#         log_path = dir_path + dir_name + "/application_delay_running_info.log"
#         with open(log_path) as log_file:
#             log_data = log_file.readlines()
        
#         for i in range(1, len(log_data)):
#             delay = log_data[i].strip().split()[-1]
#             each_iter_data.append(delay)
                    
#         new_ete_delay[app_name] = each_iter_data

#     x_ticks=[i*100 for i in range(1,(int(iterations/100)+1))]
#     x_ticklabels=[str(i) for i in x_ticks]


#     for app in applicaton:
#         data = {}
#         app_name = "Application_0" + app
#         data["old"] = old_ete_delay[app_name]
#         data["new"] = new_ete_delay[app_name]
#         p = PlotFunction(data, "Execution Iterations", "ETE Delay", x_ticklabels, x_ticks, ' for_App_0'+str(app)+'_compare')
#         p.save_figs(fig_path, p.title)


# ############################################################################################################
# ########################## Plot other performance metrics for all applications (1-5)  ######################
# ############################################################################################################
# if if_plot_other_metrics:

#     dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/11_11/multi_app/"
#     print("Work Directory is Now at :", dir_path)
#     result_path = dir_path+"results.txt"
#     fig_path = dir_path+"FIGS/"
#     link_result_path = dir_path+"LINK_RESULT/"

#     ## Parameter Setting
#     app=[2, 4, 5, 7]
#     iters=[20]
#     mem_access=[5]
#     mem_type = ['DDR3']

#     task_waiting = {}
#     for app in app:
#         app_name = "Application_0" + str(app)
#         kk = "Total_Task_Waiting_Time"
#         each_iter_data = []
#         for iter in iters:
#             for mc in mem_access:
#                 for mt in mem_type:
#                     key_word = 'Application_0' + str(app) + '_Iters_' + str(iter) + '_Memory_Access_' +\
#                         str(mc) + '_Memory_Type_' + str(mt)
#                     log_path = dir_path + key_word + "/task_waiting_time_info.log"
#                     with open(log_path) as log_file:
#                         log_data = log_file.readlines()
                    
#                     start_idx = -1
#                     for i in range(len(log_data)):
#                         if kk in log_data[i]:
#                             start_idx = i + 2
#                             break
#                     assert(start_idx != -1)

#                     for i in range(start_idx, start_idx+20):
#                         delay = log_data[i].strip().split()[-1]
#                         each_iter_data.append(delay)
#                     if app == 7:
#                         each_iter_data[12] = 300000
#                     else:
#                         each_iter_data[12]=10000
                    
#         task_waiting[app_name] = each_iter_data

#     x_ticklabels=['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19']
#     x_ticks=[i for i in range(0,20)]

#     for app in range(1, 7):
#         data = {}
#         if app == 6:
#             app=7
#         app_name = "Application_0" + str(app)
#         data["App"] = task_waiting[app_name]
#         p = PlotFunction(data, "Core Id", "task_waiting time", x_ticklabels, x_ticks, ' for_App_0'+str(app))
#         p.save_figs(fig_path, p.title)


# dir_path = "/home/wj/test/Gem5_task_graph/my_STATS/10_03/different_memory_type_and_memory_access_20/"
# result_path = dir_path+"results.txt"
# fig_path = dir_path+"FIGS/"
# link_result_path = dir_path+"LINK_RESULT/"
# log_path = dir_path + "log"

# ## Parameter Setting
# app=[2, 4, 5]
# iters=[100]
# mem_access=[5]
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
