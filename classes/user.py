"""
<User 객체>
- user를 통해 객체를 생성합니다.
(user.id로도 생성할 수 있지만 기능이 제한됩니다.)
"""

from db.seta_pgsql import S_PgSQL
from db.seta_json import get_json
from classes.room import search_land, Room
import config
import ast

from datetime import datetime

db = S_PgSQL()

DEFAULT_USER_VALUES = {
    "name": "알 수 없는 이름",
    "money": 1000,
    "exp": 0,
    "fishing_now": 0,
    "theme": [],
    "dex": {},
    "fish": [],
}


class User:
    """정적 변수"""

    user = None  # 유저 객체 자체
    id: int = None  # 유저 아이디
    name: str = "알 수 없는 유저"  # 유저 이름
    admin: bool = False  # 이프 관리 권한 여부
    lang: str = "kr"

    """ 동적 변수 """
    biggest_size: float = 0
    biggest_name: str = None
    dex: dict = {}

    """ property/setter """
    _money: int = 0
    _exp: int = 0
    _fishing_now: bool = False
    _suspicion: int = 0

    # ------------------------------------- add(상대적 값 수정/+=이나 -=대신 이쪽을 권장) ------------------------------------- #

    async def add_money(self, value: int):
        """유저의 돈을 value 만큼 더합니다.
        float 같은 값을 넣어도 더하는 값이 int로 자동변환됩니다."""
        await db.update_sql("users", f"money = money + {int(value)}", f"id='{self.id}'")
        self._money += int(value)

    async def add_exp(self, value: int):
        """유저의 경험치를 value 만큼 더합니다.
        float 같은 값을 넣어도 더하는 값이 int로 자동변환됩니다."""
        await db.update_sql("users", f"exp = exp + {int(value)}", f"id='{self.id}'")
        self._exp += int(value)

    # ------------------------------------- getter/setter(읽기/쓰기 전용) ------------------------------------- #

    @property
    def exp(self):
        return self._exp

    async def set_exp(self, value: int):
        value = 0 if value < 0 else value
        await db.update_sql("users", f"exp={value}", f"id='{self.id}'")
        self._exp = value

    @property
    def money(self):
        return self._money

    async def set_money(self, value: int):
        if value < 0:
            raise NotEnoughException
        await db.update_sql("users", f"money={value}", f"id='{self.id}'")
        self._money = value

    @property
    def fishing_now(self):
        return db.select_sql("users", "fishing_now", f"WHERE id='{self.id}'")[0][0]

    async def set_fishing_now(self, value: bool):
        await db.update_sql("users", f"fishing_now={int(value)}", f"id='{self.id}'")
        self._fishing_now = bool(value)

    @property
    def level(self):
        exp = self.exp
        return int((exp / 15) ** 0.5 + 1 if exp > 0 else 1)

    @property
    async def get_all_money(self):
        """자신의 모든 땅값까지 합쳐 계산한 총자산을 반환합니다."""
        all_money = self._money
        for i in await self.get_lands(zeroland=False):
            all_money += i[2]
        return all_money

    @property
    def theme(self):
        return self._theme[0]

    @property
    def themes(self):
        return self._theme

    @property
    def themes_name(self):
        return [
            get_json(f"utils/fish_card/theme/{i}/theme.json")["name"]
            for i in self._theme
        ]

    async def set_theme(self, value: str):
        # 가지고 있지 않은 테마로 설정하려 했을 때
        if value not in self._theme:
            raise NoTheme

        self._theme.sort(key=lambda x: x != value)
        await db.update_sql(
            "users", f"theme='{db.json_convert(self._theme)}'", f"id='{self.id}'"
        )

    async def add_theme(self, theme: str):
        self._theme.append(theme)
        await db.update_sql(
            "users", f"theme='{db.json_convert(self._theme)}'", f"id='{self.id}'"
        )

    # ------------------------------------- method(메서드) ------------------------------------- #

    async def purchase_land(self, room: Room, value):
        """해당 낚시터를 value 만큼의 금액으로 구매"""
        origin_owner_user = await User.fetch(room.owner_id)  # 원래 주인 유저 클래스 (user)
        await origin_owner_user.give_money(room.land_value)  # 원래 주인한테 돈 돌려 줌
        await self.give_money(-1 * value)  # 새 주인의 돈을 뺏음

        await room.set_land_value(value)
        await room.set_owner_id(self.id)

    async def get_lands(self, zeroland=True):
        """내가 가진 땅의 리스트를 반환
        [(ID, 이름, 지가), (ID, 이름, 지가), ...]"""
        return await search_land(self.id, zeroland)

    async def update_biggest(self, fish):
        """물고기가 현재 낚은 것보다 큰 경우 갱신
        - 작은 경우 False 반환
        - 클 경우 True 반환 후 갱신"""
        if self.biggest_size < fish.length:
            self.biggest_size = fish.length
            self.biggest_name = fish.name
            await db.update_sql(
                "users",
                f"biggest_size={fish.length}, biggest_name='{fish.name}'",
                f"id='{self.id}'",
            )
            return True
        else:
            return False

    async def get_fish(self, fish):
        if not self.fish_history:
            self.fish_history = []
        self.fish_history.append(
            {
                "id": fish.id,
                "length": fish.length,
                "cost": fish.cost(),
                "time": datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
            }
        )
        await db.update_sql(
            "users", f"fish='{db.json_convert(self.fish_history)}'", f"id='{self.id}'"
        )
        await self.write_dex(fish)

    async def write_dex(self, fish):
        if str(fish.rarity) not in self.dex.keys():
            self.dex[str(fish.rarity)] = []
        if fish.id in self.dex[str(fish.rarity)]:
            return False
        self.dex[str(fish.rarity)].append(fish.id)
        await db.update_sql(
            "users", f"dex='{db.json_convert(self.dex)}'", f"id='{self.id}'"
        )
        return True

    # ------------------------------------- __init__ ------------------------------------- #

    @staticmethod
    async def fetch(user):
        result = User()

        if isinstance(user, int):  # ID만으로 생성하는 경우(비권장)
            # logger.warn('권장되지 않은 사용 : ID로 User 객체 생성')
            result.id = user
        else:  # 유저 객체로 생성하는 경우
            result.user = user
            result.id = user.id
            result.name = user.name.replace('"', "").replace("'", "")

        result.admin = result.id in config.ADMINS
        data = await result._load_data()

        # 유저 데이터가 없다면 생성
        if not data:
            first_value = DEFAULT_USER_VALUES
            first_value["id"] = result.id
            first_value["name"] = result.name

            await db.insert_dict("users", first_value)
            # db.insert_sql('users', 'id, name', f"'{result.id}', '{result.name}'")
            data = await result._load_data()

        data = data[0]
        result.name = str(data[0]).replace("'", "").replace('"', "")
        result._money = int(data[1])
        result.biggest_size = data[2]
        result.biggest_name = data[3]
        result.dex = ast.literal_eval(str(data[4]))
        result._exp = int(data[5])
        result._theme = ast.literal_eval(str(data[6]))
        result.fish_history = ast.literal_eval(str(data[7]))

        # 저장된 유저 이름과 다르면 갱신(ID로 객체를 생성했을 때는 적용 안 됨)
        if not isinstance(user, int) and result.name != user.name.replace(
            "'", ""
        ).replace('"', ""):
            result.name = user.name.replace("'", "").replace('"', "")
            await db.update_sql("users", f"name='{result.name}'", f"id='{result.id}'")

        # 구 버전 dex 데이터가 있는 경우(구 버전 dex는 dict가 아니라 list로 되어 있음)
        if not result.dex:
            result.dex = {}

        # 최대 크기가 null인 경우
        result.biggest_size = 0 if result.biggest_size is None else result.biggest_size

        # 구 버전 theme 데이터가 있는 경우 초기화
        if not result._theme or not isinstance(result._theme, list):
            result._theme = ["default"]

        return result

    def __init__(self):
        self.name = "알 수 없음"
        self._money = 0
        self.biggest_size = 0
        self.biggest_name = "알 수 없음"
        self.dex = {}
        self._exp = 0
        self._theme = []
        self.fish_history = []

    async def reload(self):
        """데이터에서 값을 다시 불러옵니다"""

        data = (await self._load_data())[0]
        self.name = str(data[0])
        self._money = int(data[1])
        self.biggest_size = int(data[2])
        self.biggest_name = data[3]
        self.dex = ast.literal_eval(str(data[4]))
        self._exp = int(data[5])
        self._theme = data[6]
        self.fish_history = ast.literal_eval(str(data[7]))

    async def _load_data(self):
        return await db.select_sql(
            "users",
            "name, money, biggest_size, biggest_name, dex, exp, theme, fish",
            f"WHERE id='{self.id}'",
        )

    # ------------------------------- 구 버전 호환용 코드 ------------------------------- #

    async def give_money(self, value: int):
        await self.add_money(value)

    async def start_fishing(self):
        await self.set_fishing_now(True)

    async def finish_fishing(self):
        await self.set_fishing_now(False)


async def on_fishing(_id: int):
    """단순히 낚시 중인지 여부만 조사할 경우 굳이 User 객체를 만들지 않아도 되게 만들어 주는 함수입니다.
    처음 하는 유저(데이터에 없는 유저)라면 낚시 중이 아닌 것으로 반환합니다."""
    data = await db.select_sql("users", "fishing_now", f"WHERE id='{_id}'")
    if not data:
        return False
    return data[0][0]


class NotEnoughException(Exception):
    def __init__(self):
        super().__init__("유저가 가지고 있는 돈 이상을 빼려고 시도하였습니다.")


class NotVaildType(Exception):
    def __init__(self):
        super().__init__("올바른 인자값이 아닙니다.")


class NoTheme(Exception):
    def __init__(self):
        super().__init__("보유하고 있지 않은 테마입니다.")
