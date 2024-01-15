"""
    <Room 클래스>
    - channel을 통해 객체를 생성합니다.
    (channel.id로도 생성할 수 있지만 불안정하므로 비권장합니다.)

    userdata.db에서의 기본값 설정이 필요합니다.
    기본값 설정은 다음과 같습니다.

    exp = 0
    cleans = 0
    facilities = '[]'
    land_value = 0
    selling_now = 0
    fee = 5
"""

import ast
import copy
import random
from datetime import datetime, timezone

from discord import Thread
import discord

from classes.facility import Facility, NotExistFacility, UNITDATA
from classes.fish import Fish
from constants import Constants
from db.seta_pgsql import S_PgSQL
from db.seta_sqlite import S_SQLite
from utils import logger

db = S_PgSQL()
# 주의!!! 그냥 default_effects = UNITDATA["_effects"] 해 버리면
# dict 특성 상 복제가 아니라 동일 객체 취급 받아서 default_effects의 수정사항이 UNITDATA에 반영되어 버린다!!!


DEFAULT_ROOM_VALUES = {
    "name": "알 수 없는 낚시터",
    "cleans": 50,
    "season": 1,
    "biome": 0,
    "facilities": [],
    "land_value": 0,
    "fee": 0,
    "exp": 0,
}

working_now: set[int] = set()


class Room:
    """채널 기본 정보"""

    channel: discord.TextChannel = None  # 채널 객체 자체
    id = None  # 채널 아이디
    name: str = "알 수 없는 낚시터"  # 채널명

    """주요 낚시 관련 정보"""

    owner = None  # 채널이 속한 서버의 주인 (ID로 객체를 생성하면 쓸 수 없으므로 주의)
    history: int = 0  # 낚시터 설립으로부터(일 단위)
    _facilities: list = []

    """ getter/setter 사용 """

    _owner_id: int = 0  # (int) 낚시터 주인의 디스코드 ID
    _cleans: int = 0  # (int) 낚시터 청결도
    _season: int = 0  # (int 1~4) 낚시터 계절
    _biome: int = 0  # (int +) 낚시터 지형
    _fee: int = 5  # (int 1~100) 낚시터 설정된 수수료
    _exp: int = 0  # 낚시터 경험치
    _working_now: bool = False
    _land_value: int = 0  # 땅에 묶여있는 돈(0이면 서버 주인이 땅 주인)

    # ------------------------------------- add(상대적 값 수정/+=이나 -=대신 이쪽을 권장) ------------------------------------- #

    async def add_cleans(self, value: int):
        """청결도에 value 만큼 더합니다.
        float 같은 값을 넣어도 int로 자동변환합니다."""
        await db.update_sql(
            "rooms", f"cleans = cleans + {int(value)}", f"id='{self.id}'"
        )
        self._cleans += int(value)

    async def add_exp(self, value: int):
        """낚시터 명성에 value 만큼 더합니다.
        float 같은 값을 넣어도 int로 자동변환합니다."""
        await db.update_sql("rooms", f"exp = exp + {int(value)}", f"id='{self.id}'")
        self._exp += int(value)

    # ------------------------------------- getter/setter(읽기/쓰기 전용) ------------------------------------- #

    @property
    def owner_id(self):
        """int: 땅 주인의 디스코드 ID (*값 수정 가능*)"""
        return self._owner_id
        # return db.select_sql('rooms', 'owner', f'WHERE id={self.id}')[0][0]

    async def set_owner_id(self, _id: int):
        await db.update_sql("rooms", f"owner='{_id}'", f"id='{self.id}'")
        self._owner_id = _id

    @property
    def cleans(self):
        return self._cleans

    async def get_cleans(self):
        """int: 땅의 청결도 (*값 수정 가능*)
        ※ 자주 변하는 값이므로 부를 때마다 쿼리를 날려 DB에서 얻어옵니다."""
        return (await db.select_sql("rooms", "cleans", f"WHERE id='{self.id}'"))[0][0]

    async def set_cleans(self, value: int):
        await db.update_sql("rooms", f"cleans={int(value)}", f"id='{self.id}'")
        self._cleans = value

    @property
    def season(self):
        """int: 땅의 계절 (*값 수정 가능*)"""
        return self._season
        # return db.select_sql('rooms', 'season', f'WHERE id={self.id}')[0][0]

    async def set_season(self, value: int):
        await db.update_sql("rooms", f"season={int(value)}", f"id='{self.id}'")
        self._season = value

    @property
    def biome(self):
        """int: 땅의 지형 (*값 수정 가능*)"""
        return self._biome
        # return db.select_sql('rooms', 'biome', f'WHERE id={self.id}')[0][0]

    async def set_biome(self, value: int):
        await db.update_sql("rooms", f"biome={int(value)}", f"id='{self.id}'")
        self._biome = value

    @property
    def fee(self):
        """int: 현재 설정된 땅의 수수료 (*값 수정 가능*)"""
        return self._fee
        # return db.select_sql('rooms', 'fe', f'WHERE id={self.id}')[0][0]

    async def set_fee(self, value: int):
        await db.update_sql("rooms", f"fee={int(value)}", f"id='{self.id}'")
        self._fee = int(value)

    @property
    def exp(self):
        return self._exp

    async def get_exp(self):
        """int: 땅의 명성 값 (*값 수정 가능*)
        ※ 자주 변하는 값이므로 부를 때마다 쿼리를 날려 DB에서 얻어옵니다."""
        return (await db.select_sql("rooms", "exp", f"WHERE id='{self.id}'"))[0][0]

    async def set_exp(self, value: int):
        await db.update_sql("rooms", f"exp={int(value)}", f"id='{self.id}'")
        self._exp = int(value)

    @property
    def land_value(self):
        """int: 땅에 묶인 가격(땅값) (*값 수정 가능*)"""
        return self._land_value
        # return db.select_sql('rooms', 'land_value', f'WHERE id={self.id}')[0][0]

    async def set_land_value(self, value: int):
        await db.update_sql("rooms", f"land_value={int(value)}", f"id='{self.id}'")
        self._land_value = int(value)

    def get_working_now(self):
        """bool: 현재 땅이 작업 중인지 여부 (*값 수정 가능*)"""
        return self.id in working_now

    def set_working_now(self, value: bool):
        if value:
            working_now.add(self.id)
        elif self.id in working_now:
            working_now.remove(self.id)
        self._working_now = bool(value)

    def work(self):
        return Working(self)

    # ------------------------------------- getter(읽기 전용) ------------------------------------- #

    @property
    def facilities(self):
        """List[str]: 땅에 건설된 시설 코드 리스트"""
        return self._facilities
        # fac = db.select_sql('rooms', 'facilities', f'WHERE id={self.id}')[0][0]
        # return ast.literal_eval(str(fac))

    @property
    def min_purchase(self):
        """int: 땅 매입을 위한 최소 가격 ( 땅값 × 1.1 )"""
        landv = self.land_value
        return int(landv * 1.1) if not landv == 0 else 30000

    @property
    def default_fee(self):
        """int: 시설 영향이 들어간 기본 수수료, 단위는 퍼센트(%)
        ※ 이 메서드는 굳이 최신 값을 사용할 필요가 없으므로 최적화를 위해 self.exp 대신 self._exp를 씁니다."""
        return 100 + int(-9500000 / (self._exp + 100000)) + self.effects["fee"]
        # return 5 + int((self.exp/50)**(1/2)) + self.effects['fee']

    @property
    def tier(self):
        """int: 낚시터 레벨(티어, 확장)"""
        tier = 1
        for i in self.facilities:
            if i.startswith("_TIER"):
                val = int(i.replace("_TIER", ""))
                if val > tier or not val:
                    tier = val
        return tier

    @property
    def effects(self):
        """dict: 낚시터의 시설 효과가 담긴 딕셔너리, unitdata.json의 _effects를 기본 형태로 합니다."""
        effect_dict = copy.deepcopy(UNITDATA["_effects"])
        # 딕셔너리를 복제해서 수정해야 할 때는 꼭 copy.deepcopy를 쓰자!!!
        for i in self.facilities:
            try:
                facility = Facility(i)
                effect_dict = facility.set_effect(effect_dict)
            except NotExistFacility:
                logger.warn(f"존재하지 않는 시설 : {i}")
        return effect_dict

    @property
    def fee_range(self):
        """tuple: 수수료 설정 가능 범위로 단위는 퍼센트입니다."""
        default = self.default_fee
        effect = self.effects
        minimum = default - effect["feemin_down"] - effect["feerange"]
        maximum = default + effect["feemax_up"] + effect["feerange"]

        # 무조건 0~100 사이
        minimum = 0 if minimum < 0 else minimum
        minimum = 100 if minimum > 100 else minimum
        maximum = 0 if maximum < 0 else maximum
        maximum = 100 if maximum > 100 else maximum

        return minimum, maximum

    @property
    def can_build_facilities(self):
        """이 낚시터에 현재 건설할 수 있는 시설이 담긴 리스트로 반환합니다.

        * 안 나오는 경우
        - 티어가 부족한 경우
        - 명성이 부족한 경우
        - 이미 건설되어 있는 경우"""
        cb = []
        for i in UNITDATA.keys():
            if i.startswith("_"):
                continue
            fac = Facility(i)
            if (
                self.tier >= fac.tier
                and self._exp >= fac.cost
                and i not in self.facilities
            ):
                cb.append(fac)
        return cb

    @property
    def limit_level(self):
        """int: 낚시터에서 낚시가 제한되는 레벨 값을 반환합니다"""
        tier = self.tier
        if tier == 0: return 0
        elif tier == 1: return 0
        elif tier == 2: return 0
        elif tier == 3: return 20
        elif tier == 4: return 40
        elif tier == 5: return 80
        elif tier == 6: return 160
        elif tier == 7: return 0

    # ------------------------------------- method(메서드 - 시설 관련) ------------------------------------- #

    def can_build_it(self, facility: Facility):
        """bool: 해당 시설이 이 낚시터에 건설이 가능할 시 True를 반환합니다.

        Parameters
        -----------
        facility: :class:`str`
            건설 가능 여부를 확인할 시설의 코드

        Raises
        -------
        AlreadyBuilt
            이미 건설된 시설일 경우
        OverlappedFacility
            동일 계열의 건물이 존재하는 경우
        ShortTier
            건설하기 위한 티어가 부족한 경우
        """
        if facility.code in self.facilities:  # 이미 존재하는 시설
            raise AlreadyBuilt
        if self.tier < facility.tier:  # 낚시터 레벨 부족
            raise ShortTier(facility.tier)

        if facility.branch != 0:  # 0계열 시설은 중복 설치 가능
            for i in self.facilities:
                obj = Facility(i)
                if facility.branch == obj.branch:
                    raise OverlappedFacility(obj.code, obj.branch)

        if self.biome not in facility.biome:
            raise WrongBiome(facility.biome)

        return True

    async def build_facility(self, facility: str):
        """지정 코드의 시설을 건설합니다.

        Parameters
        -----------
        facility: :class:`str`
            건설할 시설의 코드

        Raises
        -------
        AlreadyBuilt
            이미 건설된 시설일 경우
        """
        if facility in self.facilities:
            raise AlreadyBuilt
        self._facilities.append(facility)
        await db.update_sql(
            "rooms",
            f"facilities='{await db.json_convert(self.facilities)}'",
            f"id='{self.id}'",
        )

    async def break_facility(self, facility: str):
        """지정 코드의 시설을 철거합니다.

        Parameters
        -----------
        facility: :class:`str`
            철거할 시설의 코드

        Raises
        -------
        Exception
            애초에 건설되어 있지 않은 시설의 경우
        """
        if facility not in self.facilities:
            raise Exception
        self._facilities.remove(facility)
        await db.update_sql(
            "rooms",
            f"facilities='{await db.json_convert(self.facilities)}'",
            f"id='{self.id}'",
        )

    # ------------------------------------- (물고기 관련) ------------------------------------- #

    async def randfish(self):
        """랜덤으로 해당 방에서 낚이는 생선 객체(:class:`Fish`)를 반환합니다. 단, 생성된 조건에서 낚일 생성이 없으면 None을 반환합니다."""
        rank = choose(self.probability_distribution)

        nominated_fishes = await db.select_sql(
            "fish",
            "id",
            f"WHERE rarity = '{rank}' and biomes LIKE '%{self.biome}%' and seasons LIKE '%{self.season}%' ORDER BY random() LIMIT 1",
        )

        if not nominated_fishes:
            return None
        else:
            fish = await Fish.fetch(nominated_fishes[0][0])
            fish.place = self
            return fish

    def probability_per(self, code: int):
        """해당 코드의 랭크의 물고기가 낚일 확률(:class:`float`)을 반환

        Parameters
        -----------
        code: :class:`int`
        """
        dt = self.probability_distribution
        full = 0
        for i in dt.values():
            full += i
        return dt[code] / full

    @property
    def fishing_probability(self):
        """float: 매 턴마다 물고기가 낚일 확률을 반환
        ※ 이 메서드는 굳이 최신 값을 사용할 필요가 없으므로 최적화를 위해 self.exp 대신 self._exp를 씁니다."""
        # 서버 역사 보정 (최대 턴당 +10%까지)
        history_effect = -1000 / (self.history + 100) + 10

        # 낚시터 명성 보정 (최대 턴당 +10%까지)
        exp_effect = -5000 / (self._exp + 500) + 10

        # 기본이 60%까지 가능하므로 시설 보정은 40% 이상 만들지 말자!
        return 20 + history_effect + exp_effect + self.effects["probability"]

    async def can_fishing_list(self):
        """List[`str`]: 해당 지역에서 낚을 수 있는 물고기의 이름 리스트를 반환"""
        rank = await db.select_sql(
            "fish",
            "name",
            f"WHERE biomes LIKE '%{self.biome}%' and seasons LIKE '%{self.season}%'",
        )
        if not rank:
            return []
        else:
            return [i[0] for i in rank]

    async def can_fishing_dict(self):
        """dict: 해당 지역에서 낚을 수 있는 등급 별 물고기의 이름 딕셔너리를 반환
        예시) {0:['쓰레기'], 1:['농어']}
        """
        can_fishing_dict = {}
        for i in range(0, 5):
            rank = await db.select_sql(
                "fish",
                "name",
                f"WHERE rarity = '{i}' and biomes LIKE '%{self.biome}%' and seasons LIKE '%{self.season}%'",
            )
            if not rank:
                can_fishing_dict[i] = []
            else:
                can_fishing_dict[i] = [i[0] for i in rank]
        return can_fishing_dict

    async def can_fishing_dict_eng(self):
        """dict: 해당 지역에서 낚을 수 있는 등급 별 물고기의 이름 딕셔너리를 반환

        예) {0:['쓰레기'], 1:['농어']}"""
        can_fishing_dict = {}
        for i in range(0, 5):
            rank = await db.select_sql(
                "fish",
                "eng_name",
                f"WHERE rarity = '{i}' and biomes LIKE '%{self.biome}%' and seasons LIKE '%{self.season}%' and eng_name is not null",
            )
            if not rank:
                can_fishing_dict[i] = []
            else:
                can_fishing_dict[i] = [i[0] for i in rank]
        return can_fishing_dict

    @property
    def probability_distribution(self):
        """dict: 등급 별 도수분포를 반환합니다.

        청결도가 음수일 경우 쓰레기의 확률이 증가합니다.
        청결도가 100보다 높아지면 흔함 물고기가 나올 확률이 감소합니다.
        """
        cleans = self._cleans
        efdict = self.effects
        ranks = {
            0: 200 + efdict["0_rank"],
            1: 640 + efdict["1_rank"],
            2: 120 + efdict["2_rank"],
            3: 30 + efdict["3_rank"],
            4: 9 + efdict["4_rank"],
            5: 1 + efdict["5_rank"],
        }
        if cleans < 0:
            ranks[0] += -10 * cleans
        if cleans > 100:  # 청결도가 높으면 흔한 물고기가 나올 확률이 감소
            ranks[1] -= (-20000 / cleans) + 200

        for i in ranks.keys():
            if ranks[i] < 0:
                ranks[i] = 0
        return ranks

    @property
    def bonus(self):
        """float: 시설 물고기 가격 보너스 효과를 배수로 반환합니다. (1.3, 0.8 같이)"""
        effect = self.effects
        return round(effect["_price"] * 100 - 100)

    @property
    def maintenance(self):
        """int: 유지비 값을 퍼센트로 반환합니다. (10, 30 같이)"""
        maint = self.effects["maintenance"]
        return maint if maint > 0 else 0

    @property
    def fish_percentage(self):
        """float: 턴당이 아닌 낚시를 한 번 했을 때 물고기가 낚일 확률을 계산하여 제시합니다. (아무 것도 안 낚일 확률의 여사건)"""
        return 1 - (1 - self.fishing_probability / 100) ** 5

    # ------------------------------------- __init__ ------------------------------------- #

    @staticmethod
    async def fetch(channel):
        room = Room()

        if isinstance(channel, int) or isinstance(
            channel, str
        ):  # ID만으로 생성하는 경우(매우 비권장)
            # logger.warn('권장되지 않은 사용 : ID로 Room 객체 생성')
            room.id = channel

        elif isinstance(channel, Thread):
            # 스레드로 생성하는 경우 엄마 채널을 기준으로 간주함.
            channel = channel.parent
            if not channel:
                raise Exception
            room.id = channel.id
            room.name = channel.name.replace('"', "").replace("'", "")
            room.history = (datetime.now(timezone.utc) - channel.created_at).days

        else:
            # 채널 객체로 생성하는 경우
            room.channel = channel
            room.id = channel.id
            room.name = channel.name.replace('"', "").replace("'", "")
            room.history = (datetime.now(timezone.utc) - channel.created_at).days

        data = await room._load_data()

        # 낚시터 데이터가 없다면 생성
        if not data:
            # ID로 최초 객체를 생성한 경우 이프가 기본 주인이 됨.
            await room.set_owner_id(
                room.channel.guild.owner_id
                if room.channel is not None
                else 693818502657867878
            )

            print(str(type(channel)))
            if "VoiceChannel" in str(type(channel)):
                biome = choose({7: 80, 8: 20, 9: 1})
            else:
                biome = choose({0: 1, 1: 7, 2: 10, 3: 3, 4: 5, 5: 2, 6: 3})

            first_data = DEFAULT_ROOM_VALUES
            first_data["id"] = str(room.id)
            first_data["name"] = room.name
            first_data["owner"] = room.owner_id
            first_data["season"] = random.randint(1, 4)
            first_data["biome"] = biome
            await db.insert_dict("rooms", first_data)
            """
            db.insert_sql(
                'rooms',
                'id, name, owner, season, biome',
                f"'{self.id}', '{self.name}', '{owner_id}', {random.randint(1, 4)}, {biome}"
                )
            """
            data = await room._load_data()

        data = data[0]
        room._owner_id = int(data[1])
        room._exp = int(data[2])
        room._cleans = int(data[3])
        room._season = int(data[4])
        room._biome = int(data[5])
        room._facilities = ast.literal_eval(str(data[6]))
        room._land_value = int(data[7])
        room._fee = int(data[8])
        if isinstance(channel, int):
            room.name = data[0]

        # 저장된 채널명과 다르면 갱신(ID로 객체를 생성했을 때는 적용 안 됨)
        if not isinstance(channel, int) and room.name != data[0]:
            await db.update_sql("rooms", f"name='{room.name}'", f"id='{room.id}'")

        # 지가가 0인데 땅주인과 채널 주인이 다르면 채널 주인으로 지정
        if (
            room.channel is not None
            and room.land_value == 0
            and room.owner_id != channel.guild.owner_id
        ):
            await room.set_owner_id(room.channel.guild.owner_id)

        # 수수료가 범위 밖으로 설정된 경우
        payfromto = room.fee_range
        if room.fee < payfromto[0]:
            logger.debug("가능 수수료보다 낮아서 재조정")
            await room.set_fee(payfromto[0])

        elif room.fee > payfromto[1]:
            logger.debug("가능 수수료보다 높아서 재조정")
            await room.set_fee(payfromto[1])

        return room

    async def reload(self):
        """데이터에서 값을 다시 불러옵니다"""

        data = (await self._load_data())[0]
        self._owner_id = int(data[1])
        self._exp = data[2]
        self._cleans = data[3]
        self._season = data[4]
        self._biome = data[5]
        self._facilities = ast.literal_eval(str(data[6]))
        self._land_value = data[7]
        self._fee = data[8]

    async def _load_data(self):
        return await db.select_sql(
            "rooms",
            "name, owner, exp, cleans, season, biome, facilities, land_value, fee",
            f"WHERE id='{self.id}'",
        )

    async def delete(self):
        """낚시터 정보를 삭제합니다."""
        return await db.delete_sql("rooms", f"WHERE id='{self.id}'")


# ------------------------------------- 외부 함수 ------------------------------------- #


def choose(probabilities: dict):
    """dict 형태로 도수분포를 전달하면 알아서 뽑음
    (예시) {'키뮤':2, '크시':1} 이라는 걸 넣으면 2/3 확률로 키뮤를, 1/3 확률로 크시를 반환함"""
    for i in probabilities.keys():
        if probabilities[i] < 0:
            probabilities[i] = 0
    prb_list = []
    for i in probabilities.keys():
        for j in range(0, int(probabilities[i])):
            prb_list.append(i)
    return random.choice(prb_list)


async def search_land(owner_id, zeroland=True):
    """해당 ID를 가진 사람의 땅 이름, 지가 리스트를 반환
    zeroland : 0원 땅도 불러올지 여부
    """
    return await db.select_sql(
        "rooms",
        "id, name, land_value",
        f"WHERE owner='{owner_id}' {'and not land_value = 0' if not zeroland else ''} ORDER BY land_value DESC",
    )


def get_working_now(_id: int):
    """Room 객체를 굳이 생성하지 않아도 땅의 작업 중 여부를 받아올 수 있게 함"""
    return _id in working_now


class Working:
    def __init__(self, room: Room) -> None:
        self.room = room

    async def __aenter__(self):
        self.room.set_working_now(True)

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.room.set_working_now(False)


# ------------------------------------- 오류 ------------------------------------- #


class AlreadyBuilt(Exception):
    def __init__(self):
        super().__init__(
            "어... 같은 건물을 두 개 세울 필요는 없다고 봐!" "\n`❗ 동일 건물을 중복하여 건설할 수 없습니다.`"
        )


class OverlappedFacility(Exception):
    def __init__(self, overlapped_fac: str, branch: int):
        self.branch = branch
        super().__init__(
            "흐음... 이미 비슷한 용도의 시설이 존재하는 것 같아!"
            f"\n`❗ 같은 계열 시설인 '{Facility(overlapped_fac).name}'을(를) 철거하고 다시 시도해 주세요.`"
        )


class ShortTier(Exception):
    def __init__(self, require: int):
        super().__init__(
            "흐음... 지금의 이 낚시터에는 지을 수 없을 것 같아!"
            f"\n`❗ 이 시설은 낚시터 {require}단계 이상의 확장을 해야 지을 수 있습니다.`"
        )


class WrongBiome(Exception):
    def __init__(self, require: list):
        biome_str_list = []
        for i in require:
            biome_str_list.append(Constants.BIOME_KR[i])
        super().__init__(
            "여기에는 이 시설을 건설할 수 없는 모양이야!"
            f"\n`❗ 이 시설은 {', '.join(biome_str_list)} 지형에서만 건설할 수 있습니다.`"
        )


class NotVaild(Exception):
    def __init__(self):
        super().__init__("올바른 값이 아닙니다.")
