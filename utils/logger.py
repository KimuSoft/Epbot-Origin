"""
    <logger.py>
    로깅 유틸
"""

from datetime import datetime
import os
import traceback

import config


def err(error):
    """
    오류 기록을 남길 때 사용해요!
    """
    try:
        raise error
    except Exception:
        error_message = traceback.format_exc()
        log(f"[오류] {error_message}\n\n", True)
        return error_message


def warn(message: str):
    """
    경고 기록을 남길 때 사용해요!
    """
    log(f"[경고] {message}")


def info(message: str):
    """
    일반적인 기록을 남길 때 사용해요!
    """
    log(f"[정보] {message}")


def debug(message: str):
    """
    디버그 모드를 켰을 때만 기록해 줘요!
    """
    if config.debug:
        log(f"[디버그] {message}")


def msg(message):
    """
    디스코드 메시지를 깔끔하게 정리해 기록해 줘요!
    """
    if message.content == "":
        return

    author = message.author

    """message를 넣으면 로그를 씀"""
    if "DM" in str(type(message.channel)):
        log_msg = f"DM <{author.name}> {message.content}"
    else:
        guild = message.guild
        channel = message.channel
        log_msg = f"<{channel.name} | {author.name}> {message.content} ({guild.name}, {author.id})"

    log(log_msg)


def query(message: str):
    """쿼리 로그 옵션이 켜져 있을 때만 기록해 줘요!"""
    if config.query_logging:
        log("[쿼리] {}".format(message))


def log(message: str, iserror=False):
    now = datetime.now()
    hour = now.strftime("%H")
    minute = now.strftime("%M")
    log_msg = f"{hour}시 {minute}분 / {message}"
    print(log_msg)
    save(log_msg)
    if iserror:
        save_error(log_msg)


def save(message):
    if not (os.path.isdir("logs")):
        os.makedirs(os.path.join("logs"))
    now = datetime.now()
    time_text = now.strftime("%Y-%m-%d")
    if not os.path.isfile("logs/log_" + time_text + ".txt"):
        f = open("logs/log_" + time_text + ".txt", "w", encoding="utf-8")
    else:
        f = open("logs/log_" + time_text + ".txt", "a", encoding="utf-8")
    f.write(message + "\n")
    f.close()


def save_error(message):
    now = datetime.now()
    time_text = now.strftime("%Y-%m-%d")
    if not os.path.isfile("logs/error_log_" + time_text + ".txt"):
        f = open("logs/error_log_" + time_text + ".txt", "w", encoding="utf-8")
    else:
        f = open("logs/error_log_" + time_text + ".txt", "a", encoding="utf-8")
    f.write(message + "\n")
    f.close()
