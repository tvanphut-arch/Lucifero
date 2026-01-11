import os
import discord
from discord import app_commands
from discord.ext import tasks
from flask import Flask
from threading import Thread
import random

# --- 1. GIỮ ONLINE 24/7 ---
app = Flask('')

@app.route('/')
def home():
    return "Lucifero is Online!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. CẤU TRÚC BOT LUCIFERO ---
class LuciferoBot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.target_channel_id = None
        self.target_emoji = None

    async def setup_hook(self):
        # Đồng bộ lệnh Slash ngay khi khởi động để tránh lỗi không phản hồi
        await self.tree.sync()
        print("✅ Lucifero: Đã đồng bộ lệnh Slash thành công!")

    async def on_ready(self):
        print(f'✅ Đã đăng nhập: {self.user}')
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

# --- 3. LỆNH SLASH ĐẸP TRAI (Thang điểm 1-100) ---
@bot.tree.command(name="handsomerate", description="Lucifero chấm điểm đẹp trai ngẫu nhiên 1-100")
async def handsomerate(interaction: discord.Interaction):
    # Tỉ lệ 1% nhận được điểm 101 (Vượt khung)
    if random.random() < 0.01:
        score = 101
    else:
        score = random.randint(1, 100)
    
    # Xác định lời phán dựa trên thang điểm 100
    if score > 100:
        comment, color = "⚠️ LỖI HỆ THỐNG: Vẻ đẹp vượt qua mọi giới hạn của quỷ dữ! 👑", 0xFFFFFF # Trắng sáng
    elif score >= 90:
        comment, color = "Real chad. ✨", 0xFFD700 # Vàng Gold
    elif score >= 70:
        comment, color = "Cực phẩm! Khí chất ngời ngời, vạn người mê. 😎", 0x2ECC71 # Xanh lá
    elif score >= 50:
        comment, color = "Khá khen, nhan sắc này cũng có chút gọi là ưa nhìn. 👍", 0x3498DB # Xanh dương
    elif score >= 30:
        comment, color = "Bth vl. 😐", 0x95A5A6 # Xám
    else:
        comment, color = "Địt mẹ mày , xấu thế... 💀", 0xE74C3C # Đỏ

    embed = discord.Embed(
        title="⚔️ Phán Quyết Của Lucifero",
        description=f"Nhan sắc của {interaction.user.mention} được đánh giá là:",
        color=color
    )
    embed.add_field(name="Hệ số nhan sắc", value=f"**{score}/100**", inline=True)
    embed.add_field(name="Lời phán", value=f"*{comment}*", inline=False)
    
    # Hiển thị ảnh đại diện người dùng để tăng tính tương tác
    if interaction.user.display_avatar:
        embed.set_thumbnail(url=interaction.user.display_avatar.url)

    embed.set_footer(text="Lucifero Beauty Rating System • 2026")

    # Phản hồi lệnh Slash
    await interaction.response.send_message(embed=embed)

# --- 4. LỆNH ADMIN (set_auto/stop_auto) ---
@bot.tree.command(name="set_auto", description="Bật gửi emoji tự động (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def set_auto(interaction: discord.Interaction, channel_id: str, emoji: str):
    try:
        bot.target_channel_id = int(channel_id)
        bot.target_emoji = emoji
        if not bot.send_emoji_task.is_running():
            bot.send_emoji_task.start()
        await interaction.response.send_message(f"✅ **Lucifero**: Đã bật tự động gửi {emoji} tại <#{channel_id}>.")
    except:
        await interaction.response.send_message("❌ ID kênh không hợp lệ hoặc thiếu quyền.", ephemeral=True)

@bot.tree.command(name="stop_auto", description="Tắt gửi emoji tự động (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def stop_auto(interaction: discord.Interaction):
    bot.target_channel_id = None
    bot.target_emoji = None
    if bot.send_emoji_task.is_running():
        bot.send_emoji_task.stop()
    await interaction.response.send_message("🛑 **Lucifero**: Đã dừng việc gửi emoji tự động.")

# --- 5. CHẠY BOT ---
if __name__ == "__main__":
    keep_alive()
    token = os.getenv('TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ Lỗi: Thiếu TOKEN trong Environment Variables!")
