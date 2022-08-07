"""
    <admin.py>
    봇 관리자 전용 명령어를 모아 두었습니다.
    TODO: 너무 많아서 분류 별로 클래스를 나누자
    eval 명령어도 추가
"""

import ast
import datetime
import os
import random

import discord

# 필수 임포트
from discord.commands import slash_command
from discord.ext import commands, tasks

import config
from classes.room import Room
from classes.user import User
from utils import logger

# 부가 임포트
from utils import on_working
from utils.util_box import wait_for_saying, ox

# https://gist.github.com/simmsb/2c3c265813121492655bc95aa54da6b9
def insert_returns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])

    if isinstance(body[-1], ast.If):
        insert_returns(body[-1].body)
        insert_returns(body[-1].orelse)

    if isinstance(body[-1], ast.With):
        insert_returns(body[-1].body)


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @on_working.administrator()
    @slash_command(
        name="계란",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        decription="관리자 디버그용 도구입니다. (관리자 전용)",
    )
    async def 계란(self, ctx: discord.ApplicationContext, args: str):
        here = await Room.fetch(ctx.channel)
        me = await User.fetch(ctx.author)

        logger.info(f"{me.name}이(가) {here.name}에서 계란 명령어 사용")

        text = args
        try:

            async def aexec(code):
                exec(
                    f"async def __ex(): " + "".join(f"\n {l}" for l in code.split("\n"))
                )
                return await locals()["__ex"]()

            await aexec(text)
        except Exception as e:
            embed = discord.Embed(color=0x980000, timestamp=datetime.datetime.today())
            embed.add_field(
                name="🐣  **Cracked!**",
                value=f"```css\n[입구] {text}\n[오류] {e}```",
                inline=False,
            )
            logger.err(e)
        else:
            embed = discord.Embed(color=0x00A495, timestamp=datetime.datetime.today())
            embed.add_field(
                name="🥚  **Oxec**", value=f"```css\n[입구] {text}```", inline=False
            )
        embed.set_footer(
            text=f"{ctx.author.name} • 달걀",
            # 작동하지 않음
            # icon_url=str(ctx.author.avatar_url_as(static_format="png", size=128)),
        )
        await ctx.respond(embed=embed)

    @on_working.administrator()
    @slash_command(
        name="달걀",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        description="관리자 디버그용 도구입니다. (관리자 전용)",
    )
    async def 달걀(self, ctx: discord.ApplicationContext, args: str):
        here = await Room.fetch(ctx.channel)
        me = await User.fetch(ctx.author)

        logger.info(f"{me.name}이(가) {here.name}에서 달걀 명령어 사용")

        text = args
        try:
            fn_name = "_eval_expr"

            cmd = text

            # add a layer of indentation
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())

            # wrap in async def body
            body = f"async def {fn_name}():\n{cmd}"

            parsed = ast.parse(body)
            body = parsed.body[0].body

            insert_returns(body)

            env = {
                "bot": ctx.bot,
                "discord": discord,
                "ctx": ctx,
                "__import__": __import__,
                "here": here,
                "me": me,
                "Room": Room,
                "User": User,
            }
            exec(compile(parsed, filename="<ast>", mode="exec"), env)

            result = await eval(f"{fn_name}()", env)
        except Exception as e:
            embed = discord.Embed(color=0x980000, timestamp=datetime.datetime.today())
            embed.add_field(
                name="🐣  **Cracked!**",
                value=f"```css\n[입구] {text}\n[오류] {e}```",
                inline=False,
            )
            logger.err(e)
        else:
            embed = discord.Embed(color=0x00A495, timestamp=datetime.datetime.today())
            embed.add_field(
                name="🥚  **Oval**",
                value=f"```css\n[입구] {text}\n[출구] {result}```",
                inline=False,
            )
        embed.set_footer(
            text=f"{ctx.author.name} • 달걀",
            # 작동하지 않음
            # icon_url=str(ctx.author.avatar_url_as(static_format="png", size=128)),
        )
        await ctx.respond(embed=embed)

    # 팡 하면 펑 하고 터짐
    @on_working.administrator()
    @slash_command(
        name="팡",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        description="관리자 디버그용 도구입니다. (관리자 전용)",
    )
    async def 팡(self, ctx):
        await ctx.respond(f"펑! 💥\n`지연 시간 : {int(self.bot.latency * 1000)}ms`")
        raise Exception

    # 팡 하면 펑 하고 터짐
    @on_working.administrator()
    @slash_command(
        name="핑핑",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        description="관리자 디버그용 도구입니다. (관리자 전용)",
    )
    async def 핑핑(self, ctx):
        ping = [f"#shard_{i[0]} ({int(i[1] * 1000)}ms)" for i in self.bot.latencies]
        text = "\n".join(ping)
        await ctx.respond(f"퐁퐁! 🏓🏓\n```css\n[ 지연 시간 ]\n{text}```")

    @slash_command(
        name="공지",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        description="관리자 공지용 도구입니다. (관리자 전용)",
    )
    @on_working.administrator()
    async def 공지(self, ctx: discord.commands.context.ApplicationContext):
        old = await ctx.respond(
            """공지를 어떻게 쓸 거야?
            `✏️ 미리 복사해 둔 공지 내용을 붙여넣어 줘! (준비가 안 됐다면 '취소'라고 적어줘!)`"""
        )
        message = await wait_for_saying(self.bot, 10, ctx, user=ctx.author)
        if not message or message.content == "취소":
            return await old.edit(content="준비되면 말해 줘!\n`❗ 입력이 취소되었다.`")

        news_embed = discord.Embed(
            title="📰  **이프 속보!**", color=0x00A495, timestamp=datetime.datetime.now()
        )
        news_embed.add_field(
            name="**❝" + message.content.split("\n")[0] + "❞**",
            value="\n".join(message.content.split("\n")[1:]),
            inline=False,
        )
        news_embed.add_field(
            name="ㆍ",
            value="**이프 공식 서버 바로가기** ▶ [키뮤의 과학실](https://discord.gg/XQuexpQ)\n`채널 주제에 '#공지'가 있는 곳에 우선적으로 공지를 전송해요!`",
            inline=False,
        )
        news_embed.set_footer(
            text=f"{ctx.author.name} • #공지",
            # 작동하지 않음
            # icon_url=str(ctx.author.avatar_url_as(static_format="png", size=128)),
        )
        """
        news_embed.set_thumbnail(
            url=str(self.bot.user.avatar_url_as(static_format="png", size=256))
        )
        """
        await old.delete()
        try:
            window = await ctx.send(
                content="이렇게 보낼 거야?", embed=news_embed, reference=message
            )
        except Exception:
            await ctx.send(content="최소 두 줄 이상이어야 해!\n`❗ 첫 줄은 제목, 둘째 줄부터는 내용이다.`")
            return None
        if await ox(self.bot, window, ctx):
            await window.edit(content="잘 확인해서 다시 써 줘!\n```❗ 입력이 취소되었다.```")
            return None

        embed = discord.Embed(title="⌛  **공지를 보낼 채널을 선정하는 중...**", color=0x00A495)
        target_list = []
        await ctx.send(content="", embed=embed)

        load_error = 0
        error_num = 0
        success = 0
        for guild in self.bot.guilds:  # 서버 리스트
            if not guild.text_channels:
                load_error += 1
                continue

            target = None
            for channel in guild.text_channels:  # 서버 리스트 -> 텍스트 채널 리스트
                if "#공지" in str(channel.topic):
                    target = channel
                    break
            if target is None:  # 공지 태그가 있는 채널이 없으면 랜덤 전송
                target_list.append(random.choice(guild.text_channels))
            else:
                target_list.append(target)

        @tasks.loop(seconds=10)
        async def progress():
            if error_num + success == len(target_list):
                logger.warn("공지 progress가 헛돎")
                return None
            now = datetime.datetime.today()
            embed = discord.Embed(
                title=f"⌛  **뉴스를 뿌리는 중... ({error_num + success}/{len(target_list)})**",
                description=f"`성공 : {success}번 / 실패 : {error_num} / 불러올 수 없음 : {load_error}\n({now.strftime('%Hh %Mm %Ss')})`",
                color=0x00A495,
            )
            await window.edit(embed=embed)

        progress.start()
        for channel in target_list:
            try:
                await channel.send(embed=news_embed)
                success += 1
            except Exception:
                error_num += 1

        progress.stop()
        now = datetime.datetime.today()
        embed = discord.Embed(
            title=f"✅  **전송 완료! ({len(target_list)}/{len(target_list)})**",
            description=f"`성공 : {success}번 / 실패 : {error_num} / 불러올 수 없음 : {load_error}\n({now.strftime('%Hh %Mmin %SSec')})`",
            color=0x00A495,
        )
        await window.edit(embed=embed)

    @slash_command(
        name="업데이트공지",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        description="관리자 공지용 도구입니다. (관리자 전용)",
    )
    @on_working.administrator()
    async def 업데이트공지(self, ctx: discord.ApplicationContext, arg):
        embed = discord.Embed(
            title="**공지사항**", color=0x00A495, timestamp=datetime.datetime.now()
        )
        """
        embed.set_thumbnail(
            url=str(self.bot.user.avatar_url_as(static_format="png", size=256))
        )
        """
        embed.add_field(
            name="**<이프 업데이트 공지>**",
            value=f"이프가 **`{arg}`**동안 업데이트 될 예정입니다.\n업데이트 중에는 이프를 사용하실수 없습니다.\n\n감사합니다.",
            inline=False,
        )
        embed.set_footer(
            text=f"{ctx.author.name} • #공지",
            # icon_url=str(ctx.author.avatar_url_as(static_format="png", size=128)),
        )
        end = []
        for guild in self.bot.guilds:  # 서버 리스트
            for channel in guild.text_channels:  # 서버 리스트 -> 텍스트 채널 리스트
                for i in range(len(guild.text_channels)):
                    if channel.topic is not None:
                        if "#공지" in str(channel.topic).split(" "):
                            try:
                                await self.bot.get_channel(int(channel.id)).send(
                                    embed=embed, content=f"`전송 코드 : {i}`"
                                )
                                end.append(guild.id)
                                break
                            except discord.errors.Forbidden:
                                pass
        for guild in self.bot.guilds:  # 서버 리스트
            for channel in guild.text_channels:
                if guild.id in end:
                    break
                else:
                    try:
                        await self.bot.get_channel(int(channel.id)).send(embed=embed)
                        break
                    except discord.errors.Forbidden:
                        pass
        await ctx.respond("전체 발송 완료!")


class LogManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(
        name="로그",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        description="관리자 디버그용 도구입니다. (관리자 전용)",
    )
    @on_working.administrator()
    async def 로그(self, ctx: discord.ApplicationContext, args: str):
        arg = (
            "".join(args)
            .replace("_", "-")
            .replace(" ", "")
            .replace("월", "")
            .replace("년", "")
            .replace("일", "")
        )
        if os.path.isfile(f"logs/log_{arg}.txt"):
            await ctx.respond(file=discord.File(f"logs/log_{arg}.txt"))
        else:
            await ctx.respond(f"'logs/log_{arg}.txt'는 없는 파일입니다.")

    @slash_command(
        name="에러로그",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        description="관리자 디버그용 도구입니다. (관리자 전용)",
    )
    @on_working.administrator()
    async def 에러로그(self, ctx: discord.ApplicationContext, args: str):
        arg = (
            "".join(args)
            .replace("_", "-")
            .replace(" ", "")
            .replace("월", "")
            .replace("년", "")
            .replace("일", "")
        )
        if os.path.isfile(f"logs/error_log_{arg}.txt"):
            await ctx.send(file=discord.File(f"logs/error_log_{arg}.txt"))
        else:
            await ctx.send(f"'logs/error_log_{arg}.txt'는 없는 파일입니다.")


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(AdminCog(bot))
    bot.add_cog(LogManagerCog(bot))
    # bot.add_cog(DBManagerCog(bot)) # Legacy Code
