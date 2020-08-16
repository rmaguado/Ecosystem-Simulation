#!/bin/bash
echo "open http://z97mx.local:6006/"
tensorboard --logdir=~/Ecosystem-Simulation/runs/ > board.log 2>&1 &