"""_summary_

Returns:
    _type_: _description_
"""
import logging
import os
import subprocess
import sys
import time
from typing import Literal

from pipeline import Pipeline

logger = logging.getLogger("MCServer")

class Server():
    """_summary_
    """
    process: subprocess.Popen

    def __init__(self, server_path: str, ram: int = 8, hcap: int = 6, dcap: int = 3):
        self.server_path = server_path
        self.server_name = os.path.basename(server_path)
        self.hcap = hcap
        self.dcap = dcap
        self.backup_flag = False

        os.chdir(self.server_path)
        logger.info('Starting server')
        self.run(ram=ram)

        logger.info("Server started.")
        self.p = Pipeline(src_dir=self.server_path, project_name=self.server_name)

    def run(self, ram: int = 8):
        """ Called when the server is launched.

            Launches and attaches the server process to self.process variable.
            This is called in __init__ and must finish before any interactions with the server can
            occur.
            
        Args:
            ram (int): Amount of ram in Gigabytes to allocate for the server.
        """
        executable = ""
        for filename in os.listdir(self.server_path):
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
        """_summary_

        Args:
            zip_name (str): _description_

        Returns:
            _type_: _description_
        """
        return self.p.restore(zip_name=zip_name)
