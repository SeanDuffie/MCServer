#usr/bin/bash
while :
do
	#set -e
	echo [$(date +"%T")] "Running World Script..."
	java -Xms2500M -Xmx6000M -jar ./paper.jar nogui
	echo [$(date +"%T")] "Restarting World!"
done
