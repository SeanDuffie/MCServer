""" _summary_
"""
import configparser
import datetime
import logging
import os

import logFormat

### PATH SECTION ###
DEFAULT_PATH = os.path.dirname(__file__)
ACTIVE_PATH = f"{DEFAULT_PATH}/active/"

### LOGGING SECTION ###
logname = ACTIVE_PATH + '/' + 'MCSERVER.log'
logFormat.format_logs(logger_name="MCLOG")
logger = logging.getLogger("MCLOG")
logger.info("Logname: %s", logname)

gitignore = [
    '*\n',
    '!eula.txt\n',
    '!.gitignore\n'
]

eula = [
    "#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://aka.ms/MinecraftEULA).\n",
    datetime.datetime.now().astimezone().strftime("#%a %b %d %H:%M:%S %Z %Y\n"),
    "eula=TRUE\n"
]

config = configparser.ConfigParser()

def write_file(it, name):
    with open(file=f"{ACTIVE_PATH}{name}", mode='w+', encoding='utf_8') as f:
        f.writelines(it)


def read_properties(path: str):
    logger.info("Reading properties")
    if not os.path.exists(path):
        logger.error("File doesn't exist!")

    with open(file=path, mode='r', encoding='utf_8') as f:
        config.read_string('[config]\n' + f.read())

    logger.info(f.name)
    for k, v in config['config'].items():
        print(k, v)

def set_properties():
    # difficulty: Default Game Difficulty. Easy by default, but I prefer Hard.
    # enforce-secure-profile: Enables chat reporting. This is stupid and dumb.
    # enforce-whitelist: Kicks all players not present on the whitelist
    # TODO: force-gamemode: Survival is the goal, but maybe adventure is a better option?
    #     gamemode: Same as above
    # hardcore: ignore difficulty and set to spectator after death
    # level-name: Name of the directory containing world files
    # level-seed: seed of the world
    # motd: Message displayed below the client server name. Add some personality!
    # online-mode: Require Mojang authorized accounts. Default True, leave it on. Changing this will also delete/unlink all existing player data.
    # previews-chat: Shows previews for features like chat color before sending. Default false, set true.
    # simulation-distance: Maximum distance that client can update server or ticks can occur
    # view-distance: world data sent to the client (server-side viewing distance). Default 10
    # white-list: Enables whitelist (Not enforced yet, but can be added to)
    pass

if __name__ == "__main__":
    if not os.path.exists(f"{ACTIVE_PATH}.gitignore"):
        write_file(gitignore, '.gitignore')
    if not os.path.exists(f"{ACTIVE_PATH}eula.txt"):
        write_file(eula, 'eula.txt')

    read_properties(f"{ACTIVE_PATH}server.properties")
