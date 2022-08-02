# 필수 임포트
import discord
from discord.ext import commands
from discord.commands import slash_command
from discord.commands import Option
import os

import config
from constants import Constants
from utils import logger

# 부가 임포트
from classes.room import Room
from classes.user import User
from utils.on_working import administrator


class FishAdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="디버그",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        description="관리자 디버그용 도구입니다. (관리자 전용)",
    )
    @administrator()
    async def test(
        self,
        ctx,
        command_type: Option(
            str, "관리자 명령어 종류", choices=["지형변경", "명성설정", "명성부여", "돈부여", "기타"]
        ),
        num: int = None,
        user: discord.Member = None,
    ):
        room = await Room.fetch(ctx.channel)
        if command_type == "지형변경":
            await room.set_biome(num)
            await ctx.respond(content=f"여기의 지형을 '{Constants.BIOME_KR[num]}'(으)로 바꿔써!")

        elif command_type == "명성설정":
            origin_exp = await room.get_exp()
            await room.set_exp(num)
            await ctx.respond(content=f"여기의 명성을 `{origin_exp}`에서 `{num}`(으)로 바꿔써!")

        elif command_type == "명성부여":
            origin_exp = await room.get_exp()
            room.set_exp(origin_exp + num)
            await ctx.respond(
                content=f"여기의 명성을 `{origin_exp}`에서 `{await room.get_exp():,}`(으)로 바꿔써!"
            )

        elif command_type == "돈부여":
            user = await User.fetch(user)
            await user.give_money(num)
            await ctx.respond(f"<@!{user.id}>가 `{user.money:,}💰` 가 됐어!")

        else:
            await ctx.respond("Hello, This is KOI3125 test command!")


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(FishAdminCog(bot))
