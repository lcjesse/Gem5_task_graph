#!/bin/bash
DIR_NAME=`date +"%m_%d_%H"`
./build/NULL/gem5.debug  \
--outdir my_STATS/${DIR_NAME} \
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
--task-graph-file="./my_benchmarks/CMP-0906/Application_01.stp" \
--execution-iteration=2 \
--routing-algorithm=2 \
--vcs-per-vnet=2 \
--architecture-file="./my_benchmarks/CMP-0906/Heterogeneous_SoC_with_Ring_Topology.arch" \
#--ruby-clock=2GHz
#--sys-clock=2GHz
# --debug-flags=TaskGraph
