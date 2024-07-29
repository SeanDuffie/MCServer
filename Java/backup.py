""" @file backup.py
    @author Sean Duffie
    @brief Functions that are responsible for wrapping the backup and restore functionality.
"""
import datetime
import logging
import os
import zipfile
from tkinter import filedialog

### PATH SECTION ###
DEFAULT_PATH = os.path.dirname(__file__)
ACTIVE_PATH = os.path.join(DEFAULT_PATH, "project")
TEST_PATH = os.path.join(DEFAULT_PATH, "restore_project")
BACKUP_PATH = os.path.join(DEFAULT_PATH, "backups")
if not os.path.isdir(ACTIVE_PATH):
    os.mkdir(ACTIVE_PATH)
if not os.path.isdir(BACKUP_PATH):
    os.mkdir(BACKUP_PATH)

### LOGGING SECTION ###
logger = logging.getLogger("MCLOG")

# def is_changed(path: str):
#     pass

class Pipeline:
    """_summary_

    Returns:
        _type_: _description_
    """
    def __init__(self, src_dir: str = ACTIVE_PATH, project_name: str = "Project"):
        # Path of directory containing the files to compress
        self.src_dir: str = src_dir
        assert os.path.isdir(self.src_dir)

        # Path of output ZIP archive
        self.zip_dir: str = os.path.join(BACKUP_PATH, project_name)
        if not os.path.exists(self.zip_dir):
            os.mkdir(self.zip_dir)

    def backup(self, backup_type: str = "Manual"):
        """ Compresses the active directory into a zip archive that can be accessed later.

        Args:
            backup_type (str): How should this backup be classified? (Hourly, Daily, Manual)

        Returns:
            bool: Success?
        """
        assert backup_type in ["Hourly", "Daily", "Manual", "Revert"]

        tstmp = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        filename = f"{tstmp}_{backup_type}.zip"
        zip_path = os.path.join(self.zip_dir, filename)

        # Validity Checks
        assert os.path.isdir(self.src_dir)

        # Open Zipfile for writing
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            # Iterate over the files in the directory
            for dirpath, _, filenames in os.walk(self.src_dir):
                for filename in filenames:
                    # TODO: In the future, here is where I should filter unnecessary files
                    
                    # Acquire the source path
                    src_path = os.path.join(dirpath, filename)
                    # Determine the output path
                    local_path = src_path.replace(self.src_dir, "")

                flagged_words = ["Backups"]
                if flagged_words not in local_path:
                    print(f"Accepted: {local_path}")
                    # Add each file to the ZIP archive
                    zip_file.write(src_path, local_path)
                else:
                    print(f"Rejected: {local_path}")

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
            target_dir = ACTIVE_PATH

        # Validity Checks
        try:
            zip_path = os.path.join(self.zip_dir, zip_name)
            assert os.path.exists(zip_path)
        except AssertionError:
            zip_path = zip_name
            try:
                assert os.path.exists(zip_path)
            except AssertionError:
                return False

        # Open Zipfile for reading
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(TEST_PATH)

        logger.info("Files extracted from: (%s) to (%s)", zip_path, TEST_PATH)

        return True

if __name__ == "__main__":
    p = Pipeline()
    p.backup()
    restore_name = filedialog.askopenfilename(
        initialdir=BACKUP_PATH,
        title="Select Zip",
        filetypes=[('Compressed Files', '*.zip')]
    )
    if restore_name != "":
        p.restore(restore_name)
