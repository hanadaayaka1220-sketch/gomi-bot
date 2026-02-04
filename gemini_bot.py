import discord
from discord.ext import commands
import google.generativeai as genai
import os
from flask import Flask
from threading import Thread
import logging

# ログの設定：何が起きているかRenderのLogs画面で確認しやすくします
logging.basicConfig(level=logging.INFO)

# 1. Renderの「Port scan timeout」を回避するためのウェブサーバー設定
app = Flask('')
@app.route('/')
def home():
    return "お手伝いさんは元気に稼働中！"

def run():
    # Renderが指定するポート（10000番）を確実に開いて「準備OK」と伝えます
    port = int(os.environ.get("PORT", 10000))
    logging.info(f"Starting web server on port {port}...")
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# 2. Gemini AIの設定
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# モデル名を 1.5 Flash に固定（404エラー対策）
model = genai.GenerativeModel("gemini-1.5-flash")

# 3. Discord Botの設定
intents = discord.Intents.default()
intents.message_content = True # これがONならメッセージが読めます
# タイポ修正済み：command_prefix を正しく設定
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user.name}')
    print("お手伝いさん、準備万端やで！")

@bot.event
async def on_message(message):
    # Bot自身の発言には反応しない
    if message.author == bot.user:
        return

    # メンションされた時だけお返事します
    if bot.user.mentioned_in(message):
        async with message.channel.typing():
            try:
                # メンション部分を消してAIに渡す
                prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
                if not prompt:
                    prompt = "こんにちは！"
                
                # Geminiで回答を生成
                response = model.generate_content(prompt)
                await message.reply(response.text)
            except Exception as e:
                logging.error(f"Error: {e}")
                # 万が一エラーが出た時のお返事
                await message.reply(f"ごめん、ちょっと頭が痛くて（エラー：{e}）")

# 4. 実行開始
if __name__ == "__main__":
    keep_alive() # 先にウェブサーバーを起動してRenderを安心させる
    # Renderの環境変数からトークンを読み込みます
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
