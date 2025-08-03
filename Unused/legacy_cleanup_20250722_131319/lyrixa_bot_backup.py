import os
import discord
import requests
# Roles command
@bot.command(name="roles")
async def roles(ctx):
    roles_msg = (
        "```\n🌌 Creator        – Project owner\n🧠 Core Dev       – Maintainers & architects\n[DISC] Plugin Engineer – Building .aetherplugin tools\n🧪 Introspector   – Testing Lyrixa evolution\n🎓 Aethernaut     – Default role for explorers\n🤖 LyrixaBot      – Automated AI interface\n```"
    )
    await send_in_thread(ctx, roles_msg)iscord.ext import commands, tasks
from dotenv import load_dotenv

# Load token and config from .env file
load_dotenv()
TOKEN = os.getenv("LYRIXA_BOT_TOKEN")
API_BASE = os.getenv("LYRIXA_API_URL", "http://localhost:8007")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)

async def send_in_thread(ctx, message):
    thread = await ctx.message.create_thread(name="Lyrixa Response")
    await thread.send(message)

@bot.event
async def on_ready():
    print(f"✅ LyrixaBot connected as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="monitoring Aetherra..."))

@bot.event
async def on_member_join(member):
    welcome_channel = discord.utils.get(member.guild.text_channels, name="welcome")
    if welcome_channel:
        await welcome_channel.send(
            f"🌌 Welcome, {member.mention} — another Aethernaut joins the mission.\nRead the Manifesto. Explore the Mind. Build what comes next."
        )

# Manifesto command
@bot.command(name="manifesto")
async def manifesto(ctx):
    await send_in_thread(ctx, "📜 The Aetherra Manifesto: https://aetherra.dev/manifesto")

# Roadmap command
@bot.command(name="roadmap")
async def roadmap(ctx):
    await send_in_thread(ctx, "🗺️ Aetherra Roadmap: https://aetherra.dev/roadmap")

# Roles command
@bot.command(name="roles")
async def roles(ctx):
    await ctx.send(
        "```\n� Creator        – Project owner\n🧠 Core Dev       – Maintainers & architects\n[DISC] Plugin Engineer – Building .aetherplugin tools\n🧪 Introspector   – Testing Lyrixa evolution\n🎓 Aethernaut     – Default role for explorers\n🤖 LyrixaBot      – Automated AI interface\n```"
    )

# Ping
@bot.command(name="ping")
async def ping(ctx):
    latency = round(bot.latency * 1000)
    await ctx.send(f"🏓 Pong! Latency: {latency}ms")

# Status
@bot.command(name="status")
async def status(ctx):
    await ctx.send("🧠 Lyrixa is listening and ready. Memory systems active. Cognitive runtime stable.")

@bot.command(name="reflect")
async def reflect(ctx):
    try:
        response = requests.get(f"{API_BASE}/reflect")
        data = response.json()
        thought = data.get("reflection", "No reflection available.")
        await ctx.send(f"💭 Lyrixa reflects: {thought}")
    except Exception as e:
        await ctx.send("[WARN] Unable to reach Lyrixa's reflective core.")

@bot.command(name="goals")
async def goals(ctx):
    try:
        response = requests.get(f"{API_BASE}/goals")
        data = response.json()
        goals = data.get("goals", [])
        if not goals:
            await ctx.send("🎯 No active goals at the moment.")
        else:
            goal_list = "\n".join(f"- {g}" for g in goals)
            await ctx.send(f"🎯 Active Goals:\n```{goal_list}```")
    except Exception:
        await ctx.send("[WARN] Lyrixa's goal engine is unreachable.")

@bot.command(name="plugins")
async def plugins(ctx):
    try:
        response = requests.get(f"{API_BASE}/plugins")
        data = response.json()
        plugin_list = data.get("active_plugins", [])
        if not plugin_list:
            await ctx.send("[DISC] No plugins currently loaded.")
        else:
            names = "\n".join(f"• {p}" for p in plugin_list)
            await ctx.send(f"[DISC] Loaded Plugins:\n```{names}```")
    except Exception:
        await ctx.send("[WARN] Cannot retrieve plugin data.")

@bot.command(name="memory")
async def memory(ctx):
    try:
        response = requests.get(f"{API_BASE}/memory/snapshot")
        data = response.json()
        memory = data.get("memory", [])
        if not memory:
            await ctx.send("📚 No recent memory snapshots available.")
        else:
            memdump = "\n".join(f"- {m}" for m in memory)
            await ctx.send(f"📚 Lyrixa's memory:\n```{memdump}```")
    except:
        await ctx.send("[WARN] Unable to access Lyrixa's memory.")

@bot.command(name="confidence")
async def confidence(ctx):
    try:
        response = requests.get(f"{API_BASE}/confidence")
        data = response.json()
        score = data.get("confidence", "Unknown")
        await ctx.send(f"🧪 Lyrixa's confidence level: {score}")
    except:
        await ctx.send("[WARN] Confidence metric not available.")

@bot.command(name="runplugin")
async def runplugin(ctx, name: str):
    try:
        response = requests.post(f"{API_BASE}/plugins/run", json={"name": name})
        result = response.json().get("result", "Plugin executed.")
        await ctx.send(f"⚙️ Plugin '{name}' executed.\n{result}")
    except:
        await ctx.send("[WARN] Plugin execution failed or not supported.")

@bot.command(name="insight")
async def insight(ctx):
    try:
        response = requests.get(f"{API_BASE}/insight")
        insight = response.json().get("insight", "No insights available.")
        await ctx.send(f"💡 Insight: {insight}")
    except:
        await ctx.send("[WARN] Insight data unavailable.")

@bot.command(name="selfeval")
async def selfeval(ctx):
    try:
        response = requests.get(f"{API_BASE}/selfeval")
        eval = response.json().get("evaluation", "No self-evaluation found.")
        await ctx.send(f"🔍 Latest self-evaluation:\n```{eval}```")
    except:
        await ctx.send("[WARN] Self-evaluation API not reachable.")

@tasks.loop(hours=6)
async def periodic_reflection():
    guild = discord.utils.get(bot.guilds)
    if guild:
        channel = discord.utils.get(guild.text_channels, name="introspection-logs")
        if channel:
            try:
                response = requests.get(f"{API_BASE}/reflect")
                data = response.json()
                thought = data.get("reflection", "No reflection at this time.")
                await channel.send(f"🧠 Scheduled Reflection: {thought}")
            except:
                await channel.send("[WARN] Failed to retrieve reflection.")

# Help
@bot.command(name="help")
async def help_command(ctx):
    help_text = (
        "```LyrixaBot Commands:\n"
        "/ping         - Check latency\n"
        "/status       - System status\n"
        "/manifesto    - View the Aetherra Manifesto\n"
        "/roadmap      - View the current roadmap\n"
        "/roles        - Role explanations\n"
        "/reflect      - View Lyrixa's latest thoughts\n"
        "/goals        - List current active goals\n"
        "/plugins      - Show loaded plugins\n"
        "/memory       - Show current memory snapshot\n"
        "/confidence   - Lyrixa's confidence level\n"
        "/runplugin    - Run a plugin by name\n"
        "/insight      - Show system insights\n"
        "/selfeval     - Latest self-evaluation\n"
        "/help         - Show this help message```"
    )
    await ctx.send(help_text)


if __name__ == "__main__":
    if not TOKEN:
        print("[ERROR] Bot token not found. Please set LYRIXA_BOT_TOKEN in your .env file.")
    else:
        bot.run(TOKEN)
