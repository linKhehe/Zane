import time
import asyncio
import traceback

import aioredis
from discord.ext import commands


class Redis(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.loop.create_task(self.setup_redis())

    async def setup_redis(self):
        redis = await asyncio.wait_for(aioredis.create_redis_pool(
            self.bot.redis_url,
            password=self.bot.redis_pass
        ), timeout=5)
        self.bot.redis = redis

    @commands.command(name="redis", hidden=True)
    @commands.is_owner()
    async def redis(self, ctx, method: str, *redis_args):
        try:
            start = time.perf_counter()
            dirty_out = await self.bot.redis.execute(method, *redis_args)
            out = getattr(dirty_out, "decode", dirty_out.__str__)()
            duration = (time.perf_counter() - start) * 1000.0
        except:
            return await ctx.send(f'```py\n{traceback.format_exc()}\n```')

        await ctx.send(f"*{round(duration, 2)}ms:* `{out}`")


def setup(bot):
    bot.add_cog(Redis(bot))
