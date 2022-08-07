import discord.commands.context
from discord import DMChannel
from discord.ext.commands import check
from classes.user import User, on_fishing
from classes.room import Room, get_working_now
from utils import logger


def on_working(fishing=False, landwork=False, prohibition=False, owner_only=False):
    """
    fishing : 낚시와 동시에 불가능
    landwork : 낚시터 작업 중이면 불가능
    prohibition : #낚시금지 태그가 있으면 불가능
    owner_only : 낚시터 주인만 작업 가능
    """

    async def predicate(ctx: discord.ApplicationContext):
        channel = ctx.channel

        if isinstance(channel, DMChannel):
            await ctx.send(f"으에, 이프는 DM은 안 받고 이써!\n`❗ 이프와는 개인 메시지로 놀 수 없습니다.`")
            return False

        if fishing:  # 낚시 중에는 금지
            if on_fishing(ctx.author.id):
                try:
                    await ctx.respond("낚시 중에는 낚시에 집중하자...!\n`❗ 이미 낚시가 진행 중이다.`")
                except Exception:
                    pass
                return False

        if landwork:  # 땅 작업 중에는 금지
            if await get_working_now(ctx.channel.id):
                try:
                    await ctx.respond(
                        "흐음... 여기 뭔가 하고 있는 거 같은데 조금 이따가 와 보자!\n`❗ 누군가 이미 땅에서 매입/매각/건설/철거 등의 작업을 하는 중이다.`"
                    )
                except Exception:
                    pass
                return False

        if prohibition:  # 낚시금지를 했다면 금지
            if channel.topic is not None and "#낚시금지" in channel.topic:
                try:
                    await ctx.respond("여긴 낚시터가 아니야...\n`❗ 낚시 금지 태그가 설정된 채널입니다.`")
                except Exception:
                    pass
                return False

            if channel.topic is not None and "#no_fishing" in channel.topic:
                try:
                    await ctx.respond(
                        "You can't fish here! >ㅅ<\n`❗ This channel is tagged with no fishing.`"
                    )
                except Exception:
                    pass
                return False

        if owner_only:  # 낚시터 주인만 가능
            room = await Room.fetch(channel)
            if room.owner_id != ctx.author.id:
                try:
                    await ctx.respond("다른 사람 땅은 건들 수 없어...!\n`❗ 자신의 땅에서만 할 수 있는 작업이다.`")
                except Exception:
                    pass
                return False

        return True

    return check(predicate)


def administrator():
    """이프 관리자만 사용 가능하게 설정할 경우"""

    async def predicate(ctx: discord.ApplicationContext):
        if not (await User.fetch(ctx.author)).admin:
            try:
                await ctx.respond("관계자 외 출입금지야!\n`❗ 이프 관리자 전용 명령어입니다.`")
            except Exception:
                pass
            return False
        return True

    return check(predicate)


def p_requirements(manage_messages=False):
    """이프의 권한이 있어야 사용 가능한 명령어"""

    async def predicate(ctx: discord.ApplicationContext):
        if isinstance(ctx.channel, DMChannel):
            return False

        per = ctx.channel.guild.me.permissions_in(ctx.channel)
        if not per.send_messages:  # 애초에 보내지도 못하면 할 수가 없지
            logger.warn(f"{ctx.channel.name}({ctx.channel.id})에서 메시지 보내기 권한이 없음")
            return False

        perdict = {
            "메시지 기록 보기": per.read_message_history,
            "반응 추가하기": per.add_reactions,
            "링크 첨부하기": per.embed_links,
            "파일 첨부하기": per.attach_files,
        }
        if manage_messages:
            perdict["메시지 관리하기"] = per.manage_messages

        if False in perdict.values():
            text = "✔️ 메시지 읽기\n✔️ 메시지 보내기"
            for i in perdict.keys():
                text += f"\n{'✔️' if perdict[i] else '❌'} {i}"
            await ctx.respond(
                f"으우... 마력이 부족해!\n`❗ 아래에 '❌'로 뜨는 권한을 이프에게 주세요!`\n```css\n{text}```"
            )
            return False
        return True

    return check(predicate)
