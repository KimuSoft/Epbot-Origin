from discord import SlashCommandGroup
from config import SLASH_COMMAND_REGISTER_SERVER as SCRS

fishing_group = SlashCommandGroup("낚시터", "낚시터 관련 명령어", guild_ids=SCRS)
land_group = fishing_group.create_subgroup("시설", "시설 관련 명령어")
