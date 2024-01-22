"""
    <fishing_game.py>
    낚시 본게임이 있는 Cog입니다
"""

import io
import os
import random

# 필수 임포트
import aiohttp
import asyncio
import discord
from discord.commands import slash_command
from discord.ext import commands
from discord.ui import View

from classes.fish import Fish
from classes.room import Room
from classes.user import User
from config import SLASH_COMMAND_REGISTER_SERVER as SCRS
from constants import Constants
from utils import logger
from utils import on_working

# 자체 낚시카드 생성 관련 임포트
from utils.fish_card import get_card_async

# 부가 임포트
from utils.util_box import rdpc


# 물고기 이미지 로드 관련 임포트(실험용)
# from utils.get_fish_img import get_image


class FishingGameCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="낚시", description="이프와 함께 물고기를 낚아요!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @on_working.on_working(fishing=True, prohibition=True)
    async def fish(self, ctx: discord.ApplicationContext):

        await ctx.defer()

        class FishButtonView(View):
            def __init__(self, ctx: discord.ApplicationContext):
                super().__init__(timeout=random.randint(1, 3) + ctx.bot.latency)
                self.ctx = ctx
                self.button_value = None

            @discord.ui.button(
                label="낚싯줄 당기기", style=discord.ButtonStyle.blurple, emoji="🎣"
            )
            async def button1_callback(
                self, button: discord.ui.Button, interaction: discord.Interaction
            ):
                self.button_value = "당김"
                self.stop()
                await interaction.response.defer()

            @discord.ui.button(label="그만하기", style=discord.ButtonStyle.secondary)
            async def button2_callback(
                self, button: discord.ui.Button, interaction: discord.Interaction
            ):
                self.button_value = "그만둠"
                self.stop()
                await interaction.response.defer()

            async def interaction_check(self, interaction) -> bool:
                if interaction.user != self.ctx.author:
                    await interaction.response.send_message(
                        "다른 사람의 낚시대를 건들면 어떻게 해!!! 💢\n```❗ 타인의 낚시를 건들 수 없습니다.```",
                        ephemeral=True,
                    )
                    self.button_value = None
                    return False
                else:
                    return True

        class TrashButtonView(View):
            def __init__(self, ctx):
                super().__init__(timeout=10)
                self.ctx = ctx
                self.button_value = None

            @discord.ui.button(
                label="쓰레기 치우기", style=discord.ButtonStyle.blurple, emoji="🧹"
            )
            async def button1_callback(self, button, interaction):
                self.button_value = "치우기"
                self.stop()
                await interaction.response.defer()

            @discord.ui.button(label="버리기", style=discord.ButtonStyle.red, emoji="💦")
            async def button2_callback(self, button, interaction):
                self.button_value = "버리기"
                self.stop()
                await interaction.response.defer()

            async def interaction_check(self, interaction) -> bool:
                if interaction.user != self.ctx.author:
                    await interaction.response.send_message(
                        "다른 사람의 낚시대를 건들면 어떻게 해!!! 💢\n```❗ 타인의 낚시를 건들 수 없습니다.```",
                        ephemeral=True,
                    )
                    self.button_value = None
                    return False
                else:
                    return True

        room = await Room.fetch(ctx.channel)
        user = await User.fetch(ctx.author)
        effect = room.effects
        probability_per_turn = room.fishing_probability  # 턴 당 낚일 확률

        # 낚시터 파산 확인
        if room.fee + room.maintenance > 100:
            user.set_fishing_now(False)
            return await ctx.respond(
                """이 낚시터는 파산한 듯해...\n`❗ 낚시터의 수수료와 유지비의 합이 100%을 넘기면 파산 상태가 되어 낚시를 할 수 없습니다.`
                ```cs\n#도움말\n'이프야 수수료' 명령어로 수수료를 조정하거나,\n'이프야 철거 (시설명)' 명령어로 유지비가 높은 시설을 철거해 주세요.```"""
            )

        # 낚시터 레벨 제한
        noob = False
        if user.level < room.level_limit: noob = True

        # if room.tier == 3 and user.level < 20:
        #     return await ctx.respond(
        #         "이 낚시터를 사용하기에는 낚시 자격증 레벨이 부족해..."
        #         "\n`❗ 3티어 낚시터를 이용하기 위해서는 최소 20레벨이 필요합니다.`"
        #     )
        # elif room.tier == 4 and user.level < 40:
        #     return await ctx.respond(
        #         "이 낚시터를 사용하기에는 낚시 자격증 레벨이 부족해..."
        #         "\n`❗ 4티어 낚시터를 이용하기 위해서는 최소 40레벨이 필요합니다.`"
        #     )
        # elif room.tier == 5 and user.level < 80:
        #     return await ctx.respond(
        #         "이 낚시터를 사용하기에는 낚시 자격증 레벨이 부족해..."
        #         "\n`❗ 5티어 낚시터를 이용하기 위해서는 최소 80레벨이 필요합니다.`"
        #     )
        # elif room.tier == 6 and user.level < 160:
        #     return await ctx.respond(
        #         "이 낚시터를 사용하기에는 낚시 자격증 레벨이 부족해..."
        #         "\n`❗ 6티어 낚시터를 이용하기 위해서는 최소 160레벨이 필요합니다.`"
        #     )

        # 낚시 시작
        user.set_fishing_now(True)

        try:

            # POINT와 FAKE를 낚시터 티어에 따라 추가
            points = []
            fakes = []
            for i in range(0, room.tier + 1):
                if f"lv{i}_point" in Constants.FISHING_POINT_KR.keys():
                    points += Constants.FISHING_POINT_KR[f"lv{i}_point"]
                if f"lv{i}_fake" in Constants.FISHING_POINT_KR.keys():
                    fakes += Constants.FISHING_POINT_KR[f"lv{i}_fake"]

            # 낚시가 시작되는 부분
            description = ""
            embed = discord.Embed(
                title="💦  낚시찌를 던졌다! (첨벙)",
                description=description,
                colour=Constants.TIER_COLOR[room.tier],
            )

            view = FishButtonView(ctx)
            await ctx.respond(embed=embed, view=view)
            result = await view.wait()

            if not result:
                view.stop()
                if view.button_value == "당김":
                    return await fishing_failed(ctx, user, "찌를 올렸지만 아무 것도 없었다...", noob)
                else:
                    return await fishing_stoped(ctx, user)

            timing = False
            for i in range(1, 6):  # 총 5턴까지 진행
                color = Constants.TIER_COLOR[room.tier]

                text = random.choice(Constants.FISHING_POINT_KR["normal"])
                if rdpc(probability_per_turn):
                    timing = True
                    text = random.choice(points)
                    color = discord.Colour.red()
                elif rdpc(10 + effect["fake"]):
                    text = random.choice(fakes)
                    color = discord.Colour.red()

                embed = discord.Embed(
                    title="기다리는 중...", description=text + description, colour=color
                )

                try:
                    view = FishButtonView(ctx)
                    await ctx.edit(embed=embed, view=view)
                    result = await view.wait()  # true : 시간 초과

                except discord.errors.NotFound:
                    return await ctx.send(
                        "자, 잠깐! 낚시하고 이짜나! 멋대로 메시지 삭제하지 마!!! 💢\n```❗ 낚시 중간에 메시지를 지우지 마세요.```"
                    )

                if not timing and result:
                    continue

                elif result is False and view.button_value == "그만둠":  # 그만하기로 한 경우
                    return await fishing_stoped(ctx, user)

                elif timing and result:  # 물고기는 나왔지만 누르지 않은 경우
                    return await fishing_failed(ctx, user, "물고기가 떠나가 버렸다...", noob)

                elif not timing and view.button_value == "당김":  # 물고기는 없는데 낚아올림
                    return await fishing_failed(ctx, user, "찌를 올렸지만 아무 것도 없었다...", noob)

                elif timing or view.button_value == "당김":  # 물고기 낚기 성공
                    break

                else:
                    await ctx.respond("오류 발생")
                    await user.finish_fishing()
                    return None

            if not timing:  # 끝날 때까지 한 번도 미동이 없었던 경우:
                return await fishing_failed(ctx, user, "자리를 잘못 잡았나...?", noob)

            fish = await room.randfish()

            if not fish:
                # 등급을 뽑았는데 해당하는 물고기가 없는 경우
                return await fishing_failed(ctx, user, "여기는 물고기가 잘 안 낚이는 낚시터일까...?", noob)
            else:
                fish.owner = user

            # 패널티 적용하기
            fish.set_penalty(await user.get_penalty(room))

            throw, embed, image, bytes = await fishing_result(
                ctx, user, room, fish, effect, noob
            )

            try:
                if not throw:
                    await ctx.edit(embed=embed, file=image, view=None)
                    return await user.finish_fishing()

                # 이 아래는 쓰레기인 경우의 추가 선택지
                view = TrashButtonView(ctx)
                await ctx.edit(view=view, embed=embed, file=image)
                result = await view.wait()  # true : 시간 초과

                if result or view.button_value == "버리기":
                    embed = discord.Embed(
                        title=f"💦 '{fish.name}'을(를) 물에 도로 버렸다...", colour=color
                    )
                    if not int(fish.length / 10) == 0:
                        embed.set_footer(text=f"🧹낚시터가 {int(fish.length/10)} 만큼 더러워졌어!")
                    await room.add_cleans(fish.length / -10)
                    fame = (
                        fish.exp() * effect["_exp"] if fish.exp() >= 0 else 0
                    )  # 명성 계산
                    await room.add_exp(fame)  # 쓰레기 버릴 때 명성 깎기

                else:
                    embed = discord.Embed(
                        title=f"💦 '{fish.name}'을(를) 치웠다! 물이 더 깨끗해진 것 같아!",
                        colour=0x4BC59F,
                    )
                    # 처리한 경우 크기/10 만큼의 청결도가 추가됨
                    await room.add_cleans(fish.length / 10)
                    await user.add_money(fish.cost())
                    if not int(fish.length / 10) == 0:
                        embed.set_footer(text=f"🧹낚시터가 {int(fish.length/10)} 만큼 깨끗해졌어!")

                await user.finish_fishing()  # 낚시 종료 판정
                embed.set_image(url="attachment://fishcard.png")
                await ctx.edit(embed=embed, view=None)
            finally:
                bytes.close()
        finally:
            user.set_fishing_now(False)

    @slash_command(name="ㄴㅅ", description="이프와 함께 물고기를 낚아요!")
    @commands.cooldown(1, 5, commands.BucketType.user)
    @on_working.on_working(fishing=True, prohibition=True)
    async def _short(self, ctx):
        await self.fish(ctx)


async def fishing_stoped(ctx: discord.ApplicationContext, user: User):
    """낚시를 그만 뒀을때"""
    embed = discord.Embed(
        title="낚시 중지",
        description="낚싯대를 감아 정리했다.",
        colour=discord.Colour.light_grey(),
    )
    try:
        await ctx.edit(embed=embed, view=None)
    except discord.errors.NotFound:
        await ctx.send(
            "아무리 낚시가 안 된다고 해도 그렇지 낚싯줄을 끊으면 어떻게 해!!! 💢\n```❗ 낚시 중간에 메시지를 지우지 마세요.```"
        )
    await user.finish_fishing()


async def fishing_failed(window: discord.ApplicationContext, user: User, text: str, noob: bool):
    """낚시가 실패했을 때"""
    if noob:
        text += "\n`❗ 혹시 너무 높은 티어의 낚시터에서 낚시하고 계시지 않나요?`"
    embed = discord.Embed(
        title="낚시 실패", description=text, colour=discord.Colour.light_grey()
    )
    await window.edit(embed=embed, view=None)
    await user.finish_fishing()


async def fishing_result(
    window: discord.ApplicationContext, user: User, room: Room, fish, effect, noob: bool
):
    """낚시가 성공했을 때 결과 보여주기"""
    throw = False
    net_profit = (
        fish.cost() + fish.fee(user, room) + fish.maintenance(room) + fish.bonus(room)
    )
    fame = fish.exp() * effect["_exp"] if fish.exp() >= 0 else 0  # 명성 계산
    after_money = user.money + net_profit # 낚시한 이후 유저의 돈

    # 도감 추가 & 기록 추가
    await user.get_fish(fish)

    # 물고기 금액이 양수일 경우
    if fish.cost() > 0:
        # 개인 명성 & 낚시터 명성 부여
        await user.add_exp(fame)
        await room.add_exp(fame)

        await user.give_money(net_profit)

        # 주인이 아니면 낚시터 주인에게 돈 부여
        if room.owner_id != user.id:
            owner = await User.fetch(room.owner_id)
            await owner.give_money(fish.fee(user, room) * -1)

    information = f"{fish.rarity_str()} | 📏 {fish.length:,}cm | ✨ {int(fame)} | 💵 {net_profit:,} `→ {after_money:,} 💰`"

    if await user.update_biggest(fish):
        information += "\n`📏 오늘 낚은 것 중 가장 커! (일일 최고 크기)`"

    if len(user.fish_history):
        lengthlist = [i["length"] for i in user.fish_history]
        lengthlist.sort(reverse=True)

        if lengthlist[0] < fish.length:
            information += f"\n`📏 와! 지금까지 내가 낚은 것 중에 가장 커!\n(최대 크기 기록 갱신 : {lengthlist[0]}cm → {fish.length})`"

        lengthlist.sort(reverse=True)
        if lengthlist[-1] > fish.length:
            information += f"\n`📏 와! 이렇게 조그만 거는 처음 봐...!\n(최소 크기 기록 갱신 : {lengthlist[-1]}cm → {fish.length})`"

        pricelist = [i["cost"] for i in user.fish_history]
        pricelist.sort(reverse=True)
        if pricelist[0] < fish.cost():
            information += f"\n`💰 와! 이렇게 비싼 물고기는 처음이야!\n(최대 가격 기록 갱신 : {pricelist[0]}💰 → {fish.cost()}💰)`"

    if fish.rarity == 0:
        # 가격이 0인 경우 선택권 없이 그냥 버림
        if fish.cost() == 0:
            information += "\n`💦 자연으로 돌아가렴... (그냥 버려도 될 듯해 물에 도로 던졌다)`"

        # 쓰레기이지만 처리 비용이 없는 경우 어쩔 수 없이 버림
        elif fish.cost() + user.money < 0:
            information += "\n`💦 미안하지만 널 처리하기에는 지갑이... (처리할 돈이 없어 물에 도로 던졌다)`"
            await room.add_cleans(fish.length / -10)  # 버린 경우 크기/10 만큼의 청결도가 깎임
            await room.add_exp(fame)  # 쓰레기 버릴 때 명성 깎기

        # 팔 수 있는 특수 쓰레기인 경우 오히려 돈을 얻음
        elif fish.cost() > 0:
            information += "\n`💵 이 쓰레기는 팔 수 있는 쓰레기다! (쓰레기를 팔아 돈을 벌었다)`"

        else:
            throw = True
            information += (
                "\n```diff\n- 쓰레기를 낚아 버렸다...! 어떻게 처리할까...?"
                f"\n🧹 : {-1 * fish.cost()}💰을 내고 쓰레기를 치운다. (소지금 : {str(user.money)}💰)"
                "\n💦 : ... 그냥 다시 물에 버리자```"
            )

    if noob:
        information += "\n`❗ 이 낚시터는 내가 낚시하기엔 조금 어려운거 같다...`"

    if throw:
        embed = discord.Embed(
            title=f"{fish.icon()} {fish.name}",
            description=information,
            color=discord.Colour.dark_orange(),
        )
    else:
        embed = discord.Embed(
            title=f"{fish.icon()} {fish.name}", description=information
        )

    # try:
    #     # 서버로부터 낚시카드 전송
    #     image = await get_fishcard_image_file_from_url(fish)
    # except Exception:  # aiohttp.ClientConnectorError:
    #     # 실패 시 레거시 코드로 직접 낚시카드를 만들어 전송
    #     image = await make_fishcard_image_file(window, fish, room, user)

    #     # embed.set_footer(text="※ 낚시카드 서버와의 연결에 실패하여 레거시 코드로 임시 낚시카드를 생성하였습니다.")
    bytes, image = await make_fishcard_image_file(window, fish, room, user)
    embed.set_image(url="attachment://fishcard.png")
    return throw, embed, image, bytes


async def get_fishcard_image_file_from_url(fish: Fish):
    url = fish.card_data
    if url.startswith("localhost"):
        url = "http://" + url
    logger.debug(f"낚시카드 URL: {url}")
    """낚시카드 서버로부터 받아 온 낚시카드 DiscordFile을 반환"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            loop = asyncio.get_running_loop()
            if resp.status != 200:
                logger.warn("서버로부터 낚시카드를 불러올 수 없음.")
                return
            data = await loop.run_in_executor(None, io.BytesIO, await resp.read())
            return discord.File(data, "fishcard.png")


async def make_fishcard_image_file(
    ctx: discord.ApplicationContext, fish: Fish, room: Room, user: User
):
    """직접 제작한 낚시카드 이미지 DiscordFile로 반환"""
    image = await get_card_async(ctx.bot.loop, fish, room, user)

    return image, discord.File(image, filename="fishcard.png")
    # embed.set_image(url="attachment://fishcard.png")


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(FishingGameCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
