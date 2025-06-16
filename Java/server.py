"""_summary_

Returns:
    _type_: _description_
"""
import logging
import os
import subprocess
import sys
import time
from tkinter import filedialog
from typing import Literal

from pipeline import Pipeline

logger = logging.getLogger("MCServer")

def get_mc_ver(filename: str):
    """ Get the current MC version from the Jar file name.

    Args:
        filename (str): Filename of the Minecraft server executable.

    Returns:
        float: Number to represent the version.
    """
    # Get hyphens that outline the version
    first = filename.index("-")
    last = filename.index("-", first+1)
    # Cut off the "1." (major version) to convert to float
    version = float(filename[first+1:last][2:])
    return version

def get_java(version: float):
    """ Gets the path to the proper version of Java to use for the current Minecraft version.

    Args:
        version (float): Current version of minecraft.

    Returns:
        str: Path to the corresponding version of Java.
    """
    # Select Java Version
    java_path = r"C:\Program Files\Java"

    if version == 0:
        java_path = "java"
    if version <= 16.5:
        #Java 8
        if os.path.isdir(r"C:\Program Files\Java\jdk-1.8\bin"):
            java_path = r"C:\Program Files\Java\jdk-1.8\bin\java.exe"
        else:
            logging.error("Java 8 is not detected! Please make sure it is installed")
            logging.error("properly, in the correct location, and with the correct name.")
            logging.error("http://oracle.com/java/technologies/downloads/#java8-windows")
    elif version < 18:
        #Java 16
        if os.path.isdir(r"C:\Program Files\Java\jdk-16.0.2\bin"):
            java_path = r"C:\Program Files\Java\jdk-16.0.2\bin\java.exe"
        elif os.path.isdir(r"C:\Program Files\Java\jdk-16.0.1\bin"):
            java_path = r"C:\Program Files\Java\jdk-16.0.1\bin\java.exe"
        elif os.path.isdir(r"C:\Program Files\Java\jdk-16\bin"):
            java_path = r"C:\Program Files\Java\jdk-16\bin\java.exe"
        else:
            logging.error("Java 16 is not detected! Please make sure it is installed")
            logging.error("properly, in the correct location, and with the correct name.")
            logging.error("https://jdk.java.net/archive/")
            sys.exit(1)
    elif version <= 20.4:
        #Java 17
        if os.path.isdir(r"C:\Program Files\Java\jdk-17\bin"):
            java_path = r"C:\Program Files\Java\jdk-17\bin\java.exe"
        elif os.path.isdir(r"C:\Program Files\Java\jdk-17.0.2\bin"):
            java_path = r"C:\Program Files\Java\jdk-17.0.2\bin\java.exe"
        elif os.path.isdir(r"C:\Program Files\Java\jdk-17.0.1\bin"):
            java_path = r"C:\Program Files\Java\jdk-17.0.1\bin\java.exe"
        else:
            logging.error("Java 17 is not detected! Please make sure it is installed")
            logging.error("properly, in the correct location, and with the correct name.")
            logging.error("https://www.oracle.com/java/technologies/downloads/#java17-windows")
            sys.exit(1)
    else:
        #Java 21 https://www.oracle.com/java/technologies/downloads/#jdk21-windows
        # Java 24
        if os.path.isdir(r"C:\Program Files\Java\jdk-24.0.1\bin"):
            java_path = r"C:\Program Files\Java\jdk-24.0.1\bin\java.exe"
        elif os.path.isdir(r"C:\Program Files\Java\jdk-22.0.1\bin"):
            java_path = r"C:\Program Files\Java\jdk-22.0.1\bin\java.exe"
        elif os.path.isdir(r"C:\Program Files\Java\jdk-22\bin"):
            java_path = r"C:\Program Files\Java\jdk-22\bin\java.exe"
        else:
            logging.error("Java 24 is not detected! Please make sure it is installed")
            logging.error("properly, in the correct location, and with the correct name.")
            logging.error("https://jdk.java.net/24/")
            sys.exit(1)

    return java_path

class Server():
    """ The Server object provides a wrapper for functions related to the minecraft server jar
        subprocess.
    """
    process: subprocess.Popen

    def __init__(self, server_path: str, zip_dir: str, ram: int = 8, hcap: int = 6, dcap: int = 3):
        self.server_path = server_path
        self.server_name = os.path.basename(server_path)
        self.hcap = hcap
        self.dcap = dcap
        self.backup_flag = False

        os.chdir(self.server_path)
        logger.info("Starting server")
        self.run(ram=ram)

        logger.info("Server started.")
        self.p = Pipeline(src_dir=self.server_path, zip_dir=zip_dir)

    def run(self, version: float = 0, ram: int = 8):
        """ Called when the server is launched.

            Launches and attaches the server process to self.process variable.
            This is called in __init__ and must finish before any interactions with the server can
            occur.

        Args:
            java (float): What version of Java to use in the command line. By default, the java
                command is set by "JAVA_HOME" in the Environment Variables. For greater control,
                you can pass the direct path to the "java.exe" in the bin folder of the desired
                Java version.
            ram (int): Amount of ram in Gigabytes to allocate for the server.
        """
        executable = ""

        for filename in os.listdir(self.server_path):
            if filename.endswith(".jar"):
                version = get_mc_ver(filename)
                java_path = get_java(version)
                executable = f"{java_path} -Xmx{ram * 1024}m -jar \"{filename}\" nogui"
                break

        if executable == "":
            logger.error("No Executable Jar file detected! Please add one to 'active' directory")
            sys.exit(1)

        logger.info("Running command: %s", executable)
        self.process = subprocess.Popen(executable, stdin=subprocess.PIPE)

    def stop(self):
        """ Sends the stop command to the server.
            I broke this out into an external function in case other steps or features are added
            later.
        """
        self.server_command("stop")

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

    def backup(self, backup_type: Literal["Daily", "Hourly", "Manual", "Restore"], ignore_same: bool = False, whitelist: bool = False):
        """ Temporarily pauses the server autosaving to prevent corruption,
            Then backs up the server using the Pipeline.backup function.

        Args:
            backup_type (str): What type of backup is this? (Affects auto-deletion and output name)
            ignore_same (bool): If true, will skip the backup if no files have been changed.
            whitelist (bool): If true, will only backup certain files. Else will blacklist the Backups folder.

        Returns:
            bool: Did the backup succeed?
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
        check = self.p.backup(backup_type=backup_type, ignore_same=ignore_same, whitelist=whitelist)

        # Resume Autosave
        self.server_command("save-on")
        self.server_command("say Backup complete. World now saving. ")

        self.backup_flag = False
        if check:
            return True
        logger.error("There was a failure in the backup function!")
        return False

    def restore(self, zip_name: str):
        """ Stops the server, calls the Pipeline restore function, and restores it.

        Args:
            zip_name (str): Name of the file that is being restored.

        Returns:
            bool: Did the restore succeed?
        """
        # Stop the server and wait
        self.stop()
        # Delete any conflicting files
        # Call the Pipeline restore function
        check: bool = self.p.restore(zip_name=zip_name)
        if check:
            self.run()
        else:
            logger.error("Something went wrong with the restore! Attempting to revert changes...")
        return check

if __name__ == "__main__":
    print(get_mc_ver("paper-1.17.1-388.jar"))
