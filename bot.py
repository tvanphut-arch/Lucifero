import os
import discord
from discord import app_commands
from discord.ext import tasks
from flask import Flask
from threading import Thread
import random

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
                except:
                    pass

bot = LuciferoBot()

# --- CÁC LỆNH SLASH ---

# 1. Lệnh bắt đầu gửi emoji (Admin)
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

# 2. Lệnh DỪNG gửi emoji (Admin)
@bot.tree.command(name="stop_auto", description="Dừng gửi emoji tự động (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def stop_auto(interaction: discord.Interaction):
    bot.target_channel_id = None
    bot.target_emoji = None
    if bot.send_emoji_task.is_running():
        bot.send_emoji_task.stop()
    await interaction.response.send_message("🔴 **Lucifero**: Đã dừng hoàn toàn việc gửi emoji tự động.")

# 3. Lệnh ĐÁNH GIÁ ĐỘ ĐẸP TRAI (Mọi người đều dùng được)
@bot.tree.command(name="handsomerate", description="Lucifero ngẫu nhiên đánh giá độ đẹp trai từ 1 tới 10")
async def danhgia(interaction: discord.Interaction):
    score = random.randint(1, 10)
    
    # Xác định lời phán dựa trên điểm số
    if score >= 9:
        comment = "Cực phẩm! Vẻ đẹp này khiến ta cũng phải kinh ngạc. ✨"
        color = 0xFFD700 # Vàng
    elif score >= 7:
        comment = "Khá khen cho nhan sắc này, rất có khí chất! 😎"
        color = 0x2ECC71 # Xanh lá
    elif score >= 5:
        comment = "Tạm ổn, đủ để ta không thấy khó chịu khi nhìn vào. 👍"
        color = 0x3498DB # Xanh dương
    else:
        comment = "Xấu vl cân nhắc phẩu thuật thẫm mĩ đi cu... 💀"
        color = 0xE74C3C # Đỏ

    embed = discord.Embed(
        title="⚔️ Phán Quyết Của Lucifero",
        description=f"Nhan sắc của {interaction.user.mention} được chấm là:",
        color=color
    )
    embed.add_field(name="Điểm số", value=f"**{score}/10**", inline=True)
    embed.add_field(name="Lời phán", value=f"*{comment}*", inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)
    embed.set_footer(text="Lucifero Beauty Rating System")

    await interaction.response.send_message(embed=embed)

# Xử lý lỗi quyền Admin
@set_auto.error
@stop_auto.error
async def admin_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message("❌ Bạn cần quyền Administrator để dùng lệnh này!", ephemeral=True)

if __name__ == "__main__":
    keep_alive()
    bot.run(os.getenv('TOKEN'))
