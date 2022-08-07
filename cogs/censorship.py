# 필수 임포트
import os

import discord
from discord.commands import slash_command
from discord.ext import commands

from config import SLASH_COMMAND_REGISTER_SERVER as SCRS
from utils import logger

# 부가 임포트
from utils import tag as eptag


class CensorshipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="검열", description="검열 기능에 대한 설명입니다!", guild_ids=SCRS)
    async def 검열(self, ctx: discord.ApplicationContext):
        embed = discord.Embed(title="검열 기능은 어디로 갔나요?", colour=0x4BC59F)
        embed.add_field(
            name="왜 없어졌나요?",
            value="디스코드의 메세지 인텐트 정책에 의거해, 2022.09.01 부터는 검열 기능이 정상적으로 작동하지 않을 예정입니다.",
            inline=False,
        )
        embed.add_field(
            name="그럼 검열은 어디에서 해야 하나요?",
            value="키뮤소프트가 새롭게 개발중인 봇 `위브`는 검열을 위한 봇입니다! 검열 기능은 위브로 이관될 예정이니 많은 관심 부탁드릴게요!",
            inline=False,
        )
        await ctx.respond(embed=embed)

    @slash_command(name="태그", description="이 채널의 태그를 확인하세요!", guild_ids=SCRS)
    async def 태그(self, ctx: discord.ApplicationContext):
        tags = eptag.tag_to_korean(eptag.get_tags(ctx.channel))

        embed = discord.Embed(title="이 채널의 태그", colour=0x4BC59F)
        embed.add_field(
            name="총 {}개".format(len(tags)), value="#" + " #".join(tags), inline=True
        )
        await ctx.respond(embed=embed)


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(CensorshipCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
