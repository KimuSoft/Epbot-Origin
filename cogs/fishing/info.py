"""
    <info.py>
    간단한 정보가
"""

# 필수 임포트
from discord.ext import commands
import discord
import os
from utils import logger

# 부가 임포트
from classes.room import Room
from classes.user import User
from constants import Constants


class ShortInfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def 계절(self, ctx):
        room = Room(ctx.channel)
        await ctx.send(
            content=f"`이 낚시터의 계절 : {Constants.SEASON_KR[room.season]}`",
            reference=ctx.message,
        )

    @commands.command()
    async def 지형(self, ctx):
        room = Room(ctx.channel)
        await ctx.send(
            content=f"`이 낚시터의 지형 : {Constants.BIOME_KR[room.biome]}`",
            reference=ctx.message,
        )

    @commands.command()
    async def 돈(self, ctx):
        user = User(ctx.author)
        await ctx.send(content=f"`소지금 : {user.money:,}💰`", reference=ctx.message)

    @commands.command()
    async def 명성(self, ctx):
        user = User(ctx.author)
        room = Room(ctx.channel)
        await ctx.send(
            content=f"`내 개인 명성 : ✨ {user.exp:,}\n이 낚시터의 명성 : ✨ {room.exp:,}`",
            reference=ctx.message,
        )

    @commands.command()
    async def 청결도(self, ctx):
        room = Room(ctx.channel)
        await ctx.send(
            content=f"`이 낚시터의 청결도 : 🧹 {room.cleans:,}`", reference=ctx.message
        )

    @commands.command()
    async def 땅값(self, ctx):
        room = Room(ctx.channel)
        await ctx.send(
            content=f"`이 낚시터의 땅값 : {room.land_value:,} 💰\n이 낚시터의 최소 매입가 : {room.min_purchase} 💰`",
            reference=ctx.message,
        )

    @commands.command()
    async def 티어(self, ctx):
        room = Room(ctx.channel)
        await ctx.send(content=f"`이 낚시터의 레벨(티어) : {room.tier}`", reference=ctx.message)

    @commands.command()
    async def 아이디(self, ctx):
        await ctx.send(
            content=(
                f"`이 낚시터의 ID : 📑 {ctx.channel.id} ( {ctx.channel.name} )\n"
                f"내 디스코드 ID : 📑 {ctx.author.id} ( {ctx.author.name} )`"
            ),
            reference=ctx.message,
        )

    @commands.command()
    async def 내정보(self, ctx):
        user = User(ctx.author)
        embed = discord.Embed(title=ctx.author.display_name + "의 정보!", colour=0x4BC59F)
        embed.add_field(
            name="**현재 소지금**",
            value=f"**{user.money:,}💰**\n( 총 자산 {user.all_money:,}💰 )",
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
        await ctx.send(embed=embed)


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(ShortInfoCog(bot))
