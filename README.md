# malcord

malcord is small helper library to aid malicious discord development in Python using the discord.py and requests libaries.

malcord currently contains two main Python files: `ctxcommands` and `discordtoken`, as well as a third `exceptions` for storing custom exceptions.

`ctxcommands` should be used when developing Discord bots and contains many raiding-based commands, such as editing server information, spamming text channels, granting administrator, and more.

`discordtoken` should be used when handling Discord user authentication tokens. This file contains the DiscordToken class that will allow you to nuke an account, log into an account, or grab an account's information. When initializing, the DiscordToken class checks to see whether the Discord token provided is valid.