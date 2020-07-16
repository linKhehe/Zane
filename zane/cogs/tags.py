import random
from typing import AsyncGenerator

import aioredis
import discord
from discord.ext import commands
from discord.ext import menus


class TagName(commands.clean_content):
    """
    The following applies to this class.

    The MIT License (MIT)

    Copyright (c) 2015 Rapptz

    Permission is hereby granted, free of charge, to any person obtaining a
    copy of this software and associated documentation files (the "Software"),
    to deal in the Software without restriction, including without limitation
    the rights to use, copy, modify, merge, publish, distribute, sublicense,
    and/or sell copies of the Software, and to permit persons to whom the
    Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
    """

    def __init__(self, *, lower=False):
        self.lower = lower
        super().__init__()

    async def convert(self, ctx, argument):
        converted = await super().convert(ctx, argument)
        lower = converted.lower().strip()

        if not lower:
            raise commands.BadArgument("You must name your tag.")

        if len(lower) > 32:
            raise commands.BadArgument("Tag name is a maximum of 32 characters.")

        first_word, _, _ = lower.partition(' ')

        # get tag command.
        root = ctx.bot.get_command('tag')
        if first_word in root.all_commands:
            raise commands.BadArgument('This tag name starts with a reserved word.')

        return converted if not self.lower else lower


class TagPaginator(menus.AsyncIteratorPageSource):

    def __init__(self, generator, title):
        self.title = title
        super().__init__(generator, per_page=32)

    async def format_page(self, menu, entries):
        start = menu.current_page * self.per_page
        return discord.Embed(
            title=f"{self.title}: Page {menu.current_page + 1}",
            color=random.randint(0, 16_777_215),
            description="\n".join(f"**{i + 1}.** {entry}" for i, entry in enumerate(entries, start=start))
        )


# noinspection PyTypeChecker
class Tags(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @property
    def redis(self) -> aioredis.Redis:
        return self.bot.redis

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            await ctx.send(str(error))
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(str(error).capitalize())
        else:
            raise error

    @staticmethod
    def decode(raw):
        if getattr(raw, "decode", False):
            return raw.decode()
        return raw

    async def create_tag(self, guild_id: int, name: str, content: str = None, author_id: int = None):
        await self.redis.zadd(guild_id, 0, name)
        await self.redis.hmset(f"{guild_id}:{name}", "content", content, "author_id", author_id)
        await self.redis.sadd(f"{guild_id}:{author_id}", name)
        await self.redis.sadd(f"{guild_id}:all", name)

    async def tag_exists(self, guild_id: int, name: str) -> bool:
        raw = await self.redis.exists(f"{guild_id}:{name}")
        return bool(self.decode(raw))

    async def get_tag_content(self, guild_id: int, name: str) -> str:
        raw = await self.redis.hget(f"{guild_id}:{name}", "content")
        return self.decode(raw)

    async def get_tag_author(self, guild_id: int, name: str) -> int:
        raw = await self.redis.hget(f"{guild_id}:{name}", "author_id")
        return int(self.decode(raw))

    async def get_tag_usage_count(self, guild_id: int, name: str) -> int:
        raw = await self.redis.zscore(guild_id, name)
        return int(self.decode(raw))

    async def get_tag_usage_rank(self, guild_id: int, name: str) -> int:
        raw = await self.redis.zrevrank(guild_id, name)
        return int(self.decode(raw)) + 1

    async def get_all_authors_tags(self, guild_id: int, author_id: int) -> AsyncGenerator[str]:
        cur = b'0'
        while cur:
            cur, tags = await self.redis.sscan(f"{guild_id}:{author_id}", cursor=cur)
            for tag in tags:
                yield tag.decode()

    async def get_all_tags(self, guild_id: int) -> AsyncGenerator[str]:
        cur = b'0'
        while cur:
            cur, tags = await self.redis.sscan(f"{guild_id}:all", cursor=cur)
            for tag in tags:
                yield tag.decode()

    async def delete_tag(self, guild_id: int, name: str):
        author_id = await self.get_tag_author(guild_id, name)
        await self.redis.zrem(guild_id, name)
        await self.redis.hdel(f"{guild_id}:{name}", "content", "author_id")
        await self.redis.srem(f"{guild_id}:{author_id}", name)
        await self.redis.srem(f"{guild_id}:all", name)

    async def set_tag_content(self, guild_id: int, name: str, content: str):
        await self.redis.hset(f"{guild_id}:{name}", "content", content)

    async def is_tag_owner(self, user: discord.Member, name: str) -> bool:
        author_id = await self.get_tag_author(user.guild.id, name)
        return author_id == user.id

    async def increment_tag_usage(self, guild_id: int, name: str, by: int = 1):
        await self.redis.zincrby(guild_id, by, name)

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, name: TagName):
        if not await self.tag_exists(ctx.guild.id, name):
            return await ctx.send("Tag doesnt exist.")

        await self.increment_tag_usage(ctx.guild.id, name)
        await ctx.send(await self.get_tag_content(ctx.guild.id, name))

    @tag.command()
    async def create(self, ctx, name: TagName, *, content: commands.clean_content = ""):
        if await self.tag_exists(ctx.guild.id, name):
            return await ctx.send("That tag already exists. Sorry.")
        elif content == "" and not ctx.message.attachments:
            raise commands.MissingRequiredArgument("You must either provide text content or attach a file.")

        if ctx.message.attachments:
            for attachment in ctx.message.attachments:
                content += "\n" + str(attachment.url)

        await self.create_tag(ctx.guild.id, name, content=content, author_id=ctx.author.id)
        await ctx.send("Created.")

    @tag.command()
    async def edit(self, ctx, name: TagName, *, content: commands.clean_content):
        if not await self.is_tag_owner(ctx.author, name):
            return await ctx.send("You can only edit your own tags.")
        if not await self.tag_exists(ctx.guild.id, name):
            return await ctx.send("Tag doesnt exist.")

        await self.set_tag_content(ctx.guild.id, name, content)
        await ctx.send("Edited.")

    @tag.command()
    async def delete(self, ctx, name: TagName):
        if not self.is_tag_owner(ctx.author, name):
            return await ctx.send("You can only delete your own tags.")
        if not await self.tag_exists(ctx.guild.id, name):
            return await ctx.send("Tag doesnt exist.")

        await self.delete_tag(ctx.guild.id, name)
        await ctx.send("Deleted")

    @tag.command()
    async def info(self, ctx, name: TagName):
        if not await self.tag_exists(ctx.guild.id, name):
            return await ctx.send("Tag doesnt exist.")

        rank = str(await self.get_tag_usage_rank(ctx.guild.id, name))
        suffix = "th"
        if rank.endswith("1"):
            suffix = "st"
        elif rank.endswith("2"):
            suffix = "nd"
        elif rank.endswith("3"):
            suffix = "rd"

        embed = discord.Embed(
            title=f"Info: {name}",
            color=self.bot.color,
        ).add_field(
            name="Author",
            value=f"<@{await self.get_tag_author(ctx.guild.id, name)}>"
        ).add_field(
            name="Usage",
            value=f"{await self.get_tag_usage_count(ctx.guild.id, name)} time(s)"
        ).add_field(
            name="Usage Rank",
            value=rank + suffix
        )

        await ctx.send(embed=embed)

    @tag.command()
    async def all(self, ctx):
        pages = menus.MenuPages(
            source=TagPaginator(self.get_all_tags(ctx.guild.id), "All Guild Tags"),
            clear_reactions_after=True
        )
        await pages.start(ctx)

    @tag.command()
    async def list(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        pages = menus.MenuPages(
            source=TagPaginator(self.get_all_authors_tags(ctx.guild.id, member.id), f"{member}'s Tags"),
            clear_reactions_after=True
        )
        await pages.start(ctx)


def setup(bot):
    bot.add_cog(Tags(bot))
