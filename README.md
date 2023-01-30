# QuickMCServer
Just a quick setup for a minecraft server. Will allow me to save and organize some scripts

## Setup

- Edit Java Path for bash

### TODO:

    - [ ] Add branches for different stages of the Server process
        - [x] Pre Setup
        - [ ] Forge
        - [ ] Paper
        - [ ] Vanilla
    - [ ] Scripts
        - [ ] Add a script to auto configure server ip
        - [x] Add a Script to auto update paper
        - [ ] Add a Script to auto update plugins (might be difficult to be flexible)
        - [ ] Add a Script to auto back up
        - [ ] Add a script to restore backup
    - [ ] Reusability
        - [ ] Update the gitignore to exclude all unnecessary, unique, or sensitive files
        - [ ] FIXME: How do I gitignore the world directories???
        - [ ] Add a scripted way to swap worlds from an external location, can work similarly to backup/restore backup
        - [ ] Document steps to configure DiscordSRV correctly
            - Mostly in config.yml
            - DiscordConsoleChannelId = Admin discord channel id (copy id)
            - Channels = Public discord channel id (copy id)
            - BotToken = Discord Bot
            - DiscordGameStatus = Activity status for the bot account
