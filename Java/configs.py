""" _summary_
"""
import configparser
import datetime
import logging
import os

import logFormat

### PATH SECTION ###
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "Worlds/Server")

### LOGGING SECTION ###
logFormat.format_logs(logger_name="MCLOG")
logger = logging.getLogger("MCLOG")

def eula(world_path: str = DEFAULT_PATH):
    """ Generates the EULA and automatically accepts it.

    Can be used before running the jar file.

    Args:
        world_path (str, optional): Path to the world that is being run. Defaults to DEFAULT_PATH.
    """
    lines = [
        "#By changing the setting below to TRUE you are indicating your agreement to our EULA (https://aka.ms/MinecraftEULA).\n",
        datetime.datetime.now().astimezone().strftime("#%a %b %d %H:%M:%S %Z %Y\n"),
        "eula=TRUE\n"
    ]
    # Output changes to file
    write_file(line_iterator=lines, filename="eula.txt", world_path=world_path)

def gitignore(world_path: str = DEFAULT_PATH):
    """ Generates a gitignore file that ignores everything except for the gitignore file itself.

    Not completely necessary for world files, the whole server directory should be ignored anyways.

    Args:
        world_path (str, optional): Path to the world that is being run. Defaults to DEFAULT_PATH.
    """
    lines = [
    '*\n',
    '!eula.txt\n',
    '!.gitignore\n'
    ]
    # Output changes to file
    write_file(line_iterator=lines, filename=".gitignore", world_path=world_path)

def properties(world_path: str):
    """ Makes modifications to the server.properties file.

    Properties:
        difficulty: Default Game Difficulty. Easy by default, but I prefer Hard.
        enforce-secure-profile: Enables chat reporting. This is stupid and dumb.
        enforce-whitelist: Kicks all players not present on the whitelist
        TODO: force-gamemode: Survival is the goal, but maybe adventure is a better option?
            gamemode: Same as above
        hardcore: ignore difficulty and set to spectator after death
        level-name: Name of the directory containing world files
        level-seed: seed of the world
        motd: Message displayed below the client server name. Add some personality!
        online-mode: Require Mojang authorized accounts. Default True, leave it on. Changing this will also delete/unlink all existing player data.
        previews-chat: Shows previews for features like chat color before sending. Default false, set true.
        simulation-distance: Maximum distance that client can update server or ticks can occur
        view-distance: world data sent to the client (server-side viewing distance). Default 10
        white-list: Enables whitelist (Not enforced yet, but can be added to)

    Args:
        world_path (str, optional): Path to the world that is being run. Defaults to DEFAULT_PATH.
    """
    # Check that the server.properties file has already been generated
    filepath = os.path.join(world_path, "server.properties")
    if not os.path.isfile(filepath):
        logger.error("File doesn't exist! Accept the EULA and launch the executable first!")

    # Get values from the config file
    config = configparser.ConfigParser()
    with open(file=filepath, mode='r', encoding='utf_8') as f:
        config.read_string('[config]\n' + f.read())

    # logger.info(f.name)
    config_dict = {}
    for key, value in config['config'].items():
        # print(key, value)
        config_dict[key] = value

    # Modify the desired sections in the dictionary
    config_dict['difficulty'] = "hard"
    config_dict['enforce-secure-profile'] = "true"
    config_dict['enforce-whitelist'] = "false"
    config_dict['difficulty'] = "hard"
    config_dict['motd'] = "Welcome to the Reunion server!"
    config_dict['previews-chat'] = "true"
    config_dict['white-list'] = "true"

    # Convert the dictionary to a list
    config_ls = [f"{k}={v}\n" for k, v in config_dict.items()]
    tstmp = datetime.datetime.now().astimezone().strftime("#%a %b %d %H:%M:%S %Z %Y\n")
    config_ls.insert(0, tstmp)
    desc = "#Minecraft server properties\n"
    config_ls.insert(0, desc)

    # Output changes to file
    write_file(line_iterator=config_ls, filename="server.properties", world_path=world_path)

def discordsrv(world_path: str = DEFAULT_PATH):
    # Edit DiscordSRV Config
    # Output changes to file
    # write_file(line_iterator=config_ls, filename="server.properties", world_path=world_path)
    pass

def essentialsx():
    # Edit EssentialsX Config
    # Output changes to file
    # write_file(line_iterator=config_ls, filename="server.properties", world_path=world_path)
    pass

def write_file(line_iterator, filename: str, world_path: str):
    """_summary_

    Args:
        line_iterator (List): _description_
        filename (str): _description_
        world_path (str): 
    """
    with open(file=os.path.join(world_path, filename), mode='w+', encoding='utf_8') as f:
        f.writelines(line_iterator)

if __name__ == "__main__":
    eula()
    gitignore()
    properties()
    discordsrv()
    essentialsx()
