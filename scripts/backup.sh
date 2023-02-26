#usr/bin/bash

# Backs up the Minecraft server once a day, and deletes any backup older than 2 days

# Notifies the server of a backup
sudo screen -S minecraft_server -x stuff "say Daily Backup starting. Things won't save for a moment... $(printf '\r')"
sudo screen -S minecraft_server -x stuff "save-off $(printf '\r')"
sudo screen -S minecraft_server -x stuff "save-all $(printf '\r')"

# Moves to the directory
cd /home/ubuntu/FTP/Minecraft_Backups/Daily

# Remove older directory
sudo rm -f minecraft-day2.tar.gz

# Shift existing directories
# sudo mv minecraft-day3.tar.gz minecraft-day4.tar.gz
# sudo mv minecraft-day2.tar.gz minecraft-day3.tar.gz
# sudo mv minecraft-day1.tar.gz minecraft-day2.tar.gz
sudo mv minecraft-day1.tar.gz minecraft-day2.tar.gz

# Creates a new backup for the most recent day
cd /home/ubuntu/FTP/
sudo tar -zcvf Minecraft_Backups/Daily/minecraft-day1.tar.gz Minecraft_Server # --exclude
# ''

# Notifies the server of Backup Completion
sudo screen -S minecraft_server -x stuff "save-on $(printf '\r')"
sudo screen -S minecraft_server -x stuff "say Daily Backup complete! The world is saving again. $(printf '\r')"

exit 0
