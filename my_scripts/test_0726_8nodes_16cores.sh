#!/bin/bash
./build/NULL/gem5.debug --debug-flags=TaskGraph \
--outdir hh \
configs/example/garnet_synth_traffic.py \
--topology=Ring \
--num-cpus=8 \
--num-dirs=8 \
--mesh-rows=1 \
--network=garnet2.0 \
--inj-vnet=2 \
--injectionrate=0 \
--token-packet-length=6 \
--network-task-graph-enable \
--task-graph-file="./my_benchmarks/CMP-0726/h263e_mesh_4x4_1.stp" \
--execution-iteration=2 \
--routing-algorithm=2 \
--vcs-per-vnet=2 \
--architecture-file="./my_benchmarks/CMP-0726/Heterogeneous_SoC_with_Ring_Topology_16.arch"
# --debug-flags=TaskGraph
