
import discord
from discord import app_commands

# Provide fallback implementations for slash commands and Option when Pycord is unavailable.
def slash_command(*args, **kwargs):
    def decorator(func):
        app_cmd = app_commands.command(*args, **kwargs)
        async def wrapper(interaction: discord.Interaction, *fargs, **ffkwargs):
            # Provide respond and send compatibility for interactions similar to Pycord.
            interaction.respond = interaction.response.send_message
            interaction.send = interaction.followup.send
            return await func(interaction, *fargs, **ffkwargs)
        return app_cmd(wrapper)
    return decorator

class ApplicationContext(discord.Interaction):
    """Fallback ApplicationContext for discord.py."""
    pass


def Option(annotation, description=None, **kwargs):
    """
    Fallback Option for discord.py.
    In discord.py, use type annotations directly.
    """
    return annotation

class SlashCommandGroup(app_commands.Group):
    """Fallback SlashCommandGroup for discord.py."""
    pass
