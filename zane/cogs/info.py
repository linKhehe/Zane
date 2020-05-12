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

    async def insert_name(self, user: discord.User, name: str):
        try:
            await self.bot.db.execute("INSERT INTO nicks VALUES ($1, $2);", user.id, name)
        except asyncpg.UniqueViolationError:
            pass

    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        if before.name != after.name:
            await self.insert_name(after, after.name)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if before.nick != after.nick and after.nick is not None:
            await self.insert_name(after, after.nick)

    @commands.command()
    async def nicks(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        records = await self.bot.db.fetch("SELECT * FROM nicks WHERE user_id = $1", member.id)
        nicks = [record.get("nick") for record in records]
        await ctx.send(f"Names logged for {member.display_name}: {', '.join(nicks)}")

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


def setup(bot):
    bot.add_cog(Info(bot))
