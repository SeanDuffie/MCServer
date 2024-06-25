# MCServer
A quick setup for a minecraft server. Contains templates for both Bedrock and Java servers, as well as scripts for running and backing them up.
Will also allow users to plug in jar files for Paper and Minecraft Forge modded servers.

## How to Use

The following sections will give a tutorial on how to use the scripts for each application. Anything involving Java (e.g. Vanilla, Paper, Forge) will utilize the "run-server.py" file.

Bedrock, on the other hand, behaves differently, as it uses a different executable instead of a Java "jar" file as an installer.

### Vanilla (Java)

TODO

Plain old Vanilla Minecraft is by far the easiest to set up. Just pick a version, throw in the jar file, and launch the "run-server.py" script. The server will automatically install the necessary files, and then prompt you to accept the EULA. Once the EULA is accepted the script can be run again and the server will be accessible to anyone on the local network (using the local IP of the host device). Once the Port Forwarding is set up properly it will be available externally through the external IP of your network.

### Paper

TODO

PaperMC is a modified minecraft server that allows the server host to use various plugins instead of mods. These plugins are usually lighter weight, and range from simple server utilities to full on mods. The main benefit is that any mods are server side, and clients don't have to worry about downloading, updating, or configuring any modpacks to join the world. The downside is that any plugins are severely limited in potential due to being server side only, but the performance benefits of this type of server are perfect for something hosted on a Raspberry Pi.

### Forge

TODO

Minecraft Forge is the most common client for mods and modpacks. It provides some additional challenges for hosting, however it has some of the most fun modding capabilities available to it.

### Bedrock

TODO

## Additional Tools

### NOIP

TODO

### Port Forwarding

TODO

## TODO:

    - [ ] Add branches for different stages of the Server process
        - [x] Pre Setup
        - [ ] Forge
        - [ ] Paper
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
        - [ ] Add a scripted way to swap worlds from an external location, can work similarly to backup/restore backup
        - [ ] Document steps to configure DiscordSRV correctly
            - Mostly in config.yml
            - DiscordConsoleChannelId = Admin discord channel id (copy id)
            - Channels = Public discord channel id (copy id)
            - BotToken = Discord Bot
            - DiscordGameStatus = Activity status for the bot account
