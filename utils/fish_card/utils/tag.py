"""이프의 태그 관련 기능이 모인 모듈"""

from utils import logger
from db import seta_json as sj

# 문자열 -> 태그, 혹은 복합태그
tagdict = {
    "욕설금지": "yok",
    "야한말금지": "emr",
    "정치언급금지": "jci",
    "정치발언금지": "jci",
    "거친말금지": ["yok", "gcm"],
    "변태금지": ["emr", "bta"],
    "건전": ["yok", "emr", "jci"],
    "존댓말": ["예요체", "ㅂ니다체"],
    "고운말": ["yok", "emr", "jci", "gcm", "bta"],
    "반말": "반말",
}

# 태그코드 -> 문자열
tagtostr = {
    "yok": "욕설 금지",
    "emr": "야한 말 금지",
    "bta": "변태 금지",
    "gcm": "거친 말 금지",
    "jci": "정치 발언 금지",
}

# 금칙어 관련 태그
prohibit_tags = sj.get_json("db/bad_words.json").keys()


def get_log_channel(message):
    log_channel = None
    for i in message.guild.text_channels:
        if "#기록" in str(i.topic):
            log_channel = i
    if log_channel is None:
        log_channel = message.channel
    return log_channel


def tag_to_korean(tags: list):
    newtags = []
    for a in tags:
        if a in tagtostr.keys():
            newtags.append(tagtostr[a])
        else:
            newtags.append(a)
    return newtags


def get_tags(channel):
    # 태그의 형태로 존재하는 것을 리스트에 담음
    topic = channel.topic
    if topic is None or "#" not in topic:
        return []
    topic = topic.replace("_", "").replace(",", "")

    p = str(topic).split(" ")
    tags = []
    for i in p:
        if i.startswith("#"):
            tags.append(i.replace("#", ""))

    for i in tagdict.keys():
        if i in tags:
            tags.remove(i)
            if type(tagdict[i]) == str:
                tags.append(tagdict[i])
            else:
                for j in tagdict[i]:
                    tags.append(j)

    # logger.debug(list(set(tags)))
    return list(set(tags))  # p.findall(topic)
