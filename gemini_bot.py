import discord
from discord.ext import commands
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread

# 1. Renderの「ポート未検出」エラーを防ぐための設定
app = Flask('')
@app.route('/')
def home():
    return "Gemini Bot is running!"

def run():
    # Renderの無料枠で必要な10000番ポートを開放します
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Gemini AIの設定
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# 3. Discord Botの設定
intents = discord.Intents.default()
intents.message_content = True  # メッセージを読み取る設定
# 【修正済み】タイポを直しました
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    # Bot自身のメッセージには反応しない
    if message.author == bot.user:
        return

    # メンションされた時だけ反応
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                # メンション部分を除去してAIに送信
                clean_text = message.content.replace(f'<@{bot.user.id}>', '').strip()
                response = model.generate_content(clean_text)
                await message.reply(response.text)
            except Exception as e:
                await message.reply(f"エラーですね：{e}")

# 4. 実行！
if __name__ == "__main__":
    keep_alive()  # ウェブサーバーを起動
    # Renderの環境変数からトークンを読み込みます
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
