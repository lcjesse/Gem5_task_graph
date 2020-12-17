### Custom Plot Function ###
import matplotlib.pyplot as plt
from matplotlib.pyplot import legend, plot, xlabel, xticks
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
        line_type=['-x', '-*', '-^', '-o', '-s', '-<', '-v', '-D', '-1', '-2']
        plt_ptrs = []
        i = 0
        default_xticks_len = 0
        for key, value in self.y_data.items():
            legend_list.append(key)
            assert(i < len(line_type)) # aviod over the range of line_type
            plt_ptr, = plt.plot([int(x) for x in value], line_type[i])
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
            name = filename + '.jpg'
        else:
            name =  self.title + '.jpg'

        plt.savefig(dir + name)

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

dir_path = "/home/wj/gem5_multiapp/Gem5_task_graph/my_STATS/11_25/multi_app/"
result_path = dir_path+"results.txt"
fig_path = dir_path+"FIGS/"
link_result_path = dir_path+"LINK_RESULT/"
log_path = dir_path + "log"

## Parameter Setting
app=[1, 2, 3, 4, 5]
mem_access=[20]
mem_type = ['DDR3']
vc_num=[2]
vc_ddr=[0]
para = ["Flits_received", "Average_hops", "Average_flit_latency", \
    "Average_network_flit_latency", "Average_flit_queueing_latency"]

## Network Information
with open(result_path) as results_file:
    result_data = results_file.readlines()

result = {}
for line in range(1, len(result_data)):
    info = result_data[line].strip().split()
    result[info[0]] = info[1:]

for app in app:
    app_name = "Application_0" + str(app)
    for idx, param in enumerate(para):
        y_data = []
        for vd in vc_ddr:
            ddr = []
            for vn in vc_num:
                if vn > vd:
                    dir_name = "Application_0"+str(app)+"_Ring_VC_NUM_"+str(vn)+"_VC_DDR_"+str(vd)
                    if len(result[dir_name]) == len(para):
                        ddr.append(float(result[dir_name][idx]))
                    else:
                        ddr.append(0)
                else:
                    ddr.append(0)
            y_data.append(ddr)
        
        bar_width = 0.2
        tick_label = ["vc_num_2", "vc_num_4", "vc_num_6", "vc_num_8"]

        plt.clf()
        x = np.arange(4)
        for i in range(len(y_data)):
            label = "vc_ddr_" + str(vc_ddr[i])
            plt.bar(x+bar_width*i, y_data[i], bar_width, align="center", label=label, alpha=0.5)

        xlabel = "Different VC_NUM"
        plt.xlabel(xlabel)
        plt.ylabel(param)
        plt.xticks(x+bar_width, tick_label)
        plt.legend()
        plt.tight_layout()
        title = xlabel + " vs. " + param
        plt.title(title)
        plt.tight_layout()
        plt.savefig(fig_path+title+"_"+app_name+".jpg")

## ETE_Delay
x_ticklabels=['10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
x_ticks=[i*10 for i in range(1,11)]


# for ap in app:
for ap in range(1,6):
    app_name = "Application_0" + str(ap)
    data = {}
    for vd in vc_ddr:
        for vn in vc_num:
            if vn > vd:
                key_word = "VC_NUM_"+str(vn)+"_VC_DDR_"+str(vd)
                dir_name = app_name +"_Ring_VC_NUM_"+str(vn)+"_VC_DDR_"+str(vd)
                file_name = "/application_delay_info.log"
                
                with open(dir_path+dir_name+file_name) as log_file:
                    log_data = log_file.readlines()
                
                ete_delay = []
                if len(log_data) > 0:
                    for i in range(4, 4+100):
                        ete_delay.append(log_data[i].strip().split()[-1])
                
                data[key_word] = ete_delay

    p = PlotFunction(data, "Execution Iterations", "ETE Delay", x_ticklabels, x_ticks, '_'+app_name)
    p.save_figs(fig_path, p.title)
    