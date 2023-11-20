import discord
import zipfile

from datetime import datetime
from discord.ext import commands
from discord import app_commands

from utils import ui, confirm
from utils.data import icons

from io import BytesIO
from PIL import Image

class DownloadEmotes(ui.View):
    def __init__(self, bot, view_inter, guild, owned=False, timeout=180, **kwargs):
        super().__init__(view_inter, owned, timeout, **kwargs)
        self.bot = bot
        self.view_inter = view_inter
        self.guild: discord.Guild = guild
    
    @discord.ui.button(label="Download", emoji=icons.download, style=discord.ButtonStyle.blurple)
    async def download(self, inter:discord.Interaction, button):
        await inter.response.send_message(f"Downloading... (0/{len(self.guild.emojis)})", ephemeral=True)
        zip_file = BytesIO()

        with zipfile.ZipFile(zip_file, 'w') as zip_obj:
            i = 0
            for emoji in inter.guild.emojis:
                url = emoji.url
                async with self.bot.web_client.get(url) as response:
                    if response.status == 200:
                        image_data = await response.read()
                        image = Image.open(BytesIO(image_data))
                        image_filename = f"{emoji.name}.png"
                        image_byte_io = BytesIO()
                        image.save(image_byte_io, format='PNG')
                        zip_obj.writestr(
                            image_filename, image_byte_io.getvalue())
                        i += 1
                        message = f"Downloading... ({i}/{len(self.guild.emojis)})"
                        await inter.edit_original_response(content=message)
                    else:
                        await inter.followup.send(f"Failed to download {emoji.name}", ephemeral=True)
                        return
        
        zip_file.seek(0)
        await inter.followup.send(file=discord.File(zip_file, f'{self.guild.id}_emotes.zip'), ephemeral=True)

class ServerView(ui.View):
    def __init__(self, bot, guild, members, roles, emojis, view_inter, owned=False, timeout=180, **kwargs):
        super().__init__(view_inter, owned, timeout, **kwargs)
        self.bot = bot
        self.view_inter = view_inter
        self.guild = guild
        self.members = members
        self.roles = roles
        self.emojis = emojis

    def generate_embeds(self, title, footer, data, new_line=False):
        embeds = []
        current_embed = discord.Embed(description="")
        
        for i in data:
            if len(current_embed.description) + len(i) > 3000:
                embeds.append(current_embed)
                current_embed = discord.Embed(description="")
            
            current_embed.description += f"{i}\n" if new_line else f"{i} "
        
        embeds.append(current_embed)
        embeds[0].title = title
        embeds[-1].set_footer(text=footer)
        
        return embeds


    @discord.ui.button(label="Show all members", style=discord.ButtonStyle.blurple)
    async def members_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.guild.member_count > 1000:
            conf = await confirm.confirmation(interaction, "Are you sure?", "May cause spam on large servers")
            if not conf:
                return

        data = ['## Users:\n']
        for i in self.members["users"]:
            data.append(i.mention)
        data.append('\n## Bots:\n')
        for i in self.members["bots"]:
            data.append(i.mention)

        embeds = self.generate_embeds(title=f"Members in {self.guild.name}",
                                      footer=f"Showing {len(data) - 2}/{len(self.guild.members)} - Some members may be missing due to discord limitations",
                                      data=data)
        if self.guild.member_count > 1000 and conf:
            await interaction.followup.send(embed=embeds[0], ephemeral=True)
        else:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        for i in embeds[1:]:
            await interaction.followup.send(embed=i, ephemeral=True)
    
    @discord.ui.button(label="Show all emojis", style=discord.ButtonStyle.blurple)
    async def emojis_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        data = ['## Static:\n']
        for i in self.emojis["static"]:
            data.append(str(i))
        data.append('\n## Animated:\n')
        for i in self.emojis["animated"]:
            data.append(str(i))

        embeds = self.generate_embeds(title=f"Emojis in {self.guild.name}",
                                      footer=f"Total: {len(self.guild.emojis)}",
                                      data=data)

        view = DownloadEmotes(self.bot, interaction, self.guild)

        if len(embeds) == 1:
            await interaction.response.send_message(embed=embeds[0], view=view, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embeds[0], ephemeral=True)
            for i in embeds[1:]:
                if i == embeds[-1]:
                    await interaction.followup.send(embed=i, view=view, ephemeral=True)
                else:
                    await interaction.followup.send(embed=i, ephemeral=True)


    @discord.ui.button(label="Show all roles", style=discord.ButtonStyle.blurple)
    async def roles_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        data = list()        
        for i in self.roles["normal"]:
            data.append(i.mention)
        data.append('## Normal:')
        for i in self.roles["mod"]:
            data.append(i.mention)
        data.append('## Mods:')

        data.reverse()
        embeds = self.generate_embeds(title=f"Roles in {self.guild.name}",
                                      footer=f"Total: {len(self.guild.roles)}",
                                      data=data,
                                      new_line=True)
        await interaction.response.send_message(embed=embeds[0], ephemeral=True)
        for i in embeds[1:]:
            await interaction.followup.send(embed=i, ephemeral=True)


class ServerInfo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server", description="Get information about the server")
    async def serverinfo(self, inter: discord.Interaction, ephemeral: bool = True):
        guild = inter.guild

        members = {"users": [], "bots": []}
        for m in guild.members:
            if m.bot:
                members["bots"].append(m)
            else:
                members["users"].append(m)

        emojis = {"static": [], "animated": []}
        for e in guild.emojis:
            if e.animated:
                emojis["animated"].append(e)
            else:
                emojis["static"].append(e)

        roles = {"normal": [], "booster": None, "mod": [], "bot": []}
        for r in guild.roles:
            if r.is_default():
                continue
            if r.is_premium_subscriber():
                roles["booster"] = r
            elif r.permissions.administrator or (r.permissions.manage_guild and r.permissions.manage_roles and r.permissions.manage_channels and r.permissions.manage_messages):
                roles["mod"].append(r)
            elif not r.is_bot_managed() or not r.is_integration():
                roles["normal"].append(r)

        created = f'<t:{int(datetime.timestamp(guild.created_at))}:D>'
        channels = (len(guild.text_channels), len(
            guild.voice_channels), len(guild.categories))
        rules = guild.rules_channel.mention
        boost = (guild.premium_tier, guild.premium_subscription_count)

        description = ""
        if guild.description:
            description += f"\nDescription: {guild.description}"
        if rules:
            description += f"Rules channel: {rules}"
        if roles["booster"]:
            description += f"Booster role: {roles['booster'].mention}"

        embed = discord.Embed(
            title=f"Server Info for {guild.name}", description=f"Rules channel: {rules}" if rules else None)
        embed.add_field(name="Owner", value=guild.owner.mention)
        embed.add_field(
            name="Members", value=f"`{len(members['users'])}` users\n`{len(members['bots'])}` bots")
        embed.add_field(name="Created", value=created)
        embed.add_field(
            name="Channels", value=f"`{channels[2]}` categories\n├ `{channels[0]}` text\n└ `{channels[1]}` voice")
        embed.add_field(
            name="Roles", value=f"`{len(guild.roles) - 1}` roles:\n├ `{len(roles['normal'])}` normal\n└ `{len(roles['mod'])}` mods")
        embed.add_field(
            name="Emojis", value=f"`{len(guild.emojis)}` total\n├ `{len(emojis['static'])}` static\n└ `{len(emojis['animated'])}` animated")
        if boost[0]:
            embed.add_field(
                name="Boosts", value=f"Tier `{boost[0]}` with `{boost[1]}` boosts")
        embed.set_footer(text="Click the buttons below for more info")

        view = ServerView(self.bot, guild, members, roles, emojis, inter)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
            view.add_item(discord.ui.Button(row=1, label="Icon",
                          style=discord.ButtonStyle.url, url=guild.icon.url))
        if guild.banner:
            embed.set_image(url=guild.banner.url)
            view.add_item(discord.ui.Button(row=1, label="Banner",
                          style=discord.ButtonStyle.url, url=guild.banner.url))
        if guild.splash:
            view.add_item(discord.ui.Button(row=1, label="Invite splash", style=discord.ButtonStyle.url, url=guild.splash.url))
        if guild.discovery_splash:
            view.add_item(discord.ui.Button(row=1, label="Discovery splash", style=discord.ButtonStyle.url, url=guild.discovery_splash.url))
        await inter.response.send_message(embed=embed, view=view, ephemeral=ephemeral)


async def setup(bot):
    await bot.add_cog(ServerInfo(bot))
