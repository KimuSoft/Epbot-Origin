from datetime import datetime
import os

from PIL import Image, ImageDraw, ImageFont

from utils.seta_josa import Josa
from db import seta_json

here = "utils/fish_card"

font_exist = f"{here}/NotoSansCJKkr-Bold.otf"
font28 = ImageFont.truetype(font_exist, 28)
font24 = ImageFont.truetype(font_exist, 24)
font20 = ImageFont.truetype(font_exist, 20)
font16 = ImageFont.truetype(font_exist, 16)
font14 = ImageFont.truetype(font_exist, 14)
font12 = ImageFont.truetype(font_exist, 12)
font8 = ImageFont.truetype(font_exist, 8)

default_fontset = {
    8: font8,
    12: font12,
    14: font14,
    16: font16,
    20: font20,
    24: font24,
    28: font28,
}


async def get_card(fish=None, room=None, user=None):
    theme = user.theme
    theme_exist = f"{here}/theme/{theme}".replace("\\", "/")
    theme = seta_json.get_json(f"{theme_exist}/theme.json")

    # 레이아웃
    if f"rank-{fish.rarity}" not in theme.keys():
        layout = theme["default"]
    else:
        layout = theme[f"rank-{fish.rarity}"]

    # 카드 배경 불러오기
    if os.path.isfile(f"{theme_exist}/rank-{fish.rarity}.png"):
        img = Image.open(f"{theme_exist}/rank-{fish.rarity}.png")
    else:
        img = Image.open(f"{theme_exist}/default.png")

    # font 불러오기
    if "font" not in theme.keys():
        fontset = default_fontset
    else:
        fontset = {}
        font_where = f"{theme_exist}/{theme['font']}"
        for i in layout:
            if "size" in i.keys():
                font_size = int(i["size"])
                fontset[font_size] = ImageFont.truetype(font_where, font_size)

    draw = ImageDraw.Draw(img)

    time = datetime.today()
    # 기본 변수들이 들어간 딕셔너리 생성
    format_dict = {
        "id": fish.id,
        "name": fish.name,
        "eng_name": fish.eng_name,
        "cost": f"{fish.cost():,}",  # 물고기 원가
        "length": f"{fish.length:,}",  # 물고기 크기
        "average_cost": f"{fish.average_cost:,}",  # 평균 물고기 크기
        "average_length": f"{fish.average_length}",  # 물고기 평균가
        "fees_p": f"{-1 * (room.fee + room.maintenance):+}",  # 수수료 + 유지비 (%)
        "fee_p": f"{room.fee:+}",  # 수수료 (%)
        "maintenance_p": f"{room.maintenance:+}",  # 유지비 (%)
        "bonus_p": f"{room.bonus:+}",  # 보너스 (%)
        "fees": f"{fish.fee(user, room) + fish.maintenance(room):+,}",  # 수수료 + 유지비
        "fee": f"{fish.fee(user, room):+,}",  # 수수료
        "maintenance": f"{fish.maintenance(room):+,}",  # 유지비
        "bonus": f"{fish.bonus(room):+,}",  # 보너스
        "time": time.strftime("%Y-%m-%d %H"),  # 현재 시간
        "roomname": deEmojify(room.name),  # 낚은 낚시터 이름
        "username": deEmojify(user.name),  # 낚은 유저의 이름
        "profit": f"{fish.cost() + fish.fee(user, room) + fish.maintenance(room) + fish.bonus(room):,}",
    }

    OWNER = room.owner_id == user.id
    for object in layout:
        if "owner" in object.keys() and object["owner"] != OWNER:
            continue
        elif "rarity" in object.keys() and object["rarity"] != fish.rarity:
            continue
        color = (0, 0, 0)
        if "color" in object.keys():
            color = tuple(object["color"])
        draw.text(
            tuple(object["position"]),
            Josa().convert(object["text"].format(**format_dict)),
            font=fontset[object["size"]],
            fill=color,
        )

    return img


def deEmojify(inputString):
    result = inputString.encode("euc-kr", "ignore").decode("euc-kr")
    if result == "":
        return "알 수 없는 이름"
    else:
        return result
