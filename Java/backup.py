""" @file backup.py
    @author Sean Duffie
    @brief Functions that are responsible for wrapping the backup and restore functionality.
"""
import logging
import os
import zipfile

import logFormat

### PATH SECTION ###
DEFAULT_PATH = os.path.dirname(__file__)
ACTIVE_PATH = f"{DEFAULT_PATH}/project/"
BACKUP_PATH = f"{DEFAULT_PATH}/backups/"

### LOGGING SECTION ###
logname = ACTIVE_PATH + '/' + 'MCSERVER.log'
logFormat.format_logs(logger_name="MCLOG", file_name=logname)
logger = logging.getLogger("MCLOG")
logger.info("Logname: %s", logname)

def backup(zip_filename: str, target_dir: str = None, zip_path: str = None):
    """ Compresses the active directory into a zip archive that can be accessed later.

    Args:
        target_dir (str): Path of directory containing the files to compress
        destination (str): Path of output ZIP archive

    Returns:
        bool: Success?
    """
    if target_dir is None:
        target_dir = ACTIVE_PATH
    if zip_path is None:
        zip_path = f"{BACKUP_PATH}/{zip_filename}.zip"

    # Validity Checks
    assert os.path.isdir(target_dir)
    assert os.path.isdir(zip_path)

    # Open Zipfile for writing
    with zipfile.ZipFile(zip_path, 'w') as zip_file:
        # Iterate over the files in the directory
        for dirpath, _, filenames in os.walk(target_dir):
            for filename in filenames:
                # Acquire the source path
                src_path = os.path.join(dirpath, filename)
                # Determine the output path
                local_path = src_path.replace(ACTIVE_PATH, "")

                # Add each file to the ZIP archive
                zip_file.write(src_path, local_path)

    logger.info("Files compressed into: %s", zip_filename)

    return True

def restore(zip_filename: str, target_dir: str = None, zip_path: str = None):
    """ Restores a zip archive to the working directory.

    Args:
        zip_filename (str): Path and filename of the zipfile archive.
        target_dir (str): Path where the zip file will be extracted to.

    Returns:
        bool: Success?
    """
    if target_dir is None:
        target_dir = ACTIVE_PATH
    if zip_path is None:
        zip_path = f"{BACKUP_PATH}/{zip_filename}.zip"

    # Validity Checks
    print(f"{target_dir=}")
    assert os.path.isdir(target_dir)
    print(f"{zip_path=}")
    assert os.path.exists(zip_path)

    # Open Zipfile for reading
    with zipfile.ZipFile(zip_path, 'r') as zip_file:
        zip_file.extractall(target_dir)

    logger.info("Files extracted from: (%s) to (%s)", zip_path, target_dir)

    return True
