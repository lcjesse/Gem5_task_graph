#!/bin/bash
./build/X86_MOESI_hammer/gem5.fast \
--outdir my_STATS/X86_MOESI_hammer__blackscholes__router-pipe-stages-1_test_10000inst/ \
configs/example/fs.py \
--work-end-exit-count=1 \
--ruby \
--restore-with-cpu timing \
--num-cpus=64 \
--num-dirs=4 \
--mem-size=1GB \
--num-l2caches=64 \
--l1d_size=32kB \
--l1i_size=32kB \
--l1d_assoc=4 \
--l1i_assoc=4 \
--l2_size=128kB \
--l2_assoc=8 \
--network=garnet2.0 \
--topology=MeshDirCorners \
--num-rows=8 \
--vcs-per-vnet=8 \
--num-pipe-stages=1 \
-I 10000
