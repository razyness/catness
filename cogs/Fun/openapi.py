import discord
import openai
import asyncio
import requests
import io

from discord import ui
from sakana import OPENAI
from discord import app_commands
from discord.ext import commands
from typing import Literal


async def imagen(prompt, size):
    # Use the OpenAI API to generate an image
    response = openai.Image.create(
        prompt=prompt,
        n=1,
        size=size,
        model="image-alpha-001"
    )
    # Extract the generated image from the response
    image_url = response["data"][0]["url"]
    response = requests.get(image_url)
    image_data = response.content
    image_stream = io.BytesIO(image_data)
    return image_stream


# class Regen(discord.ui.View):
#     def __init__(self, prompt, size):
#         super().__init__()
#         self.value = None
#         self.prompt = prompt
#         self.size = size
# 
#     @ui.button(label="Regenerate", style=discord.ButtonStyle.blurple, emoji="<:rotateright:1054392052344950834>")
#     async def regen(self, interaction: discord.Integration, button: ui.Button):
#         try:
#             print("hi i was clicked")
# 
#             image_stream = await imagen(self.prompt, self.size)
# 
#             file = discord.File(image_stream, filename=f'{self.prompt}.png')
# 
#             await interaction.remove_attachments(interaction.attachments)
#             await interaction.add_files(file)
#         except Exception as e:
#             print(e)
# 
#     async def interaction_check(self, interaction) -> bool:
#         if self.user:
#             if interaction.user.id != self.author:
#                 await interaction.response.send_message('This is not your menu, run </openai imagen:1054381044826112002> to open your own.', ephemeral=True)
#                 return False
#         return True


class OpenAI(commands.Cog):
    def __init__(self, ce):
        super().__init__()
        self.ce = ce

    openai.api_key = OPENAI

    group = app_commands.Group(
        name="openai", description="Utilize the OpenAI's api")

    @group.command(name="imagen", description="Generate images")
    @app_commands.describe(prompt="The image prompt - no default",
                           size="The image resolution - default is 512x")
    async def imagen(self, interaction, prompt: str, size: Literal['128x128', '512x512', '1024x1024'] = "512x512"):
        await interaction.response.defer(thinking=True)

        image_stream = await imagen(prompt, size)

        file = discord.File(image_stream, filename=f'{prompt}.png')

        embed = discord.Embed(
            description=f"Prompt: `{prompt}`, Size: `{size}`")
        embed.set_author(name="Text to Image")
        try:
            await interaction.followup.send(embed=embed, file=file)
        except Exception as e:
            await interaction.followup.send(e)

    @group.command(name="completion", description="Text completion and code generation from a prompt")
    @app_commands.describe(
        prompt="The text generation prompt - no default",
        temperature="Sampling temperature. Higher values means the model will take more risks. default is 0.5")
    async def completion(self, interaction, prompt: str, temperature: float = 0.5):
        await interaction.response.defer(thinking=True)

        if temperature >= 1.0:
            temperature:int = 1

        elif temperature <= 0.0:
            temperature:int = 0

        temperature = round(temperature, 1)

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=temperature,
            max_tokens=2048
        )

        api_json = response["choices"][0]["text"]

        embed = discord.Embed()
        embed.set_author(name=f"Text Completion  ·  {temperature}/1")
        embed.description = f"**{prompt}** {api_json}"
        await interaction.followup.send(embed=embed)

    @group.command(name="edit", description="Creates a new edit for the provided input, instruction, and parameters")
    @app_commands.describe(prompt="The text the AI will work with",
                           instructions="What the AI should do with the prompt",
                           temperature="Sampling temperature. Higher values means the model will take more risks. default is 0.5")
    async def edit(self, interaction, prompt: str, instructions: str, temperature: float = 0.5):
        await interaction.response.defer(thinking=True)

        if temperature >= 1.0:
            temperature:int = 1

        elif temperature == 0.0:
            temperature:int = 0

        response = openai.Edit.create(
            model="text-davinci-edit-001",
            input=prompt,
            instruction=instructions,
            temperature=temperature
        )

        api_json = response["choices"][0]["text"]

        embed = discord.Embed()
        embed.set_author(name="Text Edit")
        embed.description = f"**{prompt}**\n*{instructions}*{api_json}"
        await interaction.followup.send(embed=embed)


async def setup(ce):
    await ce.add_cog(OpenAI(ce))
