import os
from utils.fish_card_new.fish_card import get_card


class ExampleFish:
    id = 123
    name = "물고기"
    cost = 1234

    def fee(self, *args):
        return 5

    def maintenance(self, *args):
        return 5


class ExampleUser:
    id = 123456789
    name = "유저 이름"


class ExampleRoom:
    id = 123456789
    name = "낚시터 이름"


fish = ExampleFish()
user = ExampleUser()
room = ExampleRoom()

img = get_card(fish, room, user)
img.show()
