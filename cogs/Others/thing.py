import asyncio
import discord
import aiosqlite
import sqlite3
import random

from discord.ext import commands
from discord import app_commands
from discord import ui

entries = {"response1": [],
	   	   "response2": [],
		   "response3": [],
		   "response4": []}

create_table_query = """
CREATE TABLE questions (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	question TEXT NOT NULL,
	option1 TEXT NOT NULL,
	option2 TEXT NOT NULL,
	option3 TEXT NOT NULL,
	option4 TEXT NOT NULL,
	answer INTEGER NOT NULL
);
"""

sample_questions = [
	{
		"question": "What is the capital of France?",
		"options": ["Paris", "London", "Berlin", "Madrid"],
		"answer": 0
	},
	{
		"question": "What is the highest mountain in the world?",
		"options": ["Mount Everest", "Mount Kilimanjaro", "Mount Fuji", "Mount Aconcagua"],
		"answer": 0
	},
	{
		"question": "What is the largest mammal in the world?",
		"options": ["Blue Whale", "Elephant", "Giraffe", "Hippopotamus"],
		"answer": 0
	}
]

answers = []

class QuizEngine():
	def __init__(self, ce):
		self.ce = ce
		self.value = None
		self.correct_answer = None

		self.conn = sqlite3.connect('data/questions.db')
		self.cur = self.conn.cursor()

		# Create the table if it doesn't exist
		self.cur.execute(create_table_query)
		self.conn.commit()
		print("🟦 profiles.db connected")

	async def disable_all(self, msg):
		for i in self.children:
			i.disabled = True
		await msg.edit(view=self)

	async def get_random_question():
		async with aiosqlite.connect('quiz.db') as db:
			cursor = await db.execute('SELECT * FROM questions ORDER BY RANDOM() LIMIT 1')
			question = await cursor.fetchone()
			return question

	async def start(self):
		question = await self.get_random_question()
		global answers
		for i in question:
			if "option" in i:
				answers.append(question[i])
		answers = random.shuffle(answers)

		embed = discord.Embed(title=question[1], description="You have 20 seconds to make your guesses!")
		return embed

	@ui.button(label=answers[0], style=discord.ButtonStyle.gray)
	async def button1(self, interaction, button):
		await interaction.response.defer()
		entries["response1"].append(interaction.user.id)

	@ui.button(label=answers[1], style=discord.ButtonStyle.gray)
	async def button1(self, interaction, button):
		await interaction.response.defer()
		entries["response2"].append(interaction.user.id)

	@ui.button(label=answers[2], style=discord.ButtonStyle.gray)
	async def button1(self, interaction, button):
		await interaction.response.defer()
		entries["response3"].append(interaction.user.id)

	@ui.button(label=answers[4], style=discord.ButtonStyle.gray)
	async def button1(self, interaction, button):
		await interaction.response.defer()
		entries["response4"].append(interaction.user.id)


	async def structure(self):
		pass

	async def result(self):
		await self.disable_all(self.response)
		winners = []
		global entries
		for i in entries:
			if entries[i] in  self.correct_answer:
				winners.append(i)
		if winners == []:
			return "Time's up! Nobody was able to guess!"
		
		elif entries == {}:
			return "Nobody entered! The quiz timed out.."
		
		formatted = []
		for i in winners:
			formatted.append(f"<@{i}>")
		result = ', '.join(formatted)
		entries = {"response1": [],
	   	   	       "response2": [],
		   	       "response3": [],
		   	       "response4": []}
		return f"{result} guessed the right answer! It was {self.correct_answer}"
		

class Quiz(commands.Cog):
	def __init__(self, ce: commands.Bot):
		self.ce = ce

	@app_commands.command(name="quiz", description="Start a quiz! wip. You have 20 seconds to guess the correct answer out of 4 possibilities")
	async def quiz(self, interaction):
		embed = await QuizEngine.start()
		view = QuizEngine(self.ce)
		await interaction.response.send_message(embed=embed, view=view)
		view.response = await interaction.original_response()
		asyncio.sleep(20)
		result = await QuizEngine.result()
		await interaction.followup.send(result)


async def setup(ce: commands.Bot):
	await ce.add_cog(Quiz(ce))
