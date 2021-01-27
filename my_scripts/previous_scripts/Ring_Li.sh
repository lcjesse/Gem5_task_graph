#!/bin/bash
./build/NULL/gem5.debug configs/example/garnet_synth_traffic.py \
--num-cpus=8 \
--num-dirs=8 \
--network=garnet2.0 \
--topology=Ring \
--mesh-rows=1 \
--routing-algorithm=2 \
--vcs-per-vnet=2 \
--sim-cycles=10000 \
--synthetic=uniform_random \
--injectionrate=0.01
