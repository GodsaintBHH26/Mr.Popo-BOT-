import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
from ocr_check import img_validation
from db_bot import create_db_pool

load_dotenv()

token= os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content=True
intents.members=True

bot=commands.Bot(command_prefix='&', intents=intents)

# The events that occurs automatically -------------------------------------------

@bot.event
async def on_ready():
    print(f"We are Ready to go in {bot.user.name}")
    
async def main():
    await create_db_pool()
    

# The event that will occur when the bot joins a server for the first time
@bot.event
async def on_guild_join(guild):
    general_channel = discord.utils.find(
        lambda c: c.name.lower() == 'general' and isinstance(c, discord.TextChannel),
        guild.text_channels
    )
    if general_channel:
        intro_msg = "Hello @everyone, I'm the new aide for the owner of this server. My name is Popo, You may call me Mr.Popo. Happy(😒) to be here. Worthless m@gots."
        await general_channel.send(intro_msg)
    
    
# The event that occurs when a new member joins the server
@bot.event
async def on_member_join(member):
    await member.send(f'Welcome to the server {member.name}')

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

    if message.attachments:
        for attachment in message.attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                img_bytes = await attachment.read()
                num, text = img_validation([{"bytes":img_bytes}])
                await message.channel.send(f'The text in that image: {text}')
    
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
        
    
bot.run(token, log_handler=handler, log_level=logging.DEBUG)