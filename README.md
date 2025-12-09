# MCServer
A quick setup for a minecraft server. Contains templates for both Bedrock and Java servers, as well as scripts for running and backing them up.
Will also allow users to plug in jar files for Paper and Minecraft Forge modded servers.

## How to Use

The following sections will give a tutorial on how to use the scripts for each application. Anything involving Java (e.g. Vanilla, Paper, Forge) will utilize the "run-server.py" file.

Bedrock, on the other hand, behaves differently, as it uses a different executable instead of a Java "jar" file as an installer.

### Vanilla (Java)

Plain old Vanilla Minecraft is by far the easiest to set up. Just pick a version, throw in the jar file, and launch the "run-server.py" script. The server will automatically install the necessary files, and then prompt you to accept the EULA. Once the EULA is accepted the script can be run again and the server will be accessible to anyone on the local network (using the local IP of the host device). Once the Port Forwarding is set up properly it will be available externally through the external IP of your network.

### Paper

PaperMC is a modified minecraft server that allows the server host to use various plugins instead of mods. These plugins are usually lighter weight, and range from simple server utilities to full on mods. The main benefit is that any mods are server side, and clients don't have to worry about downloading, updating, or configuring any modpacks to join the world. The downside is that any plugins are severely limited in potential due to being server side only, but the performance benefits of this type of server are perfect for something hosted on a Raspberry Pi.

#### EssentialsX

- Homes
- Warps
- Private Messages
- AFK Status Messages
- Teleports
- Nicknames
- Kicks, temp bans, mutes, jails
- Economy? (I was never able to get this working)

#### DiscordSRV

DiscordSRV is a PaperMC plugin that allows hosts to connect to a discord server

##### Create Discord Bot

1. Go to https://discord.com/developers/applications/me
2. Create New Application
3. Navigate to "Bot" tab
    1. Set Bot Username
    2. Set Bot Icon and Banner
    3. Set Server Members Intent (In Privileged Gateway Intents)
    4. Finally copy the "Token" (will be used later).
        1. This can only be accessed once and must be regenerated otherwise.

##### Configuration

1. alert.yml - This file allows you to set up alerts that occur on events, such as "Catching a Fish".
    By default it does nothing and can be quite advanced.
2. config.yml - This is the important file for setting up basic functionality of the bot.
    1. BotToken: Paste the "Application ID" from the Discord Bot you created earlier
    2. Channels: This allows you to filter which messages go to which channels, by default it picks the top one. This creates a dictionary/json structure that specifies {Type of Message}:{Channel ID}, some examples of categories are shown below:
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
    3. DiscordInviteLink: The invite link to the server. Maybe make a separate link from default invite to identify where they came from. Then make it a temporary membership for role assignments.
    4. MinecraftMentionSound - plays an in game sound to the player when they are mentioned in Discord. Default True.
    5. DiscordGameStatus: Contains a list of statuses that the Bot will cycle through, useful for storing the Domain/IP
    6. DiscordChatChannelDiscordToMinecraft: Sends Discord chat to in-game chat. Default True.
    7. DiscordChatChannelMinecraftToDiscord: Sends in-game chat to Discord. IMO this creates spam so I set it False. Default True.
3. linking.yml - Configuration options regarding linking your Minecraft account to a Discord account.
    1. Enabled: Set this to True to require linking. Default False.
    2. Whitelisted players bypass check: If someone wants to join the server but doesn't want to use Discord, this is a loophole. Default True.
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

- [ ] TODO: Assign Discord roles for different stats (like bumper jumper)

### Forge

Minecraft Forge is the most common client for mods and modpacks. It provides some additional challenges for hosting, however it has some of the most fun modding capabilities available to it.

#### Administrative Mods

#### 

### Bedrock

TODO

## Additional Tools

### NOIP

TODO

### Port Forwarding

TODO

## TODO:

TODO: add version switching
TODO: add world switching

    - [ ] LINUX SETUPS FOR OLD COMPUTERS
        - [ ] DietPi
        - [ ] Mint Cinnamon - Based on Ubuntu, 
        - [ ] Fedora
        - [ ] Lubuntu
    - [ ] Add branches for different stages of the Server process
        - [x] Pre Setup
        - [ ] Forge
        - [x] Paper
        - [x] Vanilla
    - [ ] Scripts
        - [x] Add a script to auto configure server ip
        - [x] Add a Script to auto update paper
        - [ ] Add a Script to auto update plugins (might be difficult to be flexible)
        - [x] Add a Script to auto back up
        - [ ] Add a script to restore backup
    - [ ] Reusability
        - [x] Update the gitignore to exclude all unnecessary, unique, or sensitive files
        - [x] FIXME: How do I gitignore the world directories???
            - NOTE: This can probably be done by using the default world name (for uniformity)
            - When switching worlds it will make the process easier, store the actual world name in a json elsewhere, and use similar functions to the backup/revert_backup scripts.
        - [ ] Add a scripted way to swap worlds from an external location, can work similarly to backup/restore backup
        - [ ] Document steps to configure DiscordSRV correctly
            - Mostly in config.yml
            - DiscordConsoleChannelId = Admin discord channel id (copy id)
            - Channels = Public discord channel id (copy id)
            - BotToken = Discord Bot
            - DiscordGameStatus = Activity status for the bot account
    - Features:
        - [ ] Version name and number added to the MOTD
