""" @file backup.py
    @author Sean Duffie
        - inspiration taken from xangma: https://github.com/xangma/mcbackup/blob/master/mcbackup.py
    @brief 

    TODO: Separate Backup script into separate file for simplicity and reusability

    https://www.minecraft.net/en-us/download/server
"""
import datetime
import logging
import os
import shutil
import subprocess
import tarfile
import threading
import time
from tkinter import filedialog
from typing import Literal
import logFormat

### CONSTANTS SECTION ###
RAM = 8
HCAP = 6
DCAP = 3
SERVER_NAME = "Server"
RUNNING = False

### PATH SECTION ###
DEFAULT_PATH = os.path.dirname(__file__)
SERVER_PATH = None
# SERVER_PATH = f"{DEFAULT_PATH}/{SERVER_NAME}/"

while SERVER_PATH is None:
    SERVER_PATH = filedialog.askdirectory(
                        title="Select Server Directory",
                        initialdir=f"{DEFAULT_PATH}/"
                    )
if SERVER_PATH == "":
    exit()
# BACKUP_PATH = None
BACKUP_PATH = f"{SERVER_PATH}/../backups/{SERVER_NAME}"
os.makedirs(name=BACKUP_PATH, exist_ok=True)
# while BACKUP_PATH is None:
#     BACKUP_PATH = filedialog.askdirectory(
#                         title="Select Backup Directory",
#                         initialdir=f"{DEFAULT_PATH}/"
#                     )

for filename in os.listdir(SERVER_PATH):
    if filename.endswith(".jar"):
        executable = f'java -Xmx{RAM * 1024}m -jar "{filename}"'
        break
# TODO: Is this needed?
exclude_file = "plugins/dynmap"

### LOGGING SECTION ###
logname = SERVER_PATH + '/' + 'MCSERVER.log'
logFormat.format_logs(logger_name="MCLOG", file_name=logname)
logger = logging.getLogger("MCLOG")
logger.info("Logname: %s", logname)


class Server():
    """_summary_
    """
    def __init__(self, server_name: str = "Server"):
        self.server_name = server_name
        self.backup_flag = False

        os.chdir(SERVER_PATH)
        logger.info('Starting server')
        self.process = subprocess.Popen(executable, stdin=subprocess.PIPE)
        logger.info("Server started.")

    def server_command(self, cmd: str):
        """ Sends a string from the local python script to the server shell process

        Args:
            cmd (str): The command string to be sent to the server
        """
        logger.info("Writing server command: %s", cmd)
        try:
            self.process.stdin.write(str.encode(f"{cmd}\n")) #just write the command to the input stream
            self.process.stdin.flush()
        except OSError as e:
            logger.error(e)
            logger.error("Error Writing to Server")

    def backup(self, backup_type: Literal["Daily", "Hourly", "Manual"]):
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
        self.server_command(f"say {backup_type} backup starting. World no longer saving...")
        self.server_command("save-off")
        self.server_command("save-all")
        time.sleep(3)

        # Delete Expired Backups
        logger.info('Deleting last file')
        try:
            for filename in os.listdir(SERVER_PATH):
                # Extract useful info from path, first cut off directory, then cut off the filetype. Then separate info
                parsed = os.path.basename(filename).split(".", 2)[0].split("_", 3)
                logger.warning("Parsed: ")
                print(parsed)
                s_name = parsed[0]
                prev_backup_type = parsed[1]
                tstmp = datetime.datetime.fromisoformat("%Y-%m-%d-%H-%M-%s", parsed[2])

                if prev_backup_type == "Hourly" and (cur_time - tstmp) > datetime.timedelta(hours=HCAP):
                    os.remove(filename)
                elif prev_backup_type == "Daily" and (cur_time - tstmp) > datetime.timedelta(days=DCAP):
                    os.remove(filename)
        except OSError as e:
            logger.error(e)
            logger.error("Error Removing Backup")

        # Make the Backup
        tstmp2 =cur_time.strftime("%Y-%m-%d-%H-%M-%S")
        backup_name = f"{self.server_name}_{backup_type}_{tstmp2}"
        # Create a tar archive of the Minecraft server world
        make_tarfile(f"{BACKUP_PATH}/{backup_name}.tar.gz", SERVER_PATH)
        # Create a zip archive of the Minecraft server world
        shutil.make_archive(os.path.join(BACKUP_PATH, backup_name), 'zip', SERVER_PATH)
        # Resume Autosave
        self.server_command("save-on")
        self.server_command("say Backup complete. World now saving. ")

        self.backup_flag = False
        return True

    def restore_backup(self, name: str):
        # shutil.unpack_archive()
        pass


def make_tarfile(output_filename, source_dir):
    logger.info('Making tarfile')

    def filter_function(tarinfo):
        if tarinfo.name != exclude_file:
            logger.info(tarinfo.name,"ADDED")
            return tarinfo

    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir),filter=filter_function)


class BackupTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
            next_time = datetime.datetime.now() + self.interval
            logger.info("Next %s Backup time is at %s", *self.args[0], next_time)


if __name__ == "__main__":
    server = Server(server_name=SERVER_NAME)
    time.sleep(45) # WAIT FOR IT TO START
    # TODO: Maybe check if process is alive? (EULA, crash)

    logger.info('Starting backup timer')
    h_timer = BackupTimer(360, server.backup, args=("Hourly",))
    d_timer = BackupTimer(86400, server.backup, args=("Daily",))
    logger.info("Timers Initialized")
    h_timer.start()
    d_timer.start()
    logger.info('Timer started')

    try:
        while True:
            command = input("Send a manual command: /")
            if command == "restore":
                pass
            if command == "backup":
                server.backup(backup_type="Manual")
            else:
                server.server_command(command)
    except KeyboardInterrupt:
        logger.info("User manually initiated shutdown using \"CTRL+C\"...")

    logger.info("Killing Timers...")
    h_timer.cancel()
    d_timer.cancel()
    logger.info("Timers Killed!")

    logger.warning("Stopping Server...")
    server.server_command("stop")
    time.sleep(10)
    logger.info("Server Stopped!")
    time.sleep(10)

    logger.warning("Killing Server Process...")
    server.process.kill()
    logger.warning("Done!")
