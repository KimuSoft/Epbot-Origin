""" <config.py> """
import os

""" Debug Option """
debug = False
query_logging = False


"""Administrator Setting"""
ADMINS = [
    281689852167061506,  # 키뮤
]


""" PostgreSQL Database Configuration """
HOST = os.getenv('EP_DB_HOST')  # HOST를 localhost로 세팅할 경우 HOST를 사용하지 않음(DB 서버와 이프 서버를 같이 돌릴 경우 권장)
DBNAME = os.getenv('EP_DB_NAME')
USER = os.getenv('EP_DB_USER')
PASSWORD = os.getenv('EP_DB_PASSWORD')
PORT = int(os.getenv('EP_DB_PORT', '5432'))


""" FishCard Server Setting"""
CARD_SERVER = os.getenv('EP_CARD_SERVER', '').replace('$HOST', HOST)  # 슬래시로 끝내지 말아주세요
CARD_TOKEN = os.getenv('EP_CARD_TOKEN', '')


""" Discord Bot Configuration """
TOKEN = os.getenv('EP_TOKEN')
DEBUG_TOKEN = ""

# 명령어 접두사 (띄어쓰기 주의)
PREFIXES = ["이프야 ", "ㅇ", "잎", "ep "]
# 하고 있는 게임 (프로필에 '... 하는 중'으로 보이는 것)
ACTIVITIES = [
    "{}곳의 서버에서 검열 삭제",
    "{}곳의 서버에서 낚시",
    "'이프야 도움말'을 입력해 보라고 이야기",
    "EpBot | ep help",
]
DEBUG_ACTIVITIES = ["버그 수정 중. . ."]


""" Loggin & Announcement Channel Setting """
ERROR_LOGGING_CHANNEL = int(os.getenv('EP_ERROR_LOGGING_CHANNEL'))
ANNOUNCE_CHANNEL = int(os.getenv('EP_ANNOUNCE_CHANNEL'))

""" Slash Command Option """
# 커맨드를 등록할 서버 ID 리스트. 전역 등록 시에는 None으로 지정.
SLASH_COMMAND_REGISTER_SERVER = None

# 관리자 명령어를 사용할 서버 ID
ADMIN_COMMAND_GUILD = [int(x) for x in os.getenv('EP_ADMIN_COMMAND_GUILD', '').split(',')]


def token():
    return TOKEN


def activities():
    return ACTIVITIES


@property
def prefixes_no_space():
    """접두사들을 띄어쓰기 없이 반환합니다."""
    return [i.replace(" ", "") for i in PREFIXES]
