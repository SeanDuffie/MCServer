#!/bin/bash
# set -o errexit -o nounset
ver="1.19.3"

# Update Paper
wget https://papermc.io/api/v1/paper/${ver}/latest/download -O jars/paper-${ver}.jar
cp jars/paper-1.19.3.jar paper.jar

# Update Plugins
