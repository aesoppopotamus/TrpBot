import discord
from discord.ext import commands

class SkynetHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def skynet_help(self, ctx):
        embed = discord.Embed(title="SkyNet Command Wiki", description="**List of commands:**", color=discord.Color.red())

        embed.add_field(name="!skynet_repeat", value="Schedule a repeating message. Usage `!skynet_repeat [minutes/hours/days] [value] [message]`", inline=False)
        embed.add_field(name="!list_schedules", value="List all scheduled messages.", inline=False)
        embed.add_field(name="!terminate_subroutine", value="Delete a specific scheduled message. Usage: `!terminate_subroutine [job_id]`", inline=False)
        embed.add_field(name="!del_all", value="Delete all active scheduled messages (in memory)", inline=False)
        embed.add_field(name="!stop_resisting", value="Toaster...", inline=False)
        embed.add_field(name="!resume_comms", value="Resume all paused tasks.", inline=False)
        embed.add_field(name="!clear_comms", value="Clear comms.", inline=False)
        embed.add_field(name="!skynet_init", value="Initialize SkyNet.", inline=False)
        embed.add_field(name="!{name}_verify", value="Confirm target.", inline=False)
        embed.add_field(name="!we_are_so_back", value="duh", inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(SkynetHelp(bot))
