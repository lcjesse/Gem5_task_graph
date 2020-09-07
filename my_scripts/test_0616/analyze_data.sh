#!/bin/bash
GEM5=/home/wj/Study/gem5
outfile=${GEM5}/my_STATS/test_20200616/test_iters/results.txt
echo -e "directory_name\tflits_received\taverage_hops\taverage_flit_latency" > ${outfile}
for ex_iter in 1 10 20 30 40 50
do
    for((app_num=1;app_num<=5;app_num++))
    do
        dirname=Application_0${app_num}_iters${ex_iter}
        infile=${GEM5}/my_STATS/test_20200616/test_iters/${dirname}/stats.txt
        # read specified results from stats.txt
        average_hops=`grep "average_hops" ${infile} | sed 's/system.ruby.network.average_hops\s*//' | sed 's/\s*$//'`
        flits_received=`grep "flits_received::total" ${infile} | sed 's/system.ruby.network.flits_received::total\s*//' | sed 's/\s*$//'`
        average_flit_latency=`grep "average_flit_latency" ${infile} | sed 's/system.ruby.network.average_flit_latency\s*//' | sed 's/\s*$//'`
        echo -e "${dirname}\t${flits_received}\t${average_hops}\t${average_flit_latency}" >> ${outfile}
    done
done


outfile=${GEM5}/my_STATS/test_20200616/test_msg_size/results.txt
msg_size=(
    256_512_512
    256_1600_512
    256_5120_512
    256_12288_512
    512_12288_512
    )
ex_iter=50
echo -e "directory_name\tflits_received\taverage_hops\taverage_flit_latency" > ${outfile}
for((i=0;i<=4;i++))
do
    for((app_num=1;app_num<=5;app_num++))
    do
        dirname=Application_0${app_num}_iters${ex_iter}_msg_${msg_size[i]}
        infile=${GEM5}/my_STATS/test_20200616/test_msg_size/${dirname}/stats.txt
        # read specified results from stats.txt
        average_hops=`grep "average_hops" ${infile} | sed 's/system.ruby.network.average_hops\s*//' | sed 's/\s*$//'`
        flits_received=`grep "flits_received::total" ${infile} | sed 's/system.ruby.network.flits_received::total\s*//' | sed 's/\s*$//'`
        average_flit_latency=`grep "average_flit_latency" ${infile} | sed 's/system.ruby.network.average_flit_latency\s*//' | sed 's/\s*$//'`
        echo -e "${dirname}\t${flits_received}\t${average_hops}\t${average_flit_latency}" >> ${outfile}
    done
done

