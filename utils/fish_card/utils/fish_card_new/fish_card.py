import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from functools import partial

from PIL import Image, ImageDraw, ImageFont

from db import seta_json
from utils import logger
from utils.seta_josa import Josa

font_exist = "utils/fish_card/NotoSansCJKkr-Bold.otf"
font24 = ImageFont.truetype(font_exist, 24)
font20 = ImageFont.truetype(font_exist, 20)
font16 = ImageFont.truetype(font_exist, 16)
font12 = ImageFont.truetype(font_exist, 12)
font8 = ImageFont.truetype(font_exist, 8)

fonts = {8: font8, 12: font12, 16: font16, 20: font20, 24: font24}

thread_pool = ThreadPoolExecutor()

loop = asyncio.get_event_loop()


async def get_card_async(fish=None, room=None, user=None, theme="default"):
    return await loop.run_in_executor(
        thread_pool, partial(get_card, fish, room, user, theme)
    )


def get_card(fish=None, room=None, user=None, theme="default"):
    try:
        here = os.path.dirname(os.path.realpath(__file__))
        theme_exist = f"{here}/theme/{theme}"
        theme = seta_json.get_json(f"{theme_exist}/theme.json")

        if f"rank-{fish.rarity}" not in theme.keys():
            img = Image.open(f"{theme_exist}/default.png")
            layout = theme["default"]
        else:
            img = Image.open(f"{theme_exist}/rank-{fish.rarity}.png")
            layout = theme[f"rank-{fish.rarity}"]
        draw = ImageDraw.Draw(img)

        time = datetime.today()
        # 기본 변수들이 들어간 딕셔너리 생성
        format_dict = {
            "name": fish.name,
            "cost": f"{fish.cost():,}",  # 물고기 원가
            "length": f"{fish.length:,}",  # 물고기 크기
            "average_cost": f"{fish.average_cost:,}",  # 평균 물고기 크기
            "average_length": f"{fish.average_length}",  # 물고기 평균가
            "fees_p": room.fee + room.maintenance,  # 수수료 + 유지비 (%)
            "fee_p": room.fee,  # 수수료 (%)
            "maintenance_p": room.maintenance,  # 유지비 (%)
            "bonus_p": room.bonus,  # 보너스 (%)
            "fees": fish.fee(user, room) + fish.maintenance(room),  # 수수료 + 유지비
            "fee": fish.fee(user, room),  # 수수료
            "maintenance": fish.maintenance(room),  # 유지비
            "bonus": fish.bonus(room),  # 보너스
            "time": time.strftime("%Y-%m-%d %H"),  # 현재 시간
            "roomname": room.name,  # 낚은 낚시터 이름
            "username": deEmojify(user.name),  # 낚은 유저의 이름
            "profit": fish.cost()
            + fish.fee(user, room)
            + fish.maintenance(room)
            + fish.bonus(room),
        }

        for object in layout:
            draw.text(
                tuple(object["position"]),
                Josa().convert(object["text"]).format(format_dict),
                font=fonts[object["size"]],
                fill=(0, 0, 0),
            )

        return img
    except Exception as e:
        logger.err(e)
        raise e


def deEmojify(inputString):
    result = inputString.encode("euc-kr", "ignore").decode("euc-kr")
    if result == "":
        return "알 수 없는 이름"
    else:
        return result
