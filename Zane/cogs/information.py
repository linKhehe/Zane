import time

import psutil
import discord
from discord.ext import commands

from utils.format import humanized_date, humanized_time_since
from cogs.image import WandImage as Image


class Information:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="user",
        aliases=[
            'member',
            'memberinfo',
            'userinfo'
        ]
    )
    async def _user_info_command(self, ctx, member: discord.Member = None):
        """Lists stats on the user provided.
        If the user parameter is not fulfilled, it will select you."""
        if member is None:
            member = ctx.author

        e = discord.Embed(
            title=f"User: {member.name}",
            description=f"This is all the information I could find on {member.name}...",
            color=self.bot.color
        )
        e.set_thumbnail(
            url=member.avatar_url_as(static_format="png")
        )
        e.add_field(
            name="Name",
            value=member.name
        )
        e.add_field(
            name="Discriminator",
            value=f"#{member.discriminator}"
        )
        e.add_field(
            name="ID",
            value=str(member.id)
        )
        e.add_field(
            name="Bot",
            value=str(member.bot).capitalize()
        )
        e.add_field(
            name="Highest Role",
            value=member.top_role.mention
        )
        e.add_field(
            name="Join Position",
            value=f"#{sorted(member.guild.members, key=lambda m: m.joined_at).index(member) + 1}"
        )
        e.add_field(
            name="Created Account",
            value=member.created_at.strftime("%c")
        )
        e.add_field(
            name="Joined This Server",
            value=member.joined_at.strftime("%c")
        )
        e.add_field(
            name="Roles",
            value=f"{len(member.roles)-1} Roles: {', '.join([r.mention for r in member.roles if not r.is_default()])}"
        )
        await ctx.send(embed=e)

    @commands.command(
        name="guild",
        aliases=[
            'server',
            'serverinfo',
            'guildinfo'
        ]
    )
    async def _guild_info_command(self, ctx):
        """Lists info on the current guild."""
        guild = ctx.guild
        e = discord.Embed(
            title=f"Guild: {guild.name}",
            description=f"This is what I could find on {guild.name}...",
            color=self.bot.color
        )
        e.add_field(
            name="Name",
            value=guild.name
        )
        e.add_field(
            name="ID",
            value=guild.id
        )
        e.add_field(
            name="Owner",
            value=guild.owner.mention
        )
        e.add_field(
            name="Guild Created At",
            value=guild.created_at
        )
        e.add_field(
            name="Member Count",
            value=guild.member_count
        )
        e.add_field(
            name="Roles",
            value=str(len(guild.roles))
        )
        e.add_field(
            name="Emotes",
            value=str(len(guild.emojis))
        )
        e.add_field(
            name="Text/Voice Channels",
            value=str(len(guild.text_channels)+len(guild.voice_channels))
        )
        e.set_thumbnail(
            url=guild.icon_url
        )

        await ctx.send(embed=e)

    @commands.command(
        name="stats",
        aliases=[
            "info",
            "botinfo",
            "botstats",
            "ne"
        ]
    )
    async def _stats_command(self, ctx):
        """Lists current stats on the bot."""
        members = 0
        roles = 0
        text_channels = 0

        for g in self.bot.guilds:
            members += g.member_count
            roles += len(g.roles)
            text_channels += len(g.text_channels)

        e = discord.Embed(
            title=f"{self.bot.user.name} Info",
            description="Don't worry, I know I am a cutie.",
            color=self.bot.color
        )
        e.add_field(
            name="Creator",
            value=self.bot.app_info.owner.mention
        )
        e.add_field(
            name="Guilds",
            value=str(len(self.bot.guilds))
        )
        e.add_field(
            name="Members",
            value=members
        )
        e.add_field(
            name="Roles",
            value=roles
        )
        e.add_field(
            name="Text Channels",
            value=text_channels
        )
        e.add_field(
            name="Ping",
            value=f"{round(self.bot.latency * 1000, 2)}ms"
        )
        e.add_field(
            name="CPU Usage",
            value=str(psutil.cpu_percent(interval=None)) + "%"
        )
        e.add_field(
            name="RAM Usage",
            value=str(psutil.virtual_memory().percent) + "%"
        )
        e.set_thumbnail(
            url=self.bot.user.avatar_url_as(static_format="png")
        )

        await ctx.send(embed=e)

    @commands.command(
        name="created",
        aliases=[
            'created_at',
            'createdat'
        ]
    )
    async def _created_command(self, ctx, member: discord.Member = None):
        """
        Return when a member joined discord.
        If the member argument isn't fulfilled, it will select you.
        """
        if member is None:
            member = ctx.author

        await ctx.send(f"{member.name} joined Discord on {humanized_date(member.created_at)}\
, {humanized_time_since(member.created_at)}.")

    @commands.command(
        name="joined",
        aliases=[
            'joined_at',
            'joinedat'
        ]
    )
    async def _joined_command(self, ctx, member: discord.Member = None):
        """
        Return when a member joined this server.
        If the member argument isn't fulfilled, it will select you.
        """
        if member is None:
            member = ctx.author

        await ctx.send(f"{member.name} joined this server on {humanized_date(member.joined_at)}\
, {humanized_time_since(member.joined_at)}.")

    @commands.command(
        name="avatar",
        aliases=[
            "avy",
            "pfp"
        ]
    )
    async def _avatar_command(self, ctx, member: discord.Member = None):
        """
        Return a user's avatar/profile picture.
        If the member argument isn't fulfilled, it will select you.
        """
        if member is None:
            member = ctx.author

        await ctx.message.add_reaction(self.bot.loading_emoji)

        # we only download an avatar if it is not a gif
        # this way we don't keep users waiting
        if ".gif" not in member.avatar_url_as(static_format="png"):
            image = await Image.from_link(member.avatar_url_as(static_format="png", size=512))
            image_file = image.to_discord_file(filename="avatar.png")

            # try and keep mem leaks to a minimum
            image.close()

            await ctx.send(f"{member.name}'s Avatar", file=image_file)
        else:
            e = discord.Embed(
                title=f"{member.name}'s Avatar",
                color=self.bot.color
            )
            e.set_image(
                url=member.avatar_url_as(static_format="png")
            )
            await ctx.send(embed=e)

        await ctx.message.remove_reaction(self.bot.loading_emoji, ctx.me)

    @commands.command(name="ping", aliases=['ms'])
    async def _ping_command(self, ctx):
        """
        Return the ping for the bot.
        It contains the Web Socket ping, the Round Trip ping, and the Response Time ping.
        All pings are measured in milliseconds and are rounded to the 100th place.
        """
        ws = round(self.bot.latency * 1000, 2)
        a = time.perf_counter()
        msg = await ctx.send(".")
        b = time.perf_counter()
        z = b - a
        await msg.edit(content="..")
        c = time.perf_counter()
        y = b - a
        await msg.edit(content="...")
        d = time.perf_counter()
        x = c - d
        await msg.delete()
        rtt = round(sum([z*1000, y*1000, x*1000]))
        m = time.perf_counter()
        await ctx.trigger_typing()
        rsp = round((time.perf_counter() - m)*1000)

        e = discord.Embed(
            title="Ping",
            color=self.bot.color
        )
        e.set_thumbnail(
            url=ctx.me.avatar_url_as(static_format="png", size=64)
        )
        e.add_field(
            name="Web Socket",
            value=f"{ws}ms",
            inline=False
        )
        e.add_field(
            name="Round Trip",
            value=f"{rtt}ms",
            inline=False
        )
        e.add_field(
            name="Response Time",
            value=f"{rsp}ms",
            inline=False
        )

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Information(bot))
