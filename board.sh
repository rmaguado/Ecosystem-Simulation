#!/bin/bash
<<<<<<< HEAD
echo "open http://z97mx.local:6006/"
tensorboard --logdir=~/Ecosystem-Simulation/runs/ > board.log 2>&1 &
=======
if [ -d runs ]; then
    tensorboard --logdir=runs/ > /dev/null 2>&1 &
    echo "Board starting reload browser ..."
    open http://localhost:6006/ &
else
    echo "Folder runs not found"
fi

>>>>>>> e0708a54351116944028e572bdf0d7d428f0e6e9
