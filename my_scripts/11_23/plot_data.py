### Custom Plot Function ###
import matplotlib.pyplot as plt
from matplotlib.pyplot import legend, plot, xticks

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

dir_path = "/home/wj/test/Gem5_task_graph/my_STATS/10_03/different_memory_type_and_memory_access_20/"
result_path = dir_path+"results.txt"
fig_path = dir_path+"FIGS/"
link_result_path = dir_path+"LINK_RESULT/"
log_path = dir_path + "log"

## Parameter Setting
app=[1, 2, 3, 4, 5]
iters=[100]
mem_access=[20]
mem_type = ['DDR3']

## Read File -> log
with open(log_path) as log_file:
    log_data = log_file.readlines()

old_ete_delay = {}
for app in app:
    app_name = "Application_0" + str(app)
    each_iter_data = []
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

                assert(log_data[start_idx+iter-1].strip().split()[1] == str(iter-1))
                for i in range(start_idx, start_idx+iter):
                    delay = log_data[i].strip().split()[-1]
                    each_iter_data.append(delay)

    old_ete_delay[app_name] = each_iter_data


dir_path = "/home/wj/gem5_multiapp/Gem5_task_graph/my_STATS/11_09/multi_app/"
result_path = dir_path+"results.txt"
fig_path = dir_path+"FIGS/"
link_result_path = dir_path+"LINK_RESULT/"
log_path = dir_path + "Application_07_Iters_20_Memory_Access_20_Memory_Type_DDR3/log"

with open(log_path) as log_file:
    log_data = log_file.readlines()

new_ete_delay = {}
for app in range(1, 6):
    app_name = "Application_0" + str(app)
    each_iter_data = []
    for i in range(3+103*(app-1), 103+103*(app-1)):
            delay = log_data[i].strip().split()[-1]
            each_iter_data.append(delay)

    new_ete_delay[app_name] = each_iter_data

dir_path = "/home/wj/gem5_multiapp/Gem5_task_graph/my_STATS/11_11/multi_app/"
result_path = dir_path+"results.txt"
fig_path = dir_path+"FIGS/"
link_result_path = dir_path+"LINK_RESULT/"

## Parameter Setting
app=[1, 2, 3, 4, 5]
iters=[20]
mem_access=[20]
mem_type = ['DDR3']

ete_delay = {}
for app in app:
    app_name = "Application_0" + str(app)
    each_iter_data = []
    for iter in iters:
        for mc in mem_access:
            for mt in mem_type:
                key_word = 'Application_0' + str(app) + '_Iters_' + str(iter) + '_Memory_Access_' +\
                    str(mc) + '_Memory_Type_' + str(mt)
                log_path = dir_path + key_word + "/application_delay_info.log"
                with open(log_path) as log_file:
                    log_data = log_file.readlines()

                for i in range(4, 4+100-1):
                    delay = log_data[i].strip().split()[-1]
                    each_iter_data.append(delay)

    ete_delay[app_name] = each_iter_data


x_ticklabels=['10', '20', '30', '40', '50', '60', '70', '80', '90', '100']
x_ticks=[i*10 for i in range(1,11)]


for app in range(1, 6):
    data = {}
    app_name = "Application_0" + str(app)
    data["old"] = old_ete_delay[app_name]
    data["new"] = ete_delay[app_name]
    data["multi_app"] = new_ete_delay[app_name]
    p = PlotFunction(data, "Execution Iterations", "ETE Delay", x_ticklabels, x_ticks, ' for_App_0'+str(app))
    p.save_figs(fig_path, p.title)

dir_path = "/home/wj/gem5_multiapp/Gem5_task_graph/my_STATS/11_11/multi_app/"
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
