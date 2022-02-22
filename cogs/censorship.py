"""
    <sample.py>
    여러분들의 기능을 여기에 마음껏 추가해 봐요!
"""

# 필수 임포트
from discord.ext import commands
import discord
import os
from utils import logger

# 부가 임포트
from utils import tag as eptag
from classes.sentence import Sentence
import re


class CensorshipCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 접두사에 관계없이 누군가가 메시지를 올렸을 때 여기가 실행될 거야
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or "DM" in str(type(message.channel)):  # 봇이나 DM 무시
            return None
        if message.content in ["이프야 낚시", "ㅇ낚시", "잎낚시"]:
            return None

        channel = message.channel
        p_keyword = message.content

        # 문장부호 및 띄어쓰기를 제거하여 키워드 추출
        for i in ["**", "||", "__", "`", "?", "!", ".", " ", "　"]:
            p_keyword = p_keyword.replace(i, "")

        if p_keyword == "이프야":
            await channel.send("나 불러써?")
            return None
        elif p_keyword == "":
            return None

        if not await gumyol(message):

            # 권한 확인
            per = channel.guild.me.permissions_in(channel)
            if not per.send_messages:  # 애초에 보내지도 못하면 할 수가 없지
                logger.warn(f"{channel.name}({channel.id})에서 메시지 보내기 권한이 없음")
                return None

            perdict = {
                "메시지 관리하기": per.manage_messages,
                "메시지 기록 보기": per.read_message_history,
                "링크 첨부하기": per.embed_links,
            }
            if False in perdict.values():
                text = "✔️ 메시지 읽기\n✔️ 메시지 보내기"
                for i in perdict.keys():
                    text += f"\n{'✔️' if perdict[i] else '❌'} {i}"
                await channel.send(
                    f"검열하기에는 힘이 부족해...!\n`❗ 아래에 '❌'로 뜨는 권한을 이프에게 주세요!`\n```css\n{text}```"
                )
                return None

            try:
                await message.delete()
            except discord.errors.NotFound:
                logger.warn("이미 지워진 메시지를 삭제 시도")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.bot:
            return None

        if not await gumyol(after):
            # 권한 확인
            channel = before.channel
            per = channel.guild.me.permissions_in(channel)
            if not per.send_messages:  # 애초에 보내지도 못하면 할 수가 없지
                logger.warn(f"{channel.name}({channel.id})에서 메시지 보내기 권한이 없음")
                return None

            perdict = {
                "메시지 관리하기": per.manage_messages,
                "메시지 기록 보기": per.read_message_history,
                "링크 첨부하기": per.embed_links,
            }
            if False in perdict.values():
                text = "✔️ 메시지 읽기\n✔️ 메시지 보내기"
                for i in perdict.keys():
                    text += f"\n{'✔️' if perdict[i] else '❌'} {i}"
                await channel.send(
                    f"검열하기에는 힘이 부족해...!\n`❗ 아래에 '❌'로 뜨는 권한을 이프에게 주세요!`\n```css\n{text}```"
                )
                return None
            await after.delete()

    @commands.command()
    async def 태그(self, ctx):
        tags = eptag.tag_to_korean(eptag.get_tags(ctx.channel))

        embed = discord.Embed(title="이 채널의 태그", colour=0x4BC59F)
        embed.add_field(
            name="총 {}개".format(len(tags)), value="#" + " #".join(tags), inline=True
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def 화이트리스트(self, ctx):
        await ctx.send(f"이 명령어는 이제 쓸 수 업써!\n`❗ 이 명령어는 디스코드의 봇 정책 관련으로 지원이 중지되었습니다.`")


async def gumyol(message):
    """message를 주면 검열함, 검열에 걸리면 False 뱉음"""
    author = message.author
    channel = message.channel
    content = message.content

    # 디스코드 꾸밈 부호 제거
    keyword = (
        content.replace("*", "").replace("|", "").replace("_", "").replace("`", "")
    )
    sentence = Sentence(keyword)

    # tagdict = epTagging.gettag(channel)
    tags = eptag.get_tags(channel)
    log_channel = eptag.get_log_channel(message)

    if tags == {} or message.content == "":
        return True

    # 발언의 자유가 있는 경우 패쓰
    for j in message.guild.members:
        if j.id == author.id:
            for i in j.roles:
                if i.name == "발언의 자유":
                    return True

    nas, what = sentence.prohibition(tags)
    if len(nas) > 0:
        nas = eptag.tag_to_korean(nas)
        embed = discord.Embed(
            title="{} 사용".format(", ".join(nas).replace("금지", "")),
            description=f"**말한 사람** : {author.mention}\t//\t**위치** : <#{channel.id}>```diff\n- \"{keyword}\"\n// 사용 욕설 : {str(what).replace('[', '').replace(']', '')}```",
            color=0x4BC59F,
        )
        try:
            await log_channel.send(embed=embed)
        except discord.errors.Forbidden:
            await message.channel.send(
                "기록 설정을 해 둔 채널에 이프가 메시지를 보낼 수 없어...!\n`❗ '#기록'을 쓴 채널의 권한 설정을 확인하자!`"
            )
        return False

        # save = sj.get_json('static/yoks.json', {"yoks": {}})
        # try:
        #     save["yoks"][str(author.id)]['name'] = author.name
        #     save["yoks"][str(author.id)]["content"].append({str(what).replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('\'', ''): content})
        # except KeyError:
        #     save["yoks"][str(author.id)] = {"name": author.name, "content": [{str(what).replace('[', '').replace(']', '').replace('(', '').replace(')', '').replace('\'', ''): content}]}
        # finally:
        #     sj.set_json('static/yoks.json', save)
        # return False

    # 한글 검사
    if "한글" in tags:
        han_count = len(re.findall("[\u3130-\u318F\uAC00-\uD7A3]+", keyword))
        if han_count <= 0:
            embed = discord.Embed(
                title="한글 채널",
                description=f'**말한 사람** : {author.mention}\t//\t**위치** : <#{channel.id}>```diff\n- "{keyword}"\n+ "{keyword}."\n// Please use Korean```',
                color=0x4BC59F,
            )
            await log_channel.send(embed=embed)
            return False

    # 마침표 검사
    if "마침표" in tags:
        if not sentence.machim():
            embed = discord.Embed(
                title="마침표 문제",
                description=f'**말한 사람** : {author.mention}\t//\t**위치** : <#{channel.id}>```diff\n- "{keyword}"\n+ "{keyword}."\n// 제대로 마침표 찍으라구우!```',
                color=0x4BC59F,
            )
            await log_channel.send(embed=embed)
            return False

    if (
        "예요체" in tags
        or "ㅂ니다체" in tags
        or "냥냥체" in tags
        or "멍멍체" in tags
        or "뀨뀨체" in tags
        or "음슴체" in tags
        or "애오체" in tags
        or "이즈나체" in tags
        or "읍니다체" in tags
        or "다나까체" in tags
    ):
        ter = sentence.termination(tags)
        # 말투 검사 (#지정 맞춤법 중 하나라도 일치해야 함)
        if not ter:
            embed = discord.Embed(
                title="말투나 존댓말 문제",
                description=f'**말한 사람** : {author.mention}\t//\t**위치** : <#{channel.id}>```diff\n- "{keyword}"\n// 그 말투는 쓸 수 업쪄! 채널의 말투 태그를 확인해 바!```',
                color=0x4BC59F,
            )
            await log_channel.send(embed=embed)
            return False

    # 맞춤법 검사 (#맞춤법이 있으면 다른 태그 존재 여부와 관계없이 맞춤법 틀리면 소멸행)
    if "맞춤법" in tags:
        corr, resu = sentence.spelling()
        if not corr:
            embed = discord.Embed(
                title="맞춤법 문제",
                description=f"**말한 사람** : {author.mention}\t//\t**위치** : <#{channel.id}>```diff\n{resu}```",
                color=0x4BC59F,
            )
            await log_channel.send(embed=embed)
            return False

    if "반말" in tags:
        ter = sentence.determination()
        # 말투 검사 (#지정 맞춤법 중 하나라도 일치해야 함)
        if ter:
            embed = discord.Embed(
                title="말투나 존댓말 문제",
                description=f'**말한 사람** : {author.mention}\t//\t**위치** : <#{channel.id}>```diff\n- "{keyword}"\n// 그 말투는 쓸 수 업쪄! 채널의 말투 태그를 확인해 바!```',
                color=0x4BC59F,
            )
            await log_channel.send(embed=embed)
            return False

    # 검열에 안 걸린 경우
    return True


def setup(bot):
    logger.info(f"{os.path.abspath(__file__)} 로드 완료")
    bot.add_cog(CensorshipCog(bot))  # 꼭 이렇게 위의 클래스를 이렇게 add_cog해 줘야 작동해요!
