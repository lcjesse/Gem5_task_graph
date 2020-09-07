#!/bin/bash
msg_size=(
    256_512_512
    256_1600_512
    256_5120_512
    256_12288_512
    512_12288_512
    )
ex_iter=50
for((i=0;i<=4;i++))
do
    for((app_num=1;app_num<=5;app_num++))
    do
        app_model_file=/home/wj/Study/gem5/my_benchmarks/Application/${msg_size[i]}/Application_0${app_num}.stp
        out_filename=Application_0${app_num}_iters${ex_iter}_msg_${msg_size[i]}
        ./build/NULL/gem5.debug \
        --outdir my_STATS/test_20200616/test_msg_size/${out_filename} \
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

