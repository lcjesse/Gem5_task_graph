from io import SEEK_CUR
from os import name
from types import FunctionType
import matplotlib.pyplot as plt
from matplotlib.pyplot import legend, plot, xticks

## class for plot function
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
        line_type=['-x', '-*', '-^', '-o', '-s', '-<', '-v', '-D']
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


## System Path
dir_path = "/home/wj/test/Gem5_task_graph/my_STATS/10_03/different_memory_access/"
result_path = dir_path+"results.txt"
fig_path = dir_path+"FIGS/"
link_result_path = dir_path+"LINK_RESULT/"
log_path = dir_path + "log"

## Parameter Setting
app=[1, 2, 3, 4, 5]
iters=[100]
mem_access=['10', '20', '30', '40', '50']
mem_type = ['DDR3']

## Read File -> result.txt
with open(result_path) as input_file:
    input_data = input_file.readlines()

# use dict to store info {name: [...]}
input_data_dict = {}

for i in range(1, len(input_data)):
    input_data_dict[input_data[i].split()[0]] = input_data[i].strip().split()[1:]

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
    for iter in iters:
            for mc in mem_access:
                for mt in mem_type:
                    filename = "Application_0" + str(app_num) + '_Iters_' + str(iter) + '_Memory_Access_' +\
                                    str(mc) + '_Memory_Type_' + str(mt)
                    ete_delay[app_name].append(input_data_dict[filename][5])
                    flits[app_name].append(input_data_dict[filename][0])
                    hops[app_name].append(input_data_dict[filename][1])
                    latency[app_name].append(input_data_dict[filename][2])
                    network_latency[app_name].append(input_data_dict[filename][3])
                    queueing_latency[app_name].append(input_data_dict[filename][4])

p = PlotFunction(ete_delay, 'Memory Access', 'Average ETE Delay', mem_access)
p.save_figs(fig_path)


## Read File -> log
if 0:
    with open(log_path) as log_file:
        log_data = log_file.readlines()

    for app in app:

        ete_delay = {}
        average_ete_delay = {}

        for iter in iters:
            for mc in mem_access:
                for mt in mem_type:
                    key_word = 'Application_0' + str(app) + '_Iters_' + str(iter) + '_Memory_Access_' +\
                        str(mc) + '_Memory_Type_' + str(mt)
                    start_idx = -1
                    for i in range(len(log_data)):
                        if key_word in log_data[i]:
                            start_idx = i + 3
                            break
                    assert(start_idx != -1)

                    each_iter_data = []
                    aver_data = []
                    total_delay = 0
                    assert(log_data[start_idx+iter-1].strip().split()[1] == str(iter-1))
                    for i in range(start_idx, start_idx+iter):
                        delay = log_data[i].strip().split()[-1]
                        total_delay += int(delay)
                        each_iter_data.append(delay)
                        aver_data.append(total_delay/(i-start_idx+1))

                    x_index = 'Memory_Access_' + mc # for legend
                    ete_delay[x_index] = each_iter_data
                    average_ete_delay[x_index] = aver_data

        x_ticklabels=['10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
        x_ticks=[i*10 for i in range(1,11)]
        p = PlotFunction(ete_delay, "Execution Iterations", "ETE Delay", x_ticklabels, x_ticks, ' for_App_0'+str(app))
        p.save_figs(fig_path)

        p1 = PlotFunction(average_ete_delay, "Execution Iterations", "Average ETE Delay", x_ticklabels, x_ticks, ' for_App_0'+str(app))
        p1.save_figs(fig_path)
