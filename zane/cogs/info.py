import os
import random
import inspect
import json

import asyncpg
import discord
import typing
from discord.ext import commands


class Info(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        choices = [
            "My ping is, and has always been, 0.",
            "Why do discord bots even show ping? Who cares?",
            "No, not telling you.",
            "Shut up."
        ]

        await ctx.send(random.choice(choices))

    # From Rapptz's R. Danny bot
    # https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/meta.py#L328-L366
    @commands.command()
    async def source(self, ctx, *, command: str = None):
        source_url = 'https://github.com/ir-3/zane'
        branch = 'master'
        if command is None:
            return await ctx.send(source_url)

        if command == 'help':
            src = type(self.bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.get_command(command.replace('.', ' '))
            if obj is None:
                return await ctx.send('Could not find command.')

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith('discord'):
            # not a built-in command
            location = os.path.relpath(filename).replace('\\', '/')
        else:
            location = module.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py'
            branch = 'master'

        final_url = f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        await ctx.send(final_url)

    @commands.command()
    async def about(self, ctx):
        await ctx.send("Created by linK#0001, source located at <https://github.com/ir-3/zane>.")

    @commands.command(aliases=["support", "abuse", "request", "report"])
    async def contact(self, ctx):
        """
        Contact my owner with requests or information.
        """
        await ctx.send("support@zane.4yc.pw\n"
                       "Please include your userid if the request pertains to your account/information.\n"
                       "https://support.discord.com/hc/en-us/articles/206346498-Where-can-I-find-my-User-Server-Message-ID-")

    @commands.command()
    async def avatar(self, ctx, member: discord.Member = None):
        member = member or ctx.author

        await ctx.send(str(member.avatar_url))

    @commands.group()
    async def raw(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @raw.command()
    async def message(self, ctx, message_id: int):
        resp = await self.bot.http.get_message(ctx.channel.id, message_id)
        raw = json.dumps(resp, indent=4).replace("```", "\u200b`\u200b`\u200b`")
        await ctx.send("```json\n" + raw + "```")

    @raw.command(aliases=["user"])
    async def member(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        resp = await self.bot.http.get_member(ctx.guild.id, member.id)
        raw = json.dumps(resp, indent=4).replace("```", "\u200b`\u200b`\u200b`")
        await ctx.send("```json\n" + raw + "```")

    @raw.command()
    async def channel(self, ctx, channel: typing.Union[discord.TextChannel, discord.VoiceChannel] = None):
        channel = channel or ctx.channel
        resp = await self.bot.http.get_channel(channel.id)
        raw = json.dumps(resp, indent=4).replace("```", "\u200b`\u200b`\u200b`")
        await ctx.send("```json\n" + raw + "```")

    # @raw.command()
    # async def guild(self, ctx):
    #     resp = await self.bot.http.get_guild(ctx.guild.id)
    #     raw = json.dumps(resp, indent=4).replace("```", "\u200b`\u200b`\u200b`")
    #
    #     await ctx.send("")

def setup(bot):
    bot.add_cog(Info(bot))
