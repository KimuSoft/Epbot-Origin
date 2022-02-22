# 필수 임포트
from discord.ext import commands
import os

from constants import Constants
from utils import logger

# 부가 임포트
from classes.room import Room
from classes.user import User
from utils.on_working import administrator


class FishAdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @administrator()
    async def 테스트(self, ctx):
        import discord

        embed = discord.Embed(title="테스트")
        embed.set_image(
            url="https://media.discordapp.net/attachments/804578554439270400/856481542749945867/fishcard.png"
        )
        # embed.set_image(url='https://www.nifs.go.kr/frcenter/common/species_image_download.jsp?mf_dogam_id=DG0102&mf_tax_id=MF0008776')
        await ctx.send(embed=embed, reference=ctx.message)

    @commands.command()
    @administrator()
    async def 지형변경(self, ctx, arg1=0):
        Room(ctx.channel).biome = int(arg1)
        await ctx.send(
            content=f"여기의 지형을 '{Constants.BIOME_KR[arg1]}'(으)로 바꿔써!",
            reference=ctx.message,
        )

    @commands.command()
    @administrator()
    async def 명성설정(self, ctx, arg1=-1):
        if arg1 == -1:
            await ctx.send("`이프야 명성설정 (값)`")
            return None
        room = Room(ctx.channel)
        origin_exp = room.exp
        room.exp = int(arg1)
        await ctx.send(
            content=f"여기의 명성을 `{origin_exp}`에서 `{arg1}`(으)로 바꿔써!", reference=ctx.message
        )

    @commands.command()
    @administrator()
    async def 명성부여(self, ctx, arg1=-1):
        if arg1 == -1:
            await ctx.send("`이프야 명성부여 (값)`")
            return None
        room = Room(ctx.channel)
        origin_exp = room.exp
        room.exp += int(arg1)
        await ctx.send(
            content=f"여기의 명성을 `{origin_exp}`에서 `{room.exp:,}`(으)로 바꿔써!",
            reference=ctx.message,
        )

    @commands.command()
    @administrator()
    async def 돈부여(self, ctx, *args):
        if (
            len(args) < 2
            or not args[1].isdigit()
            or not args[0].replace("<@!", "").replace(">", "").isdigit()
        ):
            await ctx.send("`이프야 돈부여 <언급> <액수>`")
            return None

        user = User(int(args[0].replace("<@!", "").replace(">", "")))
        user.give_money(int(args[1]))
        await ctx.send(f"<@!{user.id}>가 `{user.money:,}💰` 가 됐어!")


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(FishAdminCog(bot))
