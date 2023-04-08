#!/bin/bash
# set -o errexit -o nounset

# Update Paper
wget https://papermc.io/api/v1/paper/1.19.3/latest/download -O ./jars/paper-1.19.3.jar
cp ./jars/paper-1.19.3.jar ./paper.jar

# Update Plugins
