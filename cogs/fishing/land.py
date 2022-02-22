"""
    <fishing_land.py>
    매입, 매각 등 땅 관련 명령어가 모여 있습니다.
"""

# 필수 임포트
from discord.ext import commands
import discord
import os
import math
from utils import logger

# 부가 임포트
from classes.user import User
from classes.room import Room
from utils.util_box import wait_for_reaction, ox
from utils.on_working import on_working, p_requirements


class LandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @p_requirements()
    @on_working(fishing=True, landwork=True, prohibition=True, twoball=False)
    async def 매입(self, ctx, arg1=""):
        user = User(ctx.author)
        room = Room(ctx.channel)
        land_value = room.land_value
        min_purchase = room.min_purchase

        if not arg1.isdigit():
            if land_value == 0:
                value = 30000
            else:
                value = min_purchase
        else:
            value = int(arg1)

        if room.owner_id == ctx.author.id:
            await ctx.send("이미 여기 주인이자나!\n`❓ 낚시터에 걸린 돈을 조정하려면 '이프야 땅값변경' 명령어를 써 보세요.`")
            return None
        elif value < 30000:
            await ctx.send("땅 매입은 30,000 💰부터 가능해!")
            return None
        elif value > user.money:
            await ctx.send(f"자기 소지금보다 높게 부르면 안되지!\n`❗ 현재 소지금은 {user.money:,} 💰입니다.`")
            return None
        elif value < min_purchase:
            await ctx.send(
                f"{value} 💰로는 이 땅을 매입할 수 없어...!\n`❗ {room.name}의 최소 매입가는 {min_purchase:,} 💰입니다.`"
            )
            return None

        room.working_now = True
        embed = discord.Embed(
            title=f"{room.name} 땅을 {value:,}로 매입하시겠습니까?",
            description=f"소지금 : {user.money:,} 💰",
            colour=0x4BC59F,
        )
        window = await ctx.send(embed=embed, content=ctx.author.mention)

        if await ox(self.bot, window, ctx):
            embed = discord.Embed(
                title="매입을 취소하였다.", colour=discord.Colour.light_grey()
            )
            await window.edit(embed=embed)
            room.working_now = False
            return None

        origin_owner_id = room.owner_id
        user.purchase_land(room, value)
        room.working_now = False
        if min_purchase == 30000 and not (
            ctx.channel.topic is not None and "#매입보고" in ctx.channel.topic
        ):
            await ctx.send(
                f"**서버 주인**의 **{room.name}** 낚시터를 <@{user.id}>가 매입했어!"
                "\n`ℹ️ 돈이 걸려 있지 않은 땅도 매입 멘션을 받으려면 '#매입보고' 태그를 넣어 주세요!`"
            )
        else:
            await ctx.send(
                f"<@{origin_owner_id}>의 **{room.name}** 낚시터를 <@{user.id}>가 매입했어!"
            )

    @commands.command()
    @p_requirements()
    @on_working(
        fishing=True, prohibition=True, twoball=False
    )  # 번호로 다른 채널을 건드릴 수도 있으니 landwork는 제외
    async def 매각(self, ctx, *args):
        user = User(ctx.author)

        if len(args) != 0 and args[0].isdigit():  # 번호를 지정한 경우
            lands = user.myland_list()
            room = Room(lands[int(args[0]) - 1][0])
        else:
            room = Room(ctx.channel)

        if room.working_now:
            await ctx.send(
                "흐음... 여기 뭔가 하고 있는 거 같은데 조금 이따가 와 보자!\n`❗ 누군가 이미 땅에서 매입/매각/건설/철거 등의 작업을 하는 중이다.`"
            )
            return None
        elif room.owner_id != ctx.author.id:
            await ctx.send("다른 사람 땅을 내가 처리하면 안 돼지!")
            return None
        elif room.land_value == 0:
            await ctx.send("내가 만든 채널은 처리할 수 없어!")
            return None

        room.working_now = True
        if room.channel is not None and room.owner_id == room.channel.guild.owner_id:
            # 자기 서버 땅인데 추가로 돈이 걸린 경우

            embed = discord.Embed(
                title=f"{room.name} 땅의 돈을 회수하시겠습니까?\n(매각해도 지주는 바뀌지 않습니다.)",
                description=f"돌려 받는 금액 : {room.land_value:,} 💰",
                colour=0x4BC59F,
            )
            window = await ctx.send(embed=embed, content=ctx.author.mention)

            if await ox(self.bot, window, ctx):
                embed = discord.Embed(
                    title="돈 회수를 취소했다.", colour=discord.Colour.light_grey()
                )
                await window.edit(embed=embed)
                room.working_now = False
                return None

            embed = discord.Embed(
                title=f"{room.name} 땅에 있던 {room.land_value:,} 💰을 뺐다.", colour=0x4BC59F
            )
            user = User(ctx.author)
            user.add_money(room.land_value)  # 돈 돌려 주고
            room.land_value = 0

            await window.edit(embed=embed)
            room.working_now = False
            return None

        else:  # 다른 사람 땅인 경우
            embed = discord.Embed(
                title=f"{room.name} 땅을 매각하겠습니까?",
                description=f"돌려 받는 금액 : {room.land_value:,} 💰",
                colour=0x4BC59F,
            )
            window = await ctx.send(embed=embed, content=ctx.author.mention)

            if await ox(self.bot, window, ctx):
                embed = discord.Embed(
                    title="매각을 취소했다.", colour=discord.Colour.light_grey()
                )
                await window.edit(embed=embed)
                room.working_now = False
                return None

            embed = discord.Embed(
                title=f"{room.name} 땅을 매각하고 {room.land_value:,} 💰를 돌려받았다.",
                colour=0x4BC59F,
            )

            user = User(ctx.author)
            user.add_money(room.land_value)
            room.owner_id = 693818502657867878
            room.land_value = 0
            room.working_now = False

            await window.edit(embed=embed)

    @commands.command()
    @p_requirements(manage_messages=True)
    @on_working(fishing=True, prohibition=True)
    async def 내땅(self, ctx, *args):
        user = User(ctx.author)

        window = await ctx.send(content="`내 땅 목록`")
        mylands = list(user.myland_list())
        list_str = ""
        ridx = 0
        for idx, val in enumerate(mylands):
            if (len(args) == 0 and val[2] != 0) or (
                len(args) != 0 and " ".join(args) in val[1]
            ):
                list_str += "\n[{}] {} ({}💰)".format(idx + 1, val[1], val[2])
                ridx += 1
            if idx != 0 and ridx != 0 and ridx % 15 == 0:
                embed = discord.Embed(
                    title=f"💰 **내가 매입한 땅 목록 ({int((ridx-2)/15) + 1}/{math.ceil(len(mylands)/15)} 페이지)**",
                    description=f"```cs\n{list_str}```",
                    colour=0x4BC59F,
                )
                await window.edit(embed=embed)
                result = await wait_for_reaction(self.bot, window, ["➡️"], 10, ctx)
                await window.remove_reaction("➡️", ctx.author)
                if result is False:
                    await window.clear_reactions()
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
        await window.edit(embed=embed)
        await window.clear_reactions()

    @commands.command()
    @p_requirements()
    @on_working(
        fishing=True, landwork=True, prohibition=True, owner_only=True, twoball=False
    )
    async def 땅값변경(self, ctx, arg1=""):
        user = User(ctx.author)
        room = Room(ctx.channel)
        land_value = room.land_value
        room.working_now = True

        if not arg1.isdigit():
            value = 30000 if land_value == 0 else land_value + 3000
        else:
            value = int(arg1)

        if value < 30000:
            await ctx.send("땅 가격은 최소 30,000 💰부터 가능해!")
            room.working_now = False
            return None
        if value == room.land_value:
            await ctx.send("흐음... 똑같은뎅?")
            room.working_now = False
            return None
        if value > user.money + room.land_value:
            room.working_now = False
            return await ctx.send(
                f"흐음... 돈이 부족해!\n`❗ 현재 땅값과 소지금의 합이 {(room.land_value + user.money):,} 💰입니다.`"
            )

        embed = discord.Embed(
            title=f"{room.name} 땅을 {value:,}로 변경하시겠습니까?", colour=0x4BC59F
        )
        window = await ctx.send(embed=embed, content=ctx.author.mention)

        if await ox(self.bot, window, ctx):
            embed = discord.Embed(
                title="변경을 취소하였다.", colour=discord.Colour.light_grey()
            )
            await window.edit(embed=embed)
            room.working_now = False
            return None

        user.give_money(land_value - value)
        room.land_value = value
        room.working_now = False
        await ctx.send(f"{room.name} 땅의 가격을 변경했어!")

    @commands.command()
    @p_requirements()
    @on_working(
        fishing=True, landwork=True, prohibition=True, owner_only=True, twoball=False
    )
    async def 수수료(self, ctx, *args):
        if args == () or not args[0].replace("%", "").isdigit():
            await ctx.send("`이프야 수수료 (숫자)`")
            return None
        value = int(args[0].replace("%", ""))
        room = Room(ctx.channel)

        fee_range = room.fee_range
        if value < fee_range[0] or fee_range[1] < value:
            embed = discord.Embed(
                title="수수료 조정 범위를 잘 살펴 봐 줘!",
                description=f"`❗ 수수료 지정 가능 범위가 {fee_range[0]}% ~ {fee_range[1]}%입니다.`",
                colour=0x4BC59F,
            )
            await ctx.send(embed=embed, reference=ctx.message)
            return None

        embed = discord.Embed(
            title=f"{room.name} 땅의 수수료를 {value}%로 변경하시겠습니까?", colour=0x4BC59F
        )
        window = await ctx.send(embed=embed, reference=ctx.message)

        if await ox(self.bot, window, ctx):
            embed = discord.Embed(
                title="수수료 변경을 취소하였다.", colour=discord.Colour.light_grey()
            )
            await window.edit(embed=embed)
            return None

        room.fee = value
        embed = discord.Embed(
            title=f"{room.name} 땅의 수수료를 {value}%로 변경하였다!", colour=0x4BC59F
        )
        await window.edit(embed=embed)

    @commands.command()
    @p_requirements()
    @on_working(
        fishing=True, prohibition=True, twoball=False, owner_only=True, landwork=True
    )
    async def 청소업체(self, ctx):
        room = Room(ctx.channel)

        if room.cleans >= 0:
            return await ctx.send(
                "이 낚시터에는 굳이 청소 업체를 부를 필요가 없을 것 같아!\n`❗ 청소 업체는 청결도가 음수가 되었을 때만 부를 수 있습니다.`"
            )
        user = User(ctx.author)

        price = room.cleans * 150
        room.working_now = True
        embed = discord.Embed(
            title=f"청소 업체를 불러 {room.name} 땅의 청결도를 0으로 만드시겠습니까?",
            description=f"예상 필요 금액 {-1 * price:,} 💰",
            colour=0x4BC59F,
        )
        window = await ctx.send(embed=embed, content=ctx.author.mention)

        if await ox(self.bot, window, ctx):
            embed = discord.Embed(
                title="청소 업체 부르기를 취소했다.", colour=discord.Colour.light_grey()
            )
            room.working_now = False
            return await window.edit(embed=embed)

        if user.money < -1 * price:
            embed = discord.Embed(title="돈이 부족해...", colour=discord.Colour.light_grey())
            room.working_now = False
            return await window.edit(embed=embed)

        embed = discord.Embed(
            title=f"{-1 * price:,} 💰로 청소 업체를 불러서 {room.name} 낚시터가 깔끔해졌어!",
            colour=0x4BC59F,
        )
        user.add_money(price)  # 돈 돌려 주고
        room.cleans = 0

        await window.edit(embed=embed)
        room.working_now = False


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(LandCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
