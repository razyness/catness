import discord


class View(discord.ui.View):

    def __init__(self, view_inter, owned=False, timeout=180, **kwargs):
        self.view_inter = view_inter
        self.owned = owned
        super().__init__(timeout=timeout, **kwargs)

    def disable(self, obj):
        if hasattr(obj, 'url') and obj.url == None:
            obj.disabled = True
            return obj

    async def on_timeout(self):
        try:
            await self.disable_all()
        except discord.NotFound or discord.HTTPException:
            pass

    async def disable_all(self):
        message = await self.view_inter.original_response()
        if not message:
            return

        view = View.from_message(message)
        if not view:
            return

        [self.disable(child) for child in view.children]
        await message.edit(view=view)

    async def interaction_check(self, interaction) -> bool:
        if not self.owned:
            return True

        if interaction.user.id != self.view_inter.user.id:
            await interaction.response.send_message(f'This is not your menu!! Run {f"`/{self.view_inter.command.name}`" or "the command"} to open your own.', ephemeral=True)
            return False
        return True
