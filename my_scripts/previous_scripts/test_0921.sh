#!/bin/bash
GEM5=/home/wj/Study/gem5
OUT_FILE_DIR=${GEM5}/my_STATS/09_21_total_iters1

##### Run Test #####
for i in {1..5}
do
    for j in 10 20 30 40 50
    do
    {
        DIR_NAME=Application_0${i}_Iters_${j}
        mkdir -p ${OUT_FILE_DIR}/${DIR_NAME}  
        ./build/NULL/gem5.debug  \
        --outdir ${OUT_FILE_DIR}/${DIR_NAME} \
        configs/example/garnet_synth_traffic.py \
        --topology=Ring \
        --num-cpus=12 \
        --num-dirs=12 \
        --mesh-rows=1 \
        --network=garnet2.0 \
        --inj-vnet=2 \
        --injectionrate=0 \
        --token-packet-length=6 \
        --network-task-graph-enable \
        --task-graph-file="./my_benchmarks/09_21/Application_0${i}.stp" \
        --execution-iteration=${j} \
        --routing-algorithm=2 \
        --vcs-per-vnet=2 \
        --link-width-bits=256 \
        --architecture-file="./my_benchmarks/09_21/Heterogeneous_SoC_with_Ring_Topology.arch"  &> ${OUT_FILE_DIR}/${DIR_NAME}/log
        #--ruby-clock=2GHz
        #--sys-clock=2GHz
        # --debug-flags=TaskGraph
    } &
    done
done

wait

##### Collect Data #####
RESULT_FILE=${OUT_FILE_DIR}/results.txt
echo -e "Directory_name\tFlits_received\tAverage_hops\tAverage_flit_latency\tAverage_network_flit_latency\tAverage_flit_queueing_latency\taverage_application_ete_dalay" > ${RESULT_FILE}
for i in {1..5}
do
    for j in 10 20 30 40 50
    do
        DIR_NAME=Application_0${i}_Iters_${j}
        IN_FILE=${OUT_FILE_DIR}/${DIR_NAME}/stats.txt
        average_hops=`grep "average_hops" ${IN_FILE} | sed 's/system.ruby.network.average_hops\s*//' | sed 's/\s*$//'`
        flits_received=`grep "flits_received::total" ${IN_FILE} | sed 's/system.ruby.network.flits_received::total\s*//' | sed 's/\s*$//'`
        average_flit_latency=`grep "average_flit_latency" ${IN_FILE} | sed 's/system.ruby.network.average_flit_latency\s*//' | sed 's/\s*$//'`
        average_flit_network_latency=`grep "average_flit_network_latency" ${IN_FILE} | sed 's/system.ruby.network.average_flit_network_latency\s*//' | sed 's/\s*$//'`
        average_flit_queueing_latency=`grep "average_flit_queueing_latency" ${IN_FILE} | sed 's/system.ruby.network.average_flit_queueing_latency\s*//' | sed 's/\s*$//'`
        average_application_ete_dalay=`grep "average_application_ete_dalay" ${IN_FILE} | sed 's/system.ruby.network.average_application_ete_dalay\s*//' | sed 's/\s*$//'`
        echo -e "${DIR_NAME}\t${flits_received}\t${average_hops}\t${average_flit_latency}\t${average_flit_network_latency}\t${average_flit_queueing_latency}\t${average_application_ete_dalay}" >> ${RESULT_FILE}
    done
done

##### Read Log #####
LOG_FILE=${OUT_FILE_DIR}/log
echo > ${LOG_FILE}
for i in {1..5}
do
    echo "###########################################################################################################################################" >> ${LOG_FILE} 
    echo "############################################################## Application 0${i} ############################################################" >> ${LOG_FILE}
    echo "###########################################################################################################################################" >> ${LOG_FILE}
    for j in 10 20 30 40 50
    do
        DIR_NAME=Application_0${i}_Iters_${j}
        IN_FILE=${OUT_FILE_DIR}/${DIR_NAME}/log
        echo "######################################################### ${DIR_NAME} #########################################################" >> ${LOG_FILE}
        tail -n $((${j}+3)) ${IN_FILE} >> ${LOG_FILE}
        echo -e "###########################################################################################################################################\n\n" >> ${LOG_FILE} 
    done
done
