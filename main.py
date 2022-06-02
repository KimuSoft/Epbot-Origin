from discord.ext import commands
from discord.commands import slash_command
import discord

import config
from utils import logger
import traceback
import os
from datetime import datetime

from classes.user import User

logger.info("이프가 잠에서 깨어나는 중...")
boot_start = datetime.today()

LOADING_DIR = ["cogs", "cogs/fishing"]


class EpBot(commands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            help_command=None,
        )

        # Cogs 로드(Cogs 폴더 안에 있는 것이라면 자동으로 인식합니다)
        self.add_cog(ManagementCog(self))  # 기본 제공 명령어 Cog
        for _dir in LOADING_DIR:
            cog_list = [i.split(".")[0] for i in os.listdir(_dir) if ".py" in i]
            cog_list.remove("__init__")
            for i in cog_list:
                logger.info(f"{_dir.replace('/', '.')}.{i} 로드")
                self.load_extension(f"{_dir.replace('/', '.')}.{i}")

    async def on_ready(self):
        """봇이 구동되면 시작되는 부분"""
        boot_end = datetime.today()
        boot_time = boot_end - boot_start
        logger.info("///////////////////// ! 이프 기상 ! /////////////////////")
        logger.info(f"봇 계정 정보 : {self.user.name} ({self.user.id})")
        logger.info(f"서버 수 : {len(self.guilds)}곳")
        logger.info(f"디스코드 버전 : {discord.__version__}")
        logger.info(f"계정 길드 인텐트 활성화 : {self.intents.guilds}")
        logger.info(f"계정 멤버 인텐트 활성화 : {self.intents.members}")
        logger.info(f"디버그 모드 활성화 : {config.debug}")
        logger.info(f"일어날 때까지 {boot_time.total_seconds()}초 만큼 걸렸어!")
        logger.info(f"슬래시 커맨드 등록 서버 지정 : {bool(config.SLASH_COMMAND_REGISTER_SERVER)}")
        if config.SLASH_COMMAND_REGISTER_SERVER:
            logger.info(f"sid {config.SLASH_COMMAND_REGISTER_SERVER}")
        logger.info("////////////////////////////////////////////////////////")

        await self.change_presence(status=discord.Status.online)

    def run(self):
        super().run(config.token(), reconnect=True)


# 기본 제공 명령어
class ManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # cogs 폴더 안의 코드를 수정했다면 굳이 껐다 키지 않아도 다시시작 명령어로 적용이 가능해!
    @slash_command(name="다시시작", guild_ids=config.ADMIN_COMMAND_GUILD)
    async def 다시시작(self, ctx):
        if ctx.author.id not in config.ADMINS:
            return await ctx.respond("흐음... 권한이 부족한 것 같은데?" "\n`❗ 권한이 부족합니다.`")

        w = await ctx.respond("`❗ Cogs를 다시 불러오고 이써...`")
        logger.info("이프 다시시작 중...")
        for _dir in LOADING_DIR:
            cog_list = [i.split(".")[0] for i in os.listdir(_dir) if ".py" in i]
            cog_list.remove("__init__")
            if "cycle" in cog_list:
                cog_list.remove("cycle")  # 스케듈러가 제거가 안 되어서 제외
            for i in cog_list:
                self.bot.reload_extension(f"{_dir.replace('/', '.')}.{i}")
                logger.info(f"'{i}' 다시 불러옴")

        logger.info("다시시작 완료!")
        await w.edit_original_message(content="`✔️ 전부 다시 불러와써!`")

    @slash_command(name="info", description="Show Information about EpBot!")
    async def info(self, ctx):
        embed = discord.Embed(
            title="Information about EpBot(이프)",
            description="This bot is a project designed based on Kimusoft's Thetabot V2 framework.",
            colour=0x1DDB16,
        )
        embed.add_field(
            name="'키뮤의 과학실' Official Support Sever Link",
            value="🔗 https://discord.gg/XQuexpQ",
            inline=True,
        )
        embed.set_footer(
            text="Since this bot is originally a Korean bot, English support is still insufficient. 😭"
        )
        await ctx.respond(embed=embed)

    @commands.Cog.listener()
    async def on_command(self, ctx):
        logger.msg(ctx.message)

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.commands.context.ApplicationContext, error: Exception):
        """명령어 내부에서 오류 발생 시 작동하는 코드 부분"""
        channel = ctx.channel
        User(ctx.author).fishing_now = False
        if not isinstance(error, commands.CommandError):
            try:
                if isinstance(error.original, discord.errors.NotFound):
                    return await ctx.respond(
                        "저기 혹시... 갑자기 메시지를 지우거나 한 건 아니지...? 그러지 말아 줘..."
                    )
            except Exception as e:
                logger.err(e)
                pass

        # 명령어 쿨타임이 다 차지 않은 경우
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(
                f"이 명령어는 {error.cooldown.rate}번 쓰면 {error.cooldown.per}초의 쿨타임이 생겨!"
                f"\n`❗ {int(error.retry_after)}초 후에 다시 시도해 주십시오.`"
            )

        elif isinstance(error, commands.errors.CheckFailure):
            pass

        # ServerDisconnectedError의 경우 섭렉으로 판정
        elif "ServerDisconnectedError" in str(error):
            await ctx.respond(f"미, 미아내! 디스코드 랙이 있던 것 같아...\n`❗ {error}`")
            await error_send(ctx, self.bot, error, 0xFFBB00)

        else:
            logger.err(e)
            await ctx.send(f"으앙 오류가 발생했어...\n`❗ {str(error)}`")
            await error_send(ctx, self.bot, error)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):  # 슬래시 커맨드 제외 오류 처리
        """명령어 내부에서 오류 발생 시 작동하는 코드 부분"""
        channel = ctx.channel
        User(ctx.author).fishing_now = False

        if "DM" in str(type(channel)):
            if isinstance(error, commands.errors.CheckFailure):
                return
            return await ctx.send(
                """으에, 이프는 DM은 안 받고 이써!
                `❗ 이프와는 개인 메시지로 놀 수 없습니다.`"""
            )

        # 해당하는 명령어가 없는 경우
        if isinstance(error, commands.errors.CommandNotFound):
            if ctx.message.content.startswith("이프야"):
                await ctx.send("머랭!")
            elif "ep" in ctx.message.content:
                await ctx.send("Meringue! >ㅅ<")

        elif isinstance(error, discord.errors.NotFound):
            return await ctx.send(
                """저기 혹시... 갑자기 메시지를 지우거나 한 건 아니지...? 그러지 말아 줘...
                `❗ raise discord.errors.NotFound`"""
            )

        # 명령어 쿨타임이 다 차지 않은 경우
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"이 명령어는 {error.cooldown.rate}번 쓰면 {error.cooldown.per}초의 쿨타임이 생겨!"
                f"\n`❗ {int(error.retry_after)}초 후에 다시 시도해 주십시오.`"
            )

        elif isinstance(error, commands.errors.CheckFailure):
            pass

        # ServerDisconnectedError의 경우 섭렉으로 판정
        elif "ServerDisconnectedError" in str(error):
            await ctx.send(f"미, 미아내! 디스코드 랙이 있던 것 같아...\n`❗ {error}`")
            await error_send(ctx, self.bot, error, 0xFFBB00)

        else:
            await ctx.send(f"으앙 오류가 발생했어...\n`❗ {str(error)}`")
            await error_send(ctx, self.bot, error)


async def error_send(ctx, bot, error, color=0x980000):
    try:
        raise error
    except Exception:
        error_message = traceback.format_exc().split(
            "The above exception was the direct cause of the following exception:"
        )[0]
        error_message.strip()
        time = datetime.today()

        embed = discord.Embed(
            title=f"❗ 오류 발생  / {error}",
            description=f"```{error_message}```",
            colour=color,
        )
        embed.set_author(name=ctx.author)
        embed.set_footer(
            text=f"(서버) {ctx.guild.name} / (채널) {ctx.channel.name} / (시간) {time.strftime('%Y-%m-%d %Hh %Mmin')}"
        )
    try:
        await bot.get_channel(config.ERROR_LOGGING_CHANNEL).send(embed=embed)
    except Exception as e:
        logger.warn(f"오류 보드에 전송 실패\n{e}")
    logger.err(error)


epbot = EpBot()
epbot.run()
