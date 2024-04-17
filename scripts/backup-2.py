""" @file backup.py
    @author Sean Duffie
    @brief 
"""
import logging
import os
import subprocess
import sys
import tarfile
import time
from datetime import datetime
from threading import Timer
from tkinter import filedialog

### CONSTANTS SECTION ###
min_ram = 8
hourly_cap = 6
daily_cap = 3

### PATH SECTION ###
default_dir = os.path.dirname(__file__)
minecraft_dir = filedialog.askdirectory(
                    title="Select Server Directory",
                    initialdir=f"{default_dir}/world/"
                )
backup_dir = filedialog.askdirectory(
                    title="Select Backup Directory",
                    initialdir=f"{default_dir}/backups/"
                )
executable = f'java -Xmx{min_ram * 1024}m -XX:+UseConcMarkSweepGC -jar "{minecraft_dir}/spigot-1.12.2.jar"'
# TODO: Is this needed?
exclude_file = "plugins/dynmap"

### LOGGING SECTION ###
logname = minecraft_dir + '/' + 'MCSERVER.log'
file_handler = logging.FileHandler(filename=logname)
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]

logging.basicConfig(
    level=logging.DEBUG, 
    format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)

logger = logging.getLogger('MCLOG')
logging.info(f"Logname: {logname}")

def server_command(cmd: str):
    """ Sends a string from the local python script to the server shell process

    Args:
        cmd (str): The command string to be sent to the server
    """
    logging.info("Writing server command: %s", cmd)
    process.stdin.write(str.encode('%s\n' %cmd)) #just write the command to the input stream
    process.stdin.flush()

def server_start():
    """ Start the server in a subprocess and return a link to it.

    Returns:
        subprocess.Popen: The subprocess interface to the executable.
    """
    os.chdir(minecraft_dir)
    logging.info('Starting server')
    process = subprocess.Popen(executable, stdin=subprocess.PIPE)
    logging.info("Server started.")
    return process

def filter_function(tarinfo):
    """ TODO: What does this function do?

    Args:
        tarinfo (_type_): _description_

    Returns:
        _type_: _description_
    """
     if tarinfo.name != exclude_file:
          logging.info(tarinfo.name,"ADDED")
          return tarinfo

def make_tarfile(output_filename, source_dir):
    logging.info('Making tarfile')
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir),filter=filter_function)

def backup():
    global t
    server_command("say Backup starting. World no longer saving...")
    server_command("save-off")
    server_command("save-all")
    time.sleep(3)
    os.chdir(backup_dir)
    logging.info('Deleting last file')
    try:
        os.remove(f"{backup_dir}/minecraft-hour24.tar.gz")
    except OSError:
        pass
    logging.info('Renaming old files')
    # FIXME: This is a terrible iteration system, I bet I can do better with simple datetime and timeintervals
    for i in range(24,0,-1):
        try:
            os.rename(
                f"{backup_dir}\\minecraft-hour{i-1}.tar.gz",
                f"{backup_dir}\\minecraft-hour{i}.tar.gz"
            )
        except:
            pass
    make_tarfile("%s\\minecraft-hour0.tar.gz"%backup_dir, minecraft_dir+"/")
    server_command("save-on")
    server_command("say Backup complete. World now saving. ")
    logging.info('Starting new timer')
    try:
        t = Timer(next_backuptime(), backup) # FIND NEXT HOURLY MARK
        t.start() # START BACKUP FOR THEN
        logging.info('New timer started')
    except:
        logging.info('',exc_info=True)
        os.popen('TASKKILL /PID '+str(process.pid)+' /F')

def next_backuptime():
    """ TODO: Add better docs

    Returns:
        int: seconds left before next backup
    """
    logging.info('Calculating next time')
    x=datetime.today()
    if x.hour != 23:
        y=x.replace(hour=x.hour+1, minute=0, second=0, microsecond=0)
    else:
        try:
            y=x.replace(day=x.day+1,hour=0,minute=0,second=0,microsecond=0)
        except:
            try:
                y=x.replace(month=x.month+1,day=1,hour=0,minute=0,second=0,microsecond=0)
            except:
                try:
                    y=x.replace(year=x.year+1,month=1,day=1,hour=0,minute=0,second=0,microsecond=0)
                except:
                    logging.info('I, the backup script, have no idea what time it is in an hour.',exc_info=True)
                    os.popen('TASKKILL /PID '+str(process.pid)+' /F')
    logging.info('Next backup time is %s' %y)
    delta_t=y-x
    secs=delta_t.seconds+1
    return secs



if __name__ == "__main__":
    process=server_start() # START SERVER
    time.sleep(60) # WAIT FOR IT TO START

    logging.info('Starting backup timer')
    try:
        t = Timer(next_backuptime(), backup) # FIND NEXT HOURLY MARK
        t.start() # START BACKUP FOR THEN
        logging.info('Timer started')
    except:
        logging.info('',exc_info=True)
        os.popen('TASKKILL /PID '+str(process.pid)+' /F')