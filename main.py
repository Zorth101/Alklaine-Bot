import discord
from discord.ext import commands, tasks
from discord import app_commands, ui
import os
from datetime import datetime

# ------------------ Setup Intents ------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# ------------------ Bot ------------------
bot = commands.Bot(command_prefix="!", intents=intents)
ALLOWED_GUILD_ID = 1404353271593701407
LOGO_URL = "https://cdn.discordapp.com/attachments/1447711656129073252/1453088406333816913/file_00000000c3dc71f581032fc60cdf80d8.png"
WELCOME_CHANNEL_ID = 1447966843011862588
VERIFICATION_CHANNEL_ID = 1448363111307546855
VERIFIED_ROLE_NAME = "Alkaline"
LOOKING_ROLE_ID = 1404373417213300826

# ------------------ Message Count ------------------
message_count = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    message_count[message.author.id] = message_count.get(message.author.id, 0) + 1
    await bot.process_commands(message)

# ------------------ Verification Button ------------------
class VerifyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅")
    async def verify(self, interaction: discord.Interaction, button: ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE_NAME)
        if role not in interaction.user.roles:
            try:
                await interaction.user.add_roles(role)
                await interaction.response.send_message("You have been verified!", ephemeral=True)
                button.disabled = True
                self.stop()
            except discord.Forbidden:
                await interaction.response.send_message("I don't have permission to give you the role.", ephemeral=True)
        else:
            await interaction.response.send_message("You're already verified.", ephemeral=True)

# ------------------ Welcome Message ------------------
@bot.event
async def on_member_join(member):
    if member.guild.id != ALLOWED_GUILD_ID:
        return
    member_count = member.guild.member_count
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}!",
            description=(
                f"➜ Hey! Look who joined the party, **{member.mention}**!\n\n"
                f"You're member number **{member_count}** ˗ˏˋ ★ ˎˊ˗\n\n"
                "We’re excited to have you here!\n"
                "Feel free to explore the channels, meet new people, and jump into the conversations."
            ),
            color=discord.Color(int("9536E9", 16))
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_image(url=LOGO_URL)  # big logo at bottom
        await channel.send(embed=embed)

# ------------------ /greetings testgreet ------------------
@bot.tree.command(name="greetings", description="Test welcome message", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def testgreet(interaction: discord.Interaction):
    member_count = interaction.guild.member_count
    embed = discord.Embed(
        title=f"Welcome to {interaction.guild.name}!",
        description=(
            f"➜ Hey! Look who joined the party, **{interaction.user.mention}**!\n\n"
            f"You're member number **{member_count}** ˗ˏˋ ★ ˎˊ˗\n\n"
            "We’re excited to have you here!\n"
            "Feel free to explore the channels, meet new people, and jump into the conversations."
        ),
        color=discord.Color(int("9536E9", 16))
    )
    embed.set_thumbnail(url=interaction.user.avatar.url)
    embed.set_image(url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

# ------------------ /rules ------------------
@bot.tree.command(name="rules", description="Shows server rules", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Server Rules",
        description=(
            "1. Be respectful to everyone. No harassment, hate speech, or targeting others.\n"
            "2. Keep content appropriate for teens. No NSFW or disturbing material.\n"
            "3. Do not spam messages, emojis, or pings.\n"
            "4. No advertising without staff approval.\n"
            "5. Use correct channels for topics.\n"
            "6. Do not impersonate staff, bots, or members.\n"
            "7. Follow Discord ToS.\n"
            "8. Do not share private info.\n"
            "9. Listen to staff.\n"
            "10. Be kind and enjoy the server."
        ),
        color=discord.Color(int("9536E9", 16))
    )
    embed.set_image(url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

# ------------------ /userinfo ------------------
@bot.tree.command(name="userinfo", description="Shows user info", guild=discord.Object(id=ALLOWED_GUILD_ID))
@app_commands.describe(user="The user to get info on")
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    roles = ', '.join([r.name for r in user.roles if r.name != "@everyone"])
    count = message_count.get(user.id, 0)
    embed = discord.Embed(
        title=f"{user.display_name}'s Info",
        description=f"Joined: {user.joined_at.strftime('%Y-%m-%d %H:%M:%S')}\nMessages sent: {count}\nRoles: {roles}",
        color=discord.Color(int("9536E9", 16))
    )
    embed.set_thumbnail(url=user.avatar.url)
    embed.set_image(url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

# ------------------ /serverinfo ------------------
@bot.tree.command(name="serverinfo", description="Shows server info", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title=f"{guild.name} Info",
        description=f"Server created: {guild.created_at.strftime('%Y-%m-%d %H:%M:%S')}\nMembers: {guild.member_count}",
        color=discord.Color(int("9536E9", 16))
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else LOGO_URL)
    await interaction.response.send_message(embed=embed)

# ------------------ /verification ------------------
@bot.tree.command(name="verification", description="Posts verification message", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def verification(interaction: discord.Interaction):
    channel = bot.get_channel(VERIFICATION_CHANNEL_ID)
    embed = discord.Embed(
        title="Verification",
        description="Click the button below to verify!",
        color=discord.Color(int("9536E9", 16))
    )
    embed.set_image(url=LOGO_URL)
    view = VerifyView()
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message("Verification message sent!", ephemeral=True)

# ------------------ /lookingtoplay ------------------
looking_cooldowns = {}

class IllPlayView(ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=None)
        self.author_id = author_id
        self.clicked_users = set()

    @ui.button(label="I'll play!", style=discord.ButtonStyle.blurple)
    async def ill_play(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id in self.clicked_users:
            await interaction.response.send_message("You already clicked!", ephemeral=True)
            return
        self.clicked_users.add(interaction.user.id)
        await interaction.response.send_message(f"-{interaction.user.display_name} said they'll play!")

@bot.tree.command(name="lookingtoplay", description="Announce looking to play", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def lookingtoplay(interaction: discord.Interaction):
    now = datetime.utcnow()
    last_used = looking_cooldowns.get(interaction.user.id)
    if last_used and (now - last_used).total_seconds() < 900:
        remaining = 900 - int((now - last_used).total_seconds())
        await interaction.response.send_message(f"Cooldown: {remaining}s remaining", ephemeral=True)
        return
    looking_cooldowns[interaction.user.id] = now
    embed = discord.Embed(
        description=f"@{interaction.user.display_name} is looking for someone to play with! <@&{LOOKING_ROLE_ID}>",
        color=discord.Color(int("9536E9", 16))
    )
    view = IllPlayView(interaction.user.id)
    await interaction.response.send_message(embed=embed, view=view)

# ------------------ Ready Event ------------------
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    try:
        await bot.tree.sync(guild=discord.Object(id=ALLOWED_GUILD_ID))
        print("Slash commands synced!")
    except Exception as e:
        print(e)

# ------------------ Run Bot ------------------
bot.run(os.environ["DISCORD_TOKEN"]) 
