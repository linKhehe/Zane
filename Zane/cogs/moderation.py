import asyncio
import discord
from discord.ext import commands


class Moderation:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="kick"
    )
    @commands.has_permissions(
        kick_members=True
    )
    async def _kick_command(self, ctx, member: discord.Member):
        """
        Kick a member from the server.
        """
        await member.kick(reason=f"Kick requested by {ctx.author}.")

        e = discord.Embed(
            title=f"Kicked: {member.name}",
            description=f"{member.name} was kicked from the server."
        )
        e.set_thumbnail(
            url=member.avatar_url_as(static_format="png", size=64)
        )

        await ctx.send(embed=e)

    @commands.command(
        name="ban"
    )
    @commands.has_permissions(
        ban_members=True
    )
    async def _ban_command(self, ctx, member: discord.Member, time: int = False):
        """
        Ban a member from the server.
        You can use the time argument to specify then the member should be unbanned in seconds.
        """
        if time <= 0:
            raise commands.BadArgument("An invalid argument was passed. The time argument can't be negative or 0.")

        await member.ban(reason=f"Ban requested by {ctx.author}.")

        e = discord.Embed(
            title=f"Banned: {member.name}",
            description=f"{member.name} was banned from the server.",
            color=self.bot.color
        )
        e.set_thumbnail(
            url=member.avatar_url_as(static_format="png", size=64)
        )

        await ctx.send(embed=e)

        if time:
            await asyncio.sleep(time)
            await member.unban(reason="Ban timer elapsed.")
            try:
                e = discord.Embed(
                    title=f"Unbanned: {member.name}",
                    description=f"You have been unbanned in {ctx.guild.name}.",
                    color=self.bot.color
                )
                e.set_thumbnail(
                    url=ctx.guild.icon_url
                )
                await member.send(embed=e)
            except discord.Forbidden:
                pass

    @commands.command(
        name="mute"
    )
    @commands.has_permissions(
        manage_channels=True
    )
    async def _mute_command(self, ctx, member: discord.Member, time: int = False):
        """
        Mute a member in all text/voice channels.
        You can use the time argument to specify then the member should be unmuted in seconds.
        """
        success_channels = []
        for channel in ctx.guild.channels:
            try:
                if isinstance(channel, discord.channel.TextChannel):
                    await channel.set_permissions(
                        member,
                        overwrite=discord.PermissionOverwrite(
                            send_messages=False
                        )
                    )
                    success_channels.append(channel.name)
                elif isinstance(channel, discord.channel.VoiceChannel):
                    await channel.set_permissions(
                        member,
                        overwrite=discord.PermissionOverwrite(
                            speak=False
                        )
                    )
                    success_channels.append(channel.name)
            except discord.Forbidden:
                pass

        e = discord.Embed(
            title=f"Muted: {member.name}",
            description=f"I muted {member.name} in the \
{len(success_channels)} channel(s) that I have permissions to mute in!",
            color=self.bot.color
        )
        e.set_thumbnail(
            url=member.avatar_url_as(static_format="png", size=64)
        )

        await ctx.send(embed=e)

        if time:
            await asyncio.sleep(time)
            for channel in ctx.guild.channels:
                try:
                    if isinstance(channel, discord.channel.TextChannel):
                        await channel.set_permissions(
                            member,
                            overwrite=None
                        )
                    elif isinstance(channel, discord.channel.VoiceChannel):
                        await channel.set_permissions(
                            member,
                            overwrite=None
                        )
                except discord.Forbidden:
                    pass

            e = discord.Embed(
                title=f"Unmuted: {member.name}",
                description=f"I unmuted {member.name}.",
                color=self.bot.color
            )
            e.set_thumbnail(
                url=member.avatar_url_as(static_format="png", size=64)
            )

            await ctx.send(member.mention, embed=e)

    @commands.command(
        name="unmute"
    )
    @commands.has_permissions(
        manage_channels=True
    )
    async def _unmute_command(self, ctx, member: discord.Member):
        """
        Unmute a member.
        """
        for channel in ctx.guild.channels:
            try:
                if isinstance(channel, discord.channel.TextChannel):
                    await channel.set_permissions(
                        member,
                        overwrite=None
                    )
                elif isinstance(channel, discord.channel.VoiceChannel):
                    await channel.set_permissions(
                        member,
                        overwrite=None
                    )
            except discord.Forbidden:
                pass

        e = discord.Embed(
            title=f"Unmuted: {member.name}",
            description=f"I unmuted {member.name}.",
            color=self.bot.color
        )
        e.set_thumbnail(
            url=member.avatar_url_as(static_format="png", size=64)
        )

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Moderation(bot))
