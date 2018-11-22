import time

import psutil
import discord
from discord.ext import commands


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
    async def userinfo(self, ctx, member: discord.Member = None):
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
    async def guildinfo(self, ctx):
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
            "stats",
            "ne"
        ]
    )
    async def stats(self, ctx):
        """List current stats on the bot."""
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
            value=f"{round(self.bot.latency, 2)}ms"
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

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Information(bot))
