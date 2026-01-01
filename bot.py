iimport os
import discord
from discord import app_commands
from discord.ext import tasks
from flask import Flask
from threading import Thread
import random

# --- 1. GIỮ ONLINE 24/7 (Tránh Render ngủ đông) ---
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
        # Đồng bộ lệnh Slash ngay khi khởi động
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

# --- 3. LỆNH SLASH ĐẸP TRAI (Mọi người dùng được) ---
@bot.tree.command(name="handsomerate", description="Lucifero chấm điểm đẹp trai ngẫu nhiên 1-10")
async def handsomerate(interaction: discord.Interaction):
    # Phải phản hồi ngay lập tức để tránh lỗi "không phản hồi"
    score = random.randint(1, 10)
    
    # Logic phản hồi
    comments = {
        (9, 10): ("Cực phẩm! Vẻ đẹp khiến ta cũng kinh ngạc.", 0xFFD700),
        (7, 8): ("Khá lắm, rất có khí chất!", 0x2ECC71),
        (5, 6): ("Tạm ổn, đủ dùng.", 0x3498DB),
        (1, 4): ("Nên dùng phép thuật che mặt đi thì hơn...", 0xE74C3C)
    }
    
    comment, color = next(v for k, v in comments.items() if k[0] <= score <= k[1])

    embed = discord.Embed(
        title="⚔️ Phán Quyết Của Lucifero",
        description=f"Nhan sắc của {interaction.user.mention}:",
        color=color
    )
    embed.add_field(name="Điểm số", value=f"**{score}/10**")
    embed.add_field(name="Lời phán", value=f"*{comment}*", inline=False)
    embed.set_thumbnail(url=interaction.user.display_avatar.url)

    await interaction.response.send_message(embed=embed)

# --- 4. LỆNH ADMIN (Đã sửa lỗi Emoji ở tên lệnh) ---
@bot.tree.command(name="set_auto", description="Bật gửi emoji tự động (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def set_auto(interaction: discord.Interaction, channel_id: str, emoji: str):
    try:
        bot.target_channel_id = int(channel_id)
        bot.target_emoji = emoji
        if not bot.send_emoji_task.is_running():
            bot.send_emoji_task.start()
        await interaction.response.send_message(f"✅ Đã bật auto gửi {emoji} tại <#{channel_id}>.")
    except:
        await interaction.response.send_message("❌ ID kênh không hợp lệ.", ephemeral=True)

@bot.tree.command(name="stop_auto", description="Tắt gửi emoji tự động (Admin)")
@app_commands.checks.has_permissions(administrator=True)
async def stop_auto(interaction: discord.Interaction):
    bot.target_channel_id = None
    bot.target_emoji = None
    if bot.send_emoji_task.is_running():
        bot.send_emoji_task.stop()
    await interaction.response.send_message("🛑 Đã dừng auto.")

# --- 5. CHẠY BOT ---
if __name__ == "__main__":
    keep_alive()
    token = os.getenv('TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ Thiếu TOKEN trong Environment Variables!")
