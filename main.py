import discord
from discord.ext import commands, tasks
import logging
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import os
import asyncio
import datetime
import zoneinfo
from ocr_check import img_validation
from db_bot import create_db_pool
from db_bot import add_points, create_user, get_user, update_user

load_dotenv()

token= os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content=True
intents.members=True

logging.basicConfig(filename='discord.log', encoding='utf-8', level=logging.DEBUG, filemode='w')

bot=commands.Bot(command_prefix='&', intents=intents)

# Declaring the important channel variables
guild_channels = {}
IST = zoneinfo.ZoneInfo("Asia/Kolkata")
scheduler = AsyncIOScheduler(timezone=IST)
mileStones = ["Human", "Guardian", "Saiyan", "Demon", "Kai", "Destroyer", "Angel"]

# Utils functions to be used ----------------------------------------------------
# function to update the user roles in the server
async def assign_role(member, roleName):
    roles_log_channel=guild_channels[member.guild.id]["roles"]
    roleAssign=discord.utils.get(member.guild.roles, name=roleName.capitalize()) 
    if roleAssign:
        await member.add_roles(roleAssign)
        await roles_log_channel.send(f"{member.mention} was assigned the {roleName}")
    else:
        print("Role doesn't exist")

# Function to fetch data of all the members in the server and update their roles
async def hourly_check(guild):
    members=guild.members
    for member in members:
        if member.bot:
            continue
        if any(r.name == "God" for r in member.roles):
            continue
        
        currentRole=None
        for r in member.roles:
            if r.name in mileStones: currentRole=r;break
        
        if currentRole==None:continue
        
        userData=await get_user(user_id=member.id)
        role=userData['role']
        if currentRole.name != role:
            await member.remove_roles(currentRole)
            await assign_role(member=member, roleName=role)
        else: continue

# Funtion that resets Scores and roles of the users on monthly basis
async def monthly_reset(guild):
    roles_log_channel=guild_channels[guild.id]["roles"]
    members=guild.members
    await roles_log_channel.send("Starting the monthly reset process!")
    for member in members:
        if member.bot:continue
        if any(r.name == "God" for r in member.roles):
            continue
        
        await update_user(user_id=member.id, role="Human", score=0)
        await assign_role(member=member, roleName="Human")
    await roles_log_channel.send("Monthly reset process has been completed.\n@everyone, Your scores and roles have been reset.")
    
async def guild_setup(guild):
        print(f"🔧 Setting up guild: {guild.name} (ID: {guild.id})")
    
        # List all available channels for debugging
        print("Available text channels:")
        for channel in guild.text_channels:
            print(f"  - {channel.name} (ID: {channel.id})")
                
        general_channel = discord.utils.find(
                lambda c: c.name.lower() == 'general' and isinstance(c, discord.TextChannel),
                guild.text_channels
            )
        scores_channel = discord.utils.find(
                lambda c: c.name.lower() == 'member-scores' and isinstance(c, discord.TextChannel),
                guild.text_channels
            )
        announcement_channel = discord.utils.find(
                lambda c: c.name.lower() == 'announcements' and isinstance(c, discord.TextChannel), 
                guild.text_channels
            )
        roles_log_channel = discord.utils.find(
                lambda c: c.name.lower()=='roles-log' and isinstance(c, discord.TextChannel),
                guild.text_channels
            )
        guild_channels[guild.id]={
            "general":general_channel,
            "scores":scores_channel,
            "announcement":announcement_channel,
            "roles":roles_log_channel
        }
        # scheduler_setup(guild)
        print("Setup complete")
        
        
# The events that occurs automatically -------------------------------------------
@bot.event
async def on_ready():
    print(f"We are Ready to go in {bot.user.name}")
    for guild in bot.guilds:
        if guild.id not in guild_channels:
            await guild_setup(guild=guild)
        
        scheduler_setup(guild)
        good_morning_msg.start(guild)
        good_night_msg.start(guild)
        
    scheduler.start()
            
    
async def main():
    await create_db_pool()
    async with bot:
        await bot.start(token)



# The event that will occur when the bot joins a server for the first time
@bot.event
async def on_guild_join(guild):
    print(f"Bot joined guild: {guild.name} (ID: {guild.id})")
    
    await guild.fetch_channels()
    await guild_setup(guild=guild)
    general_channel=guild_channels[guild.id]["general"]
    announcement_channel=guild_channels[guild.id]["announcement"]
    
    if general_channel:
        intro_msg = "Hello @everyone, I'm the new bot for this server. \nMy name is Popo, You may call me Mr.Popo. Worthless m@gots.\nPlease check the announcement channel for more information regarding my functions and stuff."
        await general_channel.send(intro_msg)
    
    members=guild.members
    for member in members:
        if member.bot:
            continue
        if any(r.name == "God" for r in member.roles):
            continue
        
        await create_user(user_id=member.id)
        
    
    
    
# The event that occurs when a new member joins the server
@bot.event
async def on_member_join(member):
    await member.send(f'Welcome to the server {member.name}')
    await create_user(user_id=member.id)
    await assign_role(member=member, roleName="Human")
    

# The event where the bot may delete an user's message if it contains a certain words
# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#     if 'shit' in message.content.lower():
#         await message.delete()
#         await message.channel.send(f'Language, {message.author.mention}')
    
#     await bot.process_commands(message)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    print(f'here comes a message')
    try:
        if message.attachments:
            channel_name = message.channel.name.lower()
            for attachment in message.attachments:
                if attachment.content_type and attachment.content_type.startswith('image/'):
                    img_bytes = await attachment.read()
                    num, text = await img_validation([{"bytes":img_bytes}], channelName=channel_name, userId=message.author.id)
                    if text!=None: await message.channel.send(f'{text}')
        else:
            await add_points(user_id=message.author.id, points_to_add=0.5)
            
    except Exception as e:
        print(f'Error: {e}')
        await message.channel.send(f'There is an error: {e}')
    await bot.process_commands(message)


# Commands that can be used by the users and the bot ofcourse ------------------------

@bot.command()
async def hello(ctx):
    await ctx.send(f'Hello, {ctx.author.mention}!')

# Command to assign a role to someone    
@bot.command()
async def assign(ctx, roleName):
    role = discord.utils.get(ctx.guild.roles, name=roleName.capitalize())
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f'{ctx.author.mention} was assigned with the role {roleName.capitalize()}')
    else:
        await ctx.send(f'Role does not exist!')

# Command to remove a role from someone
@bot.command()
async def remove(ctx, roleName):
    role = discord.utils.get(ctx.guild.roles, name=roleName.capitalize())
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f'The {roleName.capitalize()} role is taken away from {ctx.author.mention}')
    else:
        await ctx.send(f'Role does not exist!')
        
# Command to promote ones role in the guild
@bot.command()
async def promote(ctx):
    roles_log_channel=guild_channels[ctx.author.guild.id]["roles"]
    currentRole = None
    for r in ctx.author.roles:
        if r.name in mileStones:currentRole=r;break
    
    userData = await get_user(user_id=ctx.author.id)
    promoteRole = userData['role']
    if currentRole and currentRole.name == promoteRole:
        await roles_log_channel.send(f"{ctx.author.mention}, you are already a {currentRole}.\nCan't promote.")
    else:
        await ctx.author.remove_roles(currentRole)
        await assign_role(member=ctx.author, roleName=promoteRole)
        await roles_log_channel.send(f"{ctx.author.mention} just got promoted to {promoteRole}.\nCongrats gooner 👏")

# Command to check the scores of the user
@bot.command()
async def myScore(ctx):
    scores_channel=guild_channels[ctx.author.guild.id]["scores"]
    score=await get_user(user_id=ctx.author.id)
    await scores_channel.send(f"{ctx.author.mention}, Your scores are - \nScore - {score['score']} \nRole - {score['role']}")

# Command to create a poll 
@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title='New Poll', description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")
        
        
# Adding special previllages for special users -------------------------------------------
@bot.command()
@commands.has_role('Angel')
async def secret(ctx):
    await ctx.send(f"Welcome M@got, it's a secret command!")
    
@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"Your role doesn't provide the permission to access this command.")
        
# Automated tasks that run in the background ----------------------------------------------

# Good Morning message (Good morning Pinapple! Looking very good very nice.)
@tasks.loop(time=datetime.time(hour=8, minute=35, tzinfo=IST))
async def good_morning_msg(guild):
    general_channel=guild_channels[guild.id]["general"]
    if general_channel:
        await general_channel.send("Good Morning @everyone!\nRise and Rush M@gots 🌚")

# Good Night message 
@tasks.loop(time=datetime.time(hour=22, minute=35, tzinfo=IST))
async def good_night_msg(guild):
    general_channel=guild_channels[guild.id]["general"]
    if general_channel:
        await general_channel.send("Good Night @everyone!\nThat's enough gooning for one day 😶‍🌫️")


def scheduler_setup(guild):
    # Hourly checks to update user Roles
    scheduler.add_job(
        hourly_check,
        IntervalTrigger(hours=1),
        kwargs={"guild":guild}
        )
    # Monthly Scores and Roles reset
    scheduler.add_job(
        monthly_reset,
        CronTrigger(day=1, hour=8, minute=0, timezone=IST),
        kwargs={"guild":guild}
    )
    

# Buffer for the automated tasks    
@good_morning_msg.before_loop
async def before_morning():
    await bot.wait_until_ready()
    
@good_night_msg.before_loop
async def before_night():
    await bot.wait_until_ready()
    
if __name__ == '__main__':
    asyncio.run(main())