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
import sys
# import tarfile
import threading
import time
# from tkinter import filedialog
from typing import Literal

import logFormat

### CONSTANTS SECTION ###
# TODO: Make this into an external config file that gets loaded in on startup, and updated on swap
settings = {
    "RAM": 8,
    "HCAP": 6,
    "DCAP": 3,
    "SERVER_NAME": "Server",
    "RUNNING": False,
}

### PATH SECTION ###
DEFAULT_PATH = os.path.dirname(__file__)
ACTIVE_PATH = f"{DEFAULT_PATH}/active/"
BACKUP_PATH = f"{DEFAULT_PATH}/Worlds/{settings['SERVER_NAME']}/"
# # If you want to put the backups in a different place, say on another hard drive, uncomment this
# BACKUP_PATH = None
# while BACKUP_PATH is None:
#     BACKUP_PATH = filedialog.askdirectory(
#                         title="Select Backup Directory",
#                         initialdir=f"{DEFAULT_PATH}/"
#                     )
os.makedirs(name=BACKUP_PATH, exist_ok=True)

### LOGGING SECTION ###
logname = ACTIVE_PATH + '/' + 'MCSERVER.log'
logFormat.format_logs(logger_name="MCLOG", file_name=logname)
logger = logging.getLogger("MCLOG")
logger.info("Logname: %s", logname)


class Server():
    """_summary_
    """
    process: subprocess.Popen

    def __init__(self, server_name: str = "Server"):
        self.server_name = server_name
        self.backup_flag = False

        os.chdir(ACTIVE_PATH)
        logger.info('Starting server')

        self.executable = ""
        for filename in os.listdir(ACTIVE_PATH):
            if filename.endswith(".jar"):
                self.executable = f'java -Xmx{settings['RAM'] * 1024}m -jar "{filename}" nogui'
                break

        if self.executable == "":
            logger.error("No Executable Jar file detected! Please add one to 'active' directory")
            sys.exit(1)

        self.run()

        logger.info("Server started.")

    def run(self):
        logger.info("Running command: %s", self.executable)
        self.process = subprocess.Popen(self.executable, stdin=subprocess.PIPE)

    def server_command(self, cmd: str):
        """ Sends a string from the local python script to the server shell process

        Args:
            cmd (str): The command string to be sent to the server
        """
        logger.info("Writing server command: %s", cmd)
        try:
            self.process.stdin.write(str.encode(f"{cmd}\n")) #just write the command to the input stream
            self.process.stdin.flush()
            return True
        except OSError:
            logger.error("Error Writing to Server. Is it inactive?")
            return False

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
            hourly = []
            daily = []

            for filename in os.listdir(BACKUP_PATH):
                if filename != "":
                    # Extract useful info from path, first cut off directory, then cut off the filetype. Then separate info
                    parsed = os.path.basename(filename).split(".", 2)[0].split("_", 3)
                    s_name = parsed[0]
                    tstmp = datetime.datetime.strptime(parsed[1], "%Y-%m-%d-%H-%M-%S")
                    prev_backup_type = parsed[2]

                    if prev_backup_type == "Hourly": #  and (cur_time - tstmp) > datetime.timedelta(hours=settings['HCAP']):
                        hourly.append(filename)
                    elif prev_backup_type == "Daily": # and (cur_time - tstmp) > datetime.timedelta(days=settings['DCAP']):
                        daily.append(filename)
                        # os.remove(filename)

            # TODO: Keep track of update history in a JSON
            while len(hourly) > settings['HCAP']:
                os.remove(os.path.join(BACKUP_PATH, hourly.pop(0)))
                # logger.debug(hourly)
            if len(daily) > settings['DCAP']:
                os.remove(os.path.join(BACKUP_PATH, daily.pop(0)))
                # logger.debug(daily)
        except OSError as e:
            logger.error(e)
            logger.error("Error Removing Backup")

        # Make the Backup
        tstmp2 =cur_time.strftime("%Y-%m-%d-%H-%M-%S")
        backup_name = f"{self.server_name}_{tstmp2}_{backup_type}"

        try:
            # Create a zip archive of the Minecraft server world
            shutil.make_archive(
                base_name=os.path.join(BACKUP_PATH, backup_name),
                format='zip',
                root_dir=ACTIVE_PATH,
                # logger=logger
            )
        except PermissionError:
            # import traceback
            # logger.error(traceback.format_exc())
            # logger.error("Permission Error!")
            pass

        # Resume Autosave
        self.server_command("save-on")
        self.server_command("say Backup complete. World now saving. ")

        self.backup_flag = False
        return True

    def restore_backup(self, name: str):
        # shutil.unpack_archive()
        pass


# def make_tarfile(output_filename, source_dir):
#     logger.info('Making tarfile')
#     # TODO: Is this needed?
#     exclude_file = "plugins/dynmap"

#     def filter_function(tarinfo):
#         if tarinfo.name != exclude_file:
#             logger.info(tarinfo.name,"ADDED")
#             return tarinfo

#     with tarfile.open(output_filename, "w:gz") as tar:
#         tar.add(source_dir, arcname=os.path.basename(source_dir),filter=filter_function)


class BackupTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
            now = datetime.datetime.now()
            interval = datetime.timedelta(seconds=self.interval)
            next_time = now + interval
            logger.info("Next %s Backup time is at %s", *self.args, next_time)


if __name__ == "__main__":
    server = Server(server_name=settings['SERVER_NAME'])
    time.sleep(5)
    while not server.server_command("say Are you awake yet?"):
        time.sleep(1)

    logger.info('Starting backup timer')
    h_timer = BackupTimer(3600, server.backup, args=["Hourly"])
    d_timer = BackupTimer(86400, server.backup, args=["Daily"])
    logger.info("Timers Initialized")
    h_timer.start()
    d_timer.start()
    logger.info('Timer started')

    try:
        while True:
            command = input("Send a manual command: /")
            if command.startswith("restore"):
                # TODO: restore from a certain backup
                pass
            elif command.startswith("backup"):
                server.backup(backup_type="Manual")
            elif command.startswith("swap"):
                # TODO: Take arguement for new server name
                pass
            elif command.startswith("hcap"):
                # TODO: Modify the limit of hourly backups
                pass
            elif command.startswith("dcap"):
                # TODO: Modify the limit of daily backups
                pass
            elif command.startswith("ram"):
                # TODO: Modify the value of dedicated ram
                # TODO: Restart the server
                server.server_command("restart")
                pass
            elif command.startswith("new"):
                # TODO: Backup the most recent server
                server.backup(backup_type="Manual")
                # TODO: Get a new name
                # TODO: Get a new jar type
                # TODO: If modded, load up a list of mods
                pass
            else:
                server.server_command(command)
    except KeyboardInterrupt:
        logger.info("User manually initiated shutdown using \"CTRL+C\"...")

    logger.warning("Killing Timers...")
    h_timer.cancel()
    d_timer.cancel()
    logger.info("Timers Killed!")

    logger.warning("Stopping Server...")
    server.server_command("stop")
    while server.server_command("say Go to sleep."):
        time.sleep(1)
    logger.info("Server Stopped!")

    logger.warning("Killing Server Process...")
    server.process.kill()
    logger.warning("Done!")
