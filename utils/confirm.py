import discord

from .ui import View
from .data import icons

class ConfirmationDialog(View):
    def __init__(self, invoke):
        super().__init__(invoke, True)
        self.choice = None
        self.invoke = invoke

    @discord.ui.button(emoji=icons.confirm, style=discord.ButtonStyle.green)
    async def yes(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.choice = True
        await self.stop()

    @discord.ui.button(emoji=icons.close, style=discord.ButtonStyle.red)
    async def no(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.choice = False
        await self.stop()

    async def on_timeout(self):
        return

async def confirmation(invoke, title, description):
    """
    A function that displays a confirmation dialog and waits for user input.

    ### Parameters:
    - invoke: The object that triggers the confirmation dialog.
    - title: The title of the confirmation dialog.
    - description: The description of the confirmation dialog.

    ### Returns:
    - The user's choice from the confirmation dialog.
    """
    view = ConfirmationDialog(invoke)
    embed = discord.Embed(title=title, description=description)
    await view.invoke.response.send_message(embed=embed, view=view, ephemeral=True)
    await view.wait()
    msg = await invoke.original_response()
    await msg.delete()
    return view.choice
