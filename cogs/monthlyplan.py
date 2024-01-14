import discord
from discord.ext import commands
from apscheduler.triggers.interval import IntervalTrigger
from config import ALLOWED_UNITS
from database.database import Database
from utils.utils import get_gameplan_embed, convert_month_abbr_to_fullname
import datetime

class MonthlyPlanner(commands.Cog):
    def __init__(self, bot, scheduler):
        self.bot = bot
        self.scheduler = scheduler
        self.db = Database(bot, scheduler)

    @commands.command(name='creategameplan',
                      description='Create a new gameplan record for a month. Args: month(abbreviated), "header", content')
    async def create_gameplan(self, ctx, planning_month: str, planning_header: str, *, planning_content: str):
        username = ctx.author.display_name
        channel_id = ctx.channel.id
        if not planning_month:
            await ctx.send("<:: INVALID COMMAND: Please provide month.")
            return
        if not planning_content:
            await ctx.send("INVALID COMMAND: Please provide planning details.")
            return
        if not planning_header:
            await ctx.send("<:: INVALID COMMAND: Please provide a header.")
            return
        
        month_fullname = convert_month_abbr_to_fullname(planning_month)
        if not month_fullname:
            await ctx.send(f"<:: ERROR: Invalid month abbreviation: {planning_month}")
            return
        self.db.add_gameplan_month(channel_id, planning_header, planning_content, month_fullname, username)
        await ctx.send(f"<:: Creation logged for {planning_header} for {planning_month}.")


    @commands.command(name='getgameplan',
                      description='Display gameplans for a given month. Args: month(abbreviated)')
    async def get_gameplan(self, ctx, planning_month: str):
        month_fullname = convert_month_abbr_to_fullname(planning_month)
        if not month_fullname:
            await ctx.send(f"<:: ERROR: Invalid month abbreviation: {planning_month}")
            return
        get_gameplan_db = self.db.get_gameplan_month(planning_month=month_fullname)
        if not get_gameplan_db:
            await ctx.send(f"<:: ERROR: No plans exist for {month_fullname}.")
            return
        
        embed_gameplan = discord.Embed(title=f"Gameplan for {month_fullname}", description="", color=0x00ff00)
        # embed.set_thumbnail(os.path('images/thumbnails/topheader.png'))

        gameplan_fields = get_gameplan_embed(get_gameplan_db)
        for field in gameplan_fields:
            embed_gameplan.add_field(**field)
        
        await ctx.send(embed=embed_gameplan)

    @commands.command(name='overwritegameplan')
    async def updategameplan(self, ctx, gameplan_id: int, planning_month: str, *, planning_content: str):
        month_fullname = convert_month_abbr_to_fullname(planning_month)
        if not month_fullname:
            await ctx.send(f"<:: ERROR: Invalid month abbreviation: {planning_month}")
            return
        success = self.db.overwrite_gameplan_byid(gameplan_id, month_fullname, planning_content)
        if success:
            await ctx.send(f"<:: Gameplan updated successfully.")
        else:
            await ctx.send(f"<:: ERROR: Unable to update gameplan.")
    

    @commands.command(name='appendgameplan')
    async def append_gameplan(self, ctx, gameplan_id: int, *, additional_content: str):
        success = self.db.append_to_gameplan(gameplan_id, additional_content)
        if success:
            await ctx.send("<:: Gameplan updated successfully.")
        else:
            await ctx.send("<:: ERROR: Unable to update gameplan.")


async def setup(bot):
    await bot.add_cog(MonthlyPlanner(bot, bot.scheduler))