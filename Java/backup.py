import os
import shutil

def backup():
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

#General script by github.com/tushar2704, please adjust according to you requirements.

import os
import zipfile

def zipper(target_dir: str, zip_filename: str):
    """_summary_

    Args:
        target_dir (str): Path of directory containing the files to compress
        destination (str): Path of output ZIP archive

    Returns:
        bool: Success?
    """
    # Validity Checks
    assert os.path.isdir(target_dir)
    assert zip_filename.endswith('.zip')

    # Open Zipfile for writing
    with zipfile.ZipFile(zip_filename, 'w') as zip_file:
        # Iterate over the files in the directory
        for filename in os.listdir(target_dir):
            file_path = os.path.join(target_dir, filename)

            # Add each file to the ZIP archive
            zip_file.write(file_path, filename)

    print(f"Files compressed into {zip_filename}")

    return True

def restore(zip_filename: str, target_dir: str):
    """ Restores a zip archive to the working directory.

    Args:
        zip_filename (str): Path and filename of the zipfile archive.
        target_dir (str): Path where the zip file will be extracted to.

    Returns:
        bool: Success?
    """
    # Validity Checks
    assert os.path.isdir(target_dir)
    assert zip_filename.endswith('.zip')

    # Open Zipfile for reading
    with zipfile.ZipFile(zip_filename, 'r') as zip_file:
        zip_file.extractall(target_dir)

    logger.info

    return True
