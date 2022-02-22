"""
    <sample.py>
    여러분들의 기능을 여기에 마음껏 추가해 봐요!
"""

# 필수 임포트
from discord.ext import commands
import discord
import os
import ast
from utils import logger

# 부가 임포트
from classes.room import Room, Facility, NotExistFacility
from classes.user import User
from classes.fish import Fish, NotFishException, search_fish
from db.seta_pgsql import S_PgSQL
from utils.on_working import on_working
from datetime import datetime

# 상수 임포트
from constants import Constants

userdata = S_PgSQL()


class InfoCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command()
    @on_working(prohibition=True)
    async def 여기(self, ctx):
        room = Room(ctx.channel)
        fee_range = room.fee_range
        cleans = room._cleans
        created_at = ctx.channel.created_at

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
                f"📜 {(datetime.today() - created_at).days}일 ("
                + created_at.strftime("%y-%m-%d")
                + ")"
            ),
            "owner": f"<@{room.owner_id}>",
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
                embed.set_footer(text="※ 각 시설에 대한 설명이 필요하다면 '이프야 설명 <시설명>'")

        await ctx.send(embed=embed)

    @commands.command()
    @on_working(prohibition=True)
    async def 랭킹(self, ctx, *args):
        embed = discord.Embed(title="🏆 랭킹 정보", colour=0x4BC59F)

        rows = userdata.select_sql(
            "users", "name, money", "ORDER BY money DESC LIMIT 5"
        )
        if "".join(args) == "개인":
            ranking = ""
            for idx, val in enumerate(rows):
                ranking += f"\n[{idx+1}등] {val[0]} ({int(val[1]):,}💰)"
            embed.add_field(
                name="💰 **돈 순위**", value=f"```cs\n{ranking}```", inline=False
            )

            rows = userdata.select_sql(
                "users",
                "name, biggest_name, biggest_size",
                "WHERE biggest_size > 0 ORDER BY biggest_size DESC LIMIT 5",
            )
            ranking = ""
            for idx, val in enumerate(rows):
                ranking += f"\n[{idx+1}등] {val[0]} ({val[1]}/{val[2]:,}cm)"
            embed.add_field(
                name="📏 **가장 긴 물고기**", value=f"```cs\n{ranking}```", inline=False
            )

            rows = userdata.select_sql(
                "users", "name, exp", "ORDER BY exp DESC LIMIT 5"
            )
            ranking = ""
            for idx, val in enumerate(rows):
                ranking += f"\n[{idx+1}등] {val[0]} (✒️Lv. {int((val[1]/15)**0.5 + 1 if val[1] > 0 else 1)})"
            embed.add_field(
                name="✒️ **레벨 순위**", value=f"```cs\n{ranking}```", inline=False
            )

            rows = userdata.select_sql(
                "users", "name, dex", "ORDER BY length(CAST(dex AS TEXT)) DESC LIMIT 5"
            )
            ranking = ""
            for idx, val in enumerate(rows):
                dex = ast.literal_eval(str(val[1]))
                v = 0
                for i in dex.keys():
                    if i != 0:
                        v += len(dex[i])
                ranking += f"\n[{idx+1}등] {val[0]} (📖 {int(v * 100 / 788)}%)"
            embed.add_field(
                name="📖 **도감 순위**", value=f"```cs\n{ranking}```", inline=False
            )

            await ctx.send(embed=embed)

        elif "".join(args) == "낚시터":
            rows = userdata.select_sql(
                "rooms", "name, land_value", "ORDER BY land_value DESC LIMIT 5"
            )
            ranking = ""
            for idx, val in enumerate(rows):
                ranking += f"\n[{idx+1}등] {val[0]} ({val[1]:,}💰)"
            embed.add_field(
                name="🧾 **가장 높은 땅값 순위**", value=f"```cs\n{ranking}```", inline=False
            )

            rows = userdata.select_sql(
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

            await ctx.send(embed=embed)
        else:
            await ctx.send("어떤 랭킹을 보고 싶은 거야?\n`이프야 랭킹 (개인/낚시터)`")

    @commands.cooldown(1, 600, commands.BucketType.user)
    @commands.command()
    @on_working(prohibition=True)
    async def 낚시중지(self, ctx):
        User(ctx.author).finish_fishing()
        await ctx.send(
            """낚시를 중지해써!
            `❗ 이 명령어는 꼭 시스템적으로 예기치 못한 버그가 발생했을 때만 사용해 주세요!`"""
        )

    @commands.command()
    @on_working(prohibition=True)
    async def 도감(self, ctx, arg1=None):
        # 물고기가 낚인 이후
        user = User(ctx.author)
        if arg1 is None:
            dexfish = 0
            for i in range(1, 6):
                dexfish += len(user.dex[str(i)]) if str(i) in user.dex.keys() else 0
            embed = discord.Embed(
                title="📖 이프 도감",
                description=f"완성률 **{int(100 * dexfish/788)}% (788마리 중 {dexfish}마리)**",
                colour=0x4BC59F,
            )
            embed.set_footer(
                text="※ 물고기 정보가 궁금하다면 '이프야 도감 (물고기)' // 현재 도감 완성률 기능은 베타 버전입니다! 물고기 밸런스 패치, 도감 정식 추가 이후에 초기화될 수 있어요!"
            )
            await ctx.send(embed=embed, reference=ctx.message)
            return None

        try:
            fish = Fish(search_fish(arg1))
        except NotFishException:
            return await ctx.send(
                """우움... 내 도감에서는 안 보이는데...?
                `❗ 아직 잡은 적이 없거나 존재하지 않는 물고기입니다.`"""
            )
        except Exception:
            return await ctx.send("`이프야 도감 (물고기)`")

        if fish.rarity != 1 and (
            fish.rarity not in user.dex.keys() or fish.id not in user.dex[fish.rarity]
        ):
            return await ctx.send(
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
        await ctx.send(embed=embed, reference=ctx.message)

    @commands.cooldown(3, 30)
    @commands.command()
    async def 분석(self, ctx, *args):
        accuracy = 20

        room = Room(ctx.channel)
        rank_emoji = {0: "🟫", 1: "🟦", 2: "🟩", 3: "🟪", 4: "🟨", 5: "🟥"}
        bar_str = ""
        for i in range(0, 6):
            bar_str += rank_emoji[i] * int(accuracy * room.probability_per(i))
        bar_str += "⬛" * (accuracy - len(bar_str))
        if not (len(args) == 1 and args[0] == "e"):
            bar_str = f"`{bar_str}`"
        embed = discord.Embed(title="📊 통계청 조사 결과", description=bar_str, colour=0x4BC59F)

        # 낚을 수 있는 물고기 정보
        canfishing = room.can_fishing_dict
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
        embed.set_footer(text="※ 만약 통계청 보고서가 깨져 보인다면 '이프야 분석 e'")
        await ctx.send(embed=embed)


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    userdata.update_sql("users", "fishing_now=0")  # 플레이 상태 초기화
    userdata.update_sql("rooms", "selling_now=0")  # 플레이 상태 초기화
    logger.info("낚시 중 및 땅 작업 상태 초기화")
    bot.add_cog(InfoCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
