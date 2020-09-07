#!/bin/bash
GEM5=/home/wj/Study/gem5
OUT_FILEDIR=my_STATS/Ring_bottleneck_exploration_0622/test_num_cpus
INJECTION_RATE=0.01
SIM_CYCLES=1000000

##### Run Test #####
for num_cpus in 8 16 32 64 #128 256 512
#for num_cpus in 256
do
    for i in 0.1 {1..9}
    do
    {
        INJECTION_RATE=`echo "scale=2;${i}/10" | bc`
        OUT_FILENAME=Ring_Uniform_${num_cpus}_InjectionRate_${INJECTION_RATE}_SimCycles_${SIM_CYCLES}
        echo ${INJECTION_RATE}
        ./build/NULL/gem5.debug \
        --outdir ${GEM5}/${OUT_FILEDIR}/${OUT_FILENAME} \
        configs/example/garnet_synth_traffic.py \
        --topology=Ring \
        --num-cpus=${num_cpus} \
        --num-dirs=${num_cpus} \
        --mesh-rows=1 \
        --network=garnet2.0 \
        --inj-vnet=2 \
        --injectionrate=${INJECTION_RATE} \
        --routing-algorithm=2 \
        --vcs-per-vnet=2 \
        --link-width-bits=256 \
        --synthetic=uniform_random \
        --sim-cycles=${SIM_CYCLES} 
    } &
    done
done

wait
echo "Run all tests successfully!!!"

##### Collect Data #####
RESULT_FILE=${GEM5}/${OUT_FILEDIR}/results.txt
echo -e "directory_name\tflits_received\taverage_hops\taverage_flit_latency" > ${RESULT_FILE}

for num_cpus in 8 16 32 64
do
    for i in 0.1 {1..9}
    do
        INJECTION_RATE=`echo "scale=2;${i}/10" | bc`
        IN_FILE_DIR=Ring_Uniform_${num_cpus}_InjectionRate_${INJECTION_RATE}_SimCycles_${SIM_CYCLES}
        IN_FILE=${GEM5}/${OUT_FILEDIR}/${IN_FILE_DIR}/stats.txt
        average_hops=`grep "average_hops" ${IN_FILE} | sed 's/system.ruby.network.average_hops\s*//' | sed 's/\s*$//'`
        flits_received=`grep "flits_received::total" ${IN_FILE} | sed 's/system.ruby.network.flits_received::total\s*//' | sed 's/\s*$//'`
        average_flit_latency=`grep "average_flit_latency" ${IN_FILE} | sed 's/system.ruby.network.average_flit_latency\s*//' | sed 's/\s*$//'`
        echo -e "${IN_FILE_DIR}\t${flits_received}\t${average_hops}\t${average_flit_latency}" >> ${RESULT_FILE}
    done
done
