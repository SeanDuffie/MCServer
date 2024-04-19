""" @file backup.py
    @author Sean Duffie
    @brief script to backup files on a schedule
"""
import datetime
import os
import shutil
from tkinter import filedialog

# Get the current working directory
cwd = filedialog.askdirectory(
                title="Select Directory to be zipped",
                initialdir=os.path.dirname(__file__)
            )

# Get the path to the Minecraft server world
server_world_path = os.path.join(cwd, 'world')

# Create a backup directory if it doesn't exist
backup_dir_path = os.path.join(cwd, 'backups')
if not os.path.exists(backup_dir_path):
    os.makedirs(backup_dir_path)

# Get the current date and time
date_time = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

# Create a backup file name
backup_file_name = f'minecraft_server_backup_{date_time}'

# Create a zip archive of the Minecraft server world
shutil.make_archive(os.path.join(backup_dir_path, backup_file_name), 'zip', server_world_path)

# Print a success message
print('Minecraft server backup successful!')
