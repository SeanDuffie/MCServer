""" @file backup.py
    @author Sean Duffie
    @brief 
"""
import datetime
import logging
import os
import subprocess
import sys
import time
import threading
from tkinter import filedialog

import tarfile
import shutil
from typing import Literal

### CONSTANTS SECTION ###
RAM = 8
HCAP = 6
DCAP = 3
server_name = "Server"

### PATH SECTION ###
default_path = os.path.dirname(__file__)
server_path = default_path + "/Server/"
while server_path is None:
    server_path = filedialog.askdirectory(
                        title="Select Server Directory",
                        initialdir=f"{default_path}/"
                    )
backup_path = server_path + "/backups/"
while backup_path is None:
    backup_path = filedialog.askdirectory(
                        title="Select Backup Directory",
                        initialdir=f"{default_path}/"
                    )

for filename in os.listdir(server_path):
    if filename.endswith(".jar"):
        executable = f'java -Xmx{RAM * 1024}m -jar "{filename}"'
        break
# TODO: Is this needed?
exclude_file = "plugins/dynmap"

### LOGGING SECTION ###
logname = server_path + '/' + 'MCSERVER.log'
file_handler = logging.FileHandler(filename=logname)
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger('MCLOG')
logging.info("Logname: %s", logname)

class Server():
    """_summary_
    """
    def __init__(self, server_name: str = "Server"):
        self.server_name = server_name
        self.backup_flag = False

        os.chdir(server_path)
        logging.info('Starting server')
        self.process = subprocess.Popen(executable, stdin=subprocess.PIPE)
        logging.info("Server started.")

    def __del__(self):
        logging.warning("Deleting a Server object...")
        os.popen('TASKKILL /PID '+str(self.process.pid)+' /F')
        logging.warning("Done!")

    def server_command(self, cmd: str):
        """ Sends a string from the local python script to the server shell process

        Args:
            cmd (str): The command string to be sent to the server
        """
        logging.info("Writing server command: %s", cmd)
        self.process.stdin.write(str.encode(f"{cmd}\n")) #just write the command to the input stream
        self.process.stdin.flush()

    def backup(self, backup_type: Literal["daily", "hourly", "manual"]):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Flags to ensure that different threads don't step on each other
        while self.backup_flag:
            time.sleep(.1)
        self.backup_flag = True

        # Grab the starting time for the backup
        cur_time = datetime.datetime.now()

        # Temporarily Disable Autosave
        self.server_command("say Backup starting. World no longer saving...")
        self.server_command("save-off")
        self.server_command("save-all")
        time.sleep(3)

        # Delete Expired Backups
        logging.info('Deleting last file')
        try:
            for filename in os.listdir(server_path):
                # Extract useful info from path, first cut off directory, then cut off the filetype. Then separate info
                parsed = os.path.basename(filename).split(".", 2)[0].split("_", 3)
                s_name = parsed[0]
                prev_backup_type = parsed[1]
                tstmp = datetime.datetime.fromisoformat("%Y-%m-%dT%H-%m-%s", parsed[2])

                if prev_backup_type == "hourly" and (cur_time - tstmp) > datetime.timedelta(hours=HCAP):
                    os.remove(filename)
                elif prev_backup_type == "daily" and (cur_time - tstmp) > datetime.timedelta(days=DCAP):
                    os.remove(filename)
        except OSError as e:
            logging.error(e)
            logging.error("Error Removing Backup")

        # Make the Backup
        backup_name = f"{self.server_name}_{backup_type}_{cur_time.strftime("%Y-%m-%dT%H-%m-%s")}"
        # Create a tar archive of the Minecraft server world
        make_tarfile(f"{backup_path}/{backup_name}.tar.gz", server_path)
        # Create a zip archive of the Minecraft server world
        shutil.make_archive(os.path.join(backup_path, backup_name), 'zip', server_path)
        # Resume Autosave
        self.server_command("save-on")
        self.server_command("say Backup complete. World now saving. ")

        self.backup_flag = False
        return True


def make_tarfile(output_filename, source_dir):
    logging.info('Making tarfile')

    def filter_function(tarinfo):
        if tarinfo.name != exclude_file:
            logging.info(tarinfo.name,"ADDED")
            return tarinfo

    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir),filter=filter_function)

# def next_backuptime(last: datetime.datetime, backup_type: Literal['daily', 'hourly', 'manual']):
#     """ TODO: Add better docs

#     Returns:
#         int: seconds left before next backup
#     """
#     logging.info('Calculating next time')
#     if backup_type == "daily":
#         interval = datetime.timedelta(days=1)
#     elif backup_type == "hourly":
#         interval = datetime.timedelta(hours=1)
#     elif backup_type == "manual":
#     interval = datetime.timedelta(hours=1)
#     current = datetime.datetime.today()
#     next_time = current + interval
#     logging.info("Next backup time is %s", next_time)
#     return interval

class BackupTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
            next_time = datetime.datetime.now() + self.interval
            logging.info("Next %s Backup time is at %s", *self.args[0], next_time)

if __name__ == "__main__":
    server = Server(server_name="Server")
    time.sleep(60) # WAIT FOR IT TO START
    # TODO: Maybe check if process is alive? (EULA, crash)

    logging.info('Starting backup timer')
    h_timer = BackupTimer(360, server.backup, args=("hourly",))
    d_timer = BackupTimer(86400, server.backup, args=("daily",))
    logging.info("Timers Initialized")
    h_timer.start()
    d_timer.start()
    logging.info('Timer started')

    while True:
        command = input("Send a manual command: /")
        server.server_command(command)
    # TODO: add handling for ctrl+c
    # TODO: cleanly kill threads and process
    # TODO: add text input for commands to server
    # TODO: restructure backup style and timings
