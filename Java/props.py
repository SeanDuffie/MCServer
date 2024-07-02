""" _summary_
"""
import logging
import os

import logFormat
import configparser

### PATH SECTION ###
DEFAULT_PATH = os.path.dirname(__file__)
ACTIVE_PATH = f"{DEFAULT_PATH}/active/"

### LOGGING SECTION ###
logname = ACTIVE_PATH + '/' + 'MCSERVER.log'
logFormat.format_logs(logger_name="MCLOG", file_name=logname)
logger = logging.getLogger("MCLOG")
logger.info("Logname: %s", logname)

gitignore = [
    '*\n',
    '!eula.txt\n',
    '!.gitignore\n'
]

eula = {
    #By changing the setting below to TRUE you are indicating your agreement to our EULA (https://aka.ms/MinecraftEULA).
    #Wed Jun 26 11:09:07 EDT 2024
    'eula': 'TRUE'
}

config = configparser.ConfigParser()

def write_gitignore():
    with open(file=f"{ACTIVE_PATH}.gitignore", mode='w+', encoding='utf_8') as f:
        f.writelines(gitignore)


def read_properties(path: str):
    logger.info("Reading properties")
    if not os.path.exists(path):
        logger.error("File doesn't exist!")

    with open(file=path, mode='r', encoding='utf_8') as f:
        config.read_string('[config]\n' + f.read())

    logger.info(f.name)
    for k, v in config['config'].items():
        print(k, v)

        # try:
        #     while True:
        #         print(f.readline())
        # except Exception as e:
        #     print(e)
        
# def mod_properties():
    

if __name__ == "__main__":
    # read_properties(f"{ACTIVE_PATH}server.properties")
    write_gitignore()
