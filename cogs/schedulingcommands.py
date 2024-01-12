import discord
from discord.ext import commands
from apscheduler.triggers.interval import IntervalTrigger
from config import ALLOWED_UNITS
from database.database import Database
from utils.utils import create_repeating_task

class SchedulingCommands(commands.Cog):
    def __init__(self, bot, scheduler):
        self.bot = bot
        self.scheduler = scheduler
        self.db = Database(bot, scheduler)

# Repeating message scheduling
    @commands.command(name='addsubroutine')
    async def addsubroutine(self, ctx, interval_value: int, interval_unit, *, message: str):
        if interval_unit not in ALLOWED_UNITS:
            await ctx.send(f"<:: INTERVAL DENIED: Allowed interval units are: {', '.join(ALLOWED_UNITS)}.")
            return
        if not message:
            await ctx.send(f"<:: INVALID ARGUEMENT: Please provide a message.")
        try:
            trigger = IntervalTrigger(**{interval_unit: interval_value})
            channel_id = ctx.channel.id
            message_content = message
            username = ctx.author.display_name

            self.scheduler.add_job(create_repeating_task, trigger, args=[self.bot, channel_id, message_content, username])

        except ValueError:
            await ctx.send("**Invalid interval format.** Input valid time unit (seconds, minutes, hours, days, weeks).")
        job_id = str(ctx.message.id) #exmp unique id
        channel_id = ctx.channel.id
        scheduler_username = ctx.author.display_name
        self.db.add_scheduled_message(channel_id, message, interval_unit, interval_value, job_id, scheduler_username)
        await ctx.send(f"Repeating message scheduled every {interval_value} {interval_unit}: \"{message}\"")    

    @commands.command(name='listsubroutines')
    async def listsubroutines(self, ctx):
        scheduled_messages_db = self.db.get_scheduled_messages()
        if not scheduled_messages_db and not self.scheduler.get_jobs():
            await ctx.send("<:: NO SUBROUTINES FOUND.")
            return

        embed = discord.Embed(title="Scheduled Messages", color=discord.Color.blue())
        for schedule in scheduled_messages_db:
             embed.add_field(
                 name=f"Job ID: {schedule['job_id']}",
                 value=f"Channel ID: {schedule['channel_id']}\n"
                       f"Message: {schedule['message_content']}\n"
                       f"Interval: Every {schedule['interval_value']} {schedule['interval_unit']}\n"
                       f"Scheduled By: {schedule['scheduled_by']}",
                 inline=False  # Set to True if you want fields to be inline
             )
        
        for job in self.scheduler.get_jobs():
            embed.add_field(
                name=f"Scheduler Job ID: {job.id}",
                value=f"Next Run Time: {job.next_run_time}",
            inline=False
        )

        await ctx.send(embed=embed) 

    @commands.command(name='terminatesubroutine')
    async def deletesubroutine(self, ctx, job_id: str):
        job = self.scheduler.get_job(job_id)
        if not job_id:
            await ctx.send("<:: INVALID ARGUEMENT: Input valid subroutine identifier (job_id).")
            return
        if job:
            job.remove() 
            db_removed_message = self.db.delete_scheduled_message(job_id)
            job_removed_message = f"<:: Subroutine with ID {job_id} has been removed from the scheduler."
            db_removed_message = f"<:: Subroutine with ID {job_id} has been removed from the database."
        else:
            job_removed_message = f"<:: No subroutine found with ID {job_id} in the scheduler." 

        await ctx.send(f"{job_removed_message}\n{db_removed_message}")  

    @commands.command(name='clearschedule')
    async def clear_messagearray(self, ctx):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            await ctx.send("<:: No messages found.")
        for job in jobs:
            self.scheduler.remove_all_jobs
        await ctx.send("<:: Array terminated.") 

        # Resume jobs
    @commands.command(name='resumecomms')
    async def resume_comms(self, ctx):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            await ctx.send("<:: No tasks found.")
            return
        for job in jobs:
            job.resume()    

        await ctx.send("<:: Resuming communication tasks.") 

    # Pause jobs
    @commands.command(name='clearcomms')
    async def clear_comms(self, ctx):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            await ctx.send("<:: Sisk. Clear comms.")
            return    
        for job in jobs:
            job.pause()
        await ctx.send("<:: Temporariliy censuring communications.")

async def setup(bot):
    await bot.add_cog(SchedulingCommands(bot, bot.scheduler))