#usr/bin/bash

# Backs up the Minecraft server once an hour, and deletes any backup older than 3 hours

# Notifies the server of a backup
screen -S minecraft_server -X stuff "say Hourly Backup starting. Things won't save for a moment... $(printf '\r')"
screen -S minecraft_server -X stuff "save-off $(printf '\r')"
screen -S minecraft_server -X stuff "save-all $(printf '\r')"

# Moves to the directory
cd /home/ubuntu/FTP/Minecraft_Backups/Hourly

# Remove older directory
sudo rm -f minecraft-hour3.tar.gz

# Shift existing directories
mv minecraft-hour2.tar.gz minecraft-hour3.tar.gz
mv minecraft-hour1.tar.gz minecraft-hour2.tar.gz
mv minecraft-hour0.tar.gz minecraft-hour1.tar.gz

# Creates a new backup for the most recent hour
cd /home/ubuntu/FTP/
tar -zcvf Minecraft_Backups/Hourly/minecraft-hour1.tar.gz Minecraft_Server # --exclude
# ''

# Notifies the server of Backup Completion
screen -S minecraft_server -X stuff "save-on $(printf '\r')"
screen -S minecraft_server -X stuff "say Hourly Backup complete! The world is saving again. $(printf '\r')"

exit 0
