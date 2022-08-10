"""
    <fishing_unit.py>
    건설, 철거 등 시설 관련 명령어가 있습니다.
"""

import os

import discord
from discord.commands import Option

# 필수 임포트
from discord.ext import commands
from discord.ui import View
from classes.facility import UNITDATA

# 부가 임포트
from classes.room import Room, Facility, NotExistFacility
from cogs.fishing import fishing_group, land_group
from constants import Constants
from utils import logger
from utils.on_working import on_working


async def autocomplete_facilities(ctx: discord.AutocompleteContext):
    room = await Room.fetch(ctx.interaction.channel)

    def filter_items(x):
        k: str = x[0]
        if k.startswith("_"):
            return False
        i = x[1]
        name: str = i["name"] if "name" in i else k
        if ctx.value not in name:
            return False

        try:
            if room.can_build_it(Facility(k)):
                return True
            return False
        except Exception as e:
            return False

    return [
        i["name"] if "name" in i else k in i
        for k, i in filter(
            filter_items,
            UNITDATA.items(),
        )
    ]


async def autocomplete_facilities_uninstall(ctx: discord.AutocompleteContext):
    room = await Room.fetch(ctx.interaction.channel)

    def filter_items(x):
        k: str = x[0]
        if k.startswith("_"):
            return False
        i = x[1]

        if k not in room.facilities:
            return False

        name: str = i["name"] if "name" in i else k
        if ctx.value not in name:
            return False

        return True

    return [
        i["name"] if "name" in i else k in i
        for k, i in filter(
            filter_items,
            UNITDATA.items(),
        )
    ]


class UnitCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @fishing_group.command(name="업그레이드", description="이 낚시터(채널)의 티어를 올려요!")
    @on_working(
        fishing=True, prohibition=True, landwork=True, owner_only=True, twoball=False
    )
    async def upgrade(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        room = await Room.fetch(ctx.channel)
        try:
            facility = Facility(f"_TIER{room.tier + 1}")

        # 더 이상의 업그레이드 시설이 존재하지 않는 경우
        except NotExistFacility:
            return await ctx.respond(
                """더 이상의 업그레이드는 불가능한 것 같아!
                `❗ 축하합니다! 모든 업그레이드를 완료하셨습니다!`"""
            )

        async with room.work():
            embed = discord.Embed(
                title=f"{room.name} 땅에 '{facility.name}' 시설을 건설하여 {room.tier + 1}티어로 업그레이드할 거야?",
                description=(
                    f"```cs\n{facility.description}\n{facility.effect_information()}"
                    f"```현재 낚시터 명성 : ✨ {await room.get_exp()} ( ✨ {facility.cost} 소모 )"
                ),
                colour=0x4BC59F,
            )

            class OXButtonView(View):
                def __init__(self, ctx):
                    super().__init__(timeout=10)
                    self.ctx = ctx
                    self.button_value = None

                @discord.ui.button(
                    label="업그레이드", style=discord.ButtonStyle.blurple, emoji="⭕"
                )
                async def button1_callback(self, button, interaction):
                    self.button_value = "업그레이드"
                    self.stop()
                    await interaction.response.defer()

                @discord.ui.button(
                    label="취소하기", style=discord.ButtonStyle.red, emoji="❌"
                )
                async def button2_callback(self, button, interaction):
                    self.button_value = "취소함"
                    self.stop()
                    await interaction.response.defer()

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

            await ctx.respond(embed=embed, view=view)
            result = await view.wait()

            if result is True or view.button_value == "취소함":
                embed = discord.Embed(
                    title="낚시터 업그레이드를 취소하였다.", colour=discord.Colour.light_grey()
                )
                return await ctx.edit(embed=embed, view=None)

            # 낚시터 명성이 부족한 경우
            if facility.cost > await room.get_exp():
                return await ctx.edit(
                    content=f"""으움... 기각당했어...
                    `❗ 낚시터 명성이 부족합니다. ( ✨ {facility.cost} 필요 )`""",
                    embed=None,
                    view=None,
                )

            # 1티어의 경우 전용 시설이 없으므로 무시
            if not room.tier == 1:
                await room.break_facility(f"_TIER{room.tier}")
            await room.build_facility(facility.code)
            await room.add_exp(facility.cost * -1)
            await ctx.edit(
                content=f"""<@{ctx.author.id}> {room.name} 낚시터가 {room.tier} 티어로 업그레이드 했어! 축하해!
                `🎉 이제 새로운 종류의 시설을 건설할 수 있게 되었습니다!`""",
                embed=None,
                view=None,
            )

    @fishing_group.command(name="공영화", description="낚시터를 공영화해요!")
    @on_working(fishing=True, prohibition=True, landwork=True, owner_only=True)
    async def publicize(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        room = await Room.fetch(ctx.channel)
        if ctx.channel.guild.owner_id != ctx.author.id:
            return await ctx.respond(
                "낚시터 공영화는 서버 주인만 할 수 있어!"
                "\n`❗ 공공 낚시터로 만들려면 '이프야 다운그레이드' 명령어로 1티어까지 낮춰 주세요.`"
            )
        if room.tier > 2:
            return await ctx.respond(
                """1티어 낚시터만 공공 낚시터로 만들 수 있어!
                `❗ 공공 낚시터로 만들려면 '이프야 다운그레이드' 명령어로 1티어까지 낮춰 주세요.`"""
            )
        if not room.tier:
            return await ctx.respond(
                """이미 여기는 공공 낚시터인 걸...?
                `❗ 다시 주인이 있는 낚시터로 바꾸고 싶다면 '이프야 민영화' 명령어를 사용해 보세요.`"""
            )

        embed = discord.Embed(
            title=f"{room.name} 낚시터를 공공 낚시터로 만들 거야?",
            description="**❗ 공공 낚시터로 만들 시 다른 모든 시설은 철거됩니다!**",
            colour=0x4BC59F,
        )

        async with room.work():

            class OXButtonView(View):
                def __init__(self, ctx):
                    super().__init__(timeout=10)
                    self.ctx = ctx
                    self.button_value = None

                @discord.ui.button(
                    label="공영화하기", style=discord.ButtonStyle.blurple, emoji="⭕"
                )
                async def button1_callback(self, button, interaction):
                    self.button_value = "공영화"
                    self.stop()
                    await interaction.response.defer()

                @discord.ui.button(
                    label="취소하기", style=discord.ButtonStyle.red, emoji="❌"
                )
                async def button2_callback(self, button, interaction):
                    self.button_value = "취소함"
                    self.stop()
                    await interaction.response.defer()

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

            await ctx.respond(embed=embed, view=view)
            result = await view.wait()

            if result is True or view.button_value == "취소함":
                embed = discord.Embed(
                    title="낚시터 공영화를 취소하였다.", colour=discord.Colour.light_grey()
                )
                return await ctx.edit(embed=embed, view=None)

            breaked = []
            breaked_cost = 0
            facs = room.facilities[:]  # 얕은 복사 (shallow copy)
            for i in facs:
                if i.startswith("_"):
                    continue
                fac = Facility(i)
                await room.break_facility(i)
                await room.add_exp(fac.cost)
                breaked_cost += fac.cost
                breaked.append(fac.name)
            await room.build_facility("_TIER0")
            await ctx.edit(
                content=f"<@{ctx.author.id}> {room.name} 낚시터는 이제 공공 낚시터야!",
                embed=None,
                view=None,
            )

    @fishing_group.command(name="민영화", description="이 낚시터(채널)을 민영화해요!")
    @on_working(fishing=True, prohibition=True, landwork=True, owner_only=True)
    async def privatize(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        room = await Room.fetch(ctx.channel)
        if ctx.channel.guild.owner_id != ctx.author.id:
            return await ctx.respond(
                "낚시터 민영화는 서버 주인만 할 수 있어!" "\n`❗ 낚시터 민영화는 서버 주인만 할 수 있습니다.`"
            )
        if room.tier != 0:
            return await ctx.respond(
                """여긴 이미 공공 낚시터가 아닌데...?
                `❗ 민영화는 공공 낚시터를 일반 낚시터로 되돌리는 명령어입니다.`"""
            )

        embed = discord.Embed(
            title=f"{room.name} 낚시터를 공공 낚시터에서 다시 일반 낚시터로 만들 거야?", colour=0x4BC59F
        )

        async with room.work():

            class OXButtonView(View):
                def __init__(self, ctx):
                    super().__init__(timeout=10)
                    self.ctx = ctx
                    self.button_value = None

                @discord.ui.button(
                    label="민영화하기", style=discord.ButtonStyle.blurple, emoji="⭕"
                )
                async def button1_callback(self, button, interaction):
                    self.button_value = "민영화"
                    self.stop()
                    await interaction.response.defer()

                @discord.ui.button(
                    label="취소하기", style=discord.ButtonStyle.red, emoji="❌"
                )
                async def button2_callback(self, button, interaction):
                    self.button_value = "취소함"
                    self.stop()
                    await interaction.response.defer()

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

            await ctx.respond(embed=embed, view=view)
            result = await view.wait()

            if result is True or view.button_value == "취소함":
                embed = discord.Embed(
                    title="낚시터 민영화를 취소하였다.", colour=discord.Colour.light_grey()
                )
                return await ctx.edit(embed=embed, view=None)
            await room.break_facility("_TIER0")
            await ctx.edit(
                content=f"<@{ctx.author.id}> {room.name} 낚시터는 이제 공공 낚시터가 아니야!",
                embed=None,
                view=None,
            )

    @fishing_group.command(name="다운그레이드", description="이 낚시터(채널)의 티어를 내려요!")
    @on_working(
        fishing=True, prohibition=True, landwork=True, owner_only=True, twoball=False
    )
    async def downgrade(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        room = await Room.fetch(ctx.channel)

        if room.tier == 1:
            return await ctx.respond(
                """더 이상의 다운그레이드는 불가능한 것 같아!
                `❗ 1티어에서는 다운그레이드를 하실 수 없어요!`"""
            )
        elif room.tier == 2:
            facility = None
            embed = discord.Embed(
                title=f"{room.name} 땅을 1티어로 다운그레이드할 거야?",
                description=(
                    f"**❗ 티어를 낮출 시 상위 티어의 시설들은 자동으로 철거 됩니다!**"
                    f"\n현재 낚시터 명성 : ✨ {await room.get_exp():,}"
                ),
                colour=0x4BC59F,
            )
        else:
            facility = Facility(f"_TIER{room.tier - 1}")
            embed = discord.Embed(
                title=f"{room.name} 땅을 {room.tier - 1}티어로 다운그레이드할 거야?",
                description=(
                    f"**❗ 티어를 낮출 시 상위 티어의 시설들은 자동으로 철거 됩니다!**"
                    f"\n현재 낚시터 명성 : ✨ {await room.get_exp():,} ( ✨ {facility.cost:,} 다시 받음 )"
                ),
                colour=0x4BC59F,
            )

        now_facility = Facility(f"_TIER{room.tier}")

        async with room.work():

            class OXButtonView(View):
                def __init__(self, ctx):
                    super().__init__(timeout=10)
                    self.ctx = ctx
                    self.button_value = None

                @discord.ui.button(
                    label="다운그레이드", style=discord.ButtonStyle.blurple, emoji="⭕"
                )
                async def button1_callback(self, button, interaction):
                    self.button_value = "다운그레이드"
                    self.stop()
                    await interaction.response.defer()

                @discord.ui.button(
                    label="취소하기", style=discord.ButtonStyle.red, emoji="❌"
                )
                async def button2_callback(self, button, interaction):
                    self.button_value = "취소함"
                    self.stop()
                    await interaction.response.defer()

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

            await ctx.respond(embed=embed, view=view)
            result = await view.wait()

            if result is True or view.button_value == "취소함":
                embed = discord.Embed(
                    title="낚시터 다운그레이드를 취소하였다.", colour=discord.Colour.light_grey()
                )
                return await ctx.edit(embed=embed, view=None)

            breaked = []
            breaked_cost = 0
            facs = room.facilities[:]  # 얕은 복사 (shallow copy)
            for i in facs:
                if i.startswith("_"):
                    continue
                fac = Facility(i)
                if fac.tier >= room.tier:
                    await room.break_facility(i)
                    await room.add_exp(fac.cost)
                    breaked_cost += fac.cost
                    breaked.append(fac.name)

            await room.break_facility(f"_TIER{room.tier}")
            if facility is not None:  # 1티어는 건물이 따로 없음
                await room.build_facility(facility.code)
            await room.add_exp(now_facility.cost)

            bonus = (
                ""
                if breaked == []
                else f"\n`❗ {', '.join(breaked)}이(가) 철거되어 추가로 ✨{breaked_cost:,}을 돌려받았습니다.`"
            )
            await ctx.edit(
                content=f"<@{ctx.author.id}> {room.name} 낚시터를 {room.tier} 티어로 다운그레이드 했어... 소박해졌네!"
                + bonus,
                embed=None,
                view=None,
            )

    @land_group.command(name="건설가능목록", description="특정 티어의 시설중 낚시터에 알려드려요!")
    @on_working(fishing=True, prohibition=True, landwork=True, twoball=False)
    async def facility_list(
        self,
        ctx: discord.ApplicationContext,
        tier: Option(int, "시설 목록을 알고 싶은 특정 티어를 입력해주세요!") = 1,
    ):
        await ctx.defer()
        room = await Room.fetch(ctx.channel)

        if room.tier < int(tier):
            return await ctx.respond(
                f"""어... 우리 낚시터는 {room.tier}티어인데...?
                `❗ 이 낚시터 티어보다 높은 값을 입력했습니다.`"""
            )

        fs = ""
        for i in room.can_build_facilities:
            if i.tier != tier:
                continue
            fs += f"\n[{i.tier}티어 / ✨ {i.cost:,}] {i.name}"
        embed = discord.Embed(colour=0x4BC59F)
        embed.add_field(
            name=f"🏗️ **건설 가능 {tier}티어 시설 보고서**",
            value=f"```cs\n{fs if fs != '' else '[없음]'}```",
            inline=False,
        )
        embed.set_footer(
            text="이프야 시설 (티어) // 낚시터를 업그레이드하거나 명성이 올라가면 더 많은 시설이 표기될 수 있어요!"
        )
        await ctx.respond(embed=embed)

    @land_group.command(name="검색", description="시설을 설명해드려요!")
    @on_working(prohibition=True)
    async def search_facility(
        self, ctx: discord.ApplicationContext, args: Option(str, "궁금하신 시설의 이름을 입력하세요!")
    ):
        await ctx.defer()
        arg1 = " ".join(args)
        try:
            facility = Facility(arg1.upper())
        except NotExistFacility:
            return await ctx.respond(
                "어... 어떤 시설인지 잘 모르게써!" "\n`❗ '/설명 <시설명>'이에요. 다시 한 번 시설명을 확인해 주세요.`"
            )

        embed = discord.Embed(title=f"《 {facility.name} 》", colour=0x4BC59F)
        description = f"[ 건설 가격 ] ✨ {facility.cost}"
        description += f"\n[ 요구 조건 ] 낚시터 {facility.tier}단계 확장 이상"
        if len(facility.biome) > 7:
            description += "\n[ 지형 조건 ] 어디에든 가능"
        else:
            description += f"\n[ 지형 조건 ] {', '.join([Constants.BIOME_KR[i] for i in facility.biome])}"
        description += f"\n[ 시설 종류 ] {Constants.UNIT_TYPE_KR[facility.branch]}"
        description += f"\n[ 시설 설명 ] {facility.description}"
        embed.add_field(
            name="🔍 **시설 정보**", value=f"```cs\n{description}```", inline=False
        )

        embed.add_field(
            name="📦 **시설 효과**",
            value=f"```diff\n{facility.effect_information()}```",
            inline=False,
        )
        embed.set_footer(text="`※ 같은 종류의 시설은 하나만 건설할 수 있습니다.`")
        await ctx.respond(embed=embed)

    @land_group.command(name="철거", description="이 낚시터(채널)에 설치된 시설을 철거해요!")
    @on_working(
        fishing=True, prohibition=True, landwork=True, owner_only=True, twoball=False
    )
    async def break_facility(
        self,
        ctx: discord.ApplicationContext,
        name: Option(
            str, "철거하실 시설의 이름을 입력해주세요!", autocomplete=autocomplete_facilities_uninstall
        ),
    ):
        await ctx.defer()
        arg1 = " ".join(name).replace("_", "")

        try:
            facility = Facility(arg1)
        except NotExistFacility:
            return await ctx.respond(
                "흐으음... 어떤 시설을 말하는 건지 잘 모르게써!!" "\n`❗ 시설의 이름을 다시 잘 확인해 주세요.`"
            )

        if facility.code.startswith("_"):
            return await ctx.respond(
                "어... 그 시설은 이 명령어로 철거할 수 없어!"
                "\n`❗ 만약 티어를 낮추려는 거라면 '이프야 다운그레이드' 명령어를 사용해 주세요.`"
            )

        room = await Room.fetch(ctx.channel)

        if facility.code not in room.facilities:
            return await ctx.respond(
                """어... 이프한테 없는 걸 철거하는 능력은 없어.
                `❗ 아직 건설되지 않은 시설입니다.`"""
            )

        async with room.work():
            embed = discord.Embed(
                title=f"{room.name} 땅에서 '{facility.name}' 시설을 철거할 거야?",
                description=f"반환되는 낚시터 명성 : ✨ {facility.cost}",
                colour=0x4BC59F,
            )

            class OXButtonView(View):
                def __init__(self, ctx):
                    super().__init__(timeout=10)
                    self.ctx = ctx
                    self.button_value = None

                @discord.ui.button(
                    label="철거하기", style=discord.ButtonStyle.blurple, emoji="⭕"
                )
                async def button1_callback(self, button, interaction):
                    self.button_value = "철거"
                    self.stop()
                    await interaction.response.defer()

                @discord.ui.button(
                    label="취소하기", style=discord.ButtonStyle.red, emoji="❌"
                )
                async def button2_callback(self, button, interaction):
                    self.button_value = "취소함"
                    self.stop()
                    await interaction.response.defer()

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

            await ctx.respond(embed=embed, view=view)
            result = await view.wait()

            if result is True or view.button_value == "취소함":
                embed = discord.Embed(
                    title="시설 철거를 취소하였다.", colour=discord.Colour.light_grey()
                )
                await ctx.edit(embed=embed, view=None)
                return

            await room.break_facility(facility.code)
            await room.add_exp(facility.cost)
            await ctx.edit(
                content=f"<@{ctx.author.id}> {room.name} 땅에서 **{facility.name}**을(를) 철거했어!",
                embed=None,
                view=None,
            )

    @land_group.command(name="건설", description="이 낚시터(채널)에 시설을 건설해요!")
    @on_working(
        fishing=True, prohibition=True, landwork=True, owner_only=True, twoball=False
    )
    async def build_facility(
        self,
        ctx: discord.ApplicationContext,
        name: Option(str, "건설하실 시설의 이름을 입력해주세요!", autocomplete=autocomplete_facilities),
    ):
        await ctx.defer()
        arg1 = " ".join(name).replace("_", "")

        try:
            facility = Facility(arg1)
        except NotExistFacility:
            return await ctx.respond(
                """흐으음... 어떤 시설을 말하는 건지 잘 모르게써!!
                `❗ 시설의 이름을 다시 잘 확인해 주세요.`"""
            )

        if facility.code.startswith("_"):
            return await ctx.respond(
                "어... 그 시설은 이 명령어로 철거할 수 없어!"
                "\n`❗ 만약 업그레이드 하시려는 거라면 '/업그레이드' 명령어를 사용해 주세요.`"
            )

        room = await Room.fetch(ctx.channel)

        if facility.cost > await room.get_exp():
            return await ctx.respond(
                f"""흐으음... 이 낚시터에는 아직 이른 시설이라고 생각해
                `❗ 낚시터 명성이 부족합니다. ( ✨ {facility.cost} 필요 )`"""
            )

        try:
            room.can_build_it(facility)
        except Exception as e:
            return await ctx.respond(str(e))
        async with room.work():
            embed = discord.Embed(
                title=f"{room.name} 땅에 '{facility.name}' 시설을 건설할 거야?",
                description=(
                    f"```cs\n{facility.description}\n{facility.effect_information()}```"
                    f"현재 낚시터 명성 : **✨ {await room.get_exp()}** ( ✨ {facility.cost} 소모 )"
                ),
                colour=0x4BC59F,
            )

            class OXButtonView(View):
                def __init__(self, ctx):
                    super().__init__(timeout=10)
                    self.ctx = ctx
                    self.button_value = None

                @discord.ui.button(
                    label="건설하기", style=discord.ButtonStyle.blurple, emoji="⭕"
                )
                async def button1_callback(self, button, interaction):
                    self.button_value = "건설"
                    self.stop()
                    await interaction.response.defer()

                @discord.ui.button(
                    label="취소하기", style=discord.ButtonStyle.red, emoji="❌"
                )
                async def button2_callback(self, button, interaction):
                    self.button_value = "취소함"
                    self.stop()
                    await interaction.response.defer()

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

            await ctx.respond(embed=embed, view=view)
            result = await view.wait()

            if result is True or view.button_value == "취소함":
                embed = discord.Embed(
                    title="시설 건설을 취소하였다.", colour=discord.Colour.light_grey()
                )
                await ctx.edit(embed=embed, view=None)
                return

            await room.build_facility(facility.code)
            await room.add_exp(facility.cost * -1)
            await ctx.edit(
                content=f"<@{ctx.author.id}> {room.name} 땅에 **{facility.name}**을(를) 건설했어!",
                embed=None,
                view=None,
            )


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(UnitCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
