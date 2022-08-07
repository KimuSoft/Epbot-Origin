"""
    <info.py>
    간단한 정보가
"""

import os

import discord

# 필수 임포트
from discord.commands import slash_command
from discord.ext import commands

# 부가 임포트
from config import SLASH_COMMAND_REGISTER_SERVER as SCRS
from classes.user import User
from utils import logger


class ShortInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="내정보", description="자신의 정보를 확인할 수 있어요!")
    async def profile(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        user = await User.fetch(ctx.author)
        embed = discord.Embed(title=ctx.author.display_name + "의 정보!", colour=0x4BC59F)
        embed.add_field(
            name="**현재 소지금**",
            value=f"**{user.money:,}💰**\n( 총 자산 {await user.get_all_money:,}💰 )",
            inline=True,
        )
        embed.add_field(
            name=f"**{ctx.author.display_name}님의 레벨**",
            value=f"**✒️ Lv. {user.level}**\n( ✨ **{user.exp:,}** )",
            inline=True,
        )
        if user.biggest_name:
            embed.add_field(
                name="**오늘의 최고 월척!**",
                value=f"🐟 **{user.biggest_name}** ({user.biggest_size}cm)",
                inline=False,
            )
        await ctx.respond(embed=embed)

    # @slash_command(name="계절", description="이 낚시터(채널)의 계절을 알려줘요!")
    # async def 계절(self, ctx):
    #     room = await Room.fetch(ctx.channel)
    #     await ctx.respond(content=f"`이 낚시터의 계절 : {Constants.SEASON_KR[room.season]}`")
    #
    # @slash_command(name="지형", description="이 낚시터(채널)의 지형을 알려줘요!")
    # async def 지형(self, ctx):
    #     room = await Room.fetch(ctx.channel)
    #     await ctx.respond(content=f"`이 낚시터의 지형 : {Constants.BIOME_KR[room.biome]}`")
    #
    # @slash_command(name="돈", description="지금 가지고 계신 돈을 알려줘요!")
    # async def 돈(self, ctx):
    #     user = await User.fetch(ctx.author)
    #     await ctx.respond(content=f"`소지금 : {user.money:,}💰`")
    #
    # @slash_command(name="명성", description="자신과 낚시터가 가지고 있는 명성을 알려줘요!")
    # async def 명성(self, ctx):
    #     user = await User.fetch(ctx.author)
    #     room = await Room.fetch(ctx.channel)
    #     await ctx.respond(
    #         content=f"`내 개인 명성 : ✨ {user.exp:,}\n이 낚시터의 명성 : ✨ {await room.get_exp():,}`"
    #     )
    #
    # @slash_command(name="청결도", description="이 낚시터(채널)의 청결도를 보여줘요!")
    # async def 청결도(self, ctx):
    #     room = await Room.fetch(ctx.channel)
    #     await ctx.respond(content=f"`이 낚시터의 청결도 : 🧹 {room.cleans:,}`")
    #
    # @slash_command(name="땅값", description="이 낚시터(채널)의 땅값을 보여줘요!")
    # async def 땅값(self, ctx):
    #     room = await Room.fetch(ctx.channel)
    #     await ctx.respond(
    #         content=f"`이 낚시터의 땅값 : {room.land_value:,} 💰\n이 낚시터의 최소 매입가 : {room.min_purchase} 💰`"
    #     )
    #
    # @slash_command(name="티어", description="이 낚시터(채널)의 티어를 보여줘요!")
    # async def 티어(self, ctx):
    #     room = await Room.fetch(ctx.channel)
    #     await ctx.respond(content=f"`이 낚시터의 레벨(티어) : {room.tier}`")


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(ShortInfoCog(bot))
