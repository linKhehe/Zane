import traceback
import time

import asyncpg
from discord.ext import commands
import aiofiles

from zane.utils.formatting import TabularData, Plural


class Database(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        if getattr(bot.config, "db_credentials", None) is not None:
            bot.loop.create_task(self.setup_database(bot.config.db_credentials))

    async def setup_database(self, credentials):
        db = await asyncpg.create_pool(**credentials)
        async with aiofiles.open("setup.sql") as sql:
            await db.execute(await sql.read())

        self.bot.db = db

    # https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py#L208-L249
    @commands.command(hidden=True)
    @commands.is_owner()
    async def sql(self, ctx, *, query: str):
        is_multistatement = query.count(';') > 1
        if is_multistatement:
            # fetch does not support multiple statements
            strategy = self.bot.db.execute
        else:
            strategy = self.bot.db.fetch

        try:
            start = time.perf_counter()
            results = await strategy(query)
            dt = (time.perf_counter() - start) * 1000.0
        except Exception:
            return await ctx.send(f'```py\n{traceback.format_exc()}\n```')

        rows = len(results)
        if is_multistatement or rows == 0:
            return await ctx.send(f'`{dt:.2f}ms: {results}`')

        headers = list(results[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in results)
        render = table.render()

        fmt = f'```\n{render}\n```\n*Returned {Plural(row=rows)} in {dt:.2f}ms*'
        if len(fmt) > 2000:
            fp = io.BytesIO(fmt.encode('utf-8'))
            await ctx.send('Too many results...', file=discord.File(fp, 'results.txt'))
        else:
            await ctx.send(fmt)


def setup(bot):
    bot.add_cog(Database(bot))
