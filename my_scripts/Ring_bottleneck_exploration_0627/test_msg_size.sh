#!/bin/bash
msg_size=(
    256_512_512
    256_1600_512
    256_5120_512
    256_12288_512
    512_12288_512
    5120_122880_5120
    10240_245670_10240
    15360_368640_15360
    20480_491520_20480
    25600_614400_25600
    )
ex_iter=50
for((i=7;i<=9;i++))
#for i in 5
do
    for((app_num=1;app_num<=5;app_num++))
    do
        app_model_file=/home/wj/Study/gem5/my_benchmarks/Application/${msg_size[i]}/Application_0${app_num}.stp
        out_filename=Application_0${app_num}_iters${ex_iter}_msg_${msg_size[i]}
        ./build/Garnet_standalone_512cores/gem5.debug \
        --outdir my_STATS/Ring_bottleneck_exploration_0627/Application_with_different_msg_size/${out_filename} \
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

