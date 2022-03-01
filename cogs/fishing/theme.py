# 필수 임포트
from discord.commands import slash_command
from discord.commands import Option
from discord.ext import commands
import discord
import os
import io
from utils import logger

# 부가 임포트
from classes.user import User, NoTheme
from utils.fish_card.fish_card import get_card


class ThemeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name = "테마", description="낚시카드의 테마를 선택하세요!")
    async def 테마(self, ctx, arg: str = None):
        user = User(ctx.author.id)
        if not arg:
            themes = user.themes_name
            themes[0] = themes[0] + " #사용 중"
            ntheme = []
            for idx, val in enumerate(themes):
                ntheme.append(f"{idx + 1}. {val}")

            ths = "\n".join(ntheme)
            return await ctx.respond(f"> **현재 보유 중인 테마** \n```cs\n{ths}```")
        if not str(arg).isdigit():
            return await ctx.respond("`이프야 테마 <바꿀 테마 번호>`")
        try:
            user.theme = user.themes[int(arg) - 1]
            return await ctx.respond(f"`❗ 낚시카드 테마를 '{user.themes_name[0]}'(으)로 변경했습니다.`")
        except NoTheme:
            await ctx.respond("`이프야 테마 <바꿀 테마 번호>`")
        except IndexError:
            await ctx.respond("`❗ 보유하고 있는 테마의 번호를 잘 확인해 보세요.`")

""" 오류 발생 (비활성화)
    @commands.cooldown(1, 3, commands.BucketType.user)
    @slash_command(name = "미리보기", guild_ids = [742201063972667487], description="낚시카드의 테마를 미리 경헙해보세요")
    async def 미리보기(self, ctx, arg:str = None):
        if not arg:
            theme = User(ctx.author.id).theme
        else:
            theme = arg

        dummy_user = ExampleUser(theme)
        dummy_room = ExampleRoom()
        dummy_fish = ExampleFish()

        try:
            image = await get_card(dummy_fish, dummy_room, dummy_user)
        except AttributeError:
            return await ctx.send("`❗ 존재하지 않는 테마입니다.`")
        with io.BytesIO() as image_binary:  # 낚시카드 전송
            image.save(image_binary, "PNG")
            image_binary.seek(0)
            try:
                await ctx.send(
                    file=discord.File(fp=image_binary, filename="fishcard.png"),
                    reference=ctx.message,
                )
            except discord.errors.HTTPException:
                logger.warn("답장 오류 발생")
                await ctx.send(
                    file=discord.File(fp=image_binary, filename="fishcard.png")
                )
"""

def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(ThemeCog(bot))


class ExampleUser:
    def __init__(self, theme):
        self.theme = theme

    id = 123456789
    name = "유저 이름"


class ExampleRoom:
    id = 123456789
    owner_id = 123456789
    name = "낚시터 이름"
    fee = 5
    maintenance = 5
    bonus = 5


class ExampleFish:
    id = 123
    name = "물고기"
    rarity = 1
    eng_name = "Fish"
    length = 12345
    average_cost = 654321
    average_length = 54321
    _cost = 123456

    def fee(self, user, room):
        if room.owner_id == user.id:
            return 0
        else:
            return -1 * int(self.cost() * (room.fee / 100))

    def maintenance(self, room):
        return -1 * int(self.cost() * (room.maintenance / 100))

    def bonus(self):
        # 보너스는 상관없이 5%라 가정
        return int(self.cost() * 0.05)

    def cost(self):
        return self._cost
