"""
    <fishing_land.py>
    매입, 매각 등 땅 관련 명령어가 모여 있습니다.
"""

# 필수 임포트
from discord.commands import slash_command
from discord.commands import Option
from discord.ui import View
from discord.ext import commands
import discord
import os
import math

from cogs.fishing import fishing_group as _fishing_group
from utils import logger

# 부가 임포트
from classes.user import User
from classes.room import Room
from utils.on_working import on_working
from config import SLASH_COMMAND_REGISTER_SERVER as SCRS


class LandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    fishing_group = _fishing_group

    @fishing_group.command(name="매입", description="이 낚시터(채널)을 매입해요!")
    @on_working(fishing=True, landwork=True, prohibition=True, twoball=False)
    async def buy(self, ctx, price: Option(int, "매입 가격을 입력해요!") = None):
        user = await User.fetch(ctx.author)
        room = await Room.fetch(ctx.channel)
        land_value = room.land_value
        min_purchase = room.min_purchase

        if price is None:
            if land_value == 0:
                value = 30000
            else:
                value = min_purchase
        else:
            value = int(price)

        if room.owner_id == ctx.author.id:
            await ctx.respond("이미 여기 주인이자나!\n`❓ 낚시터에 걸린 돈을 조정하려면 '/땅값변경' 명령어를 써 보세요.`")
            return None
        elif value < 30000:
            await ctx.respond("땅 매입은 30,000 💰부터 가능해!")
            return None
        elif value > user.money:
            await ctx.respond(f"자기 소지금보다 높게 부르면 안되지!\n`❗ 현재 소지금은 {user.money:,} 💰입니다.`")
            return None
        elif value < min_purchase:
            await ctx.respond(
                f"{value} 💰로는 이 땅을 매입할 수 없어...!\n`❗ {room.name}의 최소 매입가는 {min_purchase:,} 💰입니다.`"
            )
            return None

        await room.set_working_now(True)

        embed = discord.Embed(
            title=f"{room.name} 땅을 {value:,}로 매입하시겠습니까?",
            description=f"소지금 : {user.money:,} 💰",
            colour=0x4BC59F,
        )

        class OXButtonView(View):
            def __init__(self, ctx):
                super().__init__(timeout=10)
                self.ctx = ctx
                self.button_value = None

            @discord.ui.button(
                label="매입하기", style=discord.ButtonStyle.blurple, emoji="⭕"
            )
            async def button1_callback(self, button, interaction):
                self.button_value = "매입"
                self.stop()

            @discord.ui.button(label="취소하기", style=discord.ButtonStyle.red, emoji="❌")
            async def button2_callback(self, button, interaction):
                self.button_value = "취소함"
                self.stop()

            async def interaction_check(self, interaction) -> bool:
                if interaction.user != self.ctx.author:
                    await interaction.response.send_message(
                        "다른 사람의 계약서를 건들면 어떻게 해!!! 💢\n```❗ 타인의 매입에 간섭할 수 없습니다.```",
                        ephemeral=True,
                    )
                    self.button_value = None
                    return False
                else:
                    return True

        view = OXButtonView(ctx)

        window = await ctx.respond(embed=embed, view=view)
        result = await view.wait()

        if result is True or view.button_value == "취소함":
            embed = discord.Embed(
                title="매입을 취소하였다.", colour=discord.Colour.light_grey()
            )
            await window.edit_original_message(embed=embed, view=None)
            await room.set_working_now(False)

            return None

        origin_owner_id = room.owner_id
        await user.purchase_land(room, value)
        await room.set_working_now(False)

        if min_purchase == 30000 and not (
            ctx.channel.topic is not None and "#매입보고" in ctx.channel.topic
        ):
            await window.edit_original_message(
                content=f"**서버 주인**의 **{room.name}** 낚시터를 <@{user.id}>가 매입했어!"
                "\n`ℹ️ 돈이 걸려 있지 않은 땅도 매입 멘션을 받으려면 '#매입보고' 태그를 넣어 주세요!`",
                embed=None,
                view=None,
            )
        else:
            await window.edit_original_message(
                content=f"<@{origin_owner_id}>의 **{room.name}** 낚시터를 <@{user.id}>가 매입했어!",
                embed=None,
                view=None,
            )

    @fishing_group.command(name="매각", description="자신의 낚시터를 매각하세요!")
    @on_working(
        fishing=True, prohibition=True, twoball=False
    )  # 번호로 다른 채널을 건드릴 수도 있으니 landwork는 제외
    async def sell(
        self,
        ctx,
        land_num: Option(int, "매각하고 싶으신 땅 번호를 입력하세요! (미입력시 이 낚시터로 자동 선택)") = None,
    ):
        user = await User.fetch(ctx.author)
        if land_num is not None:
            lands = await user.get_lands()
            room = await Room.fetch(lands[land_num - 1][0])
        else:
            room = await Room.fetch(ctx.channel)

        if await room.get_working_now():
            await ctx.respond(
                "흐음... 여기 뭔가 하고 있는 거 같은데 조금 이따가 와 보자!\n`❗ 누군가 이미 땅에서 매입/매각/건설/철거 등의 작업을 하는 중이다.`"
            )
            return None
        elif room.owner_id != ctx.author.id:
            await ctx.respond("다른 사람 땅을 내가 처리하면 안 돼지!")
            return None
        elif room.land_value == 0:
            await ctx.respond("내가 만든 채널은 처리할 수 없어!")
            return None

        class OXButtonView(View):
            def __init__(self, ctx):
                super().__init__(timeout=10)
                self.ctx = ctx
                self.button_value = None

            @discord.ui.button(
                label="매각하기", style=discord.ButtonStyle.blurple, emoji="⭕"
            )
            async def button1_callback(self, button, interaction):
                self.button_value = "매각"
                self.stop()

            @discord.ui.button(label="취소하기", style=discord.ButtonStyle.red, emoji="❌")
            async def button2_callback(self, button, interaction):
                self.button_value = "취소함"
                self.stop()

            async def interaction_check(self, interaction) -> bool:
                if interaction.user != self.ctx.author:
                    await interaction.response.send_message(
                        "다른 사람의 계약서를 건들면 어떻게 해!!! 💢\n```❗ 타인의 매각에 간섭할 수 없습니다.```",
                        ephemeral=True,
                    )
                    self.button_value = None
                    return False
                else:
                    return True

        view = OXButtonView(ctx)

        await room.set_working_now(True)

        if room.channel is not None and room.owner_id == room.channel.guild.owner_id:
            # 자기 서버 땅인데 추가로 돈이 걸린 경우

            embed = discord.Embed(
                title=f"{room.name} 땅의 돈을 회수하시겠습니까?\n(매각해도 지주는 바뀌지 않습니다.)",
                description=f"돌려 받는 금액 : {room.land_value:,} 💰",
                colour=0x4BC59F,
            )
            window = await ctx.respond(embed=embed, view=view)
            result = await view.wait()

            if result is True or view.button_value == "취소함":
                embed = discord.Embed(
                    title="돈 회수를 취소했다.", colour=discord.Colour.light_grey()
                )
                await window.edit_original_message(embed=embed, view=None)
                await room.set_working_now(False)

                return None

            embed = discord.Embed(
                title=f"{room.name} 땅에 있던 {room.land_value:,} 💰을 뺐다.", colour=0x4BC59F
            )
            user = await User.fetch(ctx.author)
            await user.add_money(room.land_value)  # 돈 돌려 주고
            await room.set_land_value(0)

            await window.edit_original_message(embed=embed, view=None)
            await room.set_working_now(False)

            return None

        else:  # 다른 사람 땅인 경우
            embed = discord.Embed(
                title=f"{room.name} 땅을 매각하겠습니까?",
                description=f"돌려 받는 금액 : {room.land_value:,} 💰",
                colour=0x4BC59F,
            )
            window = await ctx.respond(embed=embed, view=view)
            result = await view.wait()

            if result is True or view.button_value == "취소함":
                embed = discord.Embed(
                    title="땅 매각을 취소했다.", colour=discord.Colour.light_grey()
                )
                await window.edit_original_message(embed=embed, view=None)
                await room.set_working_now(False)

                return None

            embed = discord.Embed(
                title=f"{room.name} 땅을 매각하고 {room.land_value:,} 💰를 돌려받았다.",
                colour=0x4BC59F,
            )

            user = await User.fetch(ctx.author)
            await user.add_money(room.land_value)
            await room.set_owner_id(693818502657867878)
            await room.set_land_value(0)
            await room.set_working_now(False)

            await window.edit_original_message(embed=embed, view=None)

    @slash_command(name="내땅", description="무슨 땅을 가지고 있는지 확인해요!", guild_ids=SCRS)
    @on_working(fishing=True, prohibition=True)
    async def my_land(
        self,
        ctx,
        land_name: Option(str, "땅의 이름으로 검색해요! (미 입력시 소유하는 모든 땅의 목록을 보여드려요!)") = None,
    ):
        user = await User.fetch(ctx.author)

        window = await ctx.respond(content="`내 땅 목록`")
        mylands = list(await user.get_lands())
        list_str = ""
        ridx = 0

        if land_name is None:
            land_name = ""
        for idx, val in enumerate(mylands):
            if (len(land_name) == 0 and val[2] != 0) or (
                len(land_name) != 0 and " ".join(land_name) in val[1]
            ):
                list_str += "\n[{}] {} ({}💰)".format(idx + 1, val[1], val[2])
                ridx += 1
            if idx != 0 and ridx != 0 and ridx % 15 == 0:
                embed = discord.Embed(
                    title=f"💰 **내가 매입한 땅 목록 ({int((ridx-2)/15) + 1}/{math.ceil(len(mylands)/15)} 페이지)**",
                    description=f"```cs\n{list_str}```",
                    colour=0x4BC59F,
                )
                await window.edit_original_message(embed=embed)

                class NextPageView(View):
                    def __init__(self, ctx):
                        super().__init__(timeout=10)
                        self.ctx = ctx
                        self.button_value = None

                    @discord.ui.button(
                        label="다음 페이지 보기", style=discord.ButtonStyle.blurple, emoji="➡️"
                    )
                    async def button1_callback(self, button, interaction):
                        self.button_value = "넘기기"
                        self.stop()

                    @discord.ui.button(
                        label="그만보기", style=discord.ButtonStyle.red, emoji="❌"
                    )
                    async def button2_callback(self, button, interaction):
                        self.button_value = "취소함"
                        self.stop()

                    async def interaction_check(self, interaction) -> bool:
                        if interaction.user != self.ctx.author:
                            await interaction.response.send_message(
                                "다른 사람의 책을 건들면 어떻게 해!!! 💢\n```❗ 타인의 행동에 간섭할 수 없습니다.```",
                                ephemeral=True,
                            )
                            self.button_value = None
                            return False
                        else:
                            return True

                view = NextPageView(ctx)

                window = await ctx.respond(embed=embed, view=view)
                result = await view.wait()
                if result is True or view.button_value == "취소함":
                    await window.edit_original_message(view=None)
                    return None
                else:
                    list_str = ""

        if list_str == "":
            list_str = "없음"
        embed = discord.Embed(
            title=f"💰 **내가 매입한 땅 목록** ({math.ceil(len(mylands)/15)}/{math.ceil(len(mylands)/15)} 페이지)",
            description=f"```cs\n{list_str}```",
            colour=0x4BC59F,
        )
        await window.edit_original_message(embed=embed, view=None)

    @fishing_group.command(name="땅값변경", description="이 낚시터(채널)의 땅값을 바꿔요!")
    @on_working(
        fishing=True, landwork=True, prohibition=True, owner_only=True, twoball=False
    )
    async def change_land_value(self, ctx, value: Option(int, "변경하실 땅값을 입력하세요!")):
        user = await User.fetch(ctx.author)
        room = await Room.fetch(ctx.channel)
        land_value = room.land_value
        await room.set_working_now(True)

        if value < 30000:
            await ctx.respond("땅 가격은 최소 30,000 💰부터 가능해!")
            await room.set_working_now(False)
            return None
        if value == room.land_value:
            await ctx.respond("흐음... 똑같은뎅?")
            await room.set_working_now(False)
            return None
        if value > user.money + room.land_value:
            await room.set_working_now(False)
            return await ctx.respond(
                f"흐음... 돈이 부족해!\n`❗ 현재 땅값과 소지금의 합이 {(room.land_value + user.money):,} 💰입니다.`"
            )

        class OXButtonView(View):
            def __init__(self, ctx):
                super().__init__(timeout=10)
                self.ctx = ctx
                self.button_value = None

            @discord.ui.button(
                label="땅값 변경하기", style=discord.ButtonStyle.blurple, emoji="⭕"
            )
            async def button1_callback(self, button, interaction):
                self.button_value = "땅값변경"
                self.stop()

            @discord.ui.button(label="취소하기", style=discord.ButtonStyle.red, emoji="❌")
            async def button2_callback(self, button, interaction):
                self.button_value = "취소함"
                self.stop()

            async def interaction_check(self, interaction) -> bool:
                if interaction.user != self.ctx.author:
                    await interaction.response.send_message(
                        "다른 사람의 계약서를 건들면 어떻게 해!!! 💢\n```❗ 타인의 부동산에 간섭할 수 없습니다.```",
                        ephemeral=True,
                    )
                    self.button_value = None
                    return False
                else:
                    return True

        view = OXButtonView(ctx)

        embed = discord.Embed(
            title=f"{room.name} 땅을 {value:,}로 변경하시겠습니까?", colour=0x4BC59F
        )
        window = await ctx.respond(embed=embed, view=view)
        result = await view.wait()

        if result is True or view.button_value == "취소함":
            embed = discord.Embed(
                title="변경을 취소하였다.", colour=discord.Colour.light_grey()
            )
            await window.edit_original_message(embed=embed, view=None)
            await room.set_working_now(False)

            return None

        await user.give_money(land_value - value)
        await room.set_land_value(value)
        await room.set_working_now(False)

        await window.edit_original_message(
            content=f"{room.name} 땅의 가격을 변경했어!", embed=None, view=None
        )

    @fishing_group.command(name="지형변경", description="이 낚시터(채널)의 지형을 바꿔요!")
    @on_working(
        fishing=True, landwork=True, prohibition=True, owner_only=True, twoball=False
    )
    async def change_biome(
        self,
        ctx,
        value: Option(
            str,
            "변경하실 지형을 입력해주세요!",
            choices=["🏜️ 메마른 땅", "🏖️ 바닷가", "🏞️ 강가", "🚤 호수", "⛰️ 계곡", "🥬 습지", "🦀 갯벌"],
        ),
    ):
        await ctx.defer()
        room = await Room.fetch(ctx.channel.id)

        if room.cleans < 0:
            return await ctx.respond("지형을 변경하려면 청소를 하셔야 해요! (청결도가 0보다 작아요)")
        if room.tier != 1:
            return await ctx.respond("지형을 변경하려면 티어가 1티어야만 해요!")
        if len(room.facilities) != 0:
            return await ctx.respond("지형을 변경하려면 어떤 시설도 있으면 안되요!")
        if room.land_value != 0:
            return await ctx.respond(
                "지형을 변경하려면 이 땅이 매각된 땅이여야 해요! (`/매각` 을 통해 매각된 땅으로 만들 수 있어요!)"
            )
        if await room.get_exp() > 50:
            return await ctx.respond("지형을 변경하려면 명성이 50이하여야 해요!")

        biome_kr = [
            "🏜️ 메마른 땅",
            "🏖️ 바닷가",
            "🏞️ 강가",
            "🚤 호수",
            "⛰️ 계곡",
            "🥬 습지",
            "🦀 갯벌",
            "🌅 곶",
            "⛲ 샘",
            "🗻 칼데라",
        ]

        if biome_kr.index(value) == room.biome:
            return await ctx.respond("으앙 원래 지형이랑 똑같자나!")

        await room.set_biome(biome_kr.index(value))
        await ctx.respond(f"와아 이제 여긴 {value}야!")

    @fishing_group.command(name="수수료설정", description="이 낚시터(채널)의 수수료를 설정하세요!")
    @on_working(
        fishing=True, landwork=True, prohibition=True, owner_only=True, twoball=False
    )
    async def change_fee(self, ctx, value: Option(int, "변경하실 수수료를 입력해주세요!")):
        room = await Room.fetch(ctx.channel)

        fee_range = room.fee_range
        if value < fee_range[0] or fee_range[1] < value:
            embed = discord.Embed(
                title="수수료 조정 범위를 잘 살펴 봐 줘!",
                description=f"`❗ 수수료 지정 가능 범위가 {fee_range[0]}% ~ {fee_range[1]}%입니다.`",
                colour=0x4BC59F,
            )
            await ctx.respond(embed=embed)
            return None

        class OXButtonView(View):
            def __init__(self, ctx):
                super().__init__(timeout=10)
                self.ctx = ctx
                self.button_value = None

            @discord.ui.button(
                label="수수료 변경하기", style=discord.ButtonStyle.blurple, emoji="⭕"
            )
            async def button1_callback(self, button, interaction):
                self.button_value = "수수료변경"
                self.stop()

            @discord.ui.button(label="취소하기", style=discord.ButtonStyle.red, emoji="❌")
            async def button2_callback(self, button, interaction):
                self.button_value = "취소함"
                self.stop()

            async def interaction_check(self, interaction) -> bool:
                if interaction.user != self.ctx.author:
                    await interaction.response.send_message(
                        "다른 사람의 계약서를 건들면 어떻게 해!!! 💢\n```❗ 타인의 부동산에 간섭할 수 없습니다.```",
                        ephemeral=True,
                    )
                    self.button_value = None
                    return False
                else:
                    return True

        view = OXButtonView(ctx)

        embed = discord.Embed(
            title=f"{room.name} 땅의 수수료를 {value}%로 변경하시겠습니까?", colour=0x4BC59F
        )
        window = await ctx.respond(embed=embed, view=view)
        result = await view.wait()

        if result is True or view.button_value == "취소함":
            embed = discord.Embed(
                title="수수료 변경을 취소하였다.", colour=discord.Colour.light_grey()
            )
            await window.edit_original_message(embed=embed, view=None)
            return None

        await room.set_fee(value)
        embed = discord.Embed(
            title=f"{room.name} 땅의 수수료를 {value}%로 변경하였다!", colour=0x4BC59F
        )
        await window.edit_original_message(embed=embed, view=None)

    @fishing_group.command(name="청소업체", description="돈을 지불하고 청결도를 0으로 만들어요!")
    @on_working(
        fishing=True, prohibition=True, twoball=False, owner_only=True, landwork=True
    )
    async def clean_corp(self, ctx):
        room = await Room.fetch(ctx.channel)

        if room.cleans >= 0:
            return await ctx.respond(
                "이 낚시터에는 굳이 청소 업체를 부를 필요가 없을 것 같아!\n`❗ 청소 업체는 청결도가 음수가 되었을 때만 부를 수 있습니다.`"
            )
        user = await User.fetch(ctx.author)

        price = room.cleans * 150
        await room.set_working_now(True)

        embed = discord.Embed(
            title=f"청소 업체를 불러 {room.name} 땅의 청결도를 0으로 만드시겠습니까?",
            description=f"예상 필요 금액 {-1 * price:,} 💰",
            colour=0x4BC59F,
        )

        class OXButtonView(View):
            def __init__(self, ctx):
                super().__init__(timeout=10)
                self.ctx = ctx
                self.button_value = None

            @discord.ui.button(
                label="청소하기", style=discord.ButtonStyle.blurple, emoji="⭕"
            )
            async def button1_callback(self, button, interaction):
                self.button_value = "청소"
                self.stop()

            @discord.ui.button(label="취소하기", style=discord.ButtonStyle.red, emoji="❌")
            async def button2_callback(self, button, interaction):
                self.button_value = "취소함"
                self.stop()

            async def interaction_check(self, interaction) -> bool:
                if interaction.user != self.ctx.author:
                    await interaction.response.send_message(
                        "다른 사람의 계약서를 건들면 어떻게 해!!! 💢\n```❗ 타인의 부동산에 간섭할 수 없습니다.```",
                        ephemeral=True,
                    )
                    self.button_value = None
                    return False
                else:
                    return True

        view = OXButtonView(ctx)

        window = await ctx.respond(embed=embed, view=view)
        result = await view.wait()

        if result is True or view.button_value == "취소함":
            embed = discord.Embed(
                title="청소 업체 부르기를 취소했다.", colour=discord.Colour.light_grey()
            )
            await room.set_working_now(False)

            return await window.edit_original_message(embed=embed, view=None)

        if user.money < -1 * price:
            embed = discord.Embed(title="돈이 부족해...", colour=discord.Colour.light_grey())
            await room.set_working_now(False)

            return await window.edit_original_message(embed=embed, view=None)

        embed = discord.Embed(
            title=f"{-1 * price:,} 💰로 청소 업체를 불러서 {room.name} 낚시터가 깔끔해졌어!",
            colour=0x4BC59F,
        )
        await user.add_money(price)  # 돈 돌려 주고
        await room.set_cleans(0)

        await window.edit_original_message(embed=embed, view=None)
        await room.set_working_now(False)


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    cog = LandCog(bot)
    bot.add_cog(cog)  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
