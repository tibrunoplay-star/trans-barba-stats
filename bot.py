import discord
from discord.ext import commands
import psycopg
import os
import re

TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = ${{Postgres.DATABASE_URL}}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

conn = psycopg.connect(DATABASE_URL)

with conn.cursor() as cur:
    cur.execute("""
        CREATE TABLE IF NOT EXISTS ranking_semanal (
            motorista TEXT PRIMARY KEY,
            km BIGINT NOT NULL DEFAULT 0
        )
    """)
    conn.commit()


@bot.event
async def on_ready():
    print(f"Bot ligado: {bot.user}")
