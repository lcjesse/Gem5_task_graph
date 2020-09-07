#!/bin/bash
GEM5=/home/wj/Study/gem5
OUT_FILE_DIR=my_STATS/Ring_bottleneck_exploration_0627/Uniform_different_num_cores_without_HQM_vs_different_inj_rate
INJECTION_RATE=0.01
SIM_CYCLES=1000000
NUM_CPUS=(8 16 32 64 128)

RUN_TEST=0
COLLECT_DATA=1

##### Run Test #####
if [ "${RUN_TEST}" = "1" ];then
    for num_cpus in ${NUM_CPUS[@]}
    do
        for i in {1..15}
        do
        {
            INJECTION_RATE=`echo "scale=2;${i}/100" | bc`
            OUT_FILENAME=Ring_Uniform_${num_cpus}_InjectionRate_${INJECTION_RATE}_SimCycles_${SIM_CYCLES}
            ./build/NULL/gem5.debug \
            --outdir ${GEM5}/${OUT_FILE_DIR}/${OUT_FILENAME} \
            configs/example/garnet_synth_traffic.py \
            --topology=Ring \
            --num-cpus=${num_cpus} \
            --num-dirs=${num_cpus} \
            --mesh-rows=1 \
            --network=garnet2.0 \
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
fi

##### Collect Data #####
if [ "${COLLECT_DATA}" = "1" ];then
    RESULT_FILE=${GEM5}/${OUT_FILE_DIR}/results.txt
    #echo -e "Directory_name\t\t\tFlits_received\t\tAverage_hops\t\tAverage_flit_latency\t\tAverage_network_flit_latency" > ${RESULT_FILE}
    echo -e "Directory_name\t\t\tFlits_received\tAverage_hops\tAverage_flit_latency\tAverage_network_flit_latency\tAverage_flit_vnet0_latency\tAverage_flit_vnet1_latency\tAverage_flit_vnet2_latency" > ${RESULT_FILE}

    for num_cpus in ${NUM_CPUS[@]}
    do
        for i in {1..15}
        do
            INJECTION_RATE=`echo "scale=2;${i}/100" | bc`
            IN_FILE_DIR=Ring_Uniform_${num_cpus}_InjectionRate_${INJECTION_RATE}_SimCycles_${SIM_CYCLES}
            IN_FILE=${GEM5}/${OUT_FILE_DIR}/${IN_FILE_DIR}/stats.txt
            average_hops=`grep "average_hops" ${IN_FILE} | sed 's/system.ruby.network.average_hops\s*//' | sed 's/\s*$//'`
            flits_received=`grep "flits_received::total" ${IN_FILE} | sed 's/system.ruby.network.flits_received::total\s*//' | sed 's/\s*$//'`
            average_flit_latency=`grep "average_flit_latency" ${IN_FILE} | sed 's/system.ruby.network.average_flit_latency\s*//' | sed 's/\s*$//'`
            average_flit_network_latency=`grep "average_flit_network_latency" ${IN_FILE} | sed 's/system.ruby.network.average_flit_network_latency\s*//' | sed 's/\s*$//'`
	    average_flit_vnet0_latency=`grep "average_flit_vnet_latency" ${IN_FILE} | cut -d "|" -f2 | sed 's/^\s*//' | sed 's/\s*$//'`
	    average_flit_vnet1_latency=`grep "average_flit_vnet_latency" ${IN_FILE} | cut -d "|" -f3 | sed 's/^\s*//' | sed 's/\s*$//'`
	    average_flit_vnet2_latency=`grep "average_flit_vnet_latency" ${IN_FILE} | cut -d "|" -f4 | sed 's/^\s*//' | sed 's/\s*$//'`
            echo -e "${IN_FILE_DIR}\t${flits_received}\t${average_hops}\t${average_flit_latency}\t${average_flit_network_latency}\t${average_flit_vnet0_latency}\t${average_flit_vnet1_latency}\t${average_flit_vnet2_latency}" >> ${RESULT_FILE}
        done
    done
fi
