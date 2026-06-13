import discord
from discord.ext import commands
import os

import os

TOKEN = os.getenv("DISCORD_TOKEN")
print("TOKEN =", TOKEN)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot ligado: {bot.user}")

@bot.event
async def on_message(message):

    print("-------------")
    print("AUTOR:", message.author)
    print("CONTEUDO:")
    print(message.content)

    if message.embeds:
        print("EMBEDS:")
        for embed in message.embeds:
            print(embed.to_dict())

    await bot.process_commands(message)

bot.run(TOKEN)
