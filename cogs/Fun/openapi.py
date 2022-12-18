import discord
import openai
import asyncio
import requests
import io

from sakana import OPENAI_API_KEY
from discord import app_commands
from discord.ext import commands
from typing import Literal


class OpenAI(commands.Cog):
    def __init__(self, ce):
        super().__init__()
        self.ce = ce

    openai.api_key = OPENAI_API_KEY

    group = app_commands.Group(
        name="openai", description="Utilize the OpenAI's api")

    @group.command(name="imagen", description="Generate images")
    @app_commands.describe(prompt="The image prompt - no default",
                           size="The image resolution - default is 512x")
    async def imagen(self, interaction, prompt: str, size: Literal['128x128', '512x512', '1024x1024'] = "512x512"):
        await interaction.response.defer(thinking=True)

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

        file = discord.File(image_stream, filename='result.png')

        embed = discord.Embed(
            description=f"Prompt: `{prompt}`, Size: `{size}`")
        embed.set_author(name="Text to Image")
        await interaction.followup.send(embed=embed, file=file)

    @group.command(name="completion", description="Text completion and code generation from a prompt")
    @app_commands.describe(
        prompt="The text generation prompt - no default",
        temperature="Sampling temperature. Higher values means the model will take more risks. default is 0.5"
    )
    async def completion(self, interaction, prompt: str, temperature: float = 0.5):
        await interaction.response.defer(thinking=True)

        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=temperature,
            max_tokens=2048
        )

        api_json = response["choices"][0]["text"]

        embed = discord.Embed(title=prompt)
        embed.set_author(name=f"Text Completion  ·  {temperature}/1")
        embed.description = api_json
        await interaction.followup.send(embed=embed)

    @group.command(name="edit", description="Creates a new edit for the provided input, instruction, and parameters")
    @app_commands.describe(prompt="The text the AI will work with",
                           instructions="What the AI should do with the prompt",
                           temperature="Sampling temperature. Higher values means the model will take more risks. default is 0.5")
    async def edit(self, interaction, prompt: str, instructions: str, temperature: float = 0.5):
        await interaction.response.defer(thinking=True)

        response = openai.Edit.create(
            model="text-davinci-edit-001",
            input=prompt,
            instruction=instructions,
            temperature=temperature
        )

        api_json = response["choices"][0]["text"]

        embed = discord.Embed(title=prompt)
        embed.set_author(name=instructions)
        embed.set_footer(text="Text Edit")
        embed.description = api_json
        await interaction.followup.send(embed=embed)


async def setup(ce):
    await ce.add_cog(OpenAI(ce))
