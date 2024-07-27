""" _summary_
"""
import configparser
import datetime
import logging
import os

import yaml
# import ruamel.yaml

### PATH SECTION ###
DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "Worlds/Server")

### LOGGING SECTION ###
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

def properties(world_path: str = DEFAULT_PATH):
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
    """ Makes modifications to the DiscordSRV file.

    2. config.yml - This is the important file for setting up basic functionality of the bot.
        1. BotToken: Paste the "Application ID" from the Discord Bot you created earlier
        2. Channels: This allows you to filter which messages go to which channels, by default it
        picks the top one. This creates a dictionary/json structure that specifies
        {Type of Message}:{Channel ID}, some examples of categories are shown below:
            1. global - player chat messages
            2. status - server start/stop
            3. awards - player achievements
            4. deaths - player death messages
            5. join - player join messages
            6. leave - player leave messages
            7. dynmap - TODO: Not sure what this is.
            8. watchdog - TODO: performance?
            9. broadcast - in-game players using the /broadcast command to message the Discord
            10. link - account linking
        3. DiscordInviteLink: The invite link to the server. Maybe make a separate link from default
        invite to identify where they came from. Then make it a temporary membership for role
        assignments.
        4. MinecraftMentionSound - plays an in game sound to the player when they are mentioned in
        Discord. Default True.
        5. DiscordGameStatus: Contains a list of statuses that the Bot will cycle through, useful
        for storing the Domain/IP
        6. DiscordChatChannelDiscordToMinecraft: Sends Discord chat to in-game chat. Default True.
        7. DiscordChatChannelMinecraftToDiscord: Sends in-game chat to Discord. IMO this creates
        spam so I set it False. Default True.
    3. linking.yml - Configuration options regarding linking your Minecraft account to a Discord
    account.
        1. Enabled: Set this to True to require linking. Default False.
        2. Whitelisted players bypass check: If someone wants to join the server but doesn't want
        to use Discord, this is a loophole. Default True.
    4. messages.yml - Specify how you want various messages to look. E.g. Join messages, first join, leave, death.
        1. Join: Nice on servers that are semi-active! Spam on heavily active servers. Awkward on dead servers. Default True.
        2. First Join: Nice to show when new people join! Default True.
        3. Leave: Best to keep it off unless you have a reason. Maybe someone wants to know if they missed other people? Or pranks? Default True.
        4. Death: Good option for hazing opportunities. Can get spammy in some cases. Default True.
        5. Achievement: Great for competition, or even cooperative celebration! Default True.
        6. ChannelTopicUpdaterChatChannelTopicFormat: Formats the top bar of the text channel.
            - Default: "%playercount%/%playermax% players online | %totalplayers% unique players ever joined | Server online for %uptimemins% minutes | Last update: %date%"
            - Suggested: "%playercount%/%playermax% online | %tps% tps | %totalplayers% unique players | Online for %uptimemins% minutes | Last update: %date%"
    5. synchronization.yml - Allows interactions between discord role and minecraft group
        1. GroupRoleSynchronizationMinecraftIsAuthoritative: Does Minecraft set Discord roles? I say no. Default True.
        2. GroupRoleSynchronizationOneWay: Can both sides set roles on the other? I say no. Default False.
    6. voice.yml - Proximity Chat can be configured here!
        1. Voice enabled: Enables Proximity Chat. Default False.
        2. Voice Category: Create a category in the Discord, then copy the Category ID here.
        3. Lobby Channel: Create a single voice channel in the above category and copy the Channel ID here.
            - NOTE: This should be the only Channel in this Category.
            - Anyone wanting to do voice proximity chat should join this call. In the Lobby, everyone will be muted, but when they approach each other, the bot will automatically create a new channel and move them to it.
        4. Channels are visible: Set this to True for debugging purposes, but false improves immersion. Default False.

    Args:
        world_path (str, optional): Path to the world that is being run. Defaults to DEFAULT_PATH.
    """
    # Check that the server.properties file has already been generated
    alertfile = os.path.join(world_path, "plugins\\DiscordSRV\\alerts.yml")
    configfile = os.path.join(world_path, "plugins\\DiscordSRV\\config.yml")
    linkingfile = os.path.join(world_path, "plugins\\DiscordSRV\\linking.yml")
    messagesfile = os.path.join(world_path, "plugins\\DiscordSRV\\messages.yml")
    syncfile = os.path.join(world_path, "plugins\\DiscordSRV\\synchronization.yml")
    voicefile = os.path.join(world_path, "plugins\\DiscordSRV\\voice.yml")
    if not os.path.isfile(alertfile):
        logger.error("Alert File doesn't exist! Accept the EULA and launch the executable first!")
    if not os.path.isfile(configfile):
        logger.error("Config File doesn't exist! Accept the EULA and launch the executable first!")
    if not os.path.isfile(linkingfile):
        logger.error("Linking File doesn't exist! Accept the EULA and launch the executable first!")
    if not os.path.isfile(messagesfile):
        logger.error("Messages File doesn't exist! Accept the EULA and launch the executable first!")
    if not os.path.isfile(syncfile):
        logger.error("Sync File doesn't exist! Accept the EULA and launch the executable first!")
    if not os.path.isfile(voicefile):
        logger.error("Voice File doesn't exist! Accept the EULA and launch the executable first!")

    # Read and Edit DiscordSRV YAML Files
    # yaml = ruamel.yaml.YAML()
    # with open(file=alertfile, mode='r', encoding='utf_8') as f:
    #     alert = yaml.safe_load(f)
    with open(file=configfile, mode='r', encoding='utf_8') as f:
        config = yaml.safe_load(f)
        config["BotToken"] = input("Enter Discord Bot Token: ")
        public_channel = input("Enter public channel: ")
        config["Channels"] = {
            "global": input("Enter admin channel: "),
            "awards": public_channel,
            "deaths": public_channel,
            "join": public_channel,
            "broadcasts": public_channel,
            "link": input("Enter linking channel: ")
        }
        config["DiscordConsoleChannelId"] = input("Enter console channel: ")
        url = input("Enter Server URL/IP: ")
        config["DiscordGameStatus"] = [url]
        config["DiscordCannedResponses"] = {
            "!ip": url,
            "!site": url
        }
    with open(file=linkingfile, mode='r', encoding='utf_8') as f:
        linking = yaml.safe_load(f)
        linking["Require linked account to play"]["Enabled"] = True
        print(linking)
    with open(file=messagesfile, mode='r', encoding='utf_8') as f:
        messages = yaml.safe_load(f)
        messages["MinecraftPlayerLeaveMessage"]["Enabled"] = False
        messages["ChannelTopicUpdaterChatChannelTopicFormat"] = "%playercount%/%playermax% online | %tps% tps | %totalplayers% unique players | Online for %uptimemins% minutes | Last update: %date%"
        messages["ChannelTopicUpdaterChatChannelTopicAtServerShutdownFormat"] = "Server is offline | %totalplayers% unique players ever joined"
    with open(file=syncfile, mode='r', encoding='utf_8') as f:
        sync = yaml.safe_load(f)
        sync["GroupRoleSynchronizationMinecraftIsAuthoritative"] = False
        sync["GroupRoleSynchronizationOneWay"] = True
    with open(file=voicefile, mode='r', encoding='utf_8') as f:
        voice = yaml.safe_load(f)
        voice["Voice enabled"] = True
        voice["Voice category"] = input("Enter voice category: ")
        voice["Lobby channel"] = input("Enter lobby channel: ")
        # Do I want this???
        voice["Network"]["Channels are visible"] = False

    # Output changes to file
    # with open(file=alertfile, mode='w+', encoding='utf_8') as f:
    #     yaml.dump(alert, f)
    with open(file=configfile, mode='w+', encoding='utf_8') as f:
        yaml.dump(config, f)
    with open(file=linkingfile, mode='w+', encoding='utf_8') as f:
        yaml.dump(linking, f)
    with open(file=messagesfile, mode='w+', encoding='utf_8') as f:
        yaml.dump(messages, f)
    with open(file=syncfile, mode='w+', encoding='utf_8') as f:
        yaml.dump(sync, f)
    with open(file=voicefile, mode='w+', encoding='utf_8') as f:
        yaml.dump(voice, f)

def essentialsx(world_path: str = DEFAULT_PATH):
    """ Makes modifications to the EssentialsX configuration files.

    Args:
        world_path (str, optional): Path to the world that is being run. Defaults to DEFAULT_PATH.
    """
    # Check that the server.properties file has already been generated
    configfile = os.path.join(world_path, "plugins\\Essentials\\config.yml")
    if not os.path.isfile(configfile):
        logger.error("File doesn't exist! Accept the EULA and launch the executable first!")

    # Open EssentialsX YAML File
    # yaml = ruamel.yaml.YAML()
    with open(file=configfile, mode='r', encoding='utf_8') as f:
        config = yaml.safe_load(f)
        # config["custom-join-message"] = ""
        # config["custom-quit-message"] = ""
        # config["custom-new-username-message"] = ""
        config["update-check"] = False
        config["sethome-multiple"]["default"] = input("How many default homes?")
        config["sethome-multiple"]["vip"] = input("How many vip homes?")
        config["sethome-multiple"]["staff"] = input("How many staff homes?")
        config["compass-towards-home-perm"] = True
        config["confirm-home-overwrite"] = True
        # TODO: Protect
        # TODO: Disable phantom?
        # TODO: Spawn + New Players

    # Output changes to file
    with open(file=configfile, mode='w+', encoding='utf_8') as f:
        yaml.dump(config, f)

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
