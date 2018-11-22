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
                return await ctx.send(f"You are on a cooldown. You can retry in {retry_after}.")
            except discord.Forbidden:
                pass

        if isinstance(exception, commands.BadArgument):
            ctx.command.reset_cooldown(ctx)
            try:
                await ctx.send(str(exception))
            except discord.Forbidden:
                pass

        if isinstance(exception, commands.NotOwner):
            ctx.command.reset_cooldown(ctx)
            try:
                return await ctx.message.add_reaction("❌")
            except discord.Forbidden:
                try:
                    return await ctx.send("This command is owner only.")
                except discord.Forbidden:
                    pass

        if isinstance(exception, commands.MissingPermissions):
            ctx.command.reset_cooldown(ctx)
            try:
                return await ctx.send(str(exception))
            except discord.Forbidden:
                pass

        ctx.command.reset_cooldown(ctx)

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(exception), exception, exception.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
