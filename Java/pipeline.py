""" @file backup.py
    @author Sean Duffie
    @brief Functions that are responsible for wrapping the backup and restore functionality.
"""
import datetime
import logging
import os
import zipfile

### PATH SECTION ###
DEFAULT_PATH = os.path.dirname(__file__)
ACTIVE_PATH = os.path.join(DEFAULT_PATH, "project")
BACKUP_PATH = os.path.join(DEFAULT_PATH, "backups")

### LOGGING SECTION ###
logger = logging.getLogger("MCLOG")

# def is_changed(path: str):
#     pass

class Pipeline:
    """ A Pipeline object wraps the process of backing up or restoring project files.
    This will provide a function for the Scheduler process to call 
    """
    def __init__(self, src_dir: str = ACTIVE_PATH, zip_dir: str = BACKUP_PATH):
        # Path of directory containing the files to compress
        self.src_dir: str = src_dir
        assert os.path.isdir(self.src_dir)
        self.project_name: str = os.path.basename(self.src_dir)

        # Path of output ZIP archive
        self.zip_dir: str = zip_dir
        if not os.path.isdir(self.zip_dir):
            os.mkdir(self.zip_dir)

        self.hcap = 6
        self.dcap = 3

    def delete_old(self):
        """ Checks for and deletes expired backup files """
        logger.info('Deleting old files...')

        # Generate list of existing backups that require frequent purges.
        hourly = []
        daily = []
        for filename in os.listdir(BACKUP_PATH):
            if filename != "":
                try:
                    # Extract useful info from path
                    parsed = os.path.basename(filename).split(".", 2)[0].split("_", 3)
                    # s_name = parsed[0]
                    # tstmp = datetime.datetime.strptime(parsed[1], "%Y-%m-%d-%H-%M-%S")
                    prev_backup_type = parsed[2]
                except IndexError:
                    logger.error("Filename has incorrect format: %s", filename)
                    logger.error("Should be {server_name}_{timestamp}_{backup_type}")
                    return False

                if prev_backup_type == "Hourly":
                    hourly.append(filename)
                elif prev_backup_type == "Daily":
                    daily.append(filename)
                    # os.remove(filename)

        # Remove the files that exceed the backup limits
        try:
            while len(hourly) > self.hcap:
                os.remove(os.path.join(BACKUP_PATH, hourly.pop(0)))
            while len(daily) > self.dcap:
                os.remove(os.path.join(BACKUP_PATH, daily.pop(0)))
            return True
        except OSError as e:
            logger.error(e)
            logger.error("Error Removing Backups!")
            return False

    def backup(self, backup_type: str = "Manual"):
        """ Compresses the active directory into a zip archive that can be accessed later.

        Args:
            backup_type (str): How should this backup be classified? (Hourly, Daily, Manual)

        Returns:
            bool: Success?
        """
        try:
            assert backup_type in ["Hourly", "Daily", "Manual", "Revert"]
        except AssertionError:
            logger.error("Invalid Backup Type: %s", backup_type)
            return False

        tstmp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        zip_name = f"{tstmp}_{backup_type}.zip"
        zip_path = os.path.join(self.zip_dir, zip_name)

        # Validity Checks
        try:
            assert os.path.isdir(self.src_dir)
        except AssertionError:
            logger.error("Source Path for backup is not a directory! %s", self.src_dir)
            return False

        # Open Zipfile for writing
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            # Iterate over the files in the directory
            for dirpath, _, filenames in os.walk(self.src_dir):
                for filename in filenames:
                    # Acquire the source path
                    src_path = os.path.join(dirpath, filename)
                    # Determine the output path
                    local_path = src_path.replace(self.src_dir, "")

                # In the future, here is where I should filter unnecessary files
                blacklist = ["Backups"]
                # whitelist = ["world", "world_nether", "world_the_end"]
                # FIXME: checking for strings in list as substrings of another list
                if blacklist not in local_path:
                    logger.warning("Accepted: %s", local_path)
                    # Add each file to the ZIP archive
                    zip_file.write(src_path, local_path)
                else:
                    logger.warning("Rejected: %s", local_path)

        logger.debug("Files compressed into: (%s)\n\tfrom (%s)", zip_path, self.src_dir)
        return True

    def restore(self, zip_name: str, target_dir: str = None):
        """ Restores a zip archive to the working directory.

        Args:
            zip_name (str): Path and filename of the zipfile archive.

        Returns:
            bool: Success?
        """
        if target_dir is None:
            target_dir = self.src_dir
        if not os.path.isdir(target_dir):
            logger.error("Target directory doesn't exist! %s", target_dir)

        # Validity Checks
        try:
            zip_path = os.path.join(self.zip_dir, zip_name)
            assert os.path.exists(zip_path)
        except AssertionError:
            zip_path = zip_name
            try:
                assert os.path.exists(zip_name)
                zip_path = zip_name
            except AssertionError:
                logger.error("Zip File requested does not exist!")
                logger.error("Zip Dir: %s", self.zip_dir)
                logger.error("Zip Name: %s", zip_name)
                return False

        # Open Zipfile for reading
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(target_dir)

        logger.info("Files extracted from: (%s) to (%s)", zip_path, target_dir)

        return True

if __name__ == "__main__":
    from tkinter import filedialog

    p = Pipeline()
    p.backup()

    restore_name = filedialog.askopenfilename(
        initialdir=BACKUP_PATH,
        title="Select Zip",
        filetypes=[('Compressed Files', '*.zip')]
    )
    if restore_name != "":
        p.restore(restore_name)
