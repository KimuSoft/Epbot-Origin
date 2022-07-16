""" <config.py> """
from dotenv import load_dotenv
import os

load_dotenv()

""" Debug Option """
debug = True
query_logging = False
profiling = False

"""Administrator Setting"""
ADMINS = [
    281689852167061506,  # 키뮤
]

""" PostgreSQL Database Configuration """
PG_DSN = "postgresql://postgres:postgres@127.0.0.1:5432/test"

""" FishCard Server Setting"""
CARD_SERVER = "http://localhost:3000"  # 슬래시로 끝내지 말아주세요
CARD_TOKEN = os.getenv("IMAGE_GENERATOR_TOKEN", "")  # python scripts/genscript.py

""" Discord Bot Configuration """
TOKEN = ""
DEBUG_TOKEN = ""

# 명령어 접두사 (띄어쓰기 주의)
PREFIXES = ["이프야 ", "ㅇ", "잎", "ep "]
# 하고 있는 게임 (프로필에 '... 하는 중'으로 보이는 것)
ACTIVITIES = [
    "{}곳의 서버에서 검열 삭제",
    "{}곳의 서버에서 낚시",
    "'/도움말'을 입력해 보라고 이야기",
]
DEBUG_ACTIVITIES = ["버그 수정 중. . ."]

""" Logging & Announcement Channel Setting """
ERROR_LOGGING_CHANNEL = 1234567890
ANNOUNCE_CHANNEL = 1234567890

""" Slash Command Option """
# 커맨드를 등록할 서버 ID 리스트. 전역 등록 시에는 None으로 지정.
SLASH_COMMAND_REGISTER_SERVER = None

# 관리자 명령어를 사용할 서버 ID
ADMIN_COMMAND_GUILD = []


def token():
    return TOKEN if not debug else DEBUG_TOKEN


def activities():
    return ACTIVITIES if not debug else DEBUG_ACTIVITIES


@property
def prefixes_no_space():
    """접두사들을 띄어쓰기 없이 반환합니다."""
    return [i.replace(" ", "") for i in PREFIXES]
