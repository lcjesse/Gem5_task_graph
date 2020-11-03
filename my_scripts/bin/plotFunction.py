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
