import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
from ocr_check import img_validation
from db_bot import create_db_pool
from db_bot import add_points, create_user, get_user

load_dotenv()

token= os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content=True
intents.members=True

logging.basicConfig(filename='discord.log', encoding='utf-8', level=logging.DEBUG, filemode='w')

bot=commands.Bot(command_prefix='&', intents=intents)

# Declaring the important channel variables
general_channel = None
scores_channel = None
announcement_channel = None

# The events that occurs automatically -------------------------------------------

@bot.event
async def on_ready():
    global general_channel, scores_channel, announcement_channel
    print(f"We are Ready to go in {bot.user.name}")
    for guild in bot.guilds:
        if guild.name == "ArijitBHH265's server":
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
            
    
async def main():
    await create_db_pool()
    async with bot:
        await bot.start(token)



# The event that will occur when the bot joins a server for the first time
@bot.event
async def on_guild_join(guild):
    general_channel = discord.utils.find(
        lambda c: c.name.lower() == 'general' and isinstance(c, discord.TextChannel),
        guild.text_channels
    )
    await guild.chunk()
    members=guild.members
    for member in members:
        await create_user(user_id=member.id)
        
    if general_channel:
        intro_msg = "Hello @everyone, I'm the new aide for the owner of this server. My name is Popo, You may call me Mr.Popo. Happy(😒) to be here. Worthless m@gots."
        await general_channel.send(intro_msg)
    
    
# The event that occurs when a new member joins the server
@bot.event
async def on_member_join(member):
    await member.send(f'Welcome to the server {member.name}')
    await create_user(user_id=member.id)
    

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
                    await message.channel.send(f'{text}')
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
    role = discord.utils.get(ctx.guild.roles, name =roleName.capitalize())
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f'The {roleName.capitalize()} role is taken away from {ctx.author.mention}')
    else:
        await ctx.send(f'Role does not exist!')

@bot.command()
async def myScore(ctx):
    score=await get_user(user_id=ctx.author.id)
    await scores_channel.send(f"{ctx.author.mention}, Your scores are - \n Score - {score['score']} \n Role - {score['role']}")

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
        
    
if __name__ == '__main__':
    asyncio.run(main())