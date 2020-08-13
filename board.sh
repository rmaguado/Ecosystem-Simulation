#!/bin/bash
if [ -d runs ]; then
    tensorboard --logdir=runs/ > /dev/null 2>&1 &
    echo "Board starting reload browser ..."
    open http://localhost:6006/ &
else
    echo "Folder runs not found"
fi

