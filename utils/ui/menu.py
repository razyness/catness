import discord
import uuid

from . import View


class ButtonMenu(View):
	"""
	A class representing a button menu.

	Attributes:
		bot (Bot): The bot instance associated with the menu.
		owned (bool): Indicates if the menu is owned by a user.
		timeout (int): The timeout duration for the menu.
	"""

	def __init__(self, invoke, bot=None, owned=False, timeout=180, **kwargs):
		super().__init__(invoke, owned, timeout, **kwargs)
		self.bot = bot
		self.style_map = {
			'blurple': discord.ButtonStyle.blurple,
			'primary': discord.ButtonStyle.blurple,
			'gray': discord.ButtonStyle.gray,
			'grey': discord.ButtonStyle.gray,
			'secondary': discord.ButtonStyle.gray,
			'green': discord.ButtonStyle.green,
			'success': discord.ButtonStyle.green,
			'red': discord.ButtonStyle.red,
			'danger': discord.ButtonStyle.red,
			'url': discord.ButtonStyle.url,
			'link': discord.ButtonStyle.url,
		}

	def add_button(self, callback, label=None, emoji=None, style=discord.ButtonStyle.gray, url=None, custom_id=None):
		"""
		Adds a button to the menu.

		Args:
			label (str): The label text of the button.
			emoji (str): The emoji associated with the button.
			callback (Callable): The callback function to be executed when the button is clicked.
			custom_id (str, optional): The custom ID of the button. Defaults to None.
		"""

		custom_id = str(uuid.uuid4())
		button = discord.ui.Button(label=label, emoji=emoji, custom_id=custom_id, url=url, style=self.style_map[style])
		button.callback = callback
		self.add_item(button)

	def add_url(self, label=None, url=None, emoji=None):
		"""
		Adds a URL button to the menu.

		Args:
			label (str): The label text of the button.
			url (str): The URL to be opened when the button is clicked.
			emoji (str, optional): The emoji associated with the button. Defaults to None.
		"""
		button = discord.ui.Button(
			label=label, emoji=emoji, style='url', url=url)
		self.add_item(button)
