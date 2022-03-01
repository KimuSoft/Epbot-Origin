""" <config.py> """


''' Debug Option '''
debug = True
query_logging = False


'''Administrator Setting'''
ADMINS = [
    281689852167061506,  # 키뮤
]


''' PostgreSQL Database Configuration '''
HOST = '127.0.0.1'  # HOST를 localhost로 세팅할 경우 HOST를 사용하지 않음(DB 서버와 이프 서버를 같이 돌릴 경우 권장)
DBNAME = 'postgres'
USER = 'postgres'
PASSWORD = 'test'
PORT = '5432'


''' FishCard Server Setting'''
CARD_SERVER = ''  # 슬래시로 끝내지 말아주세요
CARD_TOKEN = ""


''' Discord Bot Configuration '''
TOKEN = ''
DEBUG_TOKEN = ''

# 명령어 접두사 (띄어쓰기 주의)
PREFIXES = ['이프야 ', 'ㅇ', '잎', 'ep ']
# 하고 있는 게임 (프로필에 '... 하는 중'으로 보이는 것)
ACTIVITIES = ['{}곳의 서버에서 검열 삭제', '{}곳의 서버에서 낚시',
              "'이프야 도움말'을 입력해 보라고 이야기", "EpBot | ep help"]
DEBUG_ACTIVITIES = ['버그 수정 중. . .']


''' Loggin & Announcement Channel Setting '''
ERROR_LOGGING_CHANNEL = 1234567890
ANNOUNCE_CHANNEL = 1234567890
ADMIN_COMMAND_GUILD = [] # 관리자 명령어를 사용할 서버 ID


def token():
    return TOKEN if not debug else DEBUG_TOKEN


def activities():
    return ACTIVITIES if not debug else DEBUG_ACTIVITIES


@property
def prefixes_no_space():
    ''' 접두사들을 띄어쓰기 없이 반환합니다. '''
    return [i.replace(' ', '') for i in PREFIXES]
