import discord
from discord.ext import commands
from apscheduler.triggers.interval import IntervalTrigger
from config import ALLOWED_UNITS
from database.database import Database
from utils.utils import create_repeating_task, create_repeating_cmd, format_scheduled_messages, format_scheduled_commands, create_scheduler_embed

class SchedulingCommands(commands.Cog):
    def __init__(self, bot, scheduler):
        self.bot = bot
        self.scheduler = scheduler
        self.db = Database(bot, scheduler)

# Start schedules
    @commands.command(name='startsubroutines')
    async def startsubroutines(self, ctx):
        scheduled_messages_db = self.db.get_scheduled_messages()
        scheduled_commands_db = self.db.get_scheduled_cmds()

        if not scheduled_messages_db and not scheduled_commands_db:
            await ctx.send("<:: SkyNet Status: ERROR_[NO SUBROUTINES FOUND.]")
            return
        
        await self.db.queue_repeating_messages()
        await self.db.queue_repeating_cmds()
        await ctx.send(f"<:: SkyNet Status: **ONLINE**. Subroutines initialized.")

# Repeat scheduling commands
    @commands.command(name='addsubroutinemsg',
                      description='Add a scheduled message to the queue.')
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

    @commands.command(name='addsubroutinecmd', description='Add a scheduled command to the queue.')
    async def addsubroutinecmd(self, ctx, interval_value: int, interval_unit, *, command_content: str):
        if interval_unit not in ALLOWED_UNITS:
            await ctx.send(f"<:: INTERVAL DENIED: Allowed interval units are: {', '.join(ALLOWED_UNITS)}.")
            return
        if not command_content:
            await ctx.send(f"<:: INVALID ARGUMENT: Please provide a command.")
            return
        try:
            trigger = IntervalTrigger(**{interval_unit: interval_value})
            channel_id = ctx.channel.id

            self.scheduler.add_job(create_repeating_cmd, trigger, args=[self.bot, channel_id, command_content])

        except ValueError:
            await ctx.send("**Invalid interval format.** Input valid time unit (seconds, minutes, hours, days, weeks).")
            return
        job_id = str(ctx.message.id)  # unique id
        self.db.add_scheduled_command(channel_id, command_content, interval_unit, interval_value, job_id, ctx.author.display_name)
        await ctx.send(f"Command scheduled every {interval_value} {interval_unit}: \"{command_content}\"")

# List subroutines
    @commands.command(name='listsubroutines',
                      description='List all current messages scheduled & queued.')
    async def listsubroutines(self, ctx):
        scheduled_messages_db = self.db.get_scheduled_messages()
        scheduled_commands_db = self.db.get_scheduled_cmds()
        
        if not scheduled_messages_db and not scheduled_commands_db and not self.scheduler.get_jobs():
            await ctx.send("<:: NO SUBROUTINES FOUND.")
            return

        embed_scheduled = discord.Embed(title="Scheduled Subroutines", color=discord.Color.blue())

        message_fields = format_scheduled_messages(scheduled_messages_db)
        for field in message_fields:
            embed_scheduled.add_field(**field)

        command_fields = format_scheduled_commands(scheduled_commands_db)
        for field in command_fields:
            embed_scheduled.add_field(**field)

        if message_fields or command_fields:
            await ctx.send(embed=embed_scheduled)
        
        embed_jobs, jobs_exist = create_scheduler_embed(self.scheduler)
        if jobs_exist:
            await ctx.send(embed=embed_jobs)

    @commands.command(name='terminatesubroutine',
                      description='Remove a scheduled message from the queue and delete it from the DB')
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
    @commands.command(name='clearlocalsubroutines')
    async def clear_messagearray(self, ctx):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            await ctx.send("<:: No messages found.")
        for job in jobs:
            self.scheduler.remove_all_jobs
        await ctx.send("<:: Array terminated.") 

        # Resume jobs
    @commands.command(name='resumesubroutines')
    async def resume_comms(self, ctx):
        jobs = self.scheduler.get_jobs()
        if not jobs:
            await ctx.send("<:: No tasks found.")
            return
        for job in jobs:
            job.resume()    

        await ctx.send("<:: Resuming communication tasks.") 

    # Pause jobs
    @commands.command(name='pausesubroutines')
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