"""
    <etc.py>
    미분류 명령어를 여기에 넣어요!
"""

# 필수 임포트
import datetime
import os

import discord
from discord.commands import slash_command
from discord.ext import commands

# 부가 임포트
from classes.user import User
from config import SLASH_COMMAND_REGISTER_SERVER as SCRS
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
    @slash_command(name="핑", description="이프의 현재 속도를 알려줘요!")
    async def 핑(self, ctx: discord.ApplicationContext):
        now = datetime.datetime.now()

        latency = int(self.bot.latency * 1000)
        i = await ctx.respond(
            f"퐁! 🏓\n`지연 시간 : {latency}ms (실제 지연시간 계산 중...)`",
        )

        wd = await i.original_message()

        real_latency = int(
            (wd.created_at.replace(tzinfo=None) - now).microseconds / 1000
        )
        await ctx.edit(
            content=f"퐁! 🏓\n`지연 시간 : {latency}ms (실제 지연시간 {real_latency}ms)`"
        )

    @slash_command(name="도움말", description="이프의 사용법을 알려줘요!")
    async def 도움말(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="이프의 도움말", description=INFORMATION, colour=0x4BC59F)
        embed.set_footer(
            text="제작 키뮤소프트(키뮤#8673, Hollume_#3814) / 더욱 자세한 정보가 궁금하다면 '/정보'"
        )
        await ctx.respond(embed=embed)

    @slash_command(name="정보", description="이프의 정보를 알려줘요!")
    async def 정보(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="커여운 검열삭제 장인 이프!", colour=0x4BC59F)
        embed.add_field(
            name="개발ㆍ운영 - 키뮤소프트(코로, 키뮤)",
            value=f"이프의 검열 대상 서버 : {len(self.bot.guilds)}곳",
            inline=False,
        )

        embed.add_field(
            name="이프1 코드 공개 저장소",
            value="https://github.com/KimuSoft/epbot-origin",
            inline=False,
        )
        embed.add_field(name="기여자 목록", value="KOI#4182(슬래시 커맨드)", inline=False)

        embed.add_field(
            name="공식 디스코드 서버", value="[키뮤소프트 디스코드](https://discord.gg/XQuexpQ)"
        )

        embed.add_field(
            name=f"현재 이프 버전 : {VERSION}",
            value="`※ 최근 업데이트된 내용이 궁금하다면 공식 디스코드 서버에 방문해 보세요!`",
            inline=False,
        )
        await ctx.respond(embed=embed)

    @slash_command(name="지워", description="메세지를 지워요!")
    async def 지워(self, ctx: discord.ApplicationContext, limit: int):
        if (await User.fetch(ctx.author)).admin:
            pass
        elif not ctx.author.permissions_in(ctx.channel).manage_roles:
            await ctx.respond("마력을 더욱 쌓고 오거라!!")
            return None
        limit += 1
        if limit <= 101:
            await ctx.channel.purge(limit=limit)
            await ctx.respond(
                context=f"{ctx.author.mention}님, {limit-1}개의 메세지를 지웠어요!", delete_after=4
            )
        else:
            await ctx.respond("마력을 더어어어어 더욱 쌓고 오거라!!")


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    logger.info(f"버전 정보 : 이프 V{VERSION}")
    bot.add_cog(EtcCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
