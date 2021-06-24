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
    dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_05_20/test_pe/"
    print("Work Directory is Now at :", dir_path)
    print("Plot throughput")
    fig_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_05_20/test_pe/FIGS/"

    # Parameter Setting
    apps=[1, 3]
    # app=[1]
    applicaton=[str(i) for i in apps]
    mem_access=[5]
    mem_type = ['DDR4']
    topology = ['Mesh','Ring']
    evaluation = ['original', 'pe']
    name = ['Ring_original', 'Ring_pe', 'Mesh_pe']
    # name = ['Ring_original', 'Mesh_pe']
    # PART={}
    interval=100
    all_throughput = {}
    for app in applicaton:
        # all_throughput = {}
        for access in mem_access:
            for mem in mem_type:
                for TOPO in topology:
                    # all_throughput[app] = {}
                    for EVAL in evaluation:
                        dir_name = "Application_0"+app+"_"+TOPO+"_Memory_Access_"+str(access)+"_Memory_Type_"+mem+"_"+EVAL
                        # dir_name = "Application_0"+app+"_Memory_Access_"+str(access)+"_Memory_Type_"+mem
                        log_path = dir_path + dir_name + "/application_delay_running_info.log"
                        with open(log_path) as log_file:
                            log_data = log_file.readlines()

                        for i in range(1, len(log_data)):
                            part = log_data[i].strip().split()[0].replace('.stp','')
                            if '6' in part:
                                app_name = "Application_0"+app+"_"+TOPO+"_"+EVAL
                            elif '2' in part or '4' in part:
                                app_name = "Application_0"+app+"_"+TOPO+"_"+EVAL
                            else:
                                app_name = "Application_0"+app+"_"+TOPO+"_"+EVAL
                            # if TYPE not in all_throughput:
                            #     all_throughput={}
                            # app_name = "Application_0"+app+"_"+TYPE+"_Memory_Access_"+str(access)
                            if app_name not in all_throughput:
                                all_throughput[app_name]= []

                            iteration = i
                            # iteration = log_data[i].strip().split()[1]
                            end_time = log_data[i].strip().split()[3]
                            current_tp = float(iteration)*frequency/float(end_time)
                            all_throughput[app_name].append(current_tp)

                # all_throughput[app_name] = each_throughput_data
    # x_ticks ={}
    # x_ticklabels = {}
    # x_ticks[0]=[i*50 for i in range(0,(int(500/50)+1))]
    # x_ticklabels[0]=[str(int(i)) for i in x_ticks[0]]
    x_ticks=[i*1000/interval for i in range(0,(int(10000/1000)+1))]
    x_ticklabels=[str(int(i*interval)) for i in x_ticks]
    # x_ticks=[i*1000/interval for i in range(0,(int(iterations/1000)+1))]
    # x_ticklabels=[str(int(i*interval)) for i in x_ticks]
    newappnames = ["Application_01","Application_02","Application_03","Application_04"]
    # data = {}
    # for app in applicaton:
    for app in apps:
        # for TYPE in all_throughput.keys():
        data = {}
        for NAME in name:
            app_name = "Application_0"+str(app)+'_'+NAME
                # app_name = "Application_0"+app+"_Memory_Access_"+str(access)
            data[app_name] = all_throughput[app_name][0:10000:interval]
            vardata = data[app_name][10:]    # get rid of start
            vardata = list(map(int, vardata))
            varofdata = np.var(vardata)     
            stdofdata = np.std(vardata,ddof=1)
            meanofdata = np.mean(vardata)
            print(f"mean of {app_name}: {meanofdata:.2f};    var: {varofdata:.2f};    std: {stdofdata:.2f}")
        # p = PlotFunction(data, "Execution Iterations(times)", "Throughput(pps)", x_ticklabels, x_ticks, 'Throughput vs. Execution Iterations for App_0'+str(app))
        # p.save_figs(fig_path, p.title)




############################################################################################################
########################## Plot ete delay for all applications (1-4)  ######################################
############################################################################################################
if if_plot_all:

    dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_05_20/test_pe/"
    print("Work Directory is Now at :", dir_path)
    print("Plot ete delay")
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"

    # Parameter Setting
    app=[1, 3]
    # app=[1]
    applicaton=[str(i) for i in app]
    iters=[20]
    mem_access=[5]
    mem_type = ['DDR4']
    topology = ['Mesh','Ring']
    evaluation = ['original', 'pe']
    name = ['Ring_original', 'Ring_pe', 'Mesh_pe']
    types = ['head', 'follow']

    interval=100
    ete_delay = {}
    for app in applicaton:
        ete_delay[app] = {}
        for access in mem_access:
            for mem in mem_type:
                for TOPO in topology:
                    # ete_delay[app] = {}
                    for EVAL in evaluation:
                # app_name = "Application_0"+app+"_Memory_Access_"+str(access)
                        dir_name = "Application_0"+app+"_"+TOPO+"_Memory_Access_"+str(access)+"_Memory_Type_"+mem+"_"+EVAL
                        log_path = dir_path + dir_name + "/application_delay_running_info.log"
                        with open(log_path) as log_file:
                            log_data = log_file.readlines()
                        
                        for i in range(1, len(log_data)):
                            part = log_data[i].strip().split()[0].replace('.stp','')
                            if '6' in part:
                                TYPE='follow'
                            else:
                                TYPE='head'
                            if TYPE not in ete_delay[app]:
                                ete_delay[app][TYPE]={}
                            app_name = "Application_0"+app+"_"+TOPO+"_"+EVAL
                            if app_name not in ete_delay[app][TYPE]:
                                ete_delay[app][TYPE][app_name]= []

                            iteration = log_data[i].strip().split()[1]


                            delay = log_data[i].strip().split()[4]
                            ete_delay[app][TYPE][app_name].append(delay)

    interval = {}
    interval[0] = 100
    interval[1] = 100
    x_ticks ={}
    x_ticklabels = {}
    x_ticks[0]=[i*1000/interval[0] for i in range(0,(int(10000/1000)+1))]
    x_ticklabels[0]=[str(int(i*interval[0])) for i in x_ticks[0]]
    x_ticks[1]=[i*1000/interval[1] for i in range(0,(int(10000/1000)+1))]
    x_ticklabels[1]=[str(int(i*interval[1])) for i in x_ticks[1]]
    for app in applicaton:
        for TYPE in types:
            data = {}
            if 'head' in TYPE:
                i=0
            else:
                i=1
            for NAME in name:
                app_name = "Application_0"+app+"_"+NAME
                data[app_name] = ete_delay[app][TYPE][app_name]
                if 'head' in TYPE:
                    data[app_name] = ete_delay[app][TYPE][app_name][0:10000:interval[0]]
                else:
                    data[app_name] = ete_delay[app][TYPE][app_name][0:10000:interval[1]]
                vardata = data[app_name][1:]
                vardata = list(map(int, vardata))
                varofdata = np.var(vardata)
                stdofdata = np.std(vardata,ddof=1)
                meanofdata = np.mean(vardata)
                print(f"mean of {app_name}: {meanofdata:.2f};    var: {varofdata:.2f};    std: {stdofdata:.2f}")
            # p = PlotFunction(data, "Execution Iterations(times)", "ETE Delay(cycles)", x_ticklabels[i], x_ticks[i], 'ETE Delay vs. Execution Iterations for App_0'+str(app)+'_'+TYPE)
            # p.save_figs(fig_path, p.title)



        # for TOPO in topology:
        #     for TYPE in all_throughput[app].keys():
        #         data = {}
        #         for EVAL in evaluation:
        #             app_name = "Application_0"+app+"_"+TOPO+"_"+EVAL
        #             # app_name = "Application_0"+app+"_Memory_Access_"+str(access)
        #             data[app_name] = ete_delay[app][TYPE][app_name]
                    
        #         if 'head' in TYPE:
        #             i=0
        #             appendix='head'
        #         else:
        #             i=1
        #             appendix='follow'
        #         p = PlotFunction(data, "Execution Iterations(times)", "ETE Delay(cycles)", x_ticklabels[i], x_ticks[i], 'ETE Delay vs. Execution Iterations for App_0'+str(app)+'_'+appendix+' in '+TOPO)
        #         p.save_figs(fig_path, p.title)

        # for access in mem_access:
        #     app_name = "Application_0"+app+"_Memory_Access_"+str(access)
        #     data[app_name] = ete_delay[app_name]
        # p = PlotFunction(data, "Execution Iterations(times)", "ETE Delay(cycles)", x_ticklabels, x_ticks, 'ETE Delay vs. Execution Iterations for App_0'+str(app)+'_'+TYPE)
        # p.save_figs(fig_path, p.title)


############################################################################################################
########################## Plot network performance metrics for all applications (1-5)  ####################
############################################################################################################
if if_plot_network_performance:

    dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_05_20/test_pe/"
    print("Work Directory is Now at :", dir_path)
    print("Plot network performance")
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"
    log_path = dir_path + "log"

    # Parameter Setting
    app=[1, 3]
    # app=[1]
    applicaton=[str(i) for i in app]
    mem_access=[5]
    mem_type = ['DDR4']
    topology = ['Mesh','Ring']
    evaluation = ['original', 'pe']
    name = ['Ring_original', 'Ring_pe', 'Mesh_pe']
    # name = ['Ring_original', 'Mesh_pe']
    # types = ['head', 'follow']
    interval=100

    para = ["Average_flit_latency(cycles)", "Average_network_flit_latency(cycles)", "Average_flit_queueing_latency(cycles)", "Flits_received", "Average_hops"]
    para1 = ["Average_flit_latency", "Average_network_flit_latency", "Average_flit_queueing_latency", "Flits_received", "Average_hops"]
    performance = []
    for idx, param in enumerate(para):
        temp_performance = {}
        for app in applicaton:
            temp_performance[app] = {}
            for access in mem_access:
                for mem in mem_type:
                    for TOPO in topology:
                        # temp_performance[app] = {}
                        for EVAL in evaluation:
                            dir_name = "Application_0"+app+"_"+TOPO+"_Memory_Access_"+str(access)+"_Memory_Type_"+mem+"_"+EVAL
                            log_path = dir_path + dir_name + "/network_performance.log"
                            app_name = "Application_0"+app+"_"+TOPO+"_"+EVAL
                            temp_performance[app][app_name]= []
                            with open(log_path) as log_file:
                                log_data = log_file.readlines()
                            
                            for i in range(1, len(log_data)):
                                iteration = log_data[i].strip().split()[1]
                                delay = log_data[i].strip().split()[idx+2]
                                temp_performance[app][app_name].append(delay)
                                
        performance.append(temp_performance)

    x_ticks=[i*1000/interval for i in range(0,(int(10000/1000)+1))]
    x_ticklabels=[str(int(i*interval)) for i in x_ticks]
    for idx, param in enumerate(para):
        for app in applicaton:
            data = {}
            for NAME in name:
                app_name = "Application_0"+app+"_"+NAME
                data[app_name] = performance[idx][app][app_name][0:10000:interval]
            p = PlotFunction(data, "Execution Iterations(times)", param, x_ticklabels, x_ticks, para1[idx]+' vs. Execution Iterations for App_0'+app)
            p.save_figs(fig_path, p.title)




############################################################################################################
########################## Plot network flow distribution for all applications (1-5)  ####################
############################################################################################################
if if_plot_distribution:

    dir_path = "/home/lichang/Gem5_task_graph/Gem5_task_graph/my_STATS/2021_05_20/test_pe/"
    print("Work Directory is Now at :", dir_path)
    print("Plot flow distribution")
    result_path = dir_path+"results.txt"
    fig_path = dir_path+"FIGS/"
    link_result_path = dir_path+"LINK_RESULT/"
    log_path = dir_path + "log"

    # Parameter Setting
    app=[1, 3]
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
