""" @file backup.py
    @author Sean Duffie
        - inspiration taken from xangma: https://github.com/xangma/mcbackup/blob/master/mcbackup.py
    @brief 

    TODO: Separate Backup script into separate file for simplicity and reusability

    https://www.minecraft.net/en-us/download/server
"""
import logging
import os
import shutil
import time

import log_format
from configs import discordsrv, essentialsx, eula, properties
from scheduler import Scheduler
from server import Server

### PATH SECTION ###
TOP_PATH = os.path.dirname(__file__)
DEFAULT_PATH: str = os.path.join(TOP_PATH, "Worlds")
ACTIVE_PATH: str = ""
BACKUP_PATH: str = ""
log_format.format_logs(logger_name="MCServer")
logger: logging.Formatter = logging.getLogger("MCServer")


def validate_input(ops):
    """ Capture input from user to select current server

    Args:
        ops (list[str]): list of existing world/server options.

    Returns:
        server_name (str): Name of the server that is being launched.
        ram (int): Gigabytes of ram to allocate to the server.
        known (bool): Should new folders/files be generated or use existing ones?
    """
    server_name = ""
    ram = 8
    known = True

    while True:
        try:
            sel = int(input("Select Server Index: "))

            assert isinstance(sel, int)
            assert sel >= 0
            assert sel < len(ops)

            if sel == 0:
                known = False
                while True:
                    try:
                        server_name = input("Enter New Server Name: ")
                        assert server_name is not None
                        assert server_name != "_"
                        assert not any((c in server_name) for c in "\`/<>\:\"\\|?*")
                        break
                    except AssertionError as e:
                        logger.error(e)
                        logger.error("Bad Server Name.")
                # TODO: Prompt for new stored RAM value.
            else:
                server_name = ops[sel]
                # TODO: Retrieve stored RAM value.
            break
        except AssertionError as e:
            logger.error(e)
            logger.error("Bad Server Index.")
    return server_name, ram, known

def select_world():
    """ Prompts the user to choose which world they want to load.

    Returns:
        str: The name of the world to load.
        int: Amount of ram to dedicate, in GigaBytes.
        bool: Does the world already exist or should a new one be created?
    """
    # Display Options
    print("Select World to load. If creating a new world, enter a name that doesn't exist yet.")
    ops = [x for x in os.listdir(DEFAULT_PATH) if (os.path.isdir(os.path.join(DEFAULT_PATH, x)) and x != "Backups")]
    ops.insert(0, "[New Server]")
    # print("(0) [New Server]")
    for i, op in enumerate(ops):
        print(f"({i}) {op}")

    return validate_input(ops)

def generate_world():
    """ Generates a new world from scratch.
    
    Prompts the user to decide between vanilla, paper, and forge.
    Then prompts the user to pick a version to run.
    Finally loads up any mods that can be pre-installed and pre-configured.
    """
    # If new world, set up
    launcher = ""
    while launcher not in ['vanilla', 'paper', 'forge']:
        launcher = input("What launcher will this server use? (vanilla, paper, or forge): ")
    launch_dir = os.path.join(TOP_PATH, f"versions/{launcher}")

    ver_ops = [x for x in os.listdir(launch_dir) if os.path.isdir(os.path.join(launch_dir, x))]
    for i, ver in enumerate(ver_ops):
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
        mod_ops = [
            x for x in os.listdir(addon_src_dir) if os.path.isfile(os.path.join(addon_src_dir, x))
        ]
        while True:
            # Skip if no options are available
            if not mod_ops:
                break

            # Display options and select one
            for i, mod in enumerate(mod_ops):
                print(f"({i}) {mod}")
            try:
                mod_num = int(
                    input("What Plugins/Mods do you want? (Leave blank and hit 'enter' to skip): ")
                )
            except ValueError:
                break

            # Handle selection
            if mod_num in range(len(mod_ops)):
                mod = mod_ops[mod_num]
                if launcher == "forge":
                    # Move addon into server mod directory
                    addon_target_dir = os.path.join(ACTIVE_PATH, "mods")
                elif launcher == "paper":
                    # Move addon into server mod directory
                    addon_target_dir = os.path.join(ACTIVE_PATH, "plugins")
                os.makedirs(addon_target_dir, exist_ok=True)
                logger.info(
                    "Moving addon '%s' to world addon directory '%s'",
                    mod,
                    addon_target_dir
                )
                shutil.copyfile(
                    os.path.join(addon_src_dir, mod),
                    os.path.join(addon_target_dir, mod)
                )
                mod_ops.pop(mod_num)
            else:
                logger.error("Addon not in list of options. Please select an index from the following list:")

    logger.warning("Additional Mods can be added later in the './mods' or './plugins' directory")
    logger.info("World: %s", ACTIVE_PATH)
    logger.info("Backups: %s", BACKUP_PATH)
    logger.info("Logname: %s", logname)

    # Generate Accepted EULA
    eula(world_path=ACTIVE_PATH)

    # Start World to generate config files
    temp_s, temp_h, temp_d = launch(server_path=ACTIVE_PATH, zip_dir=BACKUP_PATH, ram=RAM)
    time.sleep(5)
    kill(temp_s, temp_h, temp_d)

    # Edit initial Server config
    properties(world_path=ACTIVE_PATH, server_type=launcher)

    if launcher == "paper":
        # Edit config files for DiscordSRV and EssentialsX.
        # TODO: check to make sure that these plugins are included.
        discordsrv(world_path=ACTIVE_PATH)
        essentialsx(world_path=ACTIVE_PATH)

def launch(server_path: str, zip_dir: str, ram: int = 8):
    """ Launches the server and some parallel tasks to backup at different intervals.

    I split this off into it's own function so I can reuse it with different commands.

    Returns:
        Server: Server process/object to interface with
        Scheduler: Hourly backup timer
        Scheduler: Daily backup timer
    """
    # Launch the server
    svr = Server(server_path=server_path, zip_dir=zip_dir, ram=ram)

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

def handle_commands():
    """ Handle user inputs in an isolated function. """
    logger.error("Handle Commands has not been implemented yet!")

if __name__ == "__main__":
    SERVER_NAME, RAM, KNOWN = select_world()
    ACTIVE_PATH = os.path.join(DEFAULT_PATH, SERVER_NAME)
    os.makedirs(ACTIVE_PATH, exist_ok=True)

    ### LOGGING SECTION ###
    logname = ACTIVE_PATH + '/' + 'MCSERVER.log'
    log_format.format_logs(logger_name="MCLOG", file_name=logname)
    logger = logging.getLogger("MCLOG")

    BACKUP_PATH = os.path.join(DEFAULT_PATH, "Backups")
    # # If you want to put the backups in a different place or drive, uncomment this
    # import sys
    # from tkinter import filedialog
    # BACKUP_PATH = filedialog.askdirectory(
    #                         title="Select Backup Directory",
    #                         initialdir=f"{DEFAULT_PATH}/"
    # )
    # if BACKUP_PATH == "":
    #     logger.error("No backup path selected!")
    #     sys.exit()
    os.makedirs(name=BACKUP_PATH, exist_ok=True)

    if not KNOWN:
        generate_world()

    server, h_timer, d_timer = launch(server_path=ACTIVE_PATH, zip_dir=BACKUP_PATH, ram=RAM)

    try:
        while True:
            time.sleep(1)
            command = input("Send a manual command: /")
            if command.startswith("backup"):
                server.backup(backup_type="Manual")

            elif command.startswith("restore"):
                # Pull the name from the commandline
                try:
                    ZIP_FILE = command.split(sep=' ', maxsplit=1)[1]
                    logger.warning("Backup selected: %s", ZIP_FILE)
                    if not os.path.isfile(os.path.join(server.p.zip_dir, ZIP_FILE)):
                        logger.error(
                            "Backup (%s) doesn't exist! Try picking from the following list:",
                            ZIP_FILE
                        )
                        ZIP_FILE = ""
                except IndexError:
                    logger.error("No backup specified!")
                    ZIP_FILE = ""
                if ZIP_FILE == "":
                    logger.warning("Manually picking backup...")
                    bak_ops = os.listdir(server.p.zip_dir)
                    if bak_ops:
                        for I, IT in enumerate(bak_ops):
                            logger.info("(%s) %s", I, IT)
                        while True:
                            try:
                                index = int(input("Select zip file index from list above: "))
                                ZIP_FILE = bak_ops[index]
                                break
                            except IndexError:
                                logger.error(
                                    "Invalid index! Pick something between %d and %d",
                                    0,
                                    len(bak_ops)
                                )
                            except ValueError:
                                logger.error("Invalid input! Make sure to enter an integer!")
                    else:
                        logger.error("No Backup files yet! Back something up and try later.")

                # Take a backup of the current state in case something goes wrong with the backup
                if server.backup(backup_type="Revert"):
                    # Unpack the backup file
                    server.restore(ZIP_FILE)

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
                server, h_timer, d_timer = launch(
                    server_path=ACTIVE_PATH,
                    zip_dir=BACKUP_PATH,
                    ram=RAM
                )

            elif command.startswith("ram"):
                # Modify the value of dedicated ram
                try:
                    RAM = int(command.split(sep=' ')[1])
                except ValueError:
                    logger.error("Invalid entry, enter in an integer after the command")

                # Restart the server
                kill(server, h_timer, d_timer)
                server, h_timer, d_timer = launch(
                    server_path=ACTIVE_PATH,
                    zip_dir=BACKUP_PATH,
                    ram=RAM
                )

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
                for CMD, desc in cmd_lst:
                    logger.info("- %s: %s", CMD, desc)

            else:
                server.server_command(command)
    except KeyboardInterrupt:
        logger.info("User manually initiated shutdown using \"CTRL+C\"...")

    kill(server, h_timer, d_timer)
