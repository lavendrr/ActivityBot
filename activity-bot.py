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
import us_toolkit as us

# Start the BOT!

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content.startswith('!hello'):
        await bot.hello(client, message)
    if message.content.startswith('!gn'):
        await bot.gn(client, message)
    if message.content.startswith('!jointime'):
        await bot.join_time(client, message)
    if message.content.startswith('!game'):
        await bot.game_activity(client, message)
    if message.content.startswith('!memberactivity'):
        await bot.member_activity(client, message)
    if message.content.startswith('!listchannels'):
        await bot.list_channels(client, message)
    ##############################
    #### !SHEET UPDATES
    if message.content.startswith('!updatesheets'):
        if message.content.split(' ')[1] == 'PC' or message.content.split(' ')[1] == 'CONSOLE':
            run_mode = message.content.split(' ')[1]
            await us.update_sheets(run_mode, client)
        else:
            await message.channel.send('Please enter a valid run mode: PC/CONSOLE')
    if message.content.startswith('!channelactivity'):
        await bot.channel_activity(client, message)
    if message.content.startswith('!leaderboard'):
        await bot.update_leaderboard(client, message)
    if message.content.startswith('!test messagemembers'):
        await bot.dm_activity(client, message)
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

