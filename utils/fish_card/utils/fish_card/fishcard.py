from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from utils.seta_josa import Josa

font_exist = "utils/fish_card/NotoSansCJKkr-Bold.otf"
font24 = ImageFont.truetype(font_exist, 24)
font20 = ImageFont.truetype(font_exist, 20)
font16 = ImageFont.truetype(font_exist, 16)
font12 = ImageFont.truetype(font_exist, 12)
font8 = ImageFont.truetype(font_exist, 8)


def getCard(fish=None, room=None, user=None):
    img = Image.open(
        f"utils/fish_card/card_type_{fish.rarity}.png"
    )  # 일단 기본배경폼 이미지를 open 합니다.
    draw = ImageDraw.Draw(img)

    cost = fish.cost()
    fee = fish.fee(user, room) + fish.maintenance(room)
    bonus = fish.bonus(room)

    text_up = {
        0: "{}을(를) 낚아 버렸다;;;",
        1: "{}이(가) 낚였다!",
        2: "와! {}을(를) 낚았다!!!",
        3: "월척이야!!! {}을 낚다니!",
        4: "이건... {}?!?!",
        5: "{}(이)라고?!?! 가능한 거야???",
    }

    text = Josa().convert(text_up[fish.rarity].format(fish.name))
    if len(text) < 13:
        draw.text((71, 7), text, font=font24)
    else:
        draw.text((71, 10), text, font=font20)
    draw.text((80, 59), f"{cost}$", font=font20, fill=(0, 0, 0))

    if fish.rarity != 0:
        if room.owner_id == user.id:
            draw.text(
                (72, 85),
                f"{fee:+,}$ ({-1 * room.maintenance:+}%)",
                font=font16,
                fill=(50, 0, 0),
            )
            draw.text((72, 38), "낚시터 주인", font=font8)
        else:
            draw.text(
                (72, 85),
                f"{fee:+,}$ ({-1 * (room.fee + room.maintenance):+}%)",
                font=font16,
                fill=(50, 0, 0),
            )
        draw.text(
            (72, 105), f"{bonus:+,}$ ({room.bonus:+}%)", font=font16, fill=(0, 50, 0)
        )
        draw.text((85, 145), f"{(cost + fee + bonus):,}$", font=font24, fill=(0, 0, 0))

    if len(fish.name) < 6:
        draw.text((350, 60), f"{fish.name}", font=font24, fill=(0, 0, 0))
    else:
        draw.text((350, 60), f"{fish.name}", font=font20, fill=(0, 0, 0))
    draw.text((350, 90), f"{fish.length}cm", font=font20, fill=(0, 0, 0))
    draw.text((350, 115), f"(평균 {fish.average_length}cm)", font=font12, fill=(0, 0, 0))
    draw.text((350, 130), f"{fish.cost():,}$", font=font20, fill=(0, 0, 0))
    draw.text((350, 155), f"(평균 {fish.average_cost:,}$)", font=font12, fill=(0, 0, 0))

    time = datetime.today()
    draw.text((290, 160), f"『{deEmojify(user.name)}』", font=font8, fill=(0, 0, 0))
    draw.text(
        (280, 170),
        f"{time.strftime('%Y-%m-%d %H')}시에 '{deEmojify(room.name)}'에서",
        font=font8,
        fill=(0, 0, 0),
    )
    # img.show()

    return img


def getCard_eng(fish=None, room=None, user=None):
    img = Image.open(
        f"utils/fish_card/en_card_{fish.rarity}.png"
    )  # 일단 기본배경폼 이미지를 open 합니다.
    draw = ImageDraw.Draw(img)

    cost = fish.cost()
    fee = fish.fee(user, room) + fish.maintenance(room)
    bonus = fish.bonus(room)

    text_up = {
        0: "I caught the {} ...",
        1: "I caught a {}!",
        2: "WOW! I caught the a {}!!!",
        3: "I caught a {}! I can't belive it!!!",
        4: "This is... {}?!?!",
        5: "{}?! Is it possible?!?!",
    }

    text = text_up[fish.rarity].format(fish.eng_name)
    if len(text) < 13:
        draw.text((71, 7), text, font=font24)
    else:
        draw.text((71, 10), text, font=font20)
    draw.text((80, 59), f"{cost}$", font=font20, fill=(0, 0, 0))

    if fish.rarity != 0:
        if room.owner_id == user.id:
            draw.text(
                (72, 85),
                f"{fee:,}$ (OWNER {room.maintenance}%)",
                font=font16,
                fill=(50, 0, 0),
            )
        else:
            draw.text(
                (72, 85),
                f"{fee:,}$ ({room.fee + room.maintenance}%)",
                font=font16,
                fill=(50, 0, 0),
            )
        draw.text(
            (72, 105), f"+{bonus:,}$ ({room.bonus}%)", font=font16, fill=(0, 50, 0)
        )
        draw.text((85, 145), f"{(cost + fee + bonus):,}$", font=font24, fill=(0, 0, 0))

    if len(fish.name) < 6:
        draw.text((350, 60), f"{fish.eng_name}", font=font24, fill=(0, 0, 0))
    else:
        draw.text((350, 60), f"{fish.eng_name}", font=font20, fill=(0, 0, 0))
    draw.text((350, 90), f"{fish.length}cm", font=font20, fill=(0, 0, 0))
    draw.text(
        (350, 115), f"(Average {fish.average_length}cm)", font=font12, fill=(0, 0, 0)
    )
    draw.text((350, 130), f"{fish.cost():,}$", font=font20, fill=(0, 0, 0))
    draw.text(
        (350, 155), f"(Average {fish.average_cost:,}$)", font=font12, fill=(0, 0, 0)
    )

    time = datetime.today()
    draw.text((290, 160), f"『{deEmojify(user.name)}』", font=font8, fill=(0, 0, 0))
    draw.text(
        (280, 170),
        f"In the '{deEmojify(room.name)}' at {time.strftime('%Y-%m-%d %H')}",
        font=font8,
        fill=(0, 0, 0),
    )
    # img.show()

    return img


def deEmojify(inputString):
    fifinal = inputString.encode("euc-kr", "ignore").decode("euc-kr")
    if fifinal == "":
        return "알 수 없는 이름"
    else:
        return fifinal


# getCard()
