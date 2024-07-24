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
import threading
import time
from tkinter import filedialog
from typing import Literal

import logFormat


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
                self.executable = f"java -Xmx{settings['RAM'] * 1024}m -jar \"{filename}\" nogui"
                break

        if self.executable == "":
            logger.error("No Executable Jar file detected! Please add one to 'active' directory")
            sys.exit(1)

        self.run()

        logger.info("Server started.")

    def run(self):
        """ Called when the server is launched.

            Launches and attaches the server process to self.process variable.
            This is called in __init__ and must finish before any interactions with the server can
            occur.
        """
        logger.info("Running command: %s", self.executable)
        self.process = subprocess.Popen(self.executable, stdin=subprocess.PIPE)

    def server_command(self, cmd: str):
        """ Sends a string from the local python script to the server shell process

        Args:
            cmd (str): The command string to be sent to the server
        """
        logger.info("Writing server command: %s", cmd)
        try:
            # Write command to the input stream
            self.process.stdin.write(str.encode(f"{cmd}\n"))
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


class BackupTimer(threading.Timer):
    def __init__(self, interval, function, args=None, kwargs=None):
        threading.Timer.__init__(self, interval, function, args, kwargs)

        self.start_time = datetime.datetime.now()
        self.tprev = self.start_time
        self.invl = datetime.timedelta(seconds=self.interval)
        self.tnext = self.next_time(self.start_time, self.invl)

        logger.warning("Seconds until First %s Backup: %s", *self.args, (self.tnext - self.tprev).total_seconds())

    def next_time(self, prev: datetime.datetime, interval: datetime.timedelta):
        if interval > datetime.timedelta(seconds=86399):
            # If the program is started in the morning between 12AM and 6AM, round next time down
            if prev.hour < 6:
                day = prev.day
            # Otherwise, round next time up
            else:
                day = prev.day + interval.days

            # Always back up at the next 6AM occurrence.
            nxt = datetime.datetime(
                year=prev.year,
                month=prev.month,
                day=day,
                hour=6,
                minute=0,
                second=0,
                microsecond=0
            )
        else:
            # Always back up at the top of the next hour
            nxt = datetime.datetime(
                year=prev.year,
                month=prev.month,
                day=prev.day + interval.days,
                hour=(prev.hour + (interval.seconds // 3600)) % 24,
                minute=0,
                second=0,
                microsecond=0
            )
        logger.info("Next %s Backup time is at %s (currently %s)", *self.args, nxt, datetime.datetime.now())
        return nxt

    def get_remaining(self):
        return self.tnext - self.tprev

    def run(self):
        while not self.finished.wait((self.tnext - self.tprev).total_seconds()):
            self.tprev = self.tnext
            self.tnext = self.next_time(self.tprev, self.invl)

            self.function(*self.args, **self.kwargs)
        logger.info("BackupTimer finished.")

def launch():
    """ Launches the server and some parallel tasks to backup at different intervals.

    I split this off into it's own function so I can reuse it with different commands.

    Returns:
        Server: Server process/object to interface with
        BackupTimer: Hourly backup timer
        BackupTimer: Daily backup timer
    """
    # Launch the server
    svr = Server(server_name=settings['SERVER_NAME'])

    # Wait for the server to be active. Until it is, it will reject any attempted messages
    c = 10
    time.sleep(5)
    while not svr.server_command("say Are you awake yet?"):
        time.sleep(1)
        c -= 1
        assert c > 0

    # Start the Backup Timers
    logger.info('Starting backup timer')
    h_tmr = BackupTimer(3600, svr.backup, args=["Hourly"])
    d_tmr = BackupTimer(86400, svr.backup, args=["Daily"])
    logger.info("Timers Initialized")
    h_tmr.start()
    d_tmr.start()
    logger.info('Timer started')

    return svr, h_tmr, d_tmr

def kill(svr: Server, h_tmr: BackupTimer, d_tmr: BackupTimer):
    """ Kills the server process and all backup timers cleanly

    I split this off into it's own function so I can reuse it with different commands

    Args:
        svr (Server): Server process
        h_tmr (BackupTimer): Hourly backup process
        d_tmr (BackupTimer): Daily backup process
    """
    logger.warning("Killing Timers...")
    h_tmr.cancel()
    d_tmr.cancel()
    logger.info("Timers Killed!")

    logger.warning("Stopping Server...")
    svr.server_command("stop")
    while svr.server_command("say Go to sleep."):
        time.sleep(1)
    logger.info("Server Stopped!")

    logger.warning("Killing Server Process...")
    svr.process.kill()
    logger.warning("Done!")

if __name__ == "__main__":
    ### CONSTANTS SECTION ###
    # TODO: Make this into an external config file that gets loaded in on startup, and updated on swap
    settings = {
        "RAM": 8,
        "HCAP": 6,
        "DCAP": 3,
    }

    ### PATH SECTION ###
    TOP_PATH = os.path.dirname(__file__)
    DEFAULT_PATH = os.path.join(TOP_PATH, "Worlds")

    # Display Options
    print("Select World to load. If creating a new world, enter a name that doesn't exist yet.")
    ops = [x for x in os.listdir(DEFAULT_PATH) if os.path.isdir(os.path.join(DEFAULT_PATH, x))]
    for i, op in enumerate(ops):
        print(f"{i+1}) {op}")
    # print("0) New World\n")
    
    # Collect Input
    sel = input("Select option: ")
    SERVER_NAME = sel
    
    known = False
    if sel in ops:
        known = True

    ACTIVE_PATH = os.path.join(DEFAULT_PATH, SERVER_NAME)

    # If new world, set up
    if not known:
        launcher = ""
        while launcher not in ['vanilla', 'paper', 'forge']:
            launcher = input("What launcher will this server use? (vanilla, paper, or forge): ")
        launch_dir = os.path.join(TOP_PATH, f"versions/{launcher}")
        launch_ops = [x for x in os.listdir(launch_dir) if os.path.isdir(os.path.join(launch_dir, x))]
        version = input("What type of server will this be? ")

        # TODO: Copy server jar into active dir

        addons = []
        if type != "vanilla":
            mod = "temp"
            while mod != "":
                mod = input("What Plugins/Mods do you want?")
                addons.append(mod)
            
            mod_dir = os.path.join(launch_dir, "addons")
            # for addon in addons:
            #     if addon in [x for x in os.listdir(mod_dir) if os.path.isdir(os.path.join(mod_dir, x))]
        print("Additional Mods can be added manually later in the './mods' or './plugins' directory")

    # Pick where old backups are and new backups should go
    BACKUP_PATH = os.path.join(ACTIVE_PATH, "Backups")
    # # If you want to put the backups in a different place, say on another hard drive, uncomment this
    # BACKUP_PATH = filedialog.askdirectory(
    #                         title="Select Backup Directory",
    #                         initialdir=f"{DEFAULT_PATH}/"
    # )
    # assert BACKUP_PATH != ""
    os.makedirs(name=BACKUP_PATH, exist_ok=True)

    ### LOGGING SECTION ###
    logname = ACTIVE_PATH + '/' + 'MCSERVER.log'
    logFormat.format_logs(logger_name="MCLOG", file_name=logname)
    logger = logging.getLogger("MCLOG")
    logger.info("World: %s", ACTIVE_PATH)
    logger.info("Backups: %s", BACKUP_PATH)
    logger.info("Logname: %s", logname)
    
    # Startup
    # Select Files
    
    sys.exit()

    server, h_timer, d_timer = launch()

    try:
        while True:
            time.sleep(1)
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
            elif command.startswith("restart"):
                kill(server, h_timer, d_timer)
                server, h_timer, d_timer = launch()
            elif command.startswith("ram"):
                # TODO: Modify the value of dedicated ram
                # Restart the server
                kill(server, h_timer, d_timer)
                server, h_timer, d_timer = launch()
            elif command.startswith("new"):
                # TODO: Backup the most recent server
                server.backup(backup_type="Manual")
                # TODO: Get a new name
                # TODO: Get a new jar type
                # TODO: If modded, load up a list of mods
            elif command.startswith("get"):
                parsed = command.split(" ")
                print(parsed)
                if parsed[1] == "dtime":
                    logger.info("Next Daily Backup is %s from now", d_timer.get_remaining())
                elif parsed[1] == "htime":
                    logger.info("Next Hourly Backup is %s from now", h_timer.get_remaining())
            else:
                server.server_command(command)
    except KeyboardInterrupt:
        logger.info("User manually initiated shutdown using \"CTRL+C\"...")

    kill(server, h_timer, d_timer)
