#!/bin/bash

OUTDIR=/home/lichang/NoC-mapping/results/2021_01_12
mkdir -p ${OUTDIR}
app=(1 2 3 5)
evaluation=(mean dev cost)
topology=(Ring)

for EVAL in ${evaluation[@]}
do
    for APP in ${app[@]}
    do
        for TOPO in ${topology[@]}
        do
{
    # topology, column, architecture_file, configure_file, out_dir, evaluation function, pe_seq_iter, pe_cluster_iter, node_seq_iter
    if [ ${TOPO} = Mesh ]
    then 
        col=3
    else
        col=12
    fi
    DIR=${OUTDIR}/${TOPO}_${APP}
    mkdir -p ${DIR}
    python /home/lichang/NoC-mapping/exhausting_search.py \
    ${TOPO} \
    ${col} \
    /home/lichang/NoC_STAGE/benchmarks/test/Heterogeneous_SoC_with_Ring_Topology.arch \
    /home/lichang/NoC_STAGE/benchmarks/test/multi_application_0${APP}.cfg \
    ${DIR} \
    reconfig_Heterogeneous_SoC_with_${TOPO}_Topology_App_0${APP}_${EVAL}.arch \
    ${EVAL} \
    1000 \
    10 \
    1000 &> ${DIR}/log_${EVAL}
}&
        done
    done
done
