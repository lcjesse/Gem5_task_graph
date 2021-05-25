#!/bin/bash

OUTDIR=/home/lichang/NoC-mapping/results/2021_01_19
mkdir -p ${OUTDIR}
# US-39x23-arm 
# TURBO-160-arm 
# RT-triangle-arm 
# RT-20x20-arm 
# RT-10x10-arm 
# RSe-32x28x8-arm 
# RSd-32x28x8-arm 
# ML-FMP-40x41x41x4-arm 
# ML-FMP-20x21x21x4-arm 
# ML-FMP-12x13x13x4-arm 
# ML-ALIP-70x20x1-arm 
# MD-216-arm
# MD-144-arm 
# MD-108-arm 
# LDPC-270x32-arm 
# FFT-1024-arm
# app=(MD-108-arm)
app=(US-39x23-arm TURBO-160-arm RT-triangle-arm RT-20x20-arm RT-10x10-arm RSe-32x28x8-arm RSd-32x28x8-arm ML-FMP-40x41x41x4-arm ML-FMP-20x21x21x4-arm ML-FMP-12x13x13x4-arm ML-ALIP-70x20x1-arm MD-216-arm MD-144-arm MD-108-arm LDPC-270x32-arm FFT-1024-arm)
evaluation=(cost)
topology=(mesh)
nodes=(8x8)

for EVAL in ${evaluation[@]}
do
    for APP in ${app[@]}
    do
        for TOPO in ${topology[@]}
        do
            for NODE in ${nodes[@]}
            do
{
    # topology, column, architecture_file, configure_file, out_dir, evaluation function, pe_seq_iter, pe_cluster_iter, node_seq_iter
    DIR=${OUTDIR}/${TOPO}_${NODE}_${EVAL}/${APP}
    mkdir -p ${OUTDIR}/${TOPO}_${NODE}_${EVAL}
    mkdir -p ${DIR}
    python /home/lichang/NoC-mapping/exhausting_search_homogeneous.py \
    ${TOPO} \
    4\
    /home/lichang/NoC-mapping/benchmarks/2021_01_19/${TOPO}_${NODE}/Homogeneous_SoC_${TOPO}_${NODE}.arch \
    /home/lichang/NoC-mapping/benchmarks/2021_01_19/${TOPO}_${NODE}/${APP}.cfg \
    ${DIR} \
    reconfig_Homogeneous_SoC_${TOPO}_${NODE}_${APP}.arch \
    ${EVAL} \
    1 \
    1 \
    10000000 &> ${DIR}/log_${EVAL}
}&
            done
        done
    done
done
