import os
import traceback
from datetime import datetime

import discord
try::
    from discord.commands import slash_command, ApplicationContext
except ImportError:
    from discord_compat import slash_command, ApplicationContext
from discord.ext import commands

import config
from classes.user import fishing_now
from constants import Constants
from db.seta_pgsql import S_PgSQL
from db.seta_sqlite import S_SQLite
from utils import logger

logger.info("이프가 잠에서 깨어나는 중...")
boot_start = datetime.today()

LOADING_DIR = ["cogs", "cogs/fishing"]

db = S_PgSQL()

intents = discord.Intents.default()

fishdb = S_SQLite("static/fishing.db")


class EpBot(dcommands.AutoShardedBot):
    def __init__(self):
        super().__init__(
            help_command=None,
            intents=intents,
            debug_guilds=config.SLASH_COMMAND_REGISTER_SERVER,
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



# 기본 제공 명령어
class ManagementCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="물고기로드", guild_ids=config.ADMIN_COMMAND_GUILD)
    async def reload_fish(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        logger.info("Refreshing fish data...")

        await db.delete_sql("fish", "")

        data = fishdb.select_sql("fish", "*")

        for i in data:
            logger.info(str(i))

            engname = f"'{i[10]}'" if i[10] else "NULL"

            await db.insert_sql(
                "fish",
                "id, name, cost, length, seasons, rarity, biomes, user_num, historic, room_level, eng_name",
                f"{i[0]}, '{i[1]}', {i[2]}, '{i[3]}', {i[4]}, '{i[5]}', {i[6]}, {i[7]}, {i[8]}, {i[9]}, {engname}",
            )

        logger.info("Fish data refreshed.")
        await ctx.respond("끝!")

    # cogs 폴더 안의 코드를 수정했다면 굳이 껐다 키지 않아도 다시시작 명령어로 적용이 가능해!
    @slash_command(name="다시시작", guild_ids=config.ADMIN_COMMAND_GUILD)
    async def restart(self, ctx: discord.ApplicationContext):
        if ctx.author.id not in config.ADMINS:
            return await ctx.respond("흐음... 권한이 부족한 것 같은데?" "\n`❗ 권한이 부족합니다.`")

        w = await ctx.respond("`❗ Cogs를 다시 불러오고 이써...`")
        logger.info("이프 다시시작 중...")

        for _dir in LOADING_DIR:
            cog_list = [i.split(".")[0] for i in os.listdir(_dir) if ".py" in i]
            cog_list.remove("__init__")
            if "cycle" in cog_list:
                cog_list.remove("cycle")  # 스케줄러가 제거가 안 되어서 제외
            for i in cog_list:
                self.bot.reload_extension(f"{_dir.replace('/', '.')}.{i}")
                logger.info(f"'{i}' 다시 불러옴")

        logger.info("다시시작 완료!")
        await ctx.edit(content="`✔️ 전부 다시 불러와써!`")

    @commands.Cog.listener()
    async def on_application_command(self, ctx: ApplicationContext):
        args = ""
        if ctx.selected_options:
            for option in ctx.selected_options:
                args += f"[Name: {option['name']}, Value: {option['value']}, Type: {Constants.OPTION_TYPES[option['type']]}] "
            args = args[:-1]
        guild = f"{ctx.guild}({ctx.guild.id})" if ctx.guild else "DM"
        logger.info(f"{ctx.user}({ctx.user.id}) in {guild}: /{ctx.command.name} {args}")

    @commands.Cog.listener()
    async def on_application_command_error(
        self, ctx: discord.ApplicationContext, error: Exception
    ):
        """명령어 내부에서 오류 발생 시 작동하는 코드 부분"""
        user = ctx.author
        if user.id in fishing_now:
            fishing_now.remove(user.id)

        if isinstance(error, discord.CheckFailure):
            return

        if isinstance(error, discord.ApplicationCommandInvokeError):
            try:
                if isinstance(error.original, discord.errors.NotFound):
                    return await ctx.respond(
                        "저기 혹시... 갑자기 메시지를 지우거나 한 건 아니지...? 그러지 말아 줘..."
                    )
                raise error.original
            except Exception as e:
                logger.err(e)
                await ctx.respond(f"으앙 오류가 발생했어...\n`❗ {str(e)}`")
                await error_send(ctx, self.bot, e)
                return

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
            logger.err(error)
            await ctx.respond(f"으앙 오류가 발생했어...\n`❗ {str(error)}`")
            await error_send(ctx, self.bot, error)

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):  # 메시지 처리
        if (
            msg.content.startswith("이프야")
            or msg.content == "ㅇ낚시"
            or msg.content == "ㅇㄴㅅ"
        ):
            await msg.reply("머랭!\n`❗ 이제 이프는 슬래시 커맨드를 지원합니다! 채팅창에 한 번 '/'를 쳐 보세요!`")


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

epbot.run(token=config.token())
