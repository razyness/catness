from typing import Optional
import discord

class View(discord.ui.View):
	
	def __init__(self, original_interaction, owned=False, timeout=180, **kwargs):
		self.original_interaction = original_interaction
		self.owned = owned
		super().__init__(timeout=timeout, **kwargs)

	def disable(self, obj):
		if hasattr(obj, 'disabled') and not hasattr(obj, 'url'):
			obj.disabled = True

	async def on_timeout(self):
		await self.disable_all()

	async def disable_all(self):
		[self.disable(i) for i in self.children]
		message = await self.original_interaction.original_response()
		if message:
			await message.edit(view=self)

	async def interaction_check(self, interaction) -> bool:
		if not self.owned:
			return True

		if interaction.user.id != self.original_interaction.user.id:
			await interaction.response.send_message(f'This is not your menu, run {f"`/{self.original_interaction.command.name}`" or "the command"} to open your own.', ephemeral=True)
			return False
		return True
