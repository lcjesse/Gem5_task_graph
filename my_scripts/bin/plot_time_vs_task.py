import matplotlib.pyplot as plt

with open("task_start_time_vs_id.log", "r") as file:
    data = file.readlines()

time = []
core_id = []
core_name = ['HQM', 'Core-0', 'PE-1', 'PE-2', 'DDR-0', 'PE-3', 'PE-4', 'PE-5', 'PE-13', 'Core-1', \
                'Core-2', 'PE-6', 'PE-7', 'PE-8', 'DDR-1', 'PE-9', 'PE-10', 'PE-11', 'PE-12', 'Core-3']
task_id = []
for line in data:
    time.append(int(line.split()[0]))
    core_id.append(int(line.split()[1]))
    task_id.append(int(line.split()[2]))

if 0:
    plt.scatter(time, task_id, c='black', edgecolors='none', s=5)

if 1:
    plt.scatter(time, [core_name[int(i)] for i in core_id], c='black', edgecolors='none', s=5)

with open("task_start_end_time_vs_id.log", "r") as file1:
    min_max = file1.readlines()

max_time = []
max_core_id = []
max_task_id = []
min_time = []
min_core_id = []
min_task_id = []
for line in min_max:
    info = line.split()
    if info[0] == "max":
        max_time.append(int(info[1]))
        max_core_id.append(int(info[2]))
        max_task_id.append(int(info[3]))
    elif info[0] == "min":
        min_time.append(int(info[1]))
        min_core_id.append(int(info[2]))
        min_task_id.append(int(info[3]))

if 0:
    plt.scatter(min_time, min_task_id, c='blue', edgecolors='none', s=10)
    plt.scatter(max_time, max_task_id, c='red', edgecolors='none', s=10)
    for i in range(len(min_time)):
        plt.plot([min_time[i], max_time[i]], [min_task_id[i], max_task_id[i]], c='black')

with open("task_start_time_vs_id_iters.log", "r") as file2:
    each_data = file2.readlines()

info = [] # each iters information
for i in range(len(each_data)):
    if each_data[i] == "Execution\n":
        if len(info) > 0:
            iters_data = {} # time-task dict
            iters_core = {}
            for j in range(len(info)):
                line_data = info[j].split()
                iters_data[int(line_data[0])] = int(line_data[2])
                iters_core[int(line_data[0])] = int(line_data[1])

            # for time vs task id
            x = []
            y = []
            for j in sorted(iters_data):
                x.append(j)
                y.append(iters_data[j])
            if 0:
                plt.plot(x, y)
            # for time vs core id
            x1 = []
            y1 = []
            for j in sorted(iters_core):
                x1.append(j)
                y1.append(iters_core[j])
            if 0:
                plt.plot(x1, y1)

            info.clear()
    else:
        info.append(each_data[i])

plt.show()
