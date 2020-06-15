#!/bin/bash
./build/NULL/gem5.debug configs/example/garnet_synth_traffic.py \
--topology=Mesh_XY \
--num-cpus=64 \
--num-dirs=64 \
--mesh-rows=8 \
--network=garnet2.0 \
--inj-vnet=2 \
--injectionrate=0 \
--token-packet-length=6 \
--network-task-graph-enable \
--task-graph-file="./my_benchmarks/app_model_1.stp" \
--execution-iteration=1
