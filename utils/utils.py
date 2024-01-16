import re
from typing import Union
import random
import os
import discord
from discord.errors import Forbidden
import datetime
from discord.utils import get

# color scheme for embeds as rbg
blue_light = discord.Color.from_rgb(20, 255, 255)  # default color
green = discord.Color.from_rgb(142, 250, 60)   # success green
yellow = discord.Color.from_rgb(245, 218, 17)  # warning like 'hey, that's not cool'
orange = discord.Color.from_rgb(245, 139, 17)  # warning - rather critical like 'no more votes left'
red = discord.Color.from_rgb(255, 28, 25)      # error red

### @package utils
#
# Utilities and helper functions

def has_role(ctx, role_name):
    """Check if the user has the specified role."""
    role = get(ctx.guild.roles, name=role_name)
    return role in ctx.author.roles

def convert_month_abbr_to_fullname(month_abbr):
        try:
            return datetime.datetime.strptime(month_abbr.capitalize(), '%b').strftime('%B')
        except ValueError:
            return None
        
async def we_are_so_back_logic(image_cache):
    base_directory = 'images/wearesoback'
    files = [f for f in os.listdir(base_directory) if os.path.isfile(os.path.join(base_directory, f))]

    selected_image = random.choice(files)
    while selected_image in image_cache:
        selected_image = random.choice(files)

    image_cache.append(selected_image)

    max_cache_size = 2
    if len(image_cache) > max_cache_size:
        image_cache.popleft()

    file_path = os.path.join(base_directory, selected_image)
    return file_path

command_handler = {
    'wearesoback': we_are_so_back_logic
}

async def create_repeating_task(bot, channel_id, message_content, username):
        await bot.channel_id.send(f"{message_content}\n*(scheduled by {username})*")

## Embeds
        
def format_scheduled_messages(scheduled_messages_db):
    if not scheduled_messages_db:
        return []
    fields = []
    for schedule in scheduled_messages_db:
        field = {
            "name": f"Message Job ID: {schedule['job_id']}\n",
            "value": (
                f"Channel ID: {schedule['channel_id']}\n"
                f"Message: {schedule['message_content']}\n"
                f"Interval: Every {schedule['interval_value']} {schedule['interval_unit']}\n"
                f"Scheduled By: {schedule['scheduled_by']}"
            ),
            "inline":False
        }
        fields.append(field)
    return fields
    
def format_scheduled_commands(scheduled_commands_db):
    if not scheduled_commands_db:
        return []
    fields = []
    for command in scheduled_commands_db:
        field = {
            "name": f"Command Job ID: {command['job_id']}\n",
            "value": (
                f"Channel ID: {command['channel_id']}\n"
                f"Command: {command['command_content']}\n"
                f"Interval: Every {command['interval_value']} {command['interval_unit']}\n"
                f"Scheduled By: {command['scheduled_by']}"
            ),
            "inline":False
           
        }
        fields.append(field)
    return fields

def create_scheduler_embed(scheduler):
    embed_jobs = discord.Embed(title="Active Subroutines", color=red)
    jobs_exist = False

    for job in scheduler.get_jobs():
        embed_jobs.add_field(
            name=f"Scheduler Job ID: {job.id}\n",
            value=f"Next Run Time: {job.next_run_time}",
            inline=False
        )
        jobs_exist = True
    return embed_jobs, jobs_exist

def get_gameplan_embed(get_gameplan_db):
    if not get_gameplan_db:
        return []
    fields = []
    for gameplan in get_gameplan_db:
        field = {
            "name": f"Gameplan: {gameplan['planning_header']}\n",
            "value": (
                f"*Detail*: {gameplan['planning_content']}\n"
                f"*Owner*: {gameplan['username']}\n"
                f"*Id*: {gameplan['id']}"
            ),
            "inline":False
        }
        fields.append(field)
    return fields

def create_basic_embed(title, description, color=discord.Color.blue()):
    embed = discord.Embed(title=title, description=description, color=color)
    return embed

def create_scheduled_message_embed(scheduled_messages):
    embed = discord.Embed(title="Scheduled Messages", color=discord.Color.green())
    for schedule in scheduled_messages:
        embed.add_field(
            name=f"Job ID: {schedule['job_id']}",
            value=(
                f"Channel ID: {schedule['channel_id']}\n"
                f"Message: {schedule['message_content']}\n"
                f"Interval: Every {schedule['interval_value']} {schedule['interval_unit']}"
            ),
            inline=False
        )
    return embed

async def send_embed(ctx, embed):
    """!
    Handles the sending of embeds
    @param ctx context to send to
    @param embed embed to send

    - tries to send embed in channel
    - tries to send normal message when that fails
    - tries to send embed private with information abot missing permissions
    If this all fails: https://youtu.be/dQw4w9WgXcQ
    """
    try:
        await ctx.send(embed=embed)
    except Forbidden:
        try:
            await ctx.send("Hey, seems like I can't send embeds. Please check my permissions :)")
        except Forbidden:
            await ctx.author.send(
                f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n"
                f"May you inform the server team about this issue? :slight_smile:", embed=embed)


def make_embed(title="", color=blue_light, name="‌", value="‌", footer=None) -> discord.Embed:
    """!
    Function to generate generate an embed in one function call
    please note that name and value can't be empty - name and value contain a zero width non-joiner

    @param title Headline of embed
    @param color RGB Tuple (Red, Green, Blue)
    @param name: Of field (sub-headline)
    @param value: Text of field (actual text)
    @param footer: Text in footer
    @return Embed ready to send
    """
    # make color object
    emb = discord.Embed(title=title, color=color)
    emb.add_field(name=name, value=value)
    if footer:
        emb.set_footer(text=footer)

    return emb


def extract_id_from_string(content: str) -> Union[int, None]:
    """!
    Scans string to extract user/guild/message id\n
    Can extract IDs from mentions or plaintext

    @return extracted id as int if exists, else None
    """
    # matching string that has 18 digits surrounded by non-digits or start/end of string
    match = re.match(r'(\D+|^)(\d{18})(\D+|$)', content)

    return int(match.group(2)) if match else None


def get_member_name(member: discord.Member) -> str:
    """!
    Shorthand to extract wich name to use when addressing member
    @return member.nick if exists else member.name
    """
    return member.nick if member.nick else member.name