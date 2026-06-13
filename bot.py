import os
import discord
from discord.ext import commands
import psycopg

TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

conn = psycopg.connect(DATABASE_URL)

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking_semanal (
            motorista TEXT PRIMARY KEY,
            km BIGINT NOT NULL DEFAULT 0
        )
    """)
    conn.commit()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot ligado: {bot.user}")
    print("Base de dados ligada com sucesso!")

@bot.command()
async def ranking(ctx):
    await ctx.send("Base de dados OK ✅")

bot.run(TOKEN)
