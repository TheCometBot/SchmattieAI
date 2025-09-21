import discord
from discord.ext import commands
import os
from flask import Flask, redirect, urlfor
import threading
import time
import aiohttp
import uuid
from urllib.parse import quote

BOT_TOKEN = os.getenv("BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="§", intents=intents)

async def generate_image(prompt: str):
    url = "https://image.pollinations.ai/prompt/" + quote(prompt)
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                name = f"image_{uuid.uuid4()}.png"
                path = "../generated_images/" + name
                with open(path, 'wb') as f:
                    f.write(await resp.read())
                return path
            else:
                return None

@bot.slash_command(name="draw", description="Erstelle ein Bild mit der AI")
async def ai_draw(ctx, prompt: str):
    await ctx.defer()
    bot_message_obj = await ctx.respond("Die AI erstellt dein Bild... ⏳")
    start_time = time.time()
    image_path = await generate_image(prompt)
    if image_path:
        end_time = time.time()
        print(f"Image generated in {end_time - start_time} seconds.")
        file = discord.File(image_path, filename="generated_image.png")
        embed = discord.Embed(
            title="🖼️ Generiertes Bild",
            description=f"Prompt: {prompt[:800]}",
            color=discord.Color.blue()
        )
        embed.set_image(url="attachment://generated_image.png")
        embed.set_footer(text="Bild generiert von Pollinations AI in ~{:.2f} Sekunden".format(end_time - start_time))
        await bot_message_obj.edit(content=None, embed=embed, file=file)
    else:
        await bot_message_obj.edit(content="Fehler beim Erstellen des Bildes. Bitte versuche es später erneut.")

# Flask App
app = Flask(__name__)

def _health():
    return "Der Bot ist online!"

@app.route('/')
def home():
    return redirect(urlfor("health"))

@app.route('/health/')
def health():
    return _health()

# Funktion um den Bot in einem eigenen Thread zu starten
def run_discord_bot():
    bot.run(BOT_TOKEN)

if __name__ == "__main__":
    # Discord-Bot im Hintergrund starten
    discord_thread = threading.Thread(target=run_discord_bot)
    discord_thread.start()

    # Flask im Main-Thread starten
    app.run(host="0.0.0.0", port=os.getenv("PORT", 10000))
