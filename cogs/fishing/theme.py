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
from classes.room import Room
from utils.fish_card.fish_card import get_card
from config import SLASH_COMMAND_REGISTER_SERVER as SCRS
from constants import Constants


class ThemeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="테마", description="낚시카드의 테마를 선택하세요!", guild_ids=SCRS)
    async def 테마(self, ctx):
        epUser = User(ctx.author)
        view = ThemeSelectView(epUser)
        await ctx.respond(content="골라바", view=view)

    # @slash_command(name="테마", description="낚시카드의 테마를 선택하세요!", guild_ids=SCRS)
    # async def 테마(self, ctx, theme_num: Option(str, "바꾸실 테마 번호를 입력해주세요!") = ""):
    #     user = User(ctx.author.id)
    #     if not theme_num:
    #         themes = user.themes_name
    #         themes[0] = themes[0] + " #사용 중"
    #         ntheme = []
    #         for idx, val in enumerate(themes):
    #             ntheme.append(f"{idx + 1}. {val}")

    #         ths = "\n".join(ntheme)
    #         return await ctx.respond(f"> **현재 보유 중인 테마** \n```cs\n{ths}```")
    #     if not str(theme_num).isdigit():
    #         return await ctx.respond("`이프야 테마 <바꿀 테마 번호>`")
    #     try:
    #         user.theme = user.themes[int(theme_num) - 1]
    #         return await ctx.respond(
    #             f"`❗ 낚시카드 테마를 '{user.themes_name[0]}'(으)로 변경했습니다.`"
    #         )
    #     except NoTheme:
    #         await ctx.respond("`이프야 테마 <바꿀 테마 번호>`")
    #     except IndexError:
    #         await ctx.respond("`❗ 보유하고 있는 테마의 번호를 잘 확인해 보세요.`")

    @slash_command(name="미리보기", guild_ids=SCRS, description="낚시카드의 테마를 미리 경헙해보세요")
    async def 미리보기(
        self,
        ctx,
        theme_id: Option(str, "미리보기할 테마 아이디를 입력해 주세요.") = None,
        rarity: Option(int, "미리보기할 테마 희귀도(0~4)를 입력해 주세요.") = 1,
    ):
        if not theme_id:
            theme = User(ctx.author.id).theme
        else:
            theme = theme_id

        if rarity < -1 or rarity > 5:
            return await ctx.respond("그런 희귀도는 업서!")

        dummy_user = ExampleUser(theme)
        dummy_user.theme = theme
        fish = Room(ctx.channel).randfish()
        fish.owner = dummy_user
        fish.rarity = rarity

        from .game import get_fishcard_image_file_from_url

        try:
            # 서버로부터 낚시카드 전송
            logger.debug("테스트: 서버로부터 낚시카드 전송")
            image = await get_fishcard_image_file_from_url(fish)
        except Exception as e:  # aiohttp.ClientConnectorError:
            logger.err(e)
            return await ctx.respond("낚시카드를 불러올 수 없어써!\n" + str(e))
        await ctx.respond(file=image, view=None)


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(ThemeCog(bot))


class ThemeSelect(discord.ui.Select):
    def __init__(self, epUser: User):
        options = []
        for i in Constants.THEMES:
            icon = "✅" if i["id"] in epUser.themes else "❌"
            if i["id"] == epUser.theme:
                label = i["name"] + " (사용 중)"

            label = i["name"] + " (미보유)" if i["id"] not in epUser.themes else label
            options.append(
                discord.SelectOption(
                    label=label, description=i["description"], emoji=icon
                )
            )

        super().__init__(
            placeholder="바꿀 테마를 선택하세요.",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        # Use the interaction object to send a response message containing
        # The user's favourite colour or choice. The self object refers to the
        # Select object, and the values attribute gets a list of the user's
        # selected options. We only want the first one.
        if "(미보유)" in self.values[0]:
            return await interaction.response.edit_message(
                content="미보유 테마야!", view=None
            )
        if "(사용 중)" in self.values[0]:
            return await interaction.response.edit_message(
                content="이미 이 테마를 사용하고 있어!", view=None
            )
        if self.values[0] not in [i["name"] for i in Constants.THEMES]:
            return await interaction.response.edit_message(content="으앙 오류", view=None)
        themeId = list(filter(lambda e: e["name"] == self.values[0], Constants.THEMES))[
            0
        ]["id"]
        epUser = User(interaction.user)
        print(epUser.theme)
        print(epUser.themes)
        epUser.theme = themeId
        print(epUser.theme)
        print(epUser.themes)
        return await interaction.response.edit_message(
            content=f"테마를 `{self.values[0]}`으로 바꿨어!", view=None
        )


class ThemeSelectView(discord.ui.View):
    def __init__(self, epUser: User):
        super().__init__()
        s = ThemeSelect(epUser)
        self.add_item(s)


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
