import discord
from discord.ext import commands, tasks
from apscheduler.triggers.interval import IntervalTrigger
from config import ALLOWED_UNITS
from database.database import Database
from utils.utils import create_repeating_task, format_scheduled_messages, create_scheduler_embed

class SchedulingCommands(commands.Cog):
    def __init__(self, bot, scheduler):
        self.bot = bot
        self.scheduler = scheduler
        self.db = Database(bot, scheduler)

# Start schedules
    @commands.command(name='startsubroutines',
                      description='Schedules existing tasks in the database.')
    async def startsubroutines(self, ctx):
        scheduled_messages_db = self.db.get_scheduled_messages()

        if not scheduled_messages_db:
            await ctx.send("<:: SkyNet Status: ERROR_[NO SUBROUTINES FOUND.]")
            return
        
        await self.db.queue_repeating_messages()
        await ctx.send(f"<:: SkyNet Status: **ONLINE**. Subroutines initialized.")

# schedule message
    @commands.command(name='addsubroutine',
                      description='Add a scheduled message to the db/queue. Args: interval, interval_value[minutes, hours, days], message')
    async def addsubroutinemsg(self, ctx, interval_value: int, interval_unit, *, message: str):
        if not interval_value:
            await ctx.send("<:: INVALID COMMAND: Interval value is a required arguement.")
            return      
        if interval_value <= 0:
            await ctx.send("<:: INVALID INTERVAL: Interval value must be positive.")
            return
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
            job_id = str(ctx.message.id)
            self.scheduler.add_job(create_repeating_task, trigger, args=[self.bot, channel_id, message_content, username], id=job_id)

        except ValueError:
            await ctx.send("**Invalid interval format.** Input valid time unit (seconds, minutes, hours, days, weeks).")
        job_id = str(ctx.message.id)
        channel_id = ctx.channel.id
        scheduler_username = ctx.author.display_name
        self.db.add_scheduled_message(channel_id, message, interval_unit, interval_value, job_id, scheduler_username)
        await ctx.send(f"Repeating message scheduled every {interval_value} {interval_unit}: \"{message}\"")    

# List subroutines
    @commands.command(name='listsubroutines',
                      description='List all current messages scheduled.')
    async def listsubroutines(self, ctx):
        scheduled_messages_db = self.db.get_scheduled_messages()
        
        if not scheduled_messages_db and not self.scheduler.get_jobs():
            await ctx.send("<:: NO SUBROUTINES FOUND.")
            return

        embed_scheduled = discord.Embed(title="Scheduled Subroutines", color=discord.Color.blue())

        message_fields = format_scheduled_messages(scheduled_messages_db)
        for field in message_fields:
            embed_scheduled.add_field(**field)
        if message_fields:
            await ctx.send(embed=embed_scheduled)
        
        embed_jobs, jobs_exist = create_scheduler_embed(self.scheduler)
        if jobs_exist:
            await ctx.send(embed=embed_jobs)

    @commands.command(name='terminatesubroutine',
                      description='Remove a scheduled message from the queue and delete it from the DB. Args: job_id')
    async def deletesubroutine(self, ctx, job_id: str = None):
        if not job_id:
            await ctx.send("<:: INVALID ARGUEMENT: Input valid subroutine identifier (job_id).")
            return
        
        job = self.scheduler.get_job(job_id)

        if job:
            job.remove() 
            job_removed_message = f"<:: Subroutine with ID {job_id} has been removed from the scheduler."
        else:
            job_removed_message = f"<:: No subroutine found with ID {job_id} in the scheduler." 
        
        if self.db.delete_scheduled_message(job_id):
            db_removed_message = f"<:: Message subroutine with ID {job_id} has been removed from the database."
        elif self.db.delete_scheduled_command(job_id):
            db_removed_message = f"<:: Command subroutine with ID {job_id} has been removed from the database."
        else:
            db_removed_message = f"<:: No subroutine found with ID {job_id} in the database."

        await ctx.send(f"{job_removed_message}\n{db_removed_message}")

    # Clear jobs
    @commands.command(name='clearlocalsubroutines',
                      description='Clears bot scheduler of tasks.')
    async def clear_messagearray(self, ctx):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            await ctx.send("<:: No messages found.")
        for job in jobs:
            self.scheduler.remove_all_jobs
        await ctx.send("<:: Array terminated.") 

        # Resume jobs
    @commands.command(name='resumesubroutines',
                      description='Resumes bot scheduler.')
    async def resume_comms(self, ctx):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            await ctx.send("<:: No tasks found.")
            return
        for job in jobs:
            job.resume()    

        await ctx.send("<:: Resuming communication tasks.") 

    # Pause jobs
    @commands.command(name='pausesubroutines',
                      description='Pauses bot scheduler.')
    async def pause_comms(self, ctx):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            await ctx.send("<:: Sisk. Clear comms.")
            return    
        for job in jobs:
            job.pause()
        await ctx.send("<:: Temporarily censuring communications.")

async def setup(bot):
    await bot.add_cog(SchedulingCommands(bot, bot.scheduler))