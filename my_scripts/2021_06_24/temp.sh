#!/bin/bash
#### Note! Parameters below should be changed for your simulation purpose ! ####
# OUT_FILE_DIR
# DATE (Optional)
# app iters mem_access mem_type
# the stp and arch file in my_benchmarks
# if change arch, link ulitilization part
################################################################################

GEM5=/home/lichang/Gem5_task_graph/Gem5_task_graph
DATE=`date +%Y_%m_%d`
# OUT_FILE_DIR=${GEM5}/my_STATS/11_25/multi_app
OUT_FILE_DIR=${GEM5}/my_STATS/${DATE}/test
DIR_NAME=test
mkdir -p ${OUT_FILE_DIR}/${DIR_NAME}

##### Run Test #####
${GEM5}/build/NULL/gem5.debug \
--outdir ${OUT_FILE_DIR}/${DIR_NAME}    \
${GEM5}/configs/example/garnet_synth_traffic.py  \
--num-cpus=16 \
--num-dirs=16 \
--network=garnet2.0 \
--topology=Mesh_XY \
--mesh-rows=4  \
--sim-cycles=1000000000 \
--synthetic=uniform_random \
--vcs-per-vnet=4 \
--routing-algorithm=1 \
--injectionrate=0.01    >>${OUT_FILE_DIR}/${DIR_NAME}/log 2>&1


exit 0
