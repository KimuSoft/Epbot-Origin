"""
    <fishing_unit.py>
    건설, 철거 등 시설 관련 명령어가 있습니다.
"""

# 필수 임포트
from discord.ext import commands
import discord
import os

from constants import Constants
from utils import logger

# 부가 임포트
from classes.room import Room, Facility, NotExistFacility
from utils.util_box import ox
from utils.on_working import on_working, p_requirements


class UnitCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @p_requirements()
    @on_working(
        fishing=True, prohibition=True, landwork=True, owner_only=True, twoball=False
    )
    async def 업그레이드(self, ctx):
        room = Room(ctx.channel)
        try:
            facility = Facility(f"_TIER{room.tier + 1}")

        # 더 이상의 업그레이드 시설이 존재하지 않는 경우
        except NotExistFacility:
            return await ctx.send(
                """더 이상의 업그레이드는 불가능한 것 같아!
                `❗ 축하합니다! 모든 업그레이드를 완료하셨습니다!`"""
            )

        room.working_now = True  # 땅 작업 시작
        embed = discord.Embed(
            title=f"{room.name} 땅에 '{facility.name}' 시설을 건설하여 {room.tier + 1}티어로 업그레이드할 거야?",
            description=(
                f"```cs\n{facility.description}\n{facility.effect_information()}"
                f"```현재 낚시터 명성 : ✨ {room.exp} ( ✨ {facility.cost} 소모 )"
            ),
            colour=0x4BC59F,
        )
        window = await ctx.send(embed=embed, content=ctx.author.mention)

        if await ox(self.bot, window, ctx):
            room.working_now = False  # 땅 작업 종료
            embed = discord.Embed(
                title="낚시터 업그레이드를 취소하였다.", colour=discord.Colour.light_grey()
            )
            return await window.edit(embed=embed)

        # 낚시터 명성이 부족한 경우
        if facility.cost > room.exp:
            room.working_now = False  # 땅 작업 종료
            return await ctx.send(
                f"""으움... 기각당했어...
                `❗ 낚시터 명성이 부족합니다. ( ✨ {facility.cost} 필요 )`"""
            )

        # 1티어의 경우 전용 시설이 없으므로 무시
        if not room.tier == 1:
            room.break_facility(f"_TIER{room.tier}")
        room.build_facility(facility.code)
        room.add_exp(facility.cost * -1)
        room.working_now = False
        await ctx.send(
            f"""<@{ctx.author.id}> {room.name} 낚시터가 {room.tier} 티어로 업그레이드 했어! 축하해!
            `🎉 이제 새로운 종류의 시설을 건설할 수 있게 되었습니다!`"""
        )

    @commands.command()
    @p_requirements()
    @on_working(fishing=True, prohibition=True, landwork=True, owner_only=True)
    async def 공영화(self, ctx):
        room = Room(ctx.channel)
        if ctx.channel.guild.owner_id != ctx.author.id:
            return await ctx.send(
                "낚시터 공영화는 서버 주인만 할 수 있어!"
                "\n`❗ 공공 낚시터로 만들려면 '이프야 다운그레이드' 명령어로 1티어까지 낮춰 주세요.`"
            )
        if room.tier > 2:
            return await ctx.send(
                """1티어 낚시터만 공공 낚시터로 만들 수 있어!
                `❗ 공공 낚시터로 만들려면 '이프야 다운그레이드' 명령어로 1티어까지 낮춰 주세요.`"""
            )
        if not room.tier:
            return await ctx.send(
                """이미 여기는 공공 낚시터인 걸...?
                `❗ 다시 주인이 있는 낚시터로 바꾸고 싶다면 '이프야 민영화' 명령어를 사용해 보세요.`"""
            )

        embed = discord.Embed(
            title=f"{room.name} 낚시터를 공공 낚시터로 만들 거야?",
            description="**❗ 공공 낚시터로 만들 시 다른 모든 시설은 철거됩니다!**",
            colour=0x4BC59F,
        )

        room.working_now = True
        window = await ctx.send(embed=embed, content=ctx.author.mention)

        if await ox(self.bot, window, ctx):
            room.working_now = False
            embed = discord.Embed(
                title="낚시터 공영화를 취소하였다.", colour=discord.Colour.light_grey()
            )
            return await window.edit(embed=embed)

        breaked = []
        breaked_cost = 0
        facs = room.facilities[:]  # 얕은 복사 (shallow copy)
        for i in facs:
            if i.startswith("_"):
                continue
            fac = Facility(i)
            room.break_facility(i)
            room.add_exp(fac.cost)
            breaked_cost += fac.cost
            breaked.append(fac.name)
        room.build_facility("_TIER0")
        await ctx.send(f"<@{ctx.author.id}> {room.name} 낚시터는 이제 공공 낚시터야!")
        room.working_now = False

    @commands.command()
    @p_requirements()
    @on_working(fishing=True, prohibition=True, landwork=True, owner_only=True)
    async def 민영화(self, ctx):
        room = Room(ctx.channel)
        if ctx.channel.guild.owner_id != ctx.author.id:
            return await ctx.send(
                "낚시터 민영화는 서버 주인만 할 수 있어!" "\n`❗ 낚시터 민영화는 서버 주인만 할 수 있습니다.`"
            )
        if room.tier != 0:
            return await ctx.send(
                """여긴 이미 공공 낚시터가 아닌데...?
                `❗ 민영화는 공공 낚시터를 일반 낚시터로 되돌리는 명령어입니다.`"""
            )

        embed = discord.Embed(
            title=f"{room.name} 낚시터를 공공 낚시터에서 다시 일반 낚시터로 만들 거야?", colour=0x4BC59F
        )

        room.working_now = True
        window = await ctx.send(embed=embed, content=ctx.author.mention)

        if await ox(self.bot, window, ctx):
            room.working_now = False
            embed = discord.Embed(
                title="낚시터 민영화를 취소하였다.", colour=discord.Colour.light_grey()
            )
            return await window.edit(embed=embed)
        room.break_facility("_TIER0")
        await ctx.send(f"<@{ctx.author.id}> {room.name} 낚시터는 이제 공공 낚시터가 아니야!")
        room.working_now = False

    @commands.command()
    @p_requirements()
    @on_working(
        fishing=True, prohibition=True, landwork=True, owner_only=True, twoball=False
    )
    async def 다운그레이드(self, ctx):
        room = Room(ctx.channel)

        if room.tier == 1:
            return await ctx.send(
                """더 이상의 다운그레이드는 불가능한 것 같아!
                `❗ 1티어에서는 다운그레이드를 하실 수 없어요!`"""
            )
        elif room.tier == 2:
            facility = None
            embed = discord.Embed(
                title=f"{room.name} 땅을 1티어로 다운그레이드할 거야?",
                description=(
                    f"**❗ 티어를 낮출 시 상위 티어의 시설들은 자동으로 철거 됩니다!**"
                    f"\n현재 낚시터 명성 : ✨ {room.exp:,}"
                ),
                colour=0x4BC59F,
            )
        else:
            facility = Facility(f"_TIER{room.tier - 1}")
            embed = discord.Embed(
                title=f"{room.name} 땅을 {room.tier - 1}티어로 다운그레이드할 거야?",
                description=(
                    f"**❗ 티어를 낮출 시 상위 티어의 시설들은 자동으로 철거 됩니다!**"
                    f"\n현재 낚시터 명성 : ✨ {room.exp:,} ( ✨ {facility.cost:,} 다시 받음 )"
                ),
                colour=0x4BC59F,
            )

        now_facility = Facility(f"_TIER{room.tier}")

        room.working_now = True
        window = await ctx.send(embed=embed, content=ctx.author.mention)

        if await ox(self.bot, window, ctx):
            room.working_now = False
            embed = discord.Embed(
                title="낚시터 다운그레이드를 취소하였다.", colour=discord.Colour.light_grey()
            )
            return await window.edit(embed=embed)

        breaked = []
        breaked_cost = 0
        facs = room.facilities[:]  # 얕은 복사 (shallow copy)
        for i in facs:
            if i.startswith("_"):
                continue
            fac = Facility(i)
            if fac.tier >= room.tier:
                room.break_facility(i)
                room.add_exp(fac.cost)
                breaked_cost += fac.cost
                breaked.append(fac.name)

        room.break_facility(f"_TIER{room.tier}")
        if facility is not None:  # 1티어는 건물이 따로 없음
            room.build_facility(facility.code)
        room.add_exp(now_facility.cost)
        room.working_now = False

        bonus = (
            ""
            if breaked == []
            else f"\n`❗ {', '.join(breaked)}이(가) 철거되어 추가로 ✨{breaked_cost:,}을 돌려받았습니다.`"
        )
        await ctx.send(
            f"<@{ctx.author.id}> {room.name} 낚시터를 {room.tier} 티어로 다운그레이드 했어... 소박해졌네!"
            + bonus
        )

    @commands.command()
    @on_working(fishing=True, prohibition=True, landwork=True, twoball=False)
    async def 시설(self, ctx, arg1="1"):
        if not arg1.isdigit() or int(arg1) < 1:
            return await ctx.send("`❔ 이프야 시설 (티어)`")
        room = Room(ctx.channel)

        if room.tier < int(arg1):
            return await ctx.send(
                f"""어... 우리 낚시터는 {room.tier}티어인데...?
                `❗ 이 낚시터 티어보다 높은 값을 입력했습니다.`"""
            )

        fs = ""
        for i in room.can_build_facilities:
            if arg1.isdigit() and i.tier != int(arg1):
                continue
            fs += f"\n[{i.tier}티어 / ✨ {i.cost:,}] {i.name}"
        embed = discord.Embed(colour=0x4BC59F)
        embed.add_field(
            name=f"🏗️ **건설 가능 {arg1}티어 시설 보고서**",
            value=f"```cs\n{fs if fs != '' else '[없음]'}```",
            inline=False,
        )
        embed.set_footer(
            text="이프야 시설 (티어) // 낚시터를 업그레이드하거나 명성이 올라가면 더 많은 시설이 표기될 수 있어요!"
        )
        await ctx.send(embed=embed, reference=ctx.message)

    @commands.command()
    @on_working(prohibition=True)
    async def 설명(self, ctx, *args):
        arg1 = " ".join(args)
        if arg1 == "":
            await ctx.send("`이프야 설명 <시설명>`")
            return None
        try:
            facility = Facility(arg1.upper())
        except NotExistFacility:
            return await ctx.send(
                "어... 어떤 시설인지 잘 모르게써!" "\n`❗ '이프야 설명 <시설명>'이에요. 다시 한 번 시설명을 확인해 주세요.`"
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
        await ctx.send(embed=embed)

    @commands.command()
    @p_requirements()
    @on_working(
        fishing=True, prohibition=True, landwork=True, owner_only=True, twoball=False
    )
    async def 철거(self, ctx, *args):
        arg1 = " ".join(args).replace("_", "")
        if arg1 == "":
            return await ctx.send("`이프야 철거 <시설명>`")

        try:
            facility = Facility(arg1)
        except NotExistFacility:
            return await ctx.send(
                "흐으음... 어떤 시설을 말하는 건지 잘 모르게써!!" "\n`❗ 시설의 이름을 다시 잘 확인해 주세요.`"
            )

        if facility.code.startswith("_"):
            return await ctx.send(
                "어... 그 시설은 이 명령어로 철거할 수 없어!"
                "\n`❗ 만약 티어를 낮추려는 거라면 '이프야 다운그레이드' 명령어를 사용해 주세요.`"
            )

        room = Room(ctx.channel)

        if facility.code not in room.facilities:
            return await ctx.send(
                """어... 이프한테 없는 걸 철거하는 능력은 없어.
                `❗ 아직 건설되지 않은 시설입니다.`"""
            )

        room.working_now = True
        embed = discord.Embed(
            title=f"{room.name} 땅에서 '{facility.name}' 시설을 철거할 거야?",
            description=f"반환되는 낚시터 명성 : ✨ {facility.cost}",
            colour=0x4BC59F,
        )
        window = await ctx.send(embed=embed, content=ctx.author.mention)

        if await ox(self.bot, window, ctx):
            embed = discord.Embed(
                title="시설 철거를 취소하였다.", colour=discord.Colour.light_grey()
            )
            await window.edit(embed=embed)
            room.working_now = False
            return

        room.break_facility(facility.code)
        room.add_exp(facility.cost)
        room.working_now = False
        await ctx.send(
            f"<@{ctx.author.id}> {room.name} 땅에서 **{facility.name}**을(를) 철거했어!"
        )

    @commands.command()
    @p_requirements()
    @on_working(
        fishing=True, prohibition=True, landwork=True, owner_only=True, twoball=False
    )
    async def 건설(self, ctx, *args):
        arg1 = " ".join(args).replace("_", "")
        if arg1 == "":
            await ctx.send("`이프야 건설 <시설명>`")
            return

        try:
            facility = Facility(arg1)
        except NotExistFacility:
            return await ctx.send(
                """흐으음... 어떤 시설을 말하는 건지 잘 모르게써!!
                `❗ 시설의 이름을 다시 잘 확인해 주세요.`"""
            )

        if facility.code.startswith("_"):
            return await ctx.send(
                "어... 그 시설은 이 명령어로 철거할 수 없어!"
                "\n`❗ 만약 업그레이드 하시려는 거라면 '이프야 업그레이드' 명령어를 사용해 주세요.`"
            )

        room = Room(ctx.channel)

        if facility.cost > room.exp:
            return await ctx.send(
                f"""흐으음... 이 낚시터에는 아직 이른 시설이라고 생각해
                `❗ 낚시터 명성이 부족합니다. ( ✨ {facility.cost} 필요 )`"""
            )

        try:
            room.can_build_it(facility)
        except Exception as e:
            return await ctx.send(str(e))

        room.working_now = True  # 땅 작업 시작
        embed = discord.Embed(
            title=f"{room.name} 땅에 '{facility.name}' 시설을 건설할 거야?",
            description=(
                f"```cs\n{facility.description}\n{facility.effect_information()}```"
                f"현재 낚시터 명성 : **✨ {room.exp}** ( ✨ {facility.cost} 소모 )"
            ),
            colour=0x4BC59F,
        )
        window = await ctx.send(embed=embed, content=ctx.author.mention)

        if await ox(self.bot, window, ctx):
            embed = discord.Embed(
                title="시설 건설을 취소하였다.", colour=discord.Colour.light_grey()
            )
            await window.edit(embed=embed)
            room.working_now = False  # 땅 작업 종료
            return

        room.build_facility(facility.code)
        room.add_exp(facility.cost * -1)
        room.working_now = False  # 땅 작업 종료
        await ctx.send(
            f"<@{ctx.author.id}> {room.name} 땅에 **{facility.name}**을(를) 건설했어!"
        )


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(UnitCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
