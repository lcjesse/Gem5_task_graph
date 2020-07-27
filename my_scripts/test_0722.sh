#!/bin/bash
./build/NULL/gem5.debug --debug-flags=TaskGraph \
--outdir hh \
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
--task-graph-file="./my_benchmarks/test.stp" \
--execution-iteration=10 \
--routing-algorithm=2 \
--vcs-per-vnet=2 \
--architecture-file=Heterogeneous_SoC_with_Ring_Topology.arch
