
# -*- coding: utf-8 -*-
"""
Activity Bot created for the Shrouded Gaming Community
Author: Ricardo Moctezuma (Lavender) - Admin of Shrouded VII
Contributors: Roberto Moctezuma
"""

import discord
from datetime import datetime
import pytz
import bot_toolkit as bot
import lb_toolkit as lb
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename='activity-bot.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handler)
logger.addHandler(consoleHandler)

# Start the BOT!

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    ### MAIN FUNCTIONS
    
    # !SHEET UPDATES
    if message.content.startswith('!updatesheets'):
        await bot.update_sheets(client, message)
        
    # !DCotW UPDATES
    if message.content.startswith('!update_dcotw'):
        await bot.update_dcotw(client, message)
    if message.content.startswith('!channelactivity'):
        await bot.channel_activity(client, message)  
        
    #LEADERBOARDS
    if message.content.startswith('!leaderboard create'):
        await lb.lb_create(client,message)
        await message.channel.send('Leaderboard created!')
    if message.content.startswith('!leaderboard update'):
        lb_id = int(message.content.split('!leaderboard update ')[1])
        await message.channel.send('Updating leaderboard {}...'.format(lb_id))
        await lb.update_leaderboard(client,lb_id)
        await message.channel.send('Leaderboard {} updated!'.format(lb_id))
    if message.content.startswith('!leaderboard delete'):
        lb_id = int(message.content.split('!leaderboard delete ')[1])
        await lb.delete_leaderboard(client,lb_id)
        await message.channel.send('Leaderboard {} deleted!'.format(lb_id))

    ### SOCIAL
    if message.content.startswith('!hello'):
        await bot.hello(client, message)
    if message.content.startswith('!egg'):
        await bot.egg(client, message)
    if message.content.startswith('!gn'):
        await bot.gn(client, message)
    if message.content.startswith('!gm'):
        await bot.gm(client, message)
    ### MEME COMMANDS
    if message.content.startswith('!hoesmad'):
        x = 0
        while x < 3:
            await message.channel.send('hoes mad x' + str(x + 1))
            x += 1
    if message.content.startswith('!finthechat'):
        await message.channel.send('F')
    if message.content.startswith('!bruh'):
        await message.channel.send('bruh moment')
    if message.content.startswith('!vii'):
        await message.channel.send('VII best clan') 
    
    ### MISCELLANEOUS
    if message.content.startswith('!jointime'):
        await bot.join_time(client, message)
    if message.content.startswith('!game'):
        await bot.game_activity(client, message)
    if message.content.startswith('!memberactivity'):
        await bot.member_activity(client, message)
    if message.content.startswith('!listchannels'):
        await bot.list_channels(client, message)
    if message.content.startswith('!getavatar'):
        await bot.get_avatar(client, message)
        
    ### UNRELEASED/DEV
    if message.content.startswith('!categories'):
        await bot.get_categories(client, message)
    if message.content.startswith('!channeltype'):
        await message.channel.send(message.channel.type)
    if message.content.startswith('!test messagemembers'):
        await bot.dm_activity(client, message)
        
    if message.content.startswith('!welcomeroom1'):
        await message.channel.send('https://drive.google.com/uc?export=view&id=11XCYR8XF1uVv-w7qeKFMf-Qv5BJ_WfDx')
        
    if message.content.startswith('!welcomeroom2'):
        embed = discord.Embed(title="Expectations", colour=discord.Colour(0xcca4c6), description="VII strives to be an accepting, chill, and peaceful family, even outside of Destiny 2. As such, there are certain expectations members must adhere to in order to be part of the community.")

        embed.set_image(url="https://drive.google.com/uc?export=view&id=18PfDOSUkDSu6ieSY2kS8BSNQe8ubqxbH")
        embed.set_thumbnail(url="https://drive.google.com/uc?export=view&id=1BWRjaGycRWaD3reXPnaoBs890_cV3Y-w")
        
        embed.add_field(name="Respect", value="Members are expected to hold at least a basic level of respect for others. Treat others how you'd like to be treated. Not everyone will get along, but members are required to be courteous and tolerant in our channels. Arguments and hostile interactions are strictly prohibited.", inline=True)
        embed.add_field(name="Awareness", value="Members are expected to be conscious of the way their actions might be perceived by others. Please make sure you read the room and act accordingly. Maybe banter is fine with someone you know well, but don't go around making fun of someone who just joined.", inline=True)
        embed.add_field(name="Maturity", value="While VII does not have an age limit, please be aware that there will be mature content in our channels. Especially risque content is limited to the NSFW-marked channels " + client.get_channel(600887401946284055).mention + " and " + client.get_channel(600559413140652042).mention + ", but there may also be mature jokes and such in the general channels. Please make sure to keep yourself and others in check in this regard. We want to have fun while still making sure others are comfortable, so don't take things too far.", inline=False)
        embed.add_field(name="Acceptance", value="VII accepts people from all walks of life, regardless of age, sexuality, gender identity, religious background, etc. Discrimination of any kind is strictly prohibited.", inline=False)
        
        await message.channel.send(embed=embed)
        
    if message.content.startswith('!welcomeroom3'):
        embed = discord.Embed(title="Activity Policies", colour=discord.Colour(0xcca4c6), description="In order to maintain an active community in VII, we enforce activity in both Destiny 2 and our Discord text chats. Our inactivity thresholds are as follows:")

        embed.set_image(url="https://drive.google.com/uc?export=view&id=1Y78NfMq3c2kY-xVrYb6mftHavO9Nc4FW")
        embed.set_thumbnail(url="https://drive.google.com/uc?export=view&id=1BWRjaGycRWaD3reXPnaoBs890_cV3Y-w")
        
        embed.add_field(name="Destiny 2", value="10 days inactive in-game", inline=True)
        embed.add_field(name="Discord Text Chats", value="14 days inactive (voice chat is not counted)", inline=True)
        embed.add_field(name="__Warning/Purging__", value="If you are found inactive, you may be warned or purged from the Destiny clan. Purged members are typically still allowed to remain in the Discord as part of the extended VII family, and you can rejoin the clan at any time by applying again.", inline=False)
        embed.add_field(name="__Advance Notice__", value="Lastly, if you know in advance that you will be unavailable for a period of time, please reach out to a VII staff member to let us know - we'll mark you as \"away\" and you will not be purged. Our activity policies are not meant to stress y'all out! Just let us know what's going on and we'll do our best to accomodate you.", inline=False)
        
        await message.channel.send(embed=embed)
    
    if message.content.startswith('!welcomeroom4'):
        #commented lines are for updating the embed
        #edit_message = await message.channel.fetch_message(814579208575385610)
        
        embed = discord.Embed(title="Staff", colour=discord.Colour(0xcca4c6), description="These are the people that keep this place running smoothly! Feel free to reach out if you need any help with Destiny, Discord, or anything else.\n__Admin__ - Clan leader\n__Officer__ - Admin assistants\n__Sherpa__ - Destiny 2 guides")

        embed.set_image(url="https://drive.google.com/uc?export=view&id=14GnxB9I-9Yi2hny_BE2pzo7fyFd-YvdX")
        embed.set_thumbnail(url="https://drive.google.com/uc?export=view&id=1BWRjaGycRWaD3reXPnaoBs890_cV3Y-w")
        
        embed.add_field(name="Admin", value=client.get_user(329382120344518656).mention, inline=False)
        embed.add_field(name="Officers", value=client.get_user(248303904041861120).mention + "\n" + client.get_user(161291200719093761).mention + "\n" + client.get_user(411752126914756610).mention + "\n" + client.get_user(265325281278033930).mention, inline=True)
        embed.add_field(name="Sherpas", value=client.get_user(411752126914756610).mention + "\n" + client.get_user(255210127135735819).mention, inline=True)
        
        #await edit_message.edit(embed=embed)
        await message.channel.send(embed=embed)

run_once = False

@client.event
async def on_ready():
    global run_once
    if run_once == False:
        run_once = True
        print('Logged in as')
        print(client.user.name)
        print(client.user.id)
        print('Time: {}'.format(datetime.now(pytz.timezone('US/Central')).strftime('%H:%M:%S %Z on %b %d, %Y')))
        print('------')

client.run(bot.creds.bot_token[0])