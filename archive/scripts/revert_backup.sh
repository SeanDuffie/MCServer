#usr/bin/env bash

# This program will take inputs from the user to decide which backup to restore

# User Input
op=-1
ver=-1

while [[ "$op" -ne 0 && "$op" -ne 1 ]]
do
	read -p "Hourly[old] (0) or Daily (1)?: " op
done

while [[ "$ver" -lt 0 || "$ver" -gt 2 ]]
do
	read -p "Enter the number of the backup (0-2): " ver
done


# Default backup Prep
cd /home/ubuntu/FTP
screen -S minecraft_server -X stuff "say The server will stop to revert to a backup in 10 seconds... $(printf '\r')"
sleep 7
screen -S minecraft_server -X stuff "say Reverting to backup in 3... $(printf '\r')"
sleep 1
screen -S minecraft_server -X stuff "say 2... $(printf '\r')"
sleep 1
screen -S minecraft_server -X stuff "say 1... $(printf '\r')"
sleep 1
screen -S minecraft_server -X stuff "stop $(printf '\r')"
sleep 3
screen -X -S minecraft_server quit

rm -r /home/ubuntu/FTP/Minecraft_Backups/Depricated_Server
cp -r /home/ubuntu/FTP/Minecraft_Server /home/ubuntu/FTP/Minecraft_Backups/Depricated_Server


# Replace with Hourly backup if selected
if [ "$op" == 0 ]
then
	echo "Replacing the current server with the $ver hour backup..."
	tar -xvf "/home/ubuntu/FTP/Minecraft_Backups/Hourly/minecraft-hour${ver}.tar.gz" /home/ubuntu/FTP/Minecraft_Server
	echo "/home/ubuntu/FTP/Minecraft_Backups/Hourly/minecraft-hour${ver}.tar.gz"
fi


# Replace with Daily backup if selected
if [ "$op" == 1 ]
then
	echo "Replacing the current server with the $ver day backup..."
	tar -xvf "/home/ubuntu/FTP/Minecraft_Backups/Daily/minecraft-day${ver}.tar.gz" /home/ubuntu/FTP/Minecraft_Server
	echo "/home/ubuntu/FTP/Minecraft_Backups/Daily/minecraft-day${ver}.tar.gz"
fi


# Start the server up again
screen -dm -S minecraft_server bash /home/ubuntu/FTP/scripts/paper_server.sh
