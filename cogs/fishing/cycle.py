"""
    <cycle.py>
    스케쥴이 모인 모듈
"""

import os
from itertools import cycle

import discord

# 부가 임포트
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import slash_command

# 필수 임포트
from discord.ext import commands, tasks

import config
from classes.room import working_now
from classes.user import fishing_now
from db.seta_pgsql import S_PgSQL
from utils import logger
from utils import on_working

db = S_PgSQL()

activity = cycle(config.activities())


class CycleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # 디스코드 태스크
        logger.info("discord.ext.tasks 스케쥴 시작")
        self.change_activity.start()  # pylint: disable=maybe-no-member
        self.cleaner.start()  # pylint: disable=maybe-no-member

    @commands.Cog.listener()
    async def on_ready(self):
        logger.info("AsyncIOScheduler 스케쥴 시작")
        self.sched = AsyncIOScheduler()

        job_id = "day_end_schedule"

        if not self.sched.get_job(job_id):
            self.sched.add_job(self.day_end_schedule, "cron", hour="23", minute="55", id=job_id)
            # self.sched.add_job(self.day_end_schedule, 'cron', minute='*/5')
        
        if not self.sched.running:
            self.sched.start()

    @tasks.loop(seconds=30)
    async def change_activity(self):
        gaming = next(activity).format(len(self.bot.guilds))
        # logger.info(f'플레이 중 게임 변경 : {gaming}')
        await self.bot.change_presence(activity=discord.Game(gaming))

    @tasks.loop(minutes=600)
    async def cleaner(self):
        fishing_now.clear()
        working_now.clear()
        logger.info("낚시 상태 정기 초기화 완료")
        if len(self.bot.guilds) != 0:
            logger.info(f"통계 : 현재 서버 수 {len(self.bot.guilds)}곳")

    async def day_end_schedule(self):
        logger.info("자정 스케쥴 실행")
        await db.update_sql("rooms", "season = season + 1")  # 계절 변화
        await db.update_sql("rooms", "season = 1", "season > 4")  # 계절 변화

    @on_working.administrator()
    @slash_command(
        name="강제결산",
        guild_ids=config.ADMIN_COMMAND_GUILD,
        description="관리자 디버그용 도구입니다. (관리자 전용)",
    )
    async def force_schedule(self, ctx: discord.ApplicationContext):
        await ctx.defer()
        await self.day_end_schedule()
        await ctx.respond("강제결산 완료!")


""" 사용하지 않음

    @commands.command()
    @administrator()
    async def 강제통계(self, ctx):
        self.record_statistics()
        await ctx.send("강제통계 완료!")

    def user_num(self):
        users = 0
        for i in self.bot.guilds:
            users += len(i.members)
        return users

    def guilds_num(self):
        return len(self.bot.guilds)

    def record_statistics(self):
        stat = S_SQLite("statistics.db")
        players = len(db.select_sql("users", "id"))
        time = datetime.today()
        try:
            stat.insert_sql(
                "statistics",
                "day, servers, users, players",
                f"'{time.strftime('%Y-%m-%d')}', {self.guilds_num()}, {self.user_num()}, {players}",
            )
        except Exception:
            stat.update_sql(
                "statistics",
                f"servers={self.guilds_num()}, users={self.user_num()}, players={players}",
                f"day='{time.strftime('%Y-%m-%d')}'",
            )

    async def day_end_schedule(self):
        logger.info("자정 스케쥴 실행")
        db.update_sql("rooms", "season = season + 1")  # 계절 변화
        db.update_sql("rooms", "season = 1", "season = 5")  # 계절 변화

        today = datetime.today()

        rows = db.select_sql(
            "users",
            "name, biggest_name, biggest_size, id",
            "WHERE biggest_size > 0 ORDER BY biggest_size DESC LIMIT 5",
        )

        ranking = ""
        mentions = ""
        for idx, val in enumerate(rows):
            mentions += f"<@!{val[3]}> "
            user =await User.fetch(val[3])
            if idx == 0:
                ranking += "\n[🥇 1등 🥇] {name} ({fish}/{size}cm)".format(
                    name=str(val[0]), fish=val[1], size=val[2]
                )
                user.give_money(100000)
                user.add_exp(5000)
                logger.info(f"1등 상금 지급 - {val[0]}({val[3]})")
            elif idx == 1:
                ranking += "\n[🥈 2등 🥈] {name} ({fish}/{size}cm)".format(
                    name=str(val[0]), fish=val[1], size=val[2]
                )
                user.give_money(50000)
                user.add_exp(3000)
                logger.info(f"2등 상금 지급 - {val[0]}({val[3]})")
            elif idx == 2:
                ranking += "\n[🥉 3등 🥉] {name} ({fish}/{size}cm)".format(
                    name=str(val[0]), fish=val[1], size=val[2]
                )
                user.give_money(30000)
                user.add_exp(2000)
                logger.info(f"3등 상금 지급 - {val[0]}({val[3]})")
            elif idx == 3:
                ranking += "\n[ 4등 ] {name} ({fish}/{size}cm)".format(
                    name=str(val[0]), fish=val[1], size=val[2]
                )
                user.give_money(20000)
                user.add_exp(1000)
                logger.info(f"4등 상금 지급 - {val[0]}({val[3]})")
            elif idx == 4:
                ranking += "\n[ 5등 ] {name} ({fish}/{size}cm)".format(
                    name=str(val[0]), fish=val[1], size=val[2]
                )
                user.give_money(10000)
                user.add_exp(500)
                logger.info(f"5등 상금 지급 - {val[0]}({val[3]})")

        embed = discord.Embed(
            title=f'👑 {today.strftime("%Y-%m-%d")}의 이프 낚시 어워드!',
            description=f"```cs\n{ranking}```",
            colour=0x4BC59F,
        )
        embed.set_footer(
            text="1등 100,000💰 / 2등 50,000💰 / 3등 30,000💰 / 4등 20,000💰 / 5등 10,000💰"
        )
        try:
            channel = self.bot.get_channel(config.ANNOUNCE_CHANNEL)
            await channel.send(content=mentions, embed=embed)
        except Exception as e:
            logger.err(e)

        db.update_sql("users", "biggest_size=0, biggest_name=''")  # 최고 기록 초기화
"""


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(
        CycleCog(bot)
    )  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
