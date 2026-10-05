""" <config.py> """
import os

""" Debug Option """
debug = False
query_logging = False

"""Administrator Setting"""
ADMINS = [
    281689852167061506,  # 키뮤
    577095893451407361,  # 코로
    287177141064302592,  # 로
    628595345798201355,  # 파링
    753625063357546556   # 코이
]

""" PostgreSQL Database Configuration """
PG_DSN = os.getenv("EP_PG_DSN")

""" Discord Bot Configuration """
TOKEN = os.getenv("EP_TOKEN")
DEBUG_TOKEN = ""

# 하고 있는 게임 (프로필에 '... 하는 중'으로 보이는 것)
ACTIVITIES = [
    "{}곳의 서버에서 검열 삭제",
    "{}곳의 서버에서 낚시",
    "'/'을 입력해 보라고 이야기",
]
DEBUG_ACTIVITIES = ["버그 수정 중. . ."]

""" Loggin & Announcement Channel Setting """
ERROR_LOGGING_CHANNEL = int(os.getenv("EP_ERROR_LOGGING_CHANNEL"))
ANNOUNCE_CHANNEL = int(os.getenv("EP_ANNOUNCE_CHANNEL"))

""" Slash Command Option """
# 커맨드를 등록할 서버 ID 리스트. 전역 등록 시에는 None으로 지정.
SLASH_COMMAND_REGISTER_SERVER = None

# 관리자 명령어를 사용할 서버 ID
ADMIN_COMMAND_GUILD = [
    int(x) for x in os.getenv("EP_ADMIN_COMMAND_GUILD", "").split(",")
]


def token():
    return TOKEN


def activities():
    return ACTIVITIES
