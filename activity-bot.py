
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

# Start the BOT!

client = discord.Client()

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
        await lb.update_leaderboard(client,lb_id)
        await message.channel.send('Leaderboard {} updated!'.format(lb_id))
    if message.content.startswith('!leaderboard delete'):
        lb_id = int(message.content.split('!leaderboard delete ')[1])
        await lb.delete_leaderboard(client,lb_id)
        await message.channel.send('Leaderboard {} deleted!'.format(lb_id))

    ### SOCIAL
    if message.content.startswith('!hello'):
        await bot.hello(client, message)
    if message.content.startswith('!gn'):
        await bot.gn(client, message)
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
        
    ### UNRELEASED/DEV
    if message.content.startswith('!categories'):
        await bot.get_categories(client, message)
    if message.content.startswith('!channeltype'):
        await message.channel.send(message.channel.type)
    if message.content.startswith('!test messagemembers'):
        await bot.dm_activity(client, message)
    '''if message.content.startswith('!categoryactivity'):
        await bot.category_activity(client, message)'''

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