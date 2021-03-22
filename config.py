from pyrogram import filters

# Bot token from Bot Father
TOKEN = "1438006148:AAFxy62Yz4cHZfH_iz7mvMLgZVSlutxOZg4"

# Your API ID and Hash from https://my.telegram.org/apps
API_ID = 1711524
API_HASH = "c93b573669b12ffd1c099f62690a2ef6"

# Chat used for logs
log_chat = -1001360771442


# Sudoers and super sudoers
super_sudoers = [957539786]
sudoers = [957539786]
sudoers += super_sudoers
sudofilter = filters.user(sudoers)

# Prefixes for commands, e.g: /command and !command
prefix = ["/", "!"]


# List of disabled plugins
disabled_plugins = []


# API keys
TENOR_API_KEY = ""


# Bot version, do not touch this
with open("version.txt") as f:
    version = f.read().strip()
