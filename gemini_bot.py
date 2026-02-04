import discord
from discord.ext import commands
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread
import logging

logging.basicConfig(level=logging.INFO)

# 1. Renderのタイムアウト対策
app = Flask('')
@app.route('/')
def home(): return "Online!"

def run():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

def keep_alive():
    Thread(target=run).start()

# 2. Geminiの設定：動くモデルを自動で探します
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_working_model():
    # 2026年の無料枠で最も可能性が高い順に試します
    candidate_models = [
        "gemini-1.5-flash", 
        "gemini-1.5-flash-8b", 
        "gemini-2.0-flash",
        "gemini-1.5-pro"
    ]
    for m_name in candidate_models:
        try:
            m = genai.GenerativeModel(m_name)
            # 試しに一言喋らせて、404や429が出ないかチェック
            m.generate_content("test") 
            logging.info(f"Successfully picked model: {m_name}")
            return m
        except Exception as e:
            logging.warning(f"Model {m_name} failed: {e}")
    return genai.GenerativeModel("gemini-1.5-flash") # 最終手段

model = None

# 3. Discord Botの設定
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    global model
    model = get_working_model()
    logging.info(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.author == bot.user: return
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                clean_text = message.content.replace(f'<@{bot.user.id}>', '').strip()
                # モデルが準備できていない場合はその場で探し直す
                active_model = model or get_working_model()
                response = active_model.generate_content(clean_text or "こんにちは")
                await message.reply(response.text)
            except Exception as e:
                await message.reply(f"ごめん、まだ頭が痛いみたい…（エラー：{e}）")

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
