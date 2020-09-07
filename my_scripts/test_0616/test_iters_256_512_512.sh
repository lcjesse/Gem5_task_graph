#!/bin/bash

for ex_iter in 1 10 20 30 40 50
do
    for((app_num=1;app_num<=5;app_num++))
    do
        app_model_file=/home/wj/Study/gem5/my_benchmarks/Application/256_512_512/Application_0${app_num}.stp
        out_filename=Application_0${app_num}_iters${ex_iter}
        ./build/NULL/gem5.debug \
        --outdir my_STATS/test_20200616/test_iters/${out_filename} \
        configs/example/garnet_synth_traffic.py \
        --topology=Ring \
        --num-cpus=16 \
        --num-dirs=16 \
        --mesh-rows=1 \
        --network=garnet2.0 \
        --inj-vnet=2 \
        --injectionrate=0 \
        --token-packet-length=6 \
        --network-task-graph-enable \
        --task-graph-file=${app_model_file} \
        --execution-iteration=${ex_iter} \
        --routing-algorithm=2 \
        --vcs-per-vnet=2 \
        --link-width-bits=256 &
        # flit size 256bits
    done
done

