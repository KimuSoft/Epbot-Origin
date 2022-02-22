"""
    <etc.py>
    미분류 명령어를 여기에 넣어요!
"""

# 필수 임포트
from discord.ext import commands
import discord
import os

# 부가 임포트
from classes.user import User
from constants import Constants
from utils import logger


VERSION = Constants.VERSION
INFORMATION = (
    "[공식 도움말 낚시 편](https://blog.naver.com/hon20ke/222241633386)"
    "\n[공식 사이트 도움말](https://epbot.kro.kr/)"
    "\n※ 대부분의 물고기 데이터는 국립수산과학원 수산생명자원정보센터의 데이터를 참고하였습니다."
)


class EtcCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 핑 하면 퐁 하면서 봇의 레이턴시(지연 시간)을 알려 주는 예시 명령어야!

    @commands.cooldown(3, 10)
    @commands.command()
    async def 핑(self, ctx):
        latency = int(self.bot.latency * 1000)
        wd = await ctx.send(f"퐁! 🏓\n`지연 시간 : {latency}ms (실제 지연시간 계산 중...)`")

        real_latency = int((wd.created_at - ctx.message.created_at).microseconds / 1000)
        await wd.edit(content=f"퐁! 🏓\n`지연 시간 : {latency}ms (실제 지연시간 {real_latency}ms)`")

    @commands.command()
    async def 도움말(self, ctx):
        embed = discord.Embed(title="이프의 도움말", description=INFORMATION, colour=0x4BC59F)
        embed.set_footer(
            text="제작 키뮤소프트(키뮤#8673, Hollume_#3814) / 더욱 자세한 정보가 궁금하다면 '이프야 정보'"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def 정보(self, ctx):
        embed = discord.Embed(title="커여운 검열삭제 장인 이프!", colour=0x4BC59F)
        embed.add_field(
            name="개발ㆍ운영 - 키뮤소프트(코로, 키뮤)",
            value=f"이프의 검열 대상 서버 : {len(self.bot.guilds)}곳",
            inline=False,
        )
        embed.add_field(
            name="공식 디스코드 서버", value="[키뮤소프트 디스코드](https://discord.gg/XQuexpQ)"
        )
        embed.add_field(
            name=f"현재 이프 버전 : {VERSION}",
            value="`※ 최근 업데이트된 내용이 궁금하다면 공식 디스코드 서버에 방문해 보세요!`",
            inline=False,
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def 지워(self, ctx, *args):
        if User(ctx.author).admin:
            pass
        elif not ctx.author.permissions_in(ctx.channel).manage_roles:
            await ctx.send("마력을 더욱 쌓고 오거라!!")
            return None
        if args == ():
            await ctx.send("`이프야 지워 <!숫자>`")
            return None
        try:
            limit = int(args[0]) + 1
        except ValueError:
            await ctx.send("숫자를 적어야지!")
            return None
        if limit <= 101:
            await ctx.channel.purge(limit=limit)
            await ctx.send(
                f"{ctx.author.mention}님, {limit-1}개의 메세지를 지웠어요!", delete_after=4
            )
        else:
            await ctx.send("마력을 더어어어어 더욱 쌓고 오거라!!")


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    logger.info(f"버전 정보 : 이프 V{VERSION}")
    bot.add_cog(EtcCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
