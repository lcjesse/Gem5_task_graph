#!/bin/bash
./build/Garnet_standalone_512cores/gem5.debug configs/example/garnet_synth_traffic.py  \
        --num-cpus=256 \
        --num-dirs=256 \
        --network=garnet2.0 \
        --topology=Mesh_XY \
        --mesh-rows=16  \
        --sim-cycles=1000 \
        --synthetic=uniform_random \
        --injectionrate=0.01 \
	--vcs-per-vnet=2 \
	--inj-vnet=2 \
	--sim-cycles=10000
