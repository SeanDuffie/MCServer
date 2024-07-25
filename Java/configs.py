""" _summary_
"""
import configparser
import datetime
import logging
import os

import logFormat

### PATH SECTION ###
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "Worlds")

### LOGGING SECTION ###
logFormat.format_logs(logger_name="MCLOG")
logger = logging.getLogger("MCLOG")

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

class Properties():
    """_summary_
    """
    def __init__(self, world_path: str):
        self.world_path = world_path
        # Write the Eula
        # if not os.path.exists(f"{self.world_path}.gitignore"):
        #     self.write_file(gitignore, '.gitignore')
        if not os.path.exists(self.world_path):
            os.mkdir(self.world_path)
        if not os.path.exists(os.path.join(self.world_path, "eula.txt")):
            self.write_file(eula, 'eula.txt')

        # Launch the application
        

        # Edit server.properties
        self.config_dict = self.read_properties(world_path)
        self.set_properties()

        # Edit DiscordSRV Config
        

        # Edit EssentialsX Config
        

    def write_file(self, line_iterator, filename: str):
        """_summary_

        Args:
            line_iterator (_type_): _description_
            filename (_type_): _description_
        """
        with open(file=os.path.join(self.world_path, filename), mode='w+', encoding='utf_8') as f:
            f.writelines(line_iterator)

    def read_properties(self, path: str, name: str = "server.properties"):
        """_summary_

        Args:
            path (str): _description_

        Returns:
            _type_: _description_
        """
        filepath = os.path.join(path, name)
        if not os.path.exists(filepath):
            logger.error("File doesn't exist!")
        if os.path.isdir(filepath):
            logger.error("Path leads to a directory")

        with open(file=filepath, mode='r', encoding='utf_8') as f:
            config.read_string('[config]\n' + f.read())

        # logger.info(f.name)
        config_dict = {}
        for key, value in config['config'].items():
            # print(key, value)
            config_dict[key] = value

        return config_dict

    def set_properties(self):
        """
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
        """
        self.config_dict['difficulty'] = "hard"
        self.config_dict['enforce-secure-profile'] = "true"
        self.config_dict['enforce-whitelist'] = "false"
        self.config_dict['difficulty'] = "hard"
        self.config_dict['motd'] = "Welcome to the Reunion server!"
        self.config_dict['previews-chat'] = "true"
        self.config_dict['white-list'] = "true"

        config_ls = [f"{k}={v}\n" for k, v in self.config_dict.items()]
        TSTMP = datetime.datetime.now().astimezone().strftime("#%a %b %d %H:%M:%S %Z %Y\n")
        config_ls.insert(0, TSTMP)
        DESC = "#Minecraft server properties\n"
        config_ls.insert(0, DESC)

        self.write_file(config_ls, "server.properties")

if __name__ == "__main__":
    p = Properties(os.path.join(DEFAULT_PATH, "Test"))
