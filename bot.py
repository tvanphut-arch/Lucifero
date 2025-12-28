import os
import discord
from discord import app_commands
from discord.ext import tasks
from flask import Flask
from threading import Thread

# --- GIỮ ONLINE 24/7 ---
app = Flask('')
@app.route('/')
def home():
    return "Lucifero Bot is Live!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- CẤU TRÚC LUCIFERO BOT ---
class LuciferoBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.target_channel_id = None
        self.target_emoji = None

    async def setup_hook(self):
        await self.tree.sync()
        print("Lucifero: Đã đồng bộ các lệnh Slash!")

    async def on_ready(self):
        print(f'Lucifero đã sẵn sàng: {self.user}')
        if not self.send_emoji_task.is_running():
            self.send_emoji_task.start()

    @tasks.loop(minutes=5)
    async def send_emoji_task(self):
        if self.target_channel_id and self.target_emoji:
            channel = self.get_channel(self.target_channel_id)
            if channel:
                try:
                    await channel.send(self.target_emoji)
                except: pass

bot = LuciferoBot()

# --- CÁC LỆNH SLASH CHO ADMIN ---

# 1. Lệnh bắt đầu gửi emoji
@bot.tree.command(name="set_auto", description="Cài đặt gửi emoji tự động mỗi 5 phút (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def set_auto(interaction: discord.Interaction, channel_id: str, emoji: str):
    try:
        bot.target_channel_id = int(channel_id)
        bot.target_emoji = emoji
        if not bot.send_emoji_task.is_running():
            bot.send_emoji_task.start()
        await interaction.response.send_message(f"✅ **Lucifero**: Đã bắt đầu gửi {emoji} vào <#{channel_id}>.")
    except:
        await interaction.response.send_message("❌ Kiểm tra lại ID kênh.")

# 2. Lệnh DỪNG gửi emoji (MỚI THÊM)
@bot.tree.command(name="stop_auto", description="Dừng gửi emoji tự động (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def stop_auto(interaction: discord.Interaction):
    bot.target_channel_id = None
    bot.target_emoji = None
    if bot.send_emoji_task.is_running():
        bot.send_emoji_task.stop() # Dừng vòng lặp
    await interaction.response.send_message("🛑 **Lucifero**: Đã dừng hoàn toàn việc gửi emoji tự động.")

# Xử lý lỗi quyền Admin cho cả 2 lệnh
@set_auto.error
@stop_auto.error
async def admin_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bạn cần quyền Administrator để dùng lệnh này!", ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('TOKEN'))
