import os
import discord
from discord import app_commands
from discord.ext import tasks
from flask import Flask
from threading import Thread

# --- GIỮ ONLINE 24/7 (Cung cấp cổng cho Render) ---
app = Flask('')
@app.route('/')
def home(): return "Bot Emoji is Live!"

def run(): app.run(host='0.0.0.0', port=10000)
def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CẤU TRÚC BOT ---
class MyBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.target_channel_id = None
        self.target_emoji = None

    async def setup_hook(self):
        await self.tree.sync()
        print("Đã đồng bộ lệnh Slash!")

    async def on_ready(self):
        print(f'Đã đăng nhập: {self.user}')
        if not self.send_emoji_task.is_running():
            self.send_emoji_task.start()

    @tasks.loop(minutes=5)
    async def send_emoji_task(self):
        if self.target_channel_id and self.target_emoji:
            channel = self.get_channel(self.target_channel_id)
            if channel:
                try:
                    await channel.send(self.target_emoji)
                except Exception as e:
                    print(f"Lỗi gửi emoji: {e}")

bot = MyBot()

@bot.tree.command(name="set_auto", description="Cài đặt gửi emoji tự động")
@app_commands.describe(channel_id="ID kênh", emoji="Emoji hoặc ID Emoji")
async def set_auto(interaction: discord.Interaction, channel_id: str, emoji: str):
    try:
        bot.target_channel_id = int(channel_id)
        bot.target_emoji = emoji
        await interaction.response.send_message(f"✅ Đã cài đặt gửi {emoji} vào kênh <#{channel_id}> mỗi 5 phút.")
    except:
        await interaction.response.send_message("❌ Có lỗi xảy ra. Hãy kiểm tra lại ID kênh.")

if __name__ == "__main__":
    keep_alive() # Quan trọng để Render không tắt bot
    bot.run(os.getenv('TOKEN'))
