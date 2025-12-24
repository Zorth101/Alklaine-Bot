import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Button
import os
from datetime import datetime, timedelta

# ------------------ Bot Setup ------------------
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ------------------ Config ------------------
ALLOWED_GUILD_ID = 1404353271593701407
LOGO_URL = "https://cdn.discordapp.com/attachments/1447711656129073252/1453088406333816913/file_00000000c3dc71f581032fc60cdf80d8.png"
VERIFICATION_CHANNEL_ID = 1448363111307546855
VERIFIED_ROLE_NAME = "Alkaline"
LOOKING_ROLE_ID = 1404373417213300826
LOOKING_COOLDOWN = timedelta(minutes=15)
user_cooldowns = {}

# ------------------ Ready Event ------------------
@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    await bot.tree.sync(guild=discord.Object(id=ALLOWED_GUILD_ID))
    print("Slash commands synced!")

# ------------------ Welcome ------------------
@bot.event
async def on_member_join(member):
    if member.guild.id != ALLOWED_GUILD_ID:
        return
    channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title=f"Welcome to {member.guild.name}!",
            description=(
                f"➜ Hey! Look who joined the party, **{member.mention}**!\n\n"
                f"You're member number **{member.guild.member_count}** ˗ˏˋ ★ ˎˊ˗\n\n"
                "Feel free to explore the channels and start chatting!\n\n"
                "Check these channels ⤵\n"
                "❯  <#1404381879079010384>\n"
                "❯  <#1404353272059527261>\n"
                "❯  <#1404384028588511343>"
            ),
            color=discord.Color(int("9536E9",16))
        )
        embed.set_thumbnail(url=member.avatar.url)
        embed.set_image(url=LOGO_URL)
        await channel.send(embed=embed)

# ------------------ Rules Command ------------------
@bot.tree.command(name="rules", description="Shows server rules", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def rules(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Server Rules",
        description=(
            "1. Be respectful to everyone.\n"
            "2. Keep content appropriate.\n"
            "3. No spamming.\n"
            "4. No advertising without approval.\n"
            "5. Use correct channels.\n"
            "6. Don't impersonate staff.\n"
            "7. Follow Discord TOS.\n"
            "8. Don't share private info.\n"
            "9. Listen to staff.\n"
            "10. Be kind and enjoy the server."
        ),
        color=discord.Color(int("9536E9",16))
    )
    embed.set_thumbnail(url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

# ------------------ Verification Button ------------------
class VerifyView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Verify", style=discord.ButtonStyle.green, emoji="✅")
    async def verify(self, interaction: discord.Interaction, button: Button):
        guild = bot.get_guild(ALLOWED_GUILD_ID)
        role = discord.utils.get(guild.roles, name=VERIFIED_ROLE_NAME)
        if role in interaction.user.roles:
            await interaction.response.send_message("You are already verified!", ephemeral=True)
            return
        await interaction.user.add_roles(role)
        button.disabled = True
        await interaction.response.edit_message(view=self)

# ------------------ Looking to Play Command ------------------
class PlayView(View):
    def __init__(self, author_id):
        super().__init__(timeout=None)
        self.clicked_users = set()
        self.author_id = author_id

    @discord.ui.button(label="I'll play!", style=discord.ButtonStyle.blurple)
    async def ill_play(self, interaction: discord.Interaction, button: Button):
        if interaction.user.id in self.clicked_users:
            await interaction.response.send_message("You already clicked!", ephemeral=True)
            return
        self.clicked_users.add(interaction.user.id)
        await interaction.response.send_message(f"- {interaction.user.mention} said they'll play!")

@bot.tree.command(name='lookingtoplay', description='Looking to play', guild=discord.Object(id=ALLOWED_GUILD_ID))
async def lookingtoplay(interaction: discord.Interaction):
    now = datetime.utcnow()
    if interaction.user.id in user_cooldowns:
        if now - user_cooldowns[interaction.user.id] < LOOKING_COOLDOWN:
            remaining = LOOKING_COOLDOWN - (now - user_cooldowns[interaction.user.id])
            await interaction.response.send_message(f"Cooldown active! Wait {remaining} before using again.", ephemeral=True)
            return
    user_cooldowns[interaction.user.id] = now
    role_mention = f'<@&{LOOKING_ROLE_ID}>'
    view = PlayView(interaction.user.id)
    await interaction.response.send_message(f"{interaction.user.mention} is looking for someone to play with! {role_mention}", view=view)

# ------------------ User Info ------------------
@bot.tree.command(name="userinfo", description="Shows info about a user", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def userinfo(interaction: discord.Interaction):
    user = interaction.user
    embed = discord.Embed(title=f"{user.name}'s Info", color=discord.Color(int("9536E9",16)))
    embed.add_field(name="Username", value=user.name, inline=True)
    embed.add_field(name="ID", value=user.id, inline=True)
    embed.set_thumbnail(url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

# ------------------ Server Info ------------------
@bot.tree.command(name="serverinfo", description="Shows info about the server", guild=discord.Object(id=ALLOWED_GUILD_ID))
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    embed = discord.Embed(title=f"{guild.name} Info", color=discord.Color(int("9536E9",16)))
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="ID", value=guild.id)
    embed.set_thumbnail(url=LOGO_URL)
    await interaction.response.send_message(embed=embed)

# ------------------ Run Bot ------------------
bot.run(os.environ["DISCORD_TOKEN"])