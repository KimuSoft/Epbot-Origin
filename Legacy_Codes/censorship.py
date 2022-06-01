# 디스코드 메세지 인텐트로 인한 검열 기능 사용 제한.
# From cogs/fishing/censorship.py
'''
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
'''