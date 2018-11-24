import sys
import traceback
import datetime

import humanize
import discord
from discord.ext import commands


class ErrorHandler:

    def __init__(self, bot):
        self.bot = bot
        self.ignored = commands.CommandNotFound

    def _error_formatter(self, title: str, message: str):
        ret = discord.Embed(
            title=title,
            description=message,
            color=self.bot.color
        )
        ret.set_footer(
            icon_url=self.bot.user.avatar_url_as(static_format="png", size=64)
        )
        return ret

    async def on_command_error(self, ctx, exception):
        if hasattr(ctx.command, 'on_error'):
            return

        exception = getattr(exception, 'original', exception)

        if isinstance(exception, self.ignored):
            pass

        if isinstance(exception, commands.CommandOnCooldown):
            try:
                retry_after = datetime.timedelta(seconds=exception.retry_after)
                retry_after = humanize.naturaltime(datetime.datetime.now() + retry_after)
                e = self._error_formatter("Error: Cooldown", f"You are on a cooldown. You can retry in {retry_after}.")
                return await ctx.send(embed=e)
            except discord.Forbidden:
                pass

        if isinstance(exception, commands.BadArgument):
            ctx.command.reset_cooldown(ctx)
            try:
                e = self._error_formatter("Error: Bad Argument", str(exception))
                await ctx.send(embed=e)
            except discord.Forbidden:
                pass

        if isinstance(exception, commands.NotOwner):
            ctx.command.reset_cooldown(ctx)
            try:
                return await ctx.message.add_reaction("❌")
            except discord.Forbidden:
                try:
                    e = self._error_formatter("Error: Owner Only", "This command is owner only.")
                    return await ctx.send(embed=e)
                except discord.Forbidden:
                    pass

        if isinstance(exception, commands.MissingPermissions):
            ctx.command.reset_cooldown(ctx)
            try:
                e = self._error_formatter("Error: Missing Permissions", str(exception))
                return await ctx.send(embed=e)
            except discord.Forbidden:
                pass

        if isinstance(exception, discord.Forbidden):
            ctx.command.reset_cooldown(ctx)
            try:
                e = self._error_formatter("Error: Im Missing Permissions For That", str(exception))
                return await ctx.send(embed=e)
            except discord.Forbidden:
                pass

        ctx.command.reset_cooldown(ctx)

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
