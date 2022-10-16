# hello

import logging.handlers
import discord

TOKEN = 'MTAyOTg2NDYyMTA0NzMwNDIwMw.GuDeWV.4B9qma-1fk0Utg9PCeYuT8g6vAgqnYLvfrTJ90'

prefix = '.'

logger = logging.getLogger('discord')

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)

intents = discord.Intents.default()
