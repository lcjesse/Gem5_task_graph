#!/bin/bash
INJECTION_RATE=0.01
SIM_CYCLES=1000000

for num_cpus in 16 64 128 256 512
do
    OUT_FILENAME=Ring_Uniform_${num_cpus}_InjectionRate_${INJECTION_RATE}_SimCycles_${SIM_CYCLES}
        ./build/NULL/gem5.debug \
        --outdir my_STATS/Ring_bottleneck_exploration_0622/test_num_cpus/${OUT_FILENAME} \
        configs/example/garnet_synth_traffic.py \
        --topology=Ring \
        --num-cpus=${num_cpus} \
        --num-dirs=${num_cpus} \
        --mesh-rows=1 \
        --network=garnet2.0 \
        --inj-vnet=2 \
        --injectionrate=${INJECTION_RATE} \
        --routing-algorithm=2 \
        --vcs-per-vnet=2 \
        --link-width-bits=256 \
        --synthetic=uniform_random \
        --sim-cycles=${SIM_CYCLES} &
done
