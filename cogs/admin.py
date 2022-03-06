"""
    <admin.py>
    봇 관리자 전용 명령어를 모아 두었습니다.
    TODO: 너무 많아서 분류 별로 클래스를 나누자
    eval 명령어도 추가
"""

# 필수 임포트
from discord.commands import slash_command
from discord.commands import Option
from discord.ext import commands, tasks
import discord
import os
from utils import logger
import config

# 부가 임포트
from db import seta_json as sj
from utils import on_working
from utils.util_box import wait_for_saying, ox
from classes.sentence import reload_bw
from classes.user import User
from classes.room import Room
import datetime
import random


class AdminCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @on_working.administrator()
    @slash_command(name = "계란", guild_ids = config.ADMIN_COMMAND_GUILD, decription = "관리자 디버그용 도구입니다. (관리자 전용)")
    async def 계란(self, ctx, args: str):
        here = Room(ctx.channel)
        me = User(ctx.author)

        logger.info(f"{me.name}이(가) {here.name}에서 계란 명령어 사용")

        text = args
        try:
            exec(text)
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
            #작동하지 않음
            #icon_url=str(ctx.author.avatar_url_as(static_format="png", size=128)),
        )
        await ctx.respond(embed=embed)

    @on_working.administrator()
    @slash_command(name = "달걀", guild_ids = config.ADMIN_COMMAND_GUILD, description = "관리자 디버그용 도구입니다. (관리자 전용)")
    async def 달걀(self, ctx, args: str):
        here = Room(ctx.channel)
        me = User(ctx.author)

        logger.info(f"{me.name}이(가) {here.name}에서 달걀 명령어 사용")

        text = args
        try:
            result = eval(text)
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
            #작동하지 않음
            #icon_url=str(ctx.author.avatar_url_as(static_format="png", size=128)),
        )
        await ctx.respond(embed=embed)

    # 팡 하면 펑 하고 터짐
    @on_working.administrator()
    @slash_command(name = "팡", guild_ids = config.ADMIN_COMMAND_GUILD, description = "관리자 디버그용 도구입니다. (관리자 전용)")
    async def 팡(self, ctx):
        await ctx.respond(f"펑! 💥\n`지연 시간 : {int(self.bot.latency * 1000)}ms`")
        raise Exception

    # 팡 하면 펑 하고 터짐
    @on_working.administrator()
    @slash_command(name = "핑핑", guild_ids = config.ADMIN_COMMAND_GUILD, description = "관리자 디버그용 도구입니다. (관리자 전용)")
    async def 핑핑(self, ctx):
        ping = [f"#shard_{i[0]} ({int(i[1] * 1000)}ms)" for i in self.bot.latencies]
        text = "\n".join(ping)
        await ctx.respond(f"퐁퐁! 🏓🏓\n```css\n[ 지연 시간 ]\n{text}```")

    @slash_command(name = "공지", guild_ids = config.ADMIN_COMMAND_GUILD, description = "관리자 공지용 도구입니다. (관리자 전용)")
    @on_working.administrator()
    async def 공지(self, ctx):
        old = await ctx.send(
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
            #작동하지 않음
            #icon_url=str(ctx.author.avatar_url_as(static_format="png", size=128)),
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
        window = await ctx.send(content="", embed=embed)

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

    @slash_command(name = "업데이트공지", guild_ids = config.ADMIN_COMMAND_GUILD, description = "관리자 공지용 도구입니다. (관리자 전용)")
    @on_working.administrator()
    async def 업데이트공지(self, ctx, arg):
        embed = discord.Embed(
            title="**공지사항**", color=0x00A495, timestamp=datetime.datetime.now()
        )
        '''
        embed.set_thumbnail(
            url=str(self.bot.user.avatar_url_as(static_format="png", size=256))
        )
        '''
        embed.add_field(
            name="**<이프 업데이트 공지>**",
            value=f"이프가 **`{arg}`**동안 업데이트 될 예정입니다.\n업데이트 중에는 이프를 사용하실수 없습니다.\n\n감사합니다.",
            inline=False,
        )
        embed.set_footer(
            text=f"{ctx.author.name} • #공지",
            #icon_url=str(ctx.author.avatar_url_as(static_format="png", size=128)),
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

    @slash_command(name = "로그", guild_ids = config.ADMIN_COMMAND_GUILD, description = "관리자 디버그용 도구입니다. (관리자 전용)")
    @on_working.administrator()
    async def 로그(self, ctx, args: str):
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

    @slash_command(name = "에러로그", guild_ids = config.ADMIN_COMMAND_GUILD, description = "관리자 디버그용 도구입니다. (관리자 전용)")
    @on_working.administrator()
    async def 에러로그(self, ctx, args: str):
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


class DBManagerCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 욕설추가(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 욕설추가 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")

        newwork = " ".join(args)
        badwords["yok"].append(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 욕설 목록에 추가하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 욕설삭제(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 욕설삭제 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")
        newwork = " ".join(args)
        badwords["yok"].remove(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 욕설 목록에서 삭제하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 야한말추가(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 욕설삭제 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")
        newwork = " ".join(args)
        badwords["emr"].append(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 야한말 목록에 추가하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 야한말삭제(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 야한말삭제 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")

        newwork = " ".join(args)
        badwords["emr"].remove(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 야한말 목록에서 삭제하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 정치언급추가(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 정치언급추가 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")

        newwork = " ".join(args)
        badwords["jci"].append(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 정치언급 목록에 추가하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 정치언급삭제(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 정치언급삭제 <정규 표현식>`")
            return None

        badwords = sj.get_json("bad_words.json")

        newwork = " ".join(args)
        badwords["jci"].remove(newwork)
        sj.set_json("bad_words.json", badwords)
        reload_bw()
        await ctx.send(f"`{newwork}`을 정치언급 목록에서 삭제하였습니다!")

    @commands.command()  # 커맨드 함수라면 앞에 달아 줘야 해요! 데코레이터라고 불러요!
    @on_working.administrator()
    async def 목록(self, ctx, *args):
        if args == ():
            await ctx.send("`이프야 목록 <야한말/정치언급/욕설/변태/나쁜말/관리자>`")
            return None

        badwords = sj.get_json("bad_words.json")
        args = " ".join(args)
        embed = discord.Embed(title="목록", colour=0x4BC59F)
        if (
            args == "야한말"
            or args == "정치언급"
            or args == "욕설"
            or args == "변태"
            or args == "나쁜말"
        ):
            if args == "야한말":
                ya = "emr"
            elif args == "정치언급":
                ya = "jci"
            elif args == "욕설":
                ya = "yok"
            elif args == "변태":
                ya = "bta"
            elif args == "나쁜말":
                ya = "gcm"
            else:
                ya = "err"
            words = badwords[ya]
            num = 0
            while len(words) > 20:
                if len(words) > 20:
                    num = num + 1
                    li = ""
                    for i in words[:20]:
                        li += i + "\n"
                    embed.add_field(
                        name="{arg} {num}번 목록".format(arg=args, num=num),
                        value=li,
                        inline=True,
                    )
                    del words[:20]
                else:
                    break
            li = ""
            for i in words[:20]:
                li += i + "\n"
            embed.add_field(
                name="{arg} {num}번 목록".format(arg=args, num=num + 1),
                value=li,
                inline=True,
            )
            await ctx.send(embed=embed)
        elif args == "관리자":
            embed.add_field(
                name="{arg} 목록".format(arg=args),
                value=sj.get_json("permission.json")["user"],
                inline=True,
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send("`이프야 목록 <야한말/정치언급/욕설/변태/나쁜말/관리자>`")
            return None


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(AdminCog(bot))
    bot.add_cog(DBManagerCog(bot))
    bot.add_cog(LogManagerCog(bot))
