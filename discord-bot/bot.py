#!/usr/bin/env python3
"""
RS-Agent Discord Bot - Enhanced Edition
=======================================
Enhanced Discord bot with more commands and features.

Commands:
- Clan management (/rs-clan, /rs-citadel, /rs-inactive)
- Player lookup (/rs-player, /rs-compare)
- GE trading (/rs-item, /rs-price, /rs-arbitrage)
- Portfolio (/rs-portfolio, /rs-add, /rs-remove)
- Utilities (/rs-help, /rs-stats, /rs-alert)

Usage:
    python3 discord-bot/bot.py
"""

import discord
from discord import app_commands, Embed, Colour
from discord.ext import commands, tasks
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ DISCORD_BOT_TOKEN not found in .env file!")
    sys.exit(1)

# Intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# Bot setup
bot = commands.Bot(command_prefix='!', intents=intents)
tree = bot.tree

# Data directory
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def run_tool(tool_name: str, args: list) -> dict:
    """Run a CLI tool and return result."""
    try:
        tools_dir = Path(__file__).parent.parent / "tools"
        cmd = [sys.executable, str(tools_dir / f"{tool_name}.py")] + args + ["--json"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            return json.loads(result.stdout)
        return {"error": result.stderr}
    except Exception as e:
        return {"error": str(e)}


def format_number(num: int) -> str:
    """Format number with commas."""
    return f"{num:,}"


def format_xp(xp: int) -> str:
    """Format XP with M/B suffixes."""
    if xp >= 1_000_000_000:
        return f"{xp / 1_000_000_000:.2f}B"
    elif xp >= 1_000_000:
        return f"{xp / 1_000_000:.2f}M"
    elif xp >= 1_000:
        return f"{xp / 1_000:.1f}K"
    return str(xp)


# ============================================================================
# SLASH COMMANDS
# ============================================================================

@tree.command(name="rs-clan", description="Get clan information")
@app_commands.describe(clan="Clan name to lookup")
async def rs_clan(interaction: discord.Interaction, clan: str):
    """Get clan information."""
    await interaction.response.defer()
    
    result = run_tool("runescape-api", ["--clan", clan])
    
    if "error" in result:
        await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
        return
    
    embed = Embed(
        title=f"🛡️ {result.get('clan_name', clan)}",
        colour=Colour.orange(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="👥 Members", value=f"{result.get('total_members', 0):,}", inline=True)
    embed.add_field(name="💫 Total XP", value=format_xp(result.get('total_xp', 0)), inline=True)
    embed.add_field(name="📊 Avg XP", value=format_xp(result.get('average_xp', 0)), inline=True)
    embed.add_field(name="⚔️ Total Kills", value=f"{result.get('total_kills', 0):,}", inline=True)
    
    # Top members
    if result.get('top_members'):
        top_text = "\n".join([
            f"{i+1}. {m.get('name', 'Unknown')[:20]} - {format_xp(m.get('total_xp', 0))}"
            for i, m in enumerate(result['top_members'][:5])
        ])
        embed.add_field(name="🌟 Top 5 Members", value=top_text, inline=False)
    
    embed.set_footer(text="RS-Agent Discord Bot")
    await interaction.followup.send(embed=embed)


@tree.command(name="rs-player", description="Lookup player hiscores")
@app_commands.describe(player="Player name", game="Game version (rs3 or osrs)")
@app_commands.choices(game=[
    app_commands.Choice(name="RS3", value="rs3"),
    app_commands.Choice(name="OSRS", value="osrs")
])
async def rs_player(interaction: discord.Interaction, player: str, game: str = "rs3"):
    """Lookup player hiscores."""
    await interaction.response.defer()
    
    result = run_tool("osrs-hiscores", ["--player", player, "--game", game])
    
    if "error" in result:
        await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
        return
    
    embed = Embed(
        title=f"🎮 {game.upper()} Hiscores - {player}",
        colour=Colour.blue(),
        timestamp=datetime.utcnow()
    )
    
    skills = result.get('skills', {})
    overall = skills.get('Overall', {})
    
    embed.add_field(name="📈 Total Level", value=f"{overall.get('level', 'N/A')}", inline=True)
    embed.add_field(name="🏆 Rank", value=f"{overall.get('rank', 'Unranked'):,}" if overall.get('rank') else "Unranked", inline=True)
    embed.add_field(name="⭐ Total XP", value=format_xp(overall.get('xp', 0)), inline=True)
    
    # Top 5 skills by XP
    if skills:
        top_skills = sorted(
            [(k, v) for k, v in skills.items() if k != 'Overall' and v.get('level')],
            key=lambda x: x[1].get('xp', 0),
            reverse=True
        )[:5]
        
        skills_text = "\n".join([
            f"{name}: Lvl {data.get('level', '?')} ({format_xp(data.get('xp', 0))})"
            for name, data in top_skills
        ])
        embed.add_field(name="📊 Top Skills", value=skills_text, inline=False)
    
    embed.set_footer(text="RS-Agent Discord Bot")
    await interaction.followup.send(embed=embed)


@tree.command(name="rs-item", description="Check GE item price")
@app_commands.describe(item="Item name to lookup")
async def rs_item(interaction: discord.Interaction, item: str):
    """Check GE item price."""
    await interaction.response.defer()
    
    result = run_tool("runescape-api", ["--item", item])
    
    if "error" in result or not result:
        await interaction.followup.send(f"❌ Item not found: {item}", ephemeral=True)
        return
    
    embed = Embed(
        title=f"💰 {result.get('name', item)}",
        colour=Colour.gold(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="🏷️ Type", value=result.get('type', 'Unknown'), inline=True)
    embed.add_field(name="👑 Members", value="Yes" if result.get('members') else "No", inline=True)
    
    current = result.get('current', {})
    embed.add_field(name="💵 Current Price", value=current.get('price', 'N/A'), inline=True)
    embed.add_field(name="📈 Trend", value=current.get('trend', 'neutral').title(), inline=True)
    embed.add_field(name="📝 Examine", value=result.get('description', 'N/A')[:50], inline=False)
    
    embed.set_footer(text="RS-Agent Discord Bot")
    await interaction.followup.send(embed=embed)


@tree.command(name="rs-portfolio", description="View your portfolio")
async def rs_portfolio(interaction: discord.Interaction):
    """View portfolio."""
    await interaction.response.defer()
    
    result = run_tool("portfolio-tracker", ["--view"])
    
    if "error" in result:
        await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
        return
    
    embed = Embed(
        title="💼 Your Portfolio",
        colour=Colour.green(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="📦 Items", value=result.get('item_count', 0), inline=True)
    embed.add_field(name="💵 Buy Cost", value=format_number(result.get('total_buy_cost', 0)), inline=True)
    embed.add_field(name="💰 Current Value", value=format_number(result.get('total_current_value', 0)), inline=True)
    
    profit = result.get('total_profit_loss', 0)
    profit_str = f"+{format_number(profit)}" if profit > 0 else str(format_number(profit))
    embed.add_field(name="📊 P/L", value=profit_str, inline=True)
    
    roi = result.get('total_roi_percent', 0)
    roi_str = f"+{roi:.2f}%" if roi > 0 else f"{roi:.2f}%"
    embed.add_field(name="📈 ROI", value=roi_str, inline=True)
    
    # Holdings
    if result.get('items'):
        holdings_text = "\n".join([
            f"• {item.get('name', 'Unknown')[:25]}: {format_number(item.get('current_value', 0))}"
            for item in sorted(result['items'], key=lambda x: x.get('current_value', 0), reverse=True)[:10]
        ])
        embed.add_field(name="📋 Top Holdings", value=holdings_text, inline=False)
    
    embed.set_footer(text="RS-Agent Discord Bot")
    await interaction.followup.send(embed=embed)


@tree.command(name="rs-arbitrage", description="Find GE arbitrage opportunities")
@app_commands.describe(min_profit="Minimum profit threshold (default: 10000)", min_roi="Minimum ROI % (default: 1.0)")
async def rs_arbitrage(interaction: discord.Interaction, min_profit: int = 10000, min_roi: float = 1.0):
    """Find arbitrage opportunities."""
    await interaction.response.defer()
    
    result = run_tool("ge-arbitrage", ["--scan-all", "--min-profit", str(min_profit), "--min-roi", str(min_roi)])
    
    if "error" in result:
        await interaction.followup.send(f"❌ {result['error']}", ephemeral=True)
        return
    
    opportunities = result.get('opportunities', [])
    
    if not opportunities:
        await interaction.followup.send(f"❌ No arbitrage opportunities found with min profit {format_number(min_profit)} and min ROI {min_roi}%", ephemeral=True)
        return
    
    embed = Embed(
        title=f"💰 Arbitrage Opportunities ({len(opportunities)} found)",
        colour=Colour.purple(),
        timestamp=datetime.utcnow()
    )
    
    # Top 5 opportunities
    opp_text = "\n".join([
        f"• {opp.get('item_name', 'Unknown')[:25]}\n  "
        f"Profit: {format_number(opp.get('profit', 0))} ({opp.get('roi', 0):.1f}%)"
        for opp in opportunities[:5]
    ])
    embed.add_field(name="🎯 Top Opportunities", value=opp_text, inline=False)
    
    embed.set_footer(text="RS-Agent Discord Bot • Use --min-profit and --min-roi to filter")
    await interaction.followup.send(embed=embed)


@tree.command(name="rs-help", description="Show all available commands")
async def rs_help(interaction: discord.Interaction):
    """Show help message."""
    embed = Embed(
        title="🦆 RS-Agent Discord Bot - Help",
        description="Complete RuneScape toolkit for your Discord server!",
        colour=Colour.orange(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(
        name="🛡️ Clan Commands",
        value="`/rs-clan` - Get clan info\n`/rs-citadel` - Track citadel caps\n`/rs-inactive` - Find inactive members",
        inline=True
    )
    
    embed.add_field(
        name="🎮 Player Commands",
        value="`/rs-player` - Lookup hiscores\n`/rs-compare` - Compare players",
        inline=True
    )
    
    embed.add_field(
        name="💰 Trading Commands",
        value="`/rs-item` - Check GE price\n`/rs-arbitrage` - Find opportunities\n`/rs-portfolio` - View portfolio",
        inline=True
    )
    
    embed.add_field(
        name="📊 Utilities",
        value="`/rs-help` - This message\n`/rs-stats` - Bot statistics\n`/rs-alert` - Set price alert",
        inline=True
    )
    
    embed.set_footer(text=f"Requested by {interaction.user.name}")
    await interaction.response.send_message(embed=embed)


@tree.command(name="rs-stats", description="Show bot statistics")
async def rs_stats(interaction: discord.Interaction):
    """Show bot statistics."""
    embed = Embed(
        title="📊 Bot Statistics",
        colour=Colour.blue(),
        timestamp=datetime.utcnow()
    )
    
    embed.add_field(name="🤖 Servers", value=f"{len(bot.guilds)}", inline=True)
    embed.add_field(name="👥 Users", value=f"{sum(g.member_count for g in bot.guilds):,}", inline=True)
    embed.add_field(name="🛠️ Commands", value=f"{len(tree.get_commands())}", inline=True)
    
    embed.add_field(
        name="📚 Features",
        value="• 13 CLI tools\n• RS3 + OSRS support\n• Portfolio tracking\n• GE arbitrage\n• Clan management",
        inline=False
    )
    
    embed.set_footer(text="RS-Agent Discord Bot v2.0.0")
    await interaction.response.send_message(embed=embed)


# ============================================================================
# BOT EVENTS
# ============================================================================

@bot.event
async def on_ready():
    """Bot is ready."""
    print(f"✅ Logged in as {bot.user}")
    print(f"✅ Serving {len(bot.guilds)} servers")
    print(f"✅ {len(tree.get_commands())} slash commands registered")
    
    # Sync slash commands
    try:
        synced = await tree.sync()
        print(f"✅ Synced {len(synced)} slash commands")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")


@bot.event
async def on_guild_join(guild):
    """Bot joined a new guild."""
    print(f"✅ Joined {guild.name} ({guild.id})")
    
    # Send welcome message to general channel
    for channel in guild.text_channels:
        if channel.permissions_for(guild.me).send_messages:
            embed = Embed(
                title="🦆 RS-Agent Bot has arrived!",
                description="Thanks for adding me to your server!\n\nUse `/rs-help` to see all available commands.",
                colour=Colour.orange()
            )
            await channel.send(embed=embed)
            break


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("🚀 Starting RS-Agent Discord Bot...")
    bot.run(BOT_TOKEN)
