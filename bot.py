import os
import discord
from discord import app_commands
from discord.ext import tasks
from flask import Flask
from threading import Thread

# --- GIỮ ONLINE 24/7 CHO LUCIFERO ---
app = Flask('')
@app.route('/')
def home():
    return "Lucifero Bot is Running!"

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
        
        # Biến lưu trữ cấu hình gửi emoji
        self.target_channel_id = None
        self.target_emoji = None

    async def setup_hook(self):
        await self.tree.sync()
        print("Lucifero: Đã đồng bộ lệnh Slash!")

    async def on_ready(self):
        print(f'Lucifero đã đăng nhập: {self.user}')
        if not self.send_emoji_task.is_running():
            self.send_emoji_task.start()

    # Vòng lặp gửi Emoji mỗi 5 phút
    @tasks.loop(minutes=5)
    async def send_emoji_task(self):
        if self.target_channel_id and self.target_emoji:
            channel = self.get_channel(self.target_channel_id)
            if channel:
                try:
                    await channel.send(self.target_emoji)
                except Exception as e:
                    print(f"Lucifero lỗi gửi emoji: {e}")

bot = LuciferoBot()

# --- LỆNH SLASH (CHỈ ADMIN) ---

@bot.tree.command(name="set_auto", description="Cài đặt gửi emoji tự động mỗi 5 phút (Chỉ Admin)")
@app_commands.describe(channel_id="ID kênh muốn gửi", emoji="Mã Emoji (Định dạng <:tên:ID>)")
@app_commands.checks.has_permissions(administrator=True) # Chỉ Admin mới được dùng
async def set_auto(interaction: discord.Interaction, channel_id: str, emoji: str):
    try:
        bot.target_channel_id = int(channel_id)
        bot.target_emoji = emoji
        await interaction.response.send_message(f"✅ **Lucifero**: Đã cài đặt gửi {emoji} vào <#{channel_id}> mỗi 5 phút.")
    except Exception as e:
        await interaction.response.send_message(f"❌ Lỗi: Vui lòng kiểm tra lại ID kênh.")

# Xử lý lỗi khi người dùng không phải Admin
@set_auto.error
async def set_auto_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bạn cần quyền `Administrator` để sử dụng lệnh này của Lucifero!", ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('TOKEN'))
