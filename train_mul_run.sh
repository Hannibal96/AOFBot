#!/bin/bash

for t in value dealer blinds action suit
do
        nohup python CNN_train.py -t ${t} &
done
