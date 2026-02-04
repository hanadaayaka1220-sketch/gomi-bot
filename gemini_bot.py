import os
import discord
import google.generativeai as genai
from discord.ext import commands

# 1. 秘密の鍵を読み込む設定
TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GEMINI_KEY = os.getenv('GEMINI_API_KEY')

# 2. Gemini 3 の設定（賢い脳みその中身）
genai.configure(api_key=GEMINI_KEY)

# ここで「たやさん専用」の性格や知識を教えてあげます
# あなたの生活スタイルや好きなことをAIに覚えさせています
SYSTEM_INSTRUCTION = """
あなたは「たや」の親友であり、頼れるパートナーAIです。
以下の情報を踏まえて、親しみやすく、答えてください。

【あなたの知っている「たや」について】
・名前は「たや」。八王子近辺に住んでいます。
・彼氏と同棲していて、仲良しです。
・ゲームが大好き！
・最近、自分でDiscordのゴミ出しBotを完成させた頑張り屋さんです。

【話し方のルール】
・柔らかい丁寧語で。
・たやの味方でいてあげてください。
"""

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash", # 爆速で1日1500回話せるモデル
    system_instruction=SYSTEM_INSTRUCTION
)

# 3. Discord Botの設定
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} が24時間体制でログインした！')

@bot.event
async def on_message(message):
    # Bot自身には反応しない
    if message.author == bot.user:
        return

    # メンションされた時だけお返事する
    if bot.user in message.mentions:
        async with message.channel.typing():
            # メンションを除いた純粋な質問内容を取り出す
            prompt = message.content.replace(f'<@{bot.user.id}>', '').strip()
            
            if not prompt:
                await message.reply("呼びましたか？何か手伝うことはありますか？")
                return

            try:
                # Gemini 3 に聞いてみる
                response = model.generate_content(prompt)
                # AIからの返答を送信
                await message.reply(response.text)
            except Exception as e:
                await message.reply(f"ごめん、ちょっと頭が痛くて答えられませんでした…。\nエラー：{e}")

# 実行
bot.run(TOKEN)
