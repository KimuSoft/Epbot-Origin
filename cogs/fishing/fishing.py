# 필수 임포트
from discord.commands import slash_command
from discord.commands import Option
from discord.ext import commands
from discord import Thread
import discord
import os
import ast
from utils import logger

# 부가 임포트
from cogs.fishing import fishing_group
from classes.room import Room, Facility, NotExistFacility
from classes.user import User
from classes.fish import Fish, NotFishException, search_fish
from db.seta_pgsql import S_PgSQL
from utils.on_working import on_working
from datetime import datetime, timezone

# 상수 임포트
from constants import Constants
from config import SLASH_COMMAND_REGISTER_SERVER as SCRS

userdata = S_PgSQL()


class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @fishing_group.command(name="정보", description="이 채널의 낚시터 정보를 보여줘요!")
    @commands.cooldown(1, 10, commands.BucketType.user)
    @on_working(prohibition=True)
    async def fishing_info(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        room = await Room.fetch(ctx.channel)
        fee_range = room.fee_range
        cleans = await room.get_cleans()
        created_at = room.channel.created_at
        
        print(room.channel, created_at)

        # 기본 정보
        roomdict = {
            "season": Constants.SEASON_KR[room.season],
            "type": "🗑️ 쓰레기장" if cleans < -100 else Constants.BIOME_KR[room.biome],
            "cost": f"{room.min_purchase:,} 💰",
            "exp": f"✨ {room._exp:,}",
            "fee": f"🧾 {room.fee}%",
            "clean": f"🧹 {cleans:,}",
            "members": f"👪 {len(ctx.channel.members):,}명",
            "history": (
                f"📜 {(datetime.now(timezone.utc) - created_at).days}일 ("
                + created_at.strftime("%y-%m-%d")
                + ")"
            ),
            "owner": f"<@{room.owner_id}>",
            "level_limit": f"{room.level_limit}",
        }

        # 수수료 설정이 가능한 경우
        if fee_range[0] != fee_range[1]:
            roomdict["fee"] += f" (설정 범위 {fee_range[0]}% ~ {fee_range[1]}%)"

        # 유지비가 있는 경우
        if room.maintenance != 0:
            roomdict["fee"] += f"\n<유지비> 🧾 {room.maintenance}%"

        tier = room.tier
        if not tier:
            embed = discord.Embed(
                title=ctx.channel.name,
                description=Constants.PUBLIC_ROOM_INFO_KR.format(**roomdict),
                colour=Constants.TIER_COLOR[tier],
            )
        else:
            embed = discord.Embed(
                title=ctx.channel.name,
                description=Constants.ROOM_INFO_KR.format(**roomdict),
                colour=Constants.TIER_COLOR[tier],
            )

            # 시설 정보
            facility_names = []
            for i in room.facilities:
                try:
                    nm = Facility(i).name
                except NotExistFacility:
                    nm = f"알 수 없는 시설({i})"
                facility_names.append(nm)

            if not facility_names == []:
                embed.add_field(
                    name="🏗️ **낚시터 시설 정보**",
                    value=f"```cs\n< 낚시터 레벨 : {tier}티어 > \n- {'///- '.join(facility_names)}```".replace(
                        "///", "\n"
                    ),
                    inline=False,
                )
                embed.set_footer(text="※ 각 시설에 대한 설명이 필요하다면 '/낚시터 시설 검색 <시설명>'")

        await ctx.respond(embed=embed)

    @slash_command(name="랭킹", description="이프의 랭킹을 보여줘요!")
    @on_working(prohibition=True)
    async def ranking(
        self,
        ctx: discord.ApplicationContext,
        type: Option(str, "보고 싶으신 랭킹의 종류를 고르세요!", choices=["개인", "낚시터"]),
    ):
        await ctx.defer()

        embed = discord.Embed(title="🏆 랭킹 정보", colour=0x4BC59F)

        rows = await userdata.select_sql(
            "users", "name, money", "ORDER BY money DESC LIMIT 5"
        )
        if type == "개인":
            ranking = ""
            for idx, val in enumerate(rows):
                ranking += f"\n[{idx + 1}등] {val[0]} ({int(val[1]):,}💰)"
            embed.add_field(
                name="💰 **돈 순위**", value=f"```cs\n{ranking}```", inline=False
            )

            rows = await userdata.select_sql(
                "users",
                "name, biggest_name, biggest_size",
                "WHERE biggest_size > 0 ORDER BY biggest_size DESC LIMIT 5",
            )
            ranking = ""
            for idx, val in enumerate(rows):
                ranking += f"\n[{idx + 1}등] {val[0]} ({val[1]}/{val[2]:,}cm)"
            embed.add_field(
                name="📏 **가장 긴 물고기**", value=f"```cs\n{ranking}```", inline=False
            )

            rows = await userdata.select_sql(
                "users", "name, exp", "ORDER BY exp DESC LIMIT 5"
            )
            ranking = ""
            for idx, val in enumerate(rows):
                ranking += f"\n[{idx + 1}등] {val[0]} (✒️Lv. {int((val[1] / 15) ** 0.5 + 1 if val[1] > 0 else 1)})"
            embed.add_field(
                name="✒️ **레벨 순위**", value=f"```cs\n{ranking}```", inline=False
            )

            rows = await userdata.select_sql(
                "users", "name, dex", "ORDER BY length(CAST(dex AS TEXT)) DESC LIMIT 5"
            )
            ranking = ""
            for idx, val in enumerate(rows):
                dex = ast.literal_eval(str(val[1]))
                v = 0
                for i in dex.keys():
                    if i != 0:
                        v += len(dex[i])
                ranking += f"\n[{idx + 1}등] {val[0]} (📖 {int(v * 100 / 788)}%)"
            embed.add_field(
                name="📖 **도감 순위**", value=f"```cs\n{ranking}```", inline=False
            )

            await ctx.respond(embed=embed)

        elif type == "낚시터":
            rows = await userdata.select_sql(
                "rooms", "name, land_value", "ORDER BY land_value DESC LIMIT 5"
            )
            ranking = ""
            for idx, val in enumerate(rows):
                ranking += f"\n[{idx + 1}등] {val[0]} ({val[1]:,}💰)"
            embed.add_field(
                name="🧾 **가장 높은 땅값 순위**", value=f"```cs\n{ranking}```", inline=False
            )

            rows = await userdata.select_sql(
                "rooms", "name, exp", "ORDER BY exp DESC LIMIT 5"
            )
            ranking = ""
            for idx, val in enumerate(rows):
                ranking += "\n[{idx}등] {name} (✨{money})".format(
                    idx=idx + 1, name=str(val[0]), money=val[1]
                )
            embed.add_field(
                name="✨ **낚시터 명성 순위**", value=f"```cs\n{ranking}```", inline=False
            )

            await ctx.respond(embed=embed)

    @slash_command(name="낚시중지", description="낚시 오류 발생시 낚시를 멈춰요!")
    @commands.cooldown(1, 600, commands.BucketType.user)
    @on_working(prohibition=True)
    async def stop_fishing(self, ctx: discord.ApplicationContext):
        await ctx.defer()

        user = await User.fetch(ctx.author)

        await user.finish_fishing()
        await ctx.respond(
            """낚시를 중지해써!
`❗ 이 명령어는 꼭 시스템적으로 예기치 못한 버그가 발생했을 때만 사용해 주세요!`"""
        )

    @slash_command(name="도감", description="물고기의 정보 or 도감을 보여드려요!")
    @on_working(prohibition=True)
    async def dex(
        self,
        ctx: discord.ApplicationContext,
        fish_name: Option(str, "검색하고 싶은 물고기 이름") = None,
    ):
        await ctx.defer()

        # 물고기가 낚인 이후
        user = await User.fetch(ctx.author)
        if fish_name is None:
            dexfish = 0
            for i in range(1, 6):
                dexfish += len(user.dex[str(i)]) if str(i) in user.dex.keys() else 0
            embed = discord.Embed(
                title="📖 이프 도감",
                description=f"완성률 **{int(100 * dexfish / 788)}% (788마리 중 {dexfish}마리)**",
                colour=0x4BC59F,
            )
            embed.set_footer(
                text="※ 물고기 정보가 궁금하다면 '/도감 <물고기>' // 현재 도감 완성률 기능은 베타 버전입니다! 물고기 밸런스 패치, 도감 정식 추가 이후에 초기화될 수 있어요!"
            )
            await ctx.respond(embed=embed)
            return None

        try:
            fish = await Fish.fetch(await search_fish(fish_name))
        except NotFishException:
            return await ctx.respond(
                """우움... 내 도감에서는 안 보이는데...?
`❗ 아직 잡은 적이 없거나 존재하지 않는 물고기입니다.`"""
            )
        except Exception:
            return await ctx.respond("`/도감 <물고기>`")

        if fish.rarity != 1 and (
            fish.rarity not in user.dex.keys() or fish.id not in user.dex[fish.rarity]
        ):
            return await ctx.respond(
                """우움... 내 도감에서는 안 보이는데...?
`❗ 아직 잡은 적이 없거나 존재하지 않는 물고기입니다.`"""
            )

        color = discord.Colour.dark_orange() if not fish.rarity else 0x4BC59F
        biome = fish.biomes
        for i in range(0, len(Constants.BIOME_KR) - 1):
            biome = biome.replace(str(i), Constants.BIOME_KR[i].split(" ")[0])
        embed = discord.Embed(
            title=f"{fish.id}. {fish.icon()} {fish.name}", colour=color
        )
        embed.add_field(name="📏 **평균 크기**", value=f"**{fish.average_length}**cm")
        embed.add_field(name="✨ **희귀도**", value=f"**{fish.rarity_str()}**")
        embed.add_field(name="💵 **평균가**", value=f"**{fish.average_cost}**")
        embed.add_field(name="🏞️ **서식지**", value=f"**>> {biome}**")
        await ctx.respond(embed=embed)

    @fishing_group.command(name="분석", description="이 낚시터에 서식하는 물고기와 확률을 분석해 드려요!")
    @commands.cooldown(3, 30)
    async def statistics(
        self,
        ctx: discord.ApplicationContext,
        type: Option(str, "분석 결과의 종류", choices=["일반", "단순 표현"]),
    ):
        await ctx.defer()

        accuracy = 20

        room = await Room.fetch(ctx.channel)
        rank_emoji = {0: "🟫", 1: "🟦", 2: "🟩", 3: "🟪", 4: "🟨", 5: "🟥"}
        bar_str = ""
        for i in range(0, 6):
            bar_str += rank_emoji[i] * int(accuracy * room.probability_per(i))
        bar_str += "⬛" * (accuracy - len(bar_str))
        if not (type == "단순 표현"):
            bar_str = f"`{bar_str}`"
        embed = discord.Embed(title="📊 통계청 조사 결과", description=bar_str, colour=0x4BC59F)

        # 낚을 수 있는 물고기 정보
        canfishing = await room.can_fishing_dict()
        list_str = "[흔함] " + (
            "<없음>"
            if canfishing[1] == []
            else ", ".join(canfishing[1][:3]) + f" 등 총 {len(canfishing[1])}종"
        )
        list_str += "\n[희귀함] " + (
            "<없음>"
            if canfishing[2] == []
            else ", ".join(canfishing[2][:3]) + f" 등 총 {len(canfishing[2])}종"
        )
        list_str += "\n[매우 귀함] " + (
            "<없음>"
            if canfishing[3] == []
            else ", ".join(canfishing[3][:3]) + f" 등 총 {len(canfishing[3])}종"
        )
        list_str += "\n[전설] " + (
            "<없음>"
            if canfishing[4] == []
            else ", ".join(canfishing[4][:3]) + f" 등 총 {len(canfishing[4])}종"
        )
        embed.add_field(
            name="🐟 **여기에서 낚을 수 있는 물고기**", value=f"```css\n{list_str}```", inline=False
        )
        embed.set_footer(text="※ 만약 통계청 보고서가 깨져 보인다면 '/낚시터 분석 <단순 표현>'")
        await ctx.respond(embed=embed)


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    logger.info("낚시 중 및 땅 작업 상태 초기화")
    bot.add_cog(InfoCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
