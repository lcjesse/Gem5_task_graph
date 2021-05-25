########## Try to optimize latency of NoC (search all solution, actually not STAGE) ###################
#################################### Import ###############################
from collections import defaultdict
from heapq import *
# import xlrd
from copy import deepcopy
from random import randint,random,seed
import math
import numpy
import random
# from sklearn.ensemble import RandomForestRegressor
import timeit
import sys
import os
################################ defn. Variables #############################

'''
defn. of last move and best move:
last_move[0]: swapped core index 1
last_move[1]: swapped core index 2
'''

################################### Creating nodes ####################################
def create_nodes(architecture_file):
    nodes = []
    pes = []
    num_pe_cluster = 0
    with open(architecture_file) as f:
        # value of nodes[i] is node type
        hqm = 0 # 0
        cpu = 1 # 1 2 3 4
        pe = 5 # 5 6 7 8 9
        ddr = 10 # 10 11
        content = f.readlines()
        content = [x.strip() for x in content]
        num_nodes = int(content[0])
        num_pes = 0
        for i in range(0, num_nodes):
            nodes.append(9999)
        for i in range(1, 1+num_nodes):
            num_pes += content[i].count("PE")
            temp = content[i].split()
            num_cores_in_node = int(temp[1])
            if(content[i].find("HQM") != -1):
                nodes[i-1] = hqm
                hqm += 1
            elif(content[i].find("Core") != -1):
                nodes[i-1] = cpu
                cpu += 1
            elif(content[i].find("PE") != -1):
                nodes[i-1] = pe
                pe += 1
                num_pe_cluster += 1
                for j in range(2, 3*num_cores_in_node, 3):      ## element 2 5 8 11... is core id
                    pes.append(int(temp[j]))    # record pe number, for cluster exchange
            elif(content[i].find("DDR") != -1):
                nodes[i-1] = ddr
                ddr += 1
        # print("num_pes is "+ str(num_pes))
        # print("pes are : " + str(pes))
        # print("pe_clusters are : " +str(pe_clusters))

    return deepcopy(nodes), deepcopy(pes), num_pe_cluster


########################## Creating link connectivity based on topology #############################
def create_topology(topo_type, num_cores, col):
    links = numpy.zeros(shape=(num_cores, num_cores))
    if topo_type == 'ring' or topo_type == 'Ring' or topo_type == 'RING':
        for i in range(0, num_cores):
            for j in range(0, num_cores):
                if (abs(i - j) == 1) or (abs(i - j) == (num_cores - 1)):           ## In ring, adjacent nodes have links. First and last are connected.
                    links[i][j] = 1
        return deepcopy(links)
    elif topo_type == 'mesh' or topo_type == 'Mesh' or topo_type == 'MESH':
        for i in range(0, num_cores):
            for j in range(0, num_cores):
                ys = int(i / col)
                xs = i % col
                yd = int(j / col)
                xd = j % col
                if (ys == yd) and (abs(xd - xs) == 1):  # x-links
                    links[i][j] = 1
                elif (xs == xd) and (abs(yd - ys) == 1):  # y-links
                    links[i][j] = 1
        return deepcopy(links)


############################### Construct Architectue ###############################
def construct_architecture(architecture_file):
    with open(architecture_file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        num_nodes = int(content[0])      ## line 0 is number of nodes]
        arch = []
        arch_dict = {}
        for i in range(1, 1 + num_nodes):
            temp = content[i].split()
            num_cores_in_node = int(temp[1])
            t = []
            for j in range(2, 3*num_cores_in_node, 3):      ## element 2 5 8 11... is core id
                t.append(int(temp[j]))
                arch_dict[int(temp[j])] = temp[j+1:j+3]     # save name and thread of every core as a dictionary
            arch.append(t)
    return deepcopy(arch), deepcopy(arch_dict)


############################### Remap PE Architecture #################################
def remap_pe_architecture(pes, num_pe_clusters, nodes, arch):
    num_pes = len(pes)
    remain_pes = num_pes
    remain_pe_clusters = num_pe_clusters
    separate_form = []
    for i in range(0,num_pe_clusters-1):
        a = random.randint(1,4)         # give each cluster 1-4 pes randomly
        ratio = float(remain_pes - a) / (remain_pe_clusters - 1)
        # print("a: %d remain_pes: %d remain_pe_clusters: %d ratio: %f" % (a,remain_pes, remain_pe_clusters,ratio))
        while(1 > ratio or ratio > 4):          # limit cluster size for clusters behind
            a=random.randint(1,4)
            ratio = float(remain_pes - a) / (remain_pe_clusters - 1)
        remain_pes -= a
        remain_pe_clusters -= 1
        separate_form.append(a)
    a = remain_pes
    separate_form.append(a)

    new_pes =[]
    k = 0
    for i in range(num_pe_clusters):
        t = []
        for j in range(k, k + separate_form[i]):    # put certain number of pe together
            t.append(pes[j])
        k += separate_form[i]
        new_pes.append(t)

    pe_clusters = []
    for i in range(len(nodes)):
        if ((nodes[i] >= 5) and (nodes[i] <= 9)):
            pe_clusters.append(i)
    for i in range(len(pe_clusters)):
        arch[pe_clusters[i]]=new_pes[i]     # put new pe cluster into architecture matrix

    return arch #deepcopy(arch)


###################### reverse pe perturb ######################
# Turn everything back
def reverse_pe_perturb(pes,pe_last_move):
    rs = pe_last_move[0]
    rd = pe_last_move[1]
    t1 = pes[rs]
    pes[rs] = pes[rd]
    pes[rd] = t1  # re-exchanged nodes

    return deepcopy(pes)

###################### arch matrix to architecture file ######################
def arch_to_architecture(arch,arch_dict,re_architecture_file):
    with open (re_architecture_file,'w') as q:
        num_nodes = len(arch)
        q.write(str(num_nodes))     # number of nodes
        q.write('\n')
        for i in range(0, num_nodes):
            q.write(str(i))     # node id
            q.write(' ')
            num_cores_in_node = len(arch[i])
            q.write(str(num_cores_in_node))     # number of cores in node(cluster)
            q.write(' ')
            for j in range(num_cores_in_node):
                q.write(str(arch[i][j]))        # core id
                q.write(' ')
                for k in range(len(arch_dict[arch[i][j]])):
                    q.write(arch_dict[arch[i][j]][k])   # core name and thread
                    q.write(' ')
            q.write('\n')


##################### reconfig arch matrix based on best record #####################
def reconfigure_architect(best_record, arch, nodes):
    num_nodes = len(nodes)
    new_arch = []
    for i in range(num_nodes):
        for j in range(num_nodes):
            if (best_record[1][i] == nodes[j]):
                new_arch.append(arch[j])
    return deepcopy(new_arch)

################################### make traffic file based on arch file and stp file ####################################
def configure_traffic(arch, configure_file, nodes, out_dir, topo_type, eva_type):
    dir_name = os.path.split(configure_file)[0] + '/'
    num_nodes = len(nodes)
    traffic = [[0 for i in range(num_nodes)] for j in range(num_nodes)]
    with open(configure_file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        info = content[0].split()
        total_iter = float(info[1])
        num_app = int(info[0])
        for i in range(1, num_app+1):
            temp = content[i].split()
            traffic_file = dir_name + temp[0]
            arch_traffic_file = out_dir + "/arch_" + topo_type +"_" + eva_type +"_" + temp[0]
            percent = float(temp[1]) / total_iter
            traffic = make_traffic(arch, traffic_file, arch_traffic_file, nodes, percent, traffic)
    return traffic


################################### make traffic file based on arch file and stp file ####################################
def make_traffic(arch, traffic_file, arch_traffic_file, nodes, percent, traffic):
    with open(traffic_file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        ## line 15 in stp file contains number of node, task, edge
        temp = content[15].split()
        num_node = int(temp[1])
        num_task = int(temp[2])
        num_edge = int(temp[3])
    ## write changed traffic into stp file
    t=''
    with open (arch_traffic_file,'w') as q:
        for i in range(15):
            q.write(content[i])
            q.write('\n')
        temp15 = content[15].split()
        temp15[1] = str(len(arch))
        t = ''
        for e in range(len(temp15)):
            t=t+str(temp15[e])+'  '
        q.write(t)
        q.write("\n")
        for i in range(16, 16+num_task):    ## task info: change processor mapping
            temp1 = content[i].split()
            for j in range(0, len(arch)):
                for k in range(0, len(arch[j])):
                    if(int(temp1[1]) == arch[j][k]):
                        temp1[1] = j
                        break
            
            t = ''
            for e in range(len(temp1)):
                t=t+str(temp1[e])+'  '
            q.write(t)
            q.write("\n")
            t = ''
        for i in range(16+num_task, 16+num_task+num_edge):    ## edge info: change src and dst processor mapping 
            temp2 = content[i].split()
            for j in range(0, len(arch)):
                for k in range(0, len(arch[j])):
                    if(int(temp2[3]) == arch[j][k]):
                        temp2[3] = j
                        break
            for j in range(0, len(arch)):
                for k in range(0, len(arch[j])):
                    if(int(temp2[4]) == arch[j][k]):
                        temp2[4] = j
                        break
            t = ''
            for e in range(len(temp2)):
                t=t+str(temp2[e])+'  '
            q.write(t)
            q.write("\n")
            t = ''

    with open(arch_traffic_file) as f:
        content = f.readlines()
        content = [x.strip() for x in content]
        ## line 15 in stp file contains number of node, task, edge
        temp = content[15].split()
        num_node = int(temp[1])
        num_task = int(temp[2])
        num_edge = int(temp[3])
        #traffic = [[0 for col in range(num_node)] for row in range(num_node)]
        ## every row refers to src_node; every column refers to dst_node
        for i in range(16+num_task, 16+num_task+num_edge):
            temp1 = content[i].split()
            traffic[nodes[int(temp1[3])]][nodes[int(temp1[4])]] += (percent * float(temp1[9])/10)       ##Here traffic is the sum of token size between src and dst
    os.remove(arch_traffic_file)
    return traffic


################################# routing algorithm ###############################
def routing(topo_type, nodes, s, d, col):        ## nodes, src_node, dst_node(s and d means the place, not the content)
    if topo_type == 'ring' or topo_type == 'Ring' or topo_type == 'RING':
        num_nodes = len(nodes)
        hops = d - s
        path = (nodes[s])
        cost = 0
        while hops != 0:
            if (hops > 0 and hops <= num_nodes / 2) or (hops < (-num_nodes / 2)):
                s = (s + 1) % num_nodes
                hops = d - s
                cost += 1
                path = (nodes[s], path)
            elif (hops < 0 and hops >= (-num_nodes / 2)) or (hops > num_nodes / 2):
                s = (s - 1) % num_nodes
                hops = d - s
                cost += 1
                path = (nodes[s], path)
        return (cost, path)
    elif topo_type == 'mesh' or topo_type == 'Mesh' or topo_type == 'MESH':
        x1 = s % col
        x2 = d % col
        y1 = int(s / col)
        y2 = int(d / col)
        x_diff = x2 - x1
        y_diff = y2 - y1
        path = (nodes[s])
        cost = 0
        while (x_diff != 0) or (y_diff != 0):      ## first x then y
            if x_diff < 0:
                s -= 1
                x_diff += 1
                cost += 1
                path = (nodes[s], path)
            elif x_diff > 0:
                s += 1
                x_diff -= 1
                cost += 1
                path = (nodes[s], path)
            elif y_diff < 0:
                s -= col
                y_diff += 1
                cost += 1
                path = (nodes[s], path)
            elif y_diff > 0:
                s += col
                y_diff -= 1
                cost += 1
                path = (nodes[s], path)
        return (cost, path)


################################# Calculate hop count #################################
def calculate_hop_count(topo_type, nodes, col):
    hop_count = []
    if(topo_type == 'mesh' or topo_type == 'Mesh'  or topo_type == 'MESH'):
        for i in range(0, len(nodes)):
            t = []
            for j in range(0, len(nodes)):
                x1 = i%col
                x2 = j%col
                y1 = int(i/col)
                y2 = int(j/col)
                t.append(abs(x1-x2) + abs(y1-y2))      
            hop_count.append(t)
        return hop_count
    elif(topo_type == 'ring' or topo_type == 'Ring' or topo_type == 'RING'):
        for i in range(0, len(nodes)):
            t = []
            for j in range(0, len(nodes)):
                x = abs(i-j)
                if x > len(nodes)/2:
                    x = len(nodes) - x
                t.append(x)
            hop_count.append(t)
        return hop_count


################################# Calculate communication cost #################################
def calculate_cost(topo_type, nodes, col, traffic):
    communi_cost = 0
    hop_count = calculate_hop_count(topo_type, nodes, col)
    for i in range(0, len(nodes)):
        for j in range(0, len(nodes)):
            communi_cost += traffic[nodes[i]][nodes[j]] * hop_count[i][j] / 100       ## communication cost is hop*traffic volume
    return communi_cost


####################################### params calculation ##########################
## Calculate mean and deviation of link utilization
def calc_params(eva_type, topo_type, nodes, links, row, col, traffic):
    if eva_type == "cost" or eva_type == "Cost" or eva_type == "COST":
        return calculate_cost(topo_type, nodes, col, traffic)
    else:
        m = 0
        d = 0
        link_util = []
        num_nodes = len(nodes)
        for i in range(0, num_nodes):
            t = []
            for j in range(0, num_nodes):
                t.append(0)
            link_util.append(t)
        for i in range(0, num_nodes):
            for j in range(0, num_nodes):
                if nodes[i] == nodes[j]:
                    continue
                p = str(routing(topo_type,nodes, i, j, col))
                p_break = p.split(',')
                for k in range(1, len(p_break) - 2):
                    node1 = int(p_break[k][2:])
                    node2 = int(p_break[k + 1][2:])
                    ind1 = nodes.index(node1)
                    ind2 = nodes.index(node2)
                    if links[ind1][ind2] != 1:
                        print('something is wrong..!!')
                    link_util[ind1][ind2] = link_util[ind1][ind2] + traffic[nodes[i]][nodes[j]]     ## calculate link utilization

        for i in range(0, num_nodes):
            for j in range(0, num_nodes):
                m = m + link_util[i][j]
        m = m / (2 * row * col - row - col)             ## each planar has (col-1)*row+(row-1)*col = 2*row*col-row-col links
        if topo_type == 'ring' or topo_type == 'Ring' or topo_type == 'RING':
            m = m / num_nodes
        elif topo_type == 'mesh' or topo_type == 'Mesh' or topo_type == 'MESH':
            m = m / (2*row*col-row-col)             ## each planar has (col-1)*row+(row-1)*col = 2*row*col-row-col links
        for i in range(0, num_nodes):
            for j in range(i, num_nodes):
                if (links[i][j] != 1):
                    continue
                d = d + (link_util[i][j] + link_util[j][i] - m)**2
        d = d**0.5
        if eva_type == "mean" or eva_type == "Mean" or eva_type == "MEAN":
            return m * 10 # to banlance every eva, mean is too small
        elif eva_type == "dev" or eva_type == "Dev" or eva_type == "DEV":
            return d / 10
        else:
            print("Evaluation function wrong!")
            return 0

############################### Make Seq Perturbation #################################
def seqperturb(nodes, rs, rd, last_move):
    t1 = nodes[rs]
    nodes[rs] = nodes[rd]
    nodes[rd] = t1  #  exchanged nodes
    last_move[0] = rs   ## swapped core index 1
    last_move[1] = rd   ## swapped core index 2
    return nodes


############################### Make Perturbation for PE sequence #################################
def pe_perturb(pes):
    num_pes = len(pes)
    for i in range(5): # 5 is a random number
        rs =  random.randint(0, num_pes-1)
        rd =  random.randint(0, num_pes-1)
        t = pes[rs]
        pes[rs] = pes[rd]
        pes[rd] = t  #  exchanged nodes
    return pes


############################### Make Perturbation #################################
def perturb(nodes, last_move):
    num_nodes = len(nodes)
    rs = random.randint(0, num_nodes-1)
    rd = random.randint(0, num_nodes-1)
    t1 = nodes[rs]
    nodes[rs] = nodes[rd]
    nodes[rd] = t1  #  exchanged nodes
    last_move[0] = rs   ## swapped core index 1
    last_move[1] = rd   ## swapped core index 2
    return nodes


def random_perturb(nodes):
    num_nodes = len(nodes)
    for i in range(5): # 5 is a random number
        rs = random.randint(0, num_nodes-1)
        rd = random.randint(0, num_nodes-1)
        t = nodes[rs]
        nodes[rs] = nodes[rd]
        nodes[rd] = t
    return nodes


################################# reverse perturb ######################
## Turn everything back
def reverse_perturb(nodes,last_move):
    rs=last_move[0]
    rd=last_move[1]
    t1 = nodes[rs]
    nodes[rs] = nodes[rd]
    nodes[rd] = t1  # re-exchanged nodes
    return nodes


################################# best perturb ##########################

def best_perturb(nodes, best_move):
    rs = best_move[0]
    rd = best_move[1]
    t1 = nodes[rs]
    nodes[rs] = nodes[rd]
    nodes[rd] = t1
    return nodes


################################ MAIN #####################################
def main(topology, column, architecture_file, configure_file, out_dir, output_file, evaluation_function, pe_seq_iter, pe_cluster_iter, node_seq_iter):
    last_move = []
    best_move = []
    num_nodes = 12
    col = column
    row = num_nodes / col
    for i in range(0, 2):
        last_move.append(-1)
        best_move.append(-1)
    random.seed(1000)
    best_eva = 9999

    re_architecture_file = out_dir + "/" + output_file
    arch, arch_dict = construct_architecture(architecture_file)
    time_to_stop = node_seq_iter #1000     ## iters to node_seq_iter the process

    nodes,pes,num_pe_clusters=create_nodes(architecture_file) 
    links=create_topology(topology, num_nodes, col) 
    best_record = [9999, deepcopy(nodes), deepcopy(arch)]            ## used to record the best solution

    for i in range(pe_seq_iter):
        #################### First loop: randomly change pe sequence ####################
        pes = pe_perturb(pes)           # randomly change pes
        # print("i: %d" % i)
        for j in range(pe_cluster_iter):
            #################### Second loop: remap pe cluster distribution, form a new arch ####################
            nodes = create_nodes(architecture_file)[0]
            arch = remap_pe_architecture(pes, num_pe_clusters, nodes, arch)
            traffic = configure_traffic(arch, configure_file, nodes, out_dir, topology, evaluation_function)
            num_try = 0
            beyond_flag = 0
            while 1:
                #################### Third loop: remap nodes, record best nodes and arch(arch is vip) ####################
                for i in range(0,2):
                    best_move[i]=-1
                    last_move[i]=-1

                for i in range(0, 10):
                    num_try += 1
                    nodes = perturb(nodes, last_move)           ##randomly change nodes
                    current_eva = calc_params(evaluation_function, topology, nodes, links, row, col, traffic)
                    if current_eva < best_eva:
                        best_move = deepcopy(last_move)
                        best_eva = current_eva
                    nodes = reverse_perturb(nodes, last_move)

                temp_nodes = best_perturb(nodes, best_move)
                if(best_eva < best_record[0]):
                    best_record[0] = best_eva
                    best_record[1] = deepcopy(temp_nodes)
                    beyond_flag = 1
                if(num_try >= time_to_stop):
                    nodes = create_nodes(architecture_file)[0]
                    if(beyond_flag == 1):
                        new_arch = reconfigure_architect(best_record, arch, nodes)
                        best_record[2] = deepcopy(new_arch)
                        beyond_flag = 0
                        print(best_record)
                    break
                nodes = random_perturb(nodes)
    arch_to_architecture(best_record[2],arch_dict,re_architecture_file)
    print("Result is :")
    print(best_record)


#################### Extern parameter ####################
topology = sys.argv[1]
column = sys.argv[2]
architecture_file = sys.argv[3]
configure_file = sys.argv[4]
out_dir = sys.argv[5]
output_file = sys.argv[6]
evaluation_function = sys.argv[7]
pe_seq_iter = sys.argv[8]       # iteration for pe sequence exchange
pe_cluster_iter = sys.argv[9]       # iteration for different cluster separation based on one pe sequence
node_seq_iter = sys.argv[10]      # iteration in nodes sequence exchange

main(topology, int(column), architecture_file, configure_file, out_dir, output_file, evaluation_function, int(pe_seq_iter),int(pe_cluster_iter),int(node_seq_iter))
# topology, column, architecture_file, configure_file, out_dir, evaluation_function, pe_seq_iter, pe_cluster_iter, node_seq_iter