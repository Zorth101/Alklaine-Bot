import discord
from discord.ext import commands
from discord import app_commands, ui
import os
from datetime import datetime
from keep_alive import keep_alive

# ------------------ CONFIG ------------------
ALLOWED_GUILD_ID = 1404353271593701407
WELCOME_CHANNEL_ID = 1447966843011862588
VERIFICATION_CHANNEL_ID = 1448363111307546855
VERIFIED_ROLE_NAME = "Alkaline"
LOOKING_ROLE_ID = 1404373417213300826
LOGO_URL = "https://cdn.discordapp.com/attachments/1447711656129073252/1453088406333816913/file_00000000c3dc71f581032fc60cdf80d8.png"
PURPLE = discord.Color(int("9536E9", 16))

# ------------------ INTENTS ------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------ MESSAGE COUNTER ------------------
message_count = {}

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    message_count[message.author.id] = message_count.get(message.author.id, 0) + 1
    await bot.process_commands(message)

# ------------------ VERIFY BUTTON ------------------
class VerifyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="Verify", style=discord.ButtonStyle.success, emoji="✅")
    async def verify(self, interaction: discord.Interaction, button: ui.Button):
        role = discord.utils.get(interaction.guild.roles, name=VERIFIED_ROLE_NAME)
        if not role:
            await interaction.response.send_message("Role not found.", ephemeral=True)
            return

        if role in interaction.user.roles:
            await interaction.response.send_message("You are already verified.", ephemeral=True)
            return

        await interaction.user.add_roles(role)
        await interaction.response.send_message("✅ You are now verified!", ephemeral=True)
        button.disabled = True
        await interaction.message.edit(view=self)

# ------------------ WELCOME ------------------
@bot.event
async def on_member_join(member):
    if member.guild.id != ALLOWED_GUILD_ID:
        return

    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if not channel:
        return

    embed = discord.Embed(
        title=f"Welcome to {member.guild.name}!",
        description=(
            f"➜ Hey! Look who joined the party, **{member.mention}**!\n\n"
            f"You're member number **{member.guild.member_count}** ˗ˏˋ ★ ˎˊ˗\n\n"
            "We’re excited to have you here!"
        ),
        color=PURPLE
    )
    embed.set_thumbnail(url=member.avatar.url if member.avatar else LOGO_URL)
    embed.set_image(url=LOGO_URL)
    await channel.send(embed=embed)

# ------------------ /greetings testgreet ------------------
@bot.tree.command(name="greetings", description="Test welcome message", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def greetings(interaction: discord.Interaction):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)

    embed = discord.Embed(
        title=f"Welcome to {interaction.guild.name}!",
        description=(
            f"➜ Hey! Look who joined the party, **{interaction.user.mention}**!\n\n"
            f"You're member number **{interaction.guild.member_count}** ˗ˏˋ ★ ˎˊ˗"
        ),
        color=PURPLE
    )
    embed.set_thumbnail(url=interaction.user.avatar.url)
    embed.set_image(url=LOGO_URL)
    await channel.send(embed=embed)
    await interaction.response.send_message("Test welcome sent!", ephemeral=True)

# ------------------ /rules ------------------
@bot.tree.command(name="rules", description="Show server rules", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Server Rules",
        description=(
            "1. Be respectful\n"
            "2. Teen-appropriate content only\n"
            "3. No spam\n"
            "4. No ads\n"
            "5. Correct channels\n"
            "6. No impersonation\n"
            "7. Follow Discord ToS\n"
            "8. No personal info\n"
            "9. Listen to staff\n"
            "10. Be kind"
        ),
        color=PURPLE
    )
    embed.set_image(url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

# ------------------ /userinfo ------------------
@bot.tree.command(name="userinfo", description="User info", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def userinfo(interaction: discord.Interaction, user: discord.Member = None):
    user = user or interaction.user
    roles = ", ".join(r.name for r in user.roles if r.name != "@everyone")
    count = message_count.get(user.id, 0)

    embed = discord.Embed(
        title=f"{user.display_name}'s Info",
        description=(
            f"Joined: {user.joined_at.strftime('%Y-%m-%d')}\n"
            f"Messages: {count}\n"
            f"Roles: {roles}"
        ),
        color=PURPLE
    )
    embed.set_thumbnail(url=user.avatar.url)
    await interaction.response.send_message(embed=embed)

# ------------------ /serverinfo ------------------
@bot.tree.command(name="serverinfo", description="Server info", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(
        title=guild.name,
        description=(
            f"Created: {guild.created_at.strftime('%Y-%m-%d')}\n"
            f"Members: {guild.member_count}"
        ),
        color=PURPLE
    )
    embed.set_thumbnail(url=guild.icon.url if guild.icon else LOGO_URL)
    await interaction.response.send_message(embed=embed)

# ------------------ /verification ------------------
@bot.tree.command(name="verification", description="Post verification", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def verification(interaction: discord.Interaction):
    channel = bot.get_channel(VERIFICATION_CHANNEL_ID)

    embed = discord.Embed(
        title="Verification",
        description="Click the button below to verify!",
        color=PURPLE
    )
    embed.set_image(url=LOGO_URL)
    await channel.send(embed=embed, view=VerifyView())
    await interaction.response.send_message("Verification sent.", ephemeral=True)

# ------------------ /lookingtoplay ------------------
class PlayView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.clicked = set()

    @ui.button(label="I'll play!", style=discord.ButtonStyle.blurple)
    async def play(self, interaction: discord.Interaction, button: ui.Button):
        if interaction.user.id in self.clicked:
            await interaction.response.send_message("You already clicked!", ephemeral=True)
            return
        self.clicked.add(interaction.user.id)
        await interaction.response.send_message(f"-{interaction.user.display_name} said they'll play!")

@bot.tree.command(name="lookingtoplay", description="Find players", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def lookingtoplay(interaction: discord.Interaction):
    embed = discord.Embed(
        description=f"{interaction.user.mention} is looking to play! <@&{LOOKING_ROLE_ID}>",
        color=PURPLE
    )
    await interaction.response.send_message(embed=embed, view=PlayView())

# ------------------ READY ------------------
@bot.event
async def on_ready():
    print(f"Online as {bot.user}")
    await bot.tree.sync(guild=discord.Object(id=ALLOWED_GUILD_ID))
    print("Commands synced")

# ------------------ RUN ------------------
keep_alive()
bot.run(os.environ["DISCORD_TOKEN"])
