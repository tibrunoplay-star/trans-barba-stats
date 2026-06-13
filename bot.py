import discord
import json
import re
from collections import defaultdict
from discord.ext import commands

TOKEN = "COLOCA_AQUI_O_TOKEN"

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "data.json"

def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf8") as f:
        json.dump(data, f)

@bot.event
async def on_ready():
    print(f"Ligado como {bot.user}")

@bot.event
async def on_message(message):

    if message.author.bot:

        texto = message.content

        linhas = texto.split("\n")

        if len(linhas) > 0:

            motorista = linhas[0].strip()

            km_match = re.search(r"(\d[\d ]*) km", texto)

            if km_match:

                km = int(km_match.group(1).replace(" ", ""))

                data = load_data()

                data[motorista] = data.get(motorista, 0) + km

                save_data(data)

    await bot.process_commands(message)

@bot.command()
async def ranking(ctx):

    data = load_data()

    ranking = sorted(
        data.items(),
        key=lambda x: x[1],
        reverse=True
    )

    texto = "🏆 Ranking Trans Barba\n\n"

    for i, (nome, km) in enumerate(ranking[:10], start=1):
        texto += f"{i}. {nome} - {km:,} km\n"

    await ctx.send(texto)

bot.run(TOKEN)
