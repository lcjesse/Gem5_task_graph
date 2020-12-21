#!/bin/bash
#### Note! Parameters below should be changed for your simulation purpose ! ####
# OUT_FILE_DIR
# DATE (Optional)
# app iters mem_access mem_type
# the stp and arch file in my_benchmarks
# if change arch, link ulitilization part
################################################################################

GEM5=/home/wj/Study/gem5
DATE=`date +%m_%d_%H_%M`
# OUT_FILE_DIR=${GEM5}/my_STATS/11_25/multi_app
OUT_FILE_DIR=${GEM5}/my_STATS/${DATE}/multi_app
mkdir -p ${OUT_FILE_DIR}/FIGS
mkdir -p ${OUT_FILE_DIR}/LINK_RESULT
# OUT_FILE_DIR=${GEM5}/my_STATS/10_03/different_memory_type_and_memory_access_20

# the app.cfg file number
app=(9)
mem_access=(20)
mem_type=(DDR3)

if [ "$#" -ne 1 ]; then
    echo "$0 Usage: $0 [run | col], run for simulation and col for collect data for result.txt." >&2
    exit 1
fi

##### Run Test #####
if [ "$1" = "run" ];then
    for APP_NUM in ${app[@]}
    do
        for MEM_ACCESS in ${mem_access[@]}
        do
            for MEM_TYPE in ${mem_type[@]}
            do
    {
            DIR_NAME=Application_0${APP_NUM}_Ring
            mkdir -p ${OUT_FILE_DIR}/${DIR_NAME}  
            ${GEM5}/build/NULL/gem5.debug \
            --outdir ${OUT_FILE_DIR}/${DIR_NAME} \
            ${GEM5}/configs/example/garnet_synth_traffic.py \
            --topology=Ring \
            --num-cpus=12 \
            --num-dirs=12 \
            --network=garnet2.0 \
            --inj-vnet=2 \
            --injectionrate=0 \
            --token-packet-length=6 \
            --network-task-graph-enable \
            --task-graph-file="${GEM5}/my_benchmarks/12_18/Memory_Access_${MEM_ACCESS}_Memory_Type_${MEM_TYPE}/multi_application_0${APP_NUM}.cfg" \
            --routing-algorithm=2 \
            --vcs-per-vnet=2 \
            --link-width-bits=256 \
            --architecture-file="${GEM5}/my_benchmarks/12_18/Heterogeneous_SoC_with_Ring_Topology.arch" --print-task-execution-info
            #--print-task-execution-info #&> ${OUT_FILE_DIR}/${DIR_NAME}/log  
            #--ruby-clock=2GHz
            #--mesh-rows=1
            #--sys-clock=2GHz
            #--debug-flags=TaskGraph
            #--execution-iteration=100
            #--print-task-execution-info  &
    } 
                    done
                done
            done
fi

# wait 

# ##### Collect Data #####
if [ "$1" = "col" ]; then
    RESULT_FILE=${OUT_FILE_DIR}/results.txt
    echo -e "Directory_name\t\t\t\t\t\t\tFlits_received\tAverage_hops\tAverage_flit_latency\tAverage_network_flit_latency\tAverage_flit_queueing_latency" > ${RESULT_FILE}
    for APP_NUM in ${app[@]}
    do
        for MEM_ACCESS in ${mem_access[@]}
        do
            for MEM_TYPE in ${mem_type[@]}
            do
                for VC_NUM in ${vc_num[@]}
                do
                    for VC_DDR in ${vc_ddr[@]}
                    do
                        if [ "$VC_DDR" -lt "$VC_NUM" ]; then
                            DIR_NAME=Application_0${APP_NUM}_Ring_VC_NUM_${VC_NUM}_VC_DDR_${VC_DDR}
                            IN_FILE=${OUT_FILE_DIR}/${DIR_NAME}/stats.txt
                            average_hops=`grep "average_hops" ${IN_FILE} | sed 's/system.ruby.network.average_hops\s*//' | sed 's/\s*$//'`
                            flits_received=`grep "flits_received::total" ${IN_FILE} | sed 's/system.ruby.network.flits_received::total\s*//' | sed 's/\s*$//'`
                            average_flit_latency=`grep "average_flit_latency" ${IN_FILE} | sed 's/system.ruby.network.average_flit_latency\s*//' | sed 's/\s*$//'`
                            average_flit_network_latency=`grep "average_flit_network_latency" ${IN_FILE} | sed 's/system.ruby.network.average_flit_network_latency\s*//' | sed 's/\s*$//'`
                            average_flit_queueing_latency=`grep "average_flit_queueing_latency" ${IN_FILE} | sed 's/system.ruby.network.average_flit_queueing_latency\s*//' | sed 's/\s*$//'`
                            echo -e "${DIR_NAME}\t${flits_received}\t\t\t${average_hops}\t\t\t${average_flit_latency}\t\t\t${average_flit_network_latency}\t\t\t\t\t${average_flit_queueing_latency}" >> ${RESULT_FILE}
                        fi
                    done
                done
            done
        done
    done
fi

# ##### Read Log #####
# LOG_FILE=${OUT_FILE_DIR}/log
# echo > ${LOG_FILE}
# for APP_NUM in ${app[@]}
# do
#     echo "###########################################################################################################################################" >> ${LOG_FILE} 
#     echo "############################################################## Application 0${APP_NUM} ############################################################" >> ${LOG_FILE}
#     echo "###########################################################################################################################################" >> ${LOG_FILE}
#     for ITERS in ${iters[@]}
#     do
#         for MEM_ACCESS in ${mem_access[@]}
#         do
#             for MEM_TYPE in ${mem_type[@]}
#             do
#             DIR_NAME=Application_0${APP_NUM}_Iters_${ITERS}_Memory_Access_${MEM_ACCESS}_Memory_Type_${MEM_TYPE}
#             IN_FILE=${OUT_FILE_DIR}/${DIR_NAME}/log
#             echo "######################################################### ${DIR_NAME} #########################################################" >> ${LOG_FILE}
#             tail -n $((${ITERS}+3)) ${IN_FILE} >> ${LOG_FILE}
#             echo -e "###########################################################################################################################################\n\n" >> ${LOG_FILE} 
#             done
#         done
#     done
# done

# ##### Generate Link Ultilization #####
# for APP_NUM in ${app[@]}
# do
#     for ITERS in ${iters[@]}
#     do
#         for MEM_ACCESS in ${mem_access[@]}
#         do
#             for MEM_TYPE in ${mem_type[@]}
#             do
#                 DIR_NAME=Application_0${APP_NUM}_Iters_${ITERS}_Memory_Access_${MEM_ACCESS}_Memory_Type_${MEM_TYPE}
#                 infile=${OUT_FILE_DIR}/${DIR_NAME}/stats.txt
#                 link_outfile=${OUT_FILE_DIR}/LINK_RESULT/Link_Record_App_0${APP_NUM}_Iters_${ITERS}_Memory_Access_${MEM_ACCESS}_Memory_Type_${MEM_TYPE}.txt
#                 echo -e "router_name\tlink_utilization\t" > ${link_outfile}
#                 for((router_num=0;router_num<=9;router_num++))
#                 do
#                     link_utilization=`grep "routers0${router_num}.buffer_reads" ${infile} | sed "s/system.ruby.network.routers0${router_num}.buffer_reads\s*//" | sed 's/\s*$//'`
#                     echo -e "routers_0${router_num}\t${link_utilization}" >> ${link_outfile}
#                 done
#                 for router_num in 10 11
#                 do
#                     link_utilization=`grep "routers${router_num}.buffer_reads" ${infile} | sed "s/system.ruby.network.routers${router_num}.buffer_reads\s*//" | sed 's/\s*$//'`
#                     echo -e "routers_${router_num}\t${link_utilization}" >> ${link_outfile}
#                 done
#             done
#         done
#     done
# done

exit 0
