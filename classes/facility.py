from db import seta_json as sj

import os


_ud = {}
for dt in os.listdir("static/unitdata"):
    if not dt.endswith(".json"):
        continue
    _ud.update(sj.get_json(f"static/unitdata/{dt}"))

UNITDATA = _ud


class Facility:
    name = "UNKNOWN"
    code = "NONE"
    description = "UNKNOWN"
    effect = {}
    tier = 1
    biome = range(0, 100)

    def __init__(self, code: str):
        # 한글 이름으로 넣은 경우
        if code.upper() not in UNITDATA.keys():
            for i in UNITDATA.keys():
                if i in ["_effects", "_information"]:
                    continue
                if code.replace(" ", "") == UNITDATA[i]["name"].replace(" ", ""):
                    code = i

        # 없는 시설 코드인 경우
        if code.upper() not in UNITDATA.keys():
            raise NotExistFacility(code.upper())

        self.data = UNITDATA[code.upper()]
        self.code = code.upper()
        self.name = self.data["name"]
        self.description = (
            self.data["description"]
            if "description" in self.data.keys()
            else "설명이 없습니다."
        )
        self.effect = self.data["effects"] if "effects" in self.data.keys() else {}
        self.tier = self.data["tier"] if "tier" in self.data.keys() else 1
        self.cost = self.data["cost"]
        self.branch = self.data["branch"] if "branch" in self.data.keys() else 0
        if "biome" in self.data.keys():
            self.biome = self.data["biome"]
            if isinstance(self.biome, int):
                self.biome = [self.biome]

    def set_effect(self, effect_dict={}):
        """
        effect_dict에 이 시설의 성능을 적용합니다.
        '_'로 시작하는 효과는 기본값 1이며 곱계산됩니다. (가격보정)
        그 외 효과는 기본값 0이며 합계산됩니다. (수수료)
        """
        for i in self.effect.keys():
            if i.startswith("_"):
                if i not in effect_dict.keys():
                    effect_dict[i] = 1
                effect_dict[i] *= self.effect[i]
            else:
                if i not in effect_dict.keys():
                    effect_dict[i] = 0
                effect_dict[i] += self.effect[i]
        return effect_dict

    def can_maintain(self, room):
        """
        해당 낚시터에서 이 시설을 유치 가능한지 여부를 반환합니다.
        - 티어 부족 -> False, ''
        - 같은 계열 시설이 이미 존재함 False, '시설코드'
        """
        pass

    def effect_information(self):
        return "\n".join(
            [
                UNITDATA["_information"][i].format(self.effect[i])
                for i in self.effect.keys()
            ]
        )


class NotExistFacility(Exception):
    def __init__(self, code: str = "NONE"):
        super().__init__(f"존재하지 않는 시설입니다. ({code})")


class AlreadyBuilt(Exception):
    def __init__(self):
        super().__init__("이미 건설된 유닛입니다.")
