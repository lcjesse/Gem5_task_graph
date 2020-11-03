#!/bin/bash
GEM5=/home/wj/test/Gem5_task_graph
OUT_FILE_DIR=${GEM5}/my_STATS/test_0930/memory_access_20
mkdir -p ${OUT_FILE_DIR}/figs
mkdir -p ${OUT_FILE_DIR}/LINK_RESULT

for iters in 1 10 20 30 40 50 100
do
    for((app_num=1;app_num<=5;app_num++))
    do
        DIR_NAME=Application_0${app_num}_Iters_${iters}
        infile=${OUT_FILE_DIR}/${DIR_NAME}/stats.txt
        link_outfile=${OUT_FILE_DIR}/LINK_RESULT/link_record_App_0${app_num}_iters_${iters}.txt
        echo -e "router_name\tlink_utilization\t" > ${link_outfile}
        for((router_num=0;router_num<=9;router_num++))
        do
            link_utilization=`grep "routers0${router_num}.buffer_reads" ${infile} | sed "s/system.ruby.network.routers0${router_num}.buffer_reads\s*//" | sed 's/\s*$//'`
            echo -e "routers_0${router_num}\t${link_utilization}" >> ${link_outfile}
        done
        for router_num in 10 11
        do
            link_utilization=`grep "routers${router_num}.buffer_reads" ${infile} | sed "s/system.ruby.network.routers${router_num}.buffer_reads\s*//" | sed 's/\s*$//'`
            echo -e "routers_${router_num}\t${link_utilization}" >> ${link_outfile}
        done
    done
done