"""
<Fish 객체>
- 생선 ID 데이터로 생선 객체를 생선(?)할 수 있습니다.
(ID 데이터를 입력하지 않을 시 기본 생선으로 지정됩니다.)
- random(조건) 함수로 조건에 맞는 랜덤한 생선을 만들 수 있습니다.
- Fish는 Fish의 복수형입니다.
"""

import json
import random
from datetime import datetime

import jwt

import config
from constants import Constants
from db.seta_pgsql import S_PgSQL

db = S_PgSQL()

rarity_dict = {0: "쓰레기", 1: "흔함", 2: "희귀함", 3: "매우 귀함", 4: "전설", 5: "초전설", 6: "환상"}
rarity_dict_eng = {
    0: "Trash",
    1: "Common",
    2: "Rare",
    3: "Very Rare",
    4: "Legend",
    5: "Super Legend",
    6: "Fantasy",
}


class Fish:
    id = None  # 물고기 아이디
    name = None  # 물고기 이름
    eng_name = None
    length = 0  # 크기(랜덤 생성)
    average_length = 0  # 해당 물고기 종류의 평균 크기
    seasons = []  # 해당 물고기 등장 계절
    rarity = 0  # 해당 물고기 희귀도
    biomes = []  # 해당 물고기 등장 지형
    average_cost = 0  # 해당 물고기 평균 가격

    owner = None  # 물고기를 잡은 사람
    place = None  # 물고기를 잡은 채널

    # ------------------------------------- __init__ ------------------------------------- #

    async def fetch(code: int):
        data = await db.select_sql(
            "fish", "name, cost, length, rarity, biomes, eng_name", f"WHERE id={code}"
        )
        return Fish(data, code)

    def __init__(self, data, code: int):
        if not data:
            raise NotFishException

        data = data[0]
        self.id = code  # 물고기 아이디
        self.name = data[0]  # 물고기 이름
        self.average_length = int(data[2])  # 해당 물고기 종류의 평균 크기
        self.rarity = int(data[3])  # 해당 물고기 희귀도
        self.average_cost = int(data[1])  # 해당 물고기 평균 가격
        # self.seasons = []  # 해당 물고기 등장 계절
        self.biomes = str(data[4])  # 서식지
        self.eng_name = str(data[5])
        if self.eng_name == "None":
            self.eng_name = self.name

        while self.length <= 0:
            self.length = round(self.average_length * random.gauss(1, 0.15), 2)

    # ------------------------------------- getter(읽기 전용) ------------------------------------- #

    def rarity_str(self):
        """물고기의 희귀도를 문자열로 반환"""
        return rarity_dict[self.rarity]

    def rarity_str_eng(self):
        """물고기의 희귀도를 문자열로 반환(영어)"""
        return rarity_dict_eng[self.rarity]

    def icon(self):
        """물고기의 아이콘 이모지 반환"""
        if self.rarity == 0:
            return "🗑️"
        elif self.rarity == 1:
            return Constants.CUSTOM_EMOJI["fish"]
        elif self.rarity == 2:
            return "🐠"
        elif self.rarity == 3:
            return "🐡"
        elif self.rarity == 4:
            return "🐬"
        elif self.rarity == 5:
            return "🐳"
        elif self.rarity == 6:
            return "🐉"

    def cost(self):
        """물고기의 가격은 물고기 종류, 크기에 따라 자동 생성됩니다."""
        return round(self.average_cost * (self.length / self.average_length))

    def exp(self):
        """물고기가 주는 명성 = 가격 / 100"""
        return round(self.cost() / 100)

    # ------------------------------------- setter(쓰기 전용) ------------------------------------- #

    def set_penalty(self, penalty: float):
        while self.length <= 0:
            self.length = round(self.average_length * random.gauss(1, 0.15), 2)
        self.length = round(self.length * penalty, 2)
        return 0

    # ------------------------------------- method(메서드) ------------------------------------- #

    def fee(self, user, room):
        """
        물고기에 붙는 수수료(음수)를 반환합니다.
        discord의 user와 이프의 user 모두 받습니다.
        땅주인이면 유지수수료만 붙습니다.
        """
        if room.owner_id == user.id:
            return 0
        return -1 * int(int(self.cost() * (room.fee / 100)))

    def maintenance(self, room):
        """물고기에 붙는 유지비 값을 반환합니다."""
        effect = room.effects
        return -1 * int(self.cost() * (effect["maintenance"] / 100))

    def bonus(self, room):
        """물고기에 붙는 시설 보너스 값을 반환합니다."""
        effect = room.effects
        return int(int(self.cost() * (float(effect["_price"]) - 1)))

    @property
    def card_data(self):
        time = datetime.today()
        data = {
            "rarity": str(self.rarity),
            "id": str(self.id),
            "name": self.name,
            "eng_name": self.eng_name,
            "cost": f"{self.cost():,}",  # 물고기 원가
            "length": f"{self.length:,}",  # 물고기 크기
            "average_cost": f"{self.average_cost:,}",  # 평균 물고기 크기
            "average_length": f"{self.average_length}",  # 물고기 평균가
            # 수수료 + 유지비 (%)
            "fees_p": f"{-1 * (self.place.fee + self.place.maintenance):+}",
            "fee_p": f"{-1 * self.place.fee:+}",  # 수수료 (%)
            "maintenance_p": f"{-1 * self.place.maintenance:+}",  # 유지비 (%)
            "bonus_p": f"{self.place.bonus:+}",  # 보너스 (%)
            # 수수료 + 유지비
            "fees": f"{self.fee(self.owner, self.place) + self.maintenance(self.place):+,}",
            "fee": f"{self.fee(self.owner, self.place):+,}",  # 수수료
            "maintenance": f"{self.maintenance(self.place):+,}",  # 유지비
            "bonus": f"{self.bonus(self.place):+,}",  # 보너스
            "time": time.strftime("%Y-%m-%d %H"),  # 현재 시간
            "self.placename": de_emojify(self.place.name),  # 낚은 낚시터 이름
            "self.ownername": de_emojify(self.owner.name),  # 낚은 유저의 이름
            "profit": f"{self.cost() + self.fee(self.owner, self.place) + self.maintenance(self.place) + self.bonus(self.place):,}",
        }
        return data


async def search_fish(keyword):
    if keyword.isdigit():
        return int(keyword)

    try:
        data = await db.select_sql(
            "fish", "id", f"WHERE name LIKE '%{keyword}%' ORDER BY length(name)"
        )[0]
        return data[0]
    except Exception:
        raise NotFishException


def de_emojify(input_str: str):
    result = input_str.encode("euc-kr", "ignore").decode("euc-kr")
    if result == "":
        return "알 수 없는 이름"
    else:
        return result


class NotFishException(Exception):
    def __init__(self):
        super().__init__("존재하지 않는 물고기를 불러왔습니다.")
