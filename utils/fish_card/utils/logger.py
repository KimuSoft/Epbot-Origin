'''
    <logger.py>
    기록을 쉽게 남길 수 있게 해 주는 모듈이에요!
    print()보다는 logger.info()를 추천드려요!
    logger.py를 통해서 기록을 남기면 logs 폴더 안에 날짜 별로 기록이 자동으로 정리되니까 편할 거예요!
    ※ 파이썬 초심자라면 이 파일을 수정하지 않는 것을 추천드려요!
    - 키뮤 제작(0127 버전)
'''

from datetime import datetime
from discord import DMChannel
import os
import traceback


def err(error):
    '''
    오류 기록을 남길 때 사용해요!
    '''
    try:
        raise error
    except Exception:
        error_message = traceback.format_exc()
        log('[오류] {}\n\n'.format(error_message), True)
        return error_message


def warn(msg: str):
    '''
    경고 기록을 남길 때 사용해요!
    '''
    log('[경고] {}'.format(msg))


def info(msg: str):
    '''
    일반적인 기록을 남길 때 사용해요!
    '''
    log('[정보] {}'.format(msg))


def debug(msg: str):
    '''
    디버그 모드를 켰을 때만 기록해 줘요!
    '''
    pass


def msg(message):
    '''
    디스코드 메시지를 깔끔하게 정리해 기록해 줘요!
    '''
    if message.content == '':
        return None

    author = message.author

    '''message를 넣으면 로그를 씀'''
    if isinstance(message.channel, DMChannel):
        log_msg = 'DM <{}> {}'.format(author.name, message.content)
    else:
        guild = message.guild
        channel = message.channel
        log_msg = '{server} <{channel} | {user} | {id}> {text}'.format(
            server=guild.name,
            channel=channel.name,
            user=author.name,
            text=message.content,
            id=author.id)

    log(log_msg)


def log(msg: str, iserror=False):
    now = datetime.now()
    hour = now.strftime("%H")
    minute = now.strftime("%M")
    log_msg = '{}시 {}분 / {}'.format(hour, minute, msg)
    print(log_msg)
    save(log_msg)
    if iserror:
        save_error(log_msg)


def save(msg):
    if not(os.path.isdir('logs')):
        os.makedirs(os.path.join('logs'))
    now = datetime.now()
    time_text = now.strftime('%Y-%m-%d')
    if not os.path.isfile("logs/log_" + time_text + ".txt"):
        f = open("logs/log_" + time_text + ".txt", 'w', encoding='utf-8')
    else:
        f = open("logs/log_" + time_text + ".txt", 'a', encoding='utf-8')
    f.write(msg + '\n')
    f.close()


def save_error(msg):
    now = datetime.now()
    time_text = now.strftime('%Y-%m-%d')
    if not os.path.isfile("logs/error_log_" + time_text + ".txt"):
        f = open("logs/error_log_" + time_text + ".txt", 'w', encoding='utf-8')
    else:
        f = open("logs/error_log_" + time_text + ".txt", 'a', encoding='utf-8')
    f.write(msg + '\n')
    f.close()
