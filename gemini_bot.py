import discord
from discord.ext import commands
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread
import logging

# ログの設定
logging.basicConfig(level=logging.INFO)

# 1. Renderの「Timed Out」を完全に回避する設定
app = Flask('')
@app.route('/')
def home():
    return "Gemini 3 Flash お手伝いさんは元気に稼働中！"

def run():
    # Renderの無料枠で必要な10000番ポートを開放します
    port = int(os.environ.get("PORT", 10000))
    logging.info(f"Binding to port {port}...")
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Gemini 3 Flash の設定
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# モデル名を Gemini 3 Flash に変更しました
model = genai.GenerativeModel("gemini-2.0-flash")

# 3. Discord Botの設定
intents = discord.Intents.default()
intents.message_content = True 
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')
    print("Gemini 3 Flash 準備完了！")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # メンションされた時だけお返事します
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                # メンション部分を除去してプロンプトを作成
                prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
                if not prompt:
                    prompt = "こんにちは！"
                
                # Gemini 3 Flash で回答を生成
                response = model.generate_content(prompt)
                await message.reply(response.text)
            except Exception as e:
                logging.error(f"Error: {e}")
                # 404エラーなどが出た場合のお返事
                await message.reply(f"ごめん、ちょっと頭が痛くて（エラー：{e}）")

# 4. 実行開始
if __name__ == "__main__":
    keep_alive() # 先にウェブサーバーを起動してRenderのタイムアウトを防ぎます
    # Renderの環境変数からトークンを読み込みます
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
