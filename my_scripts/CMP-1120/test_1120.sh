#!/bin/bash
GEM5=/home/wj/test/Gem5_task_graph

for ex_iter in 100
do
{
    for app in 1
    do
    {
        for vc_num in 2 4 6 8 
        do
        {
            for vc_ddr in 0 2 4 6
            do
            {
                if (( vc_ddr < vc_num )); then
                    mkdir -p ${GEM5}/my_STATS/test_1120/App_0${app}_ring_vc_num_${vc_num}_vc_ddr_${vc_ddr}_iter_${ex_iter}
                    ${GEM5}/build/NULL/gem5.debug  \
                    --outdir ${GEM5}/my_STATS/test_1120/App_0${app}_ring_vc_num_${vc_num}_vc_ddr_${vc_ddr}_iter_${ex_iter} \
                    ${GEM5}/configs/example/garnet_synth_traffic.py \
                    --topology=Ring \
                    --num-cpus=12 \
                    --num-dirs=12 \
                    --network=garnet2.0 \
                    --inj-vnet=2 \
                    --injectionrate=0 \
                    --token-packet-length=6 \
                    --network-task-graph-enable \
                    --task-graph-file="${GEM5}/my_benchmarks/11_18/Memory_Access_20_Memory_Type_DDR3/multi_application_0${app}.cfg" \
                    --execution-iteration=${ex_iter} \
                    --link-width-bits=256 \
                    --routing-algorithm=2 \
                    --vcs-per-vnet=${vc_num} \
                    --vcs-for-ddr=${vc_ddr} \
                    --architecture-file="${GEM5}/my_benchmarks/11_18/Heterogeneous_SoC_with_Ring_Topology.arch" &> ${GEM5}/my_STATS/test_1120/App_0${app}_ring_vc_num_${vc_num}_vc_ddr_${vc_ddr}_iter_${ex_iter}/log
                fi
            }&
            done
        }&
        done
    }&
    done
}&
done

# wait

# ##### Read Log #####
# LOG_FILE=${GEM5}/my_STATS/test_1120/log
# echo > ${LOG_FILE}
# for app in 1
# do
#     echo "###########################################################################################################################################" >> ${LOG_FILE} 
#     echo "############################################################## Application 0${app} ############################################################" >> ${LOG_FILE}
#     echo "###########################################################################################################################################" >> ${LOG_FILE}
#     for ex_iter in 100
#     do
#     {
#         for vc_num in 2 4 6 8 
#         do
#         {
#             for vc_ddr in 0 2 4 6
#             do
#             {
#                 if (( vc_ddr < vc_num )); then
#                     dir_name=${GEM5}/my_STATS/test_1120/App_0${app}_ring_vc_num_${vc_num}_vc_ddr_${vc_ddr}_iter_${ex_iter}
#                     IN_FILE=${dir_name}/log
#                     echo "############################################### App_0${app}_ring_vc_num_${vc_num}_vc_ddr_${vc_ddr}_iter_${ex_iter} ###############################################" >> ${LOG_FILE}
#                     tail -n 103 ${IN_FILE} >> ${LOG_FILE}
#                     echo -e "###########################################################################################################################################\n\n" >> ${LOG_FILE} 
#                 fi
#             }
#             done
#         }
#         done
#     }
#     done
# done


# ########## Collect Data ##########
# outfile=${GEM5}/my_STATS/test_1120/results.txt
# echo -e "directory_name\taverage_ete_delay\tflits_received\taverage_hops\taverage_flit_latency\taverage_flit_network_latency\taverage_flit_queueing_latency\t" > ${outfile}
# for ex_iter in 100 
# do
#     for app in 1
#     do
#         for vc_num in 2 4 6 8
#         do
#             for vc_ddr in 0 2 4 6
#             do
#                 if (( vc_ddr < vc_num )); then
#                     dirname=App_0${app}_ring_vc_num_${vc_num}_vc_ddr_${vc_ddr}_iter_${ex_iter}
#                     infile=${GEM5}/my_STATS/test_1120/${dirname}/stats.txt
#                     # read specified results from stats.txt
#                     average_ete_delay=`grep "average_application_ete_dalay" ${infile} | sed 's/system.ruby.network.average_application_ete_dalay\s*//' | sed 's/\s*$//'`
#                     average_hops=`grep "average_hops" ${infile} | sed 's/system.ruby.network.average_hops\s*//' | sed 's/\s*$//'`
#                     flits_received=`grep "flits_received::total" ${infile} | sed 's/system.ruby.network.flits_received::total\s*//' | sed 's/\s*$//'`
#                     average_flit_latency=`grep "average_flit_latency" ${infile} | sed 's/system.ruby.network.average_flit_latency\s*//' | sed 's/\s*$//'`
#                     average_flit_network_latency=`grep "average_flit_network_latency" ${infile} | sed 's/system.ruby.network.average_flit_network_latency\s*//' | sed 's/\s*$//'`
#                     average_flit_queueing_latency=`grep "average_flit_queueing_latency" ${infile} | sed 's/system.ruby.network.average_flit_queueing_latency\s*//' | sed 's/\s*$//'`
                    
#                     echo -e "${dirname}\t${average_ete_delay}\t${flits_received}\t${average_hops}\t${average_flit_latency}\t${average_flit_network_latency}\t${average_flit_queueing_latency}" >> ${outfile}
#                 fi
#             done
#         done
#     done
# done
