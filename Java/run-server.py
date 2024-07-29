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
import time
# from tkinter import filedialog
from typing import Literal

import logFormat
from configs import discordsrv, essentialsx, eula, properties
from scheduler import Scheduler
from pipeline import Pipeline

ACTIVE_PATH: str = ""
logger: logging.Formatter = None


class Server():
    """_summary_
    """
    process: subprocess.Popen

    def __init__(self, server_name: str = "Server", ram: int = 8, hcap: int = 6, dcap: int = 3):
        self.server_name = server_name
        self.hcap = hcap
        self.dcap = dcap
        self.backup_flag = False

        os.chdir(ACTIVE_PATH)
        logger.info('Starting server')
        self.run(ram=ram)

        logger.info("Server started.")
        self.p = Pipeline()

    def run(self, ram: int = 8):
        """ Called when the server is launched.

            Launches and attaches the server process to self.process variable.
            This is called in __init__ and must finish before any interactions with the server can
            occur.
            
        Args:
            ram (int): Amount of ram in Gigabytes to allocate for the server.
        """
        executable = ""
        for filename in os.listdir(ACTIVE_PATH):
            if filename.endswith(".jar"):
                executable = f"java -Xmx{ram * 1024}m -jar \"{filename}\" nogui"
                break

        if executable == "":
            logger.error("No Executable Jar file detected! Please add one to 'active' directory")
            sys.exit(1)

        logger.info("Running command: %s", executable)
        self.process = subprocess.Popen(executable, stdin=subprocess.PIPE)

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

    def backup(self, backup_type: Literal["Daily", "Hourly", "Manual", "Restore"]):
        """_summary_

        Returns:
            _type_: _description_
        """
        # Flags to ensure that different threads don't step on each other
        while self.backup_flag:
            time.sleep(.1)
        self.backup_flag = True

        # Temporarily Disable Autosave
        self.server_command(f"say {backup_type} backup starting. World no longer saving...")
        self.server_command("save-off")
        self.server_command("save-all")
        time.sleep(3)

        self.p.delete_old()
        self.p.backup(backup_type=backup_type)

        # Resume Autosave
        self.server_command("save-on")
        self.server_command("say Backup complete. World now saving. ")

        self.backup_flag = False
        return True

    def restore(self, zip_name: str):
        # Select zip
        
        # Validity Checks

        # return True
        logger.error("Restore functionality not implemented yet!")
        return False
        # return self.p.restore()

def launch(server_name: str = "Server", ram: int = 8):
    """ Launches the server and some parallel tasks to backup at different intervals.

    I split this off into it's own function so I can reuse it with different commands.

    Returns:
        Server: Server process/object to interface with
        Scheduler: Hourly backup timer
        Scheduler: Daily backup timer
    """
    # Launch the server
    svr = Server(server_name=server_name, ram=ram)

    # Wait for the server to be active. Until it is, it will reject any attempted messages
    c = 10
    time.sleep(5)
    while not svr.server_command("say Are you awake yet?"):
        time.sleep(1)
        c -= 1
        assert c > 0

    # Start the Backup Timers
    logger.info('Starting backup timer')
    h_tmr = Scheduler(3600, svr.backup, args=["Hourly"])
    d_tmr = Scheduler(86400, svr.backup, args=["Daily"])
    logger.info("Timers Initialized")
    h_tmr.start()
    d_tmr.start()
    logger.info('Timer started')

    return svr, h_tmr, d_tmr

def kill(svr: Server, h_tmr: Scheduler, d_tmr: Scheduler):
    """ Kills the server process and all backup timers cleanly

    I split this off into it's own function so I can reuse it with different commands

    Args:
        svr (Server): Server process
        h_tmr (Scheduler): Hourly backup process
        d_tmr (Scheduler): Daily backup process
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
    ### PATH SECTION ###
    TOP_PATH = os.path.dirname(__file__)
    DEFAULT_PATH = os.path.join(TOP_PATH, "Worlds")

    # Display Options
    print("Select World to load. If creating a new world, enter a name that doesn't exist yet.")
    ops = [x for x in os.listdir(DEFAULT_PATH) if os.path.isdir(os.path.join(DEFAULT_PATH, x))]
    for i, op in enumerate(ops):
        print(f"({i}) {op}")

    # Collect Input
    sel = input("Select option: ")
    SERVER_NAME = sel
    RAM = 8

    known = False
    if sel in ops:
        known = True

    ACTIVE_PATH = os.path.join(DEFAULT_PATH, SERVER_NAME)
    os.makedirs(ACTIVE_PATH, exist_ok=True)

    ### LOGGING SECTION ###
    logname = ACTIVE_PATH + '/' + 'MCSERVER.log'
    logFormat.format_logs(logger_name="MCLOG", file_name=logname)
    logger = logging.getLogger("MCLOG")

    # If new world, set up
    if not known:
        launcher = ""
        while launcher not in ['vanilla', 'paper', 'forge']:
            launcher = input("What launcher will this server use? (vanilla, paper, or forge): ")
        launch_dir = os.path.join(TOP_PATH, f"versions/{launcher}")

        ver_ops = [x for x in os.listdir(launch_dir) if os.path.isdir(os.path.join(launch_dir, x))]
        for i, ver in enumerate(ver_ops):
            # logger.info("%d) %s", i, ver)
            print(f"({i}) {ver}")
        version = ""
        while version not in ver_ops:
            version = input("What type of server will this be? ")
        ver_dir = os.path.join(launch_dir, version)

        # Copy server jar into active dir
        for fname in os.listdir(ver_dir):
            if fname.endswith(".jar"):
                logger.info("Moving jar '%s' to world '%s'", fname, ACTIVE_PATH)
                shutil.copyfile(os.path.join(ver_dir, fname), os.path.join(ACTIVE_PATH, fname))
                
        # If not vanilla, allow for addons
        if launcher != "vanilla":
            addon_src_dir = os.path.join(ver_dir, "addons")
            mod_ops = [x for x in os.listdir(addon_src_dir) if os.path.isfile(os.path.join(addon_src_dir, x))]
            while True:
                # Skip if no options are available
                if not mod_ops:
                    break

                # Display options and select one
                for i, mod in enumerate(mod_ops):
                    # logger.info("%d) %s", i, mod)
                    print(f"({i}) {mod}")
                try:
                    mod_num = int(input("What Plugins/Mods do you want? (Leave blank and hit 'enter' to skip): "))
                except ValueError:
                    break

                # Handle selection
                if mod_num in range(len(mod_ops)):
                    mod = mod_ops[mod_num]
                    if launcher == "forge":
                        # Move addon into server mod directory
                        addon_target_dir = os.path.join(ACTIVE_PATH, "mods")
                        # shutil.copyfile(os.path.join(addon_src_dir, mod), os.path.join(ACTIVE_PATH, "mods"))
                    elif launcher == "paper":
                        # Move addon into server mod directory
                        addon_target_dir = os.path.join(ACTIVE_PATH, "plugins")
                    os.makedirs(addon_target_dir, exist_ok=True)
                    logger.info("Moving addon '%s' to world addon directory '%s'", mod, addon_target_dir)
                    shutil.copyfile(os.path.join(addon_src_dir, mod), os.path.join(addon_target_dir, mod))
                    mod_ops.pop(mod_num)
                else:
                    logger.error("Addon not in list of options. Please select an index from the following list:")

        logger.warning("Additional Mods can be added manually later in the './mods' or './plugins' directory")

    # Pick where old backups are and new backups should go
    BACKUP_PATH = os.path.join(ACTIVE_PATH, "Backups")
    # # If you want to put the backups in a different place, say on another hard drive, uncomment this
    # BACKUP_PATH = filedialog.askdirectory(
    #                         title="Select Backup Directory",
    #                         initialdir=f"{DEFAULT_PATH}/"
    # )
    # assert BACKUP_PATH != ""
    os.makedirs(name=BACKUP_PATH, exist_ok=True)

    logger.info("World: %s", ACTIVE_PATH)
    logger.info("Backups: %s", BACKUP_PATH)
    logger.info("Logname: %s", logname)

    if not known:
        # Generate Accepted EULA
        eula(world_path=ACTIVE_PATH)

        # Start World to generate config files
        server, h_timer, d_timer = launch(server_name=SERVER_NAME, ram=RAM)
        time.sleep(5)
        kill(server, h_timer, d_timer)
        
        # Edit initial Server config
        properties(world_path=ACTIVE_PATH, server_type=launcher)
        
        if launcher == "paper":
            # Edit config files for DiscordSRV and EssentialsX.
            # TODO: check to make sure that these plugins are included.
            discordsrv(world_path=ACTIVE_PATH)
            essentialsx(world_path=ACTIVE_PATH)

    server, h_timer, d_timer = launch(server_name=SERVER_NAME, ram=RAM)

    try:
        while True:
            time.sleep(1)
            command = input("Send a manual command: /")
            if command.startswith("backup"):
                server.backup(backup_type="Manual")

            elif command.startswith("restore"):
                backup = command.split(sep=' ', maxsplit=1)[1]
                # TODO: restore from a certain backup
                server.backup("Restore")
                server.restore(backup)

            elif command.startswith("remaining"):
                logger.info("Next Daily Backup is %s from now", d_timer.get_remaining())
                logger.info("Next Hourly Backup is %s from now", h_timer.get_remaining())

            elif command.startswith("hcap"):
                # Modify the limit of hourly backups
                try:
                    HCAP = int(command.split(sep=' ')[1])
                    server.hcap = HCAP
                except ValueError:
                    logger.error("Invalid entry, enter in an integer after the command")

            elif command.startswith("dcap"):
                # Modify the limit of daily backups
                try:
                    DCAP = int(command.split(sep=' ')[1])
                    server.dcap = DCAP
                except ValueError:
                    logger.error("Invalid entry, enter in an integer after the command")

            elif command.startswith("restart"):
                kill(server, h_timer, d_timer)
                server, h_timer, d_timer = launch(server_name=SERVER_NAME, ram=RAM)

            elif command.startswith("ram"):
                # Modify the value of dedicated ram
                try:
                    RAM = int(command.split(sep=' ')[1])
                except ValueError:
                    logger.error("Invalid entry, enter in an integer after the command")

                # Restart the server
                kill(server, h_timer, d_timer)
                server, h_timer, d_timer = launch(server_name=SERVER_NAME, ram=RAM)

            elif command.startswith("help"):
                cmd_lst = [
                    ("backup", "Manually initiate a backup"),
                    ("restore", "Manually restore from a previous backup. (will restart)"),
                    ("remaining", "Get amount of time remaining before next scheduled backups."),
                    ("hcap", "Set the amount of previous hourly backups that should be kept."),
                    ("dcap", "Set the amount of previous daily backups that should be kept."),
                    ("restart", "Manually initiate a server restart. (will restart)"),
                    ("ram", "Modify amount of RAM the server runs on. Default 8. (will restart)"),
                    ("help", "Display a list of commands and notes about usage.")
                ]
                for cmd, desc in cmd_lst:
                    logger.info("- %s: %s")

            else:
                server.server_command(command)
    except KeyboardInterrupt:
        logger.info("User manually initiated shutdown using \"CTRL+C\"...")

    kill(server, h_timer, d_timer)
