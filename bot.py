10.16 12:50 PM
Dm bot 
import discord
from discord import app_commands
from discord.ext import commands
import json
import os

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.dm_messages = True

bot = commands.Bot(command_prefix="!", intents=intents)

SUBSCRIBERS_FILE = "subscribers.json"

# Load subscribers from file
if os.path.exists(SUBSCRIBERS_FILE):
    with open(SUBSCRIBERS_FILE, "r") as f:
        subscribed_users = set(json.load(f))
else:
    subscribed_users = set()

def save_subscribers():
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(list(subscribed_users), f)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(e)

# Opt-in / subscribe
@bot.tree.command(name="subscribe", description="Opt-in to receive DMs from this bot.")
async def subscribe(interaction: discord.Interaction):
    subscribed_users.add(interaction.user.id)
    save_subscribers()
    await interaction.response.send_message(
        "✅ You have subscribed to receive DMs from this bot!", ephemeral=True
    )

# Opt-out / unsubscribe
@bot.tree.command(name="unsubscribe", description="Opt-out from DMs.")
async def unsubscribe(interaction: discord.Interaction):
    subscribed_users.discard(interaction.user.id)
    save_subscribers()
    await interaction.response.send_message(
        "❎ You have unsubscribed from DMs.", ephemeral=True
    )

# DM a single user
@bot.tree.command(name="dm", description="Send a DM to a specific user (Admin only).")
@app_commands.describe(user="The user to DM", message="The message to send")
async def dm(interaction: discord.Interaction, user: discord.User, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must be an admin to use this.", ephemeral=True)
        return
    try:
        await user.send(message)
        await interaction.response.send_message(f"✅ Message sent to {user.name}", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message("❌ Cannot DM that user (privacy settings).", ephemeral=True)

# DM all subscribed users
@bot.tree.command(name="dmall", description="DM all subscribed users (Admin only).")
@app_commands.describe(message="The message to send to all subscribed users.")
async def dmall(interaction: discord.Interaction, message: str):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("❌ You must be an admin to use this.", ephemeral=True)
        return

    if not subscribed_users:
        await interaction.response.send_message("⚠️ No users are subscribed.", ephemeral=True)
        return

    sent = 0
    for user_id in list(subscribed_users):
        try:
            user = await bot.fetch_user(user_id)
            await user.send(message)
            sent += 1
        except discord.Forbidden:
            subscribed_users.discard(user_id)  # Remove if cannot DM
    save_subscribers()
    await interaction.response.send_message(
        f"✅ Message sent to {sent} subscribed user(s).", ephemeral=True
    )

bot.run("YOUR_BOT_TOKEN")
