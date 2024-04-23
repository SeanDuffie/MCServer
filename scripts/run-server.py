""" @file backup.py
    @author Sean Duffie
        - inspiration taken from xangma at https://github.com/xangma/mcbackup/blob/master/mcbackup.py
    @brief 

    https://www.minecraft.net/en-us/download/server
"""
import datetime
import logging
import os
import shutil
import signal
import subprocess
import sys
import tarfile
import threading
import time
from tkinter import filedialog
from typing import Literal

### CONSTANTS SECTION ###
RAM = 8
HCAP = 6
DCAP = 3
server_name = "Server"
RUNNING = False

### PATH SECTION ###
default_path = os.path.dirname(__file__)
server_path = f"{default_path}/{server_name}/"
while server_path is None:
    server_path = filedialog.askdirectory(
                        title="Select Server Directory",
                        initialdir=f"{default_path}/"
                    )
backup_path = server_path + "../backups/"
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

FMT_MAIN = "%(asctime)s\t| %(name)s:%(lineno)d\t| %(message)s"
logging.basicConfig(
    level=logging.DEBUG,
    format=FMT_MAIN,
    handlers=handlers
)

logger = logging.getLogger('MCLOG')
logger.info("Logname: %s", logname)

FLAG = False

def handler(signum, frame) -> None:
    """This function will handle any system interrupts that we decide to use
    It relies on the "signal" python library (see documentation below)
    https://docs.python.org/3/library/signal.html

    TODO: Add more handling so that the errors can return more information

    Args:
        signum (int): number associated with interrupt
        frame (frame): = location that the interrupt came from
        signame (str): reads the name of the interrupt to the user
    Returns:
        None
    """
    signame = signal.Signals(signum).name
    logger.error("%s\t| Signal handler called with signal %s (%d)", __name__, signame, signum)
    logger.info("%s\t| Frame = %s", __name__, frame)

    # Handles a user input Ctrl + C
    if signame == "SIGINT":
        logging.info("%s\t| User manually initiated shutdown using \"CTRL+C\"...", __name__)
        global FLAG
        FLAG = False
        h_timer.cancel()
        d_timer.cancel()

class Server():
    """_summary_
    """
    def __init__(self, server_name: str = "Server"):
        self.server_name = server_name
        self.backup_flag = False

        os.chdir(server_path)
        logger.info('Starting server')
        self.process = subprocess.Popen(executable, stdin=subprocess.PIPE)
        logger.info("Server started.")

    def __del__(self):
        logging.warning("Deleting a Server object...")
        # self.server_command("stop")
        # time.sleep(10)
        logging.warning("Cancelling Process...")
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
            for filename in os.listdir(server_path):
                # Extract useful info from path, first cut off directory, then cut off the filetype. Then separate info
                parsed = os.path.basename(filename).split(".", 2)[0].split("_", 3)
                logging.warning("Parsed: ")
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
        make_tarfile(f"{backup_path}/{backup_name}.tar.gz", server_path)
        # Create a zip archive of the Minecraft server world
        shutil.make_archive(os.path.join(backup_path, backup_name), 'zip', server_path)
        shutil.unpack_archive()
        # Resume Autosave
        self.server_command("save-on")
        self.server_command("say Backup complete. World now saving. ")

        self.backup_flag = False
        return True


def make_tarfile(output_filename, source_dir):
    logger.info('Making tarfile')

    def filter_function(tarinfo):
        if tarinfo.name != exclude_file:
            logger.info(tarinfo.name,"ADDED")
            return tarinfo

    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir),filter=filter_function)

# def next_backuptime(last: datetime.datetime, backup_type: Literal['Daily', 'Hourly', 'Manual']):
#     """ TODO: Add better docs

#     Returns:
#         int: seconds left before next backup
#     """
#     logger.info('Calculating next time')
#     if backup_type == "Daily":
#         interval = datetime.timedelta(days=1)
#     elif backup_type == "Hourly":
#         interval = datetime.timedelta(hours=1)
#     elif backup_type == "Manual":
#     interval = datetime.timedelta(hours=1)
#     current = datetime.datetime.today()
#     next_time = current + interval
#     logger.info("Next backup time is %s", next_time)
#     return interval

class BackupTimer(threading.Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)
            next_time = datetime.datetime.now() + self.interval
            logger.info("Next %s Backup time is at %s", *self.args[0], next_time)

if __name__ == "__main__":
    # Initialize Listener (for CTRL+C interrupts)
    signal.signal(signal.SIGINT, handler)

    server = Server(server_name="Server")
    time.sleep(45) # WAIT FOR IT TO START
    FLAG = True
    # TODO: Maybe check if process is alive? (EULA, crash)

    logger.info('Starting backup timer')
    h_timer = BackupTimer(360, server.backup, args=("Hourly",))
    d_timer = BackupTimer(86400, server.backup, args=("Daily",))
    logger.info("Timers Initialized")
    h_timer.start()
    d_timer.start()
    logging.info('Timer started')

    # Initialize Listener (for CTRL+C interrupts)
    signal.signal(signal.SIGINT, handler)

    while FLAG:
        command = input("Send a manual command: /")
        if command == "restore":
            pass
        if command == "backup":
            server.backup(backup_type="Manual")
        else:
            server.server_command(command)
    logging.info("Exiting the loop!")
    h_timer.cancel()
    d_timer.cancel()
    logging.info("Finished!")
