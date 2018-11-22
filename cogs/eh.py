import sys
import traceback

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

        if isinstance(exception, commands.CommandOnCooldown):
            try:
                await ctx.send(f"You are on a cooldown. You can retry in {humanize.naturaltime(exception.retry_after)}.")
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
                await ctx.message.add_reaction("❌")
            except discord.Forbidden:
                try:
                    await ctx.send("This command is owner only.")
                except discord.Forbidden:
                    pass

        if isinstance(exception, commands.MissingPermissions):
            ctx.command.reset_cooldown(ctx)
            try:
                await ctx.send(str(exception))
            except discord.Forbidden:
                pass

        ctx.command.reset_cooldown(ctx)

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
