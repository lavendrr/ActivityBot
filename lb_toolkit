#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 11:03:06 2019

@author: rmoctezuma
"""

import pandas as pd
import discord
from datetime import datetime, timedelta
import pytz
import time
import bot_toolkit as bot
import us_toolkit as us

# Credentials
bot_token = bot.bot_token
bungie_api_token = bot.bungie_api_token
google_keys_file = bot.google_keys_file

# Constants
MAX_MESSAGES = us.MAX_MESSAGES
RUN_CHANNEL = us.RUN_CHANNEL
STAFF_GUILD = us.STAFF_GUILD
STAFF_CHANNEL = us.STAFF_CHANNEL

lb_file = pd.read_csv('leaderboards.csv').set_index('index').transpose()

async def update_leaderboard(client, message):
    channel_list = bot.get_multiple_channels(message)
    lb_channel = channel_list[-1]
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Eastern'))
    time_since_tues = bot.time_since_tuesday(right_now)
    # Start check
    if channel_list != []:
        try:
            activity_cutoff = datetime.now() - time_since_tues
            leaderboard = {}
            for a in channel_list[:len(channel_list) - 1]:
                history = await a.history(limit = 25000, after = activity_cutoff, oldest_first = False).flatten()
                for m in history:
                    if m.author.display_name in leaderboard:
                        leaderboard[m.author.display_name] += 1
                    else:
                        leaderboard[m.author.display_name] = 1
            lb_sorted = {}
            lb_string = '__**Shrouded Gaming Activity Leaderboard**__\n\n'
            count = 0
            for key, value in sorted(leaderboard.items(), key=lambda item: item[1], reverse = True):
                if count < 10:
                    lb_sorted[key] = value
                    count += 1
                else:
                    break
            for item, amount in lb_sorted.items():
                lb_string += ("{} - {} messages\n".format(item, amount))
            lb_string += ('\nGenerated from these channels: ')
            for a in channel_list[:len(channel_list) - 1]:
                lb_string += (a.mention + ' ')
            lb_string += ('\n\nUpdated ' + right_now.strftime('%H:%M %p %Z on %A, %B %d.'))
            msg = None
            async for m in lb_channel.history(limit = 25000):
                if m.content.startswith('__**Shrouded Gaming Activity Leaderboard**__') and m.author == client.user:
                    msg = m
                    break
            if msg == None:
                await lb_channel.send(lb_string)
                await lb_channel.last_message.pin()
                await message.channel.send('Leaderboard created!')
            else:
                await msg.edit(content = lb_string)
                await message.channel.send('Leaderboard updated!')
        except:
            pass
    else:
        await message.channel.send('That channel does not exist.')
        
### Leaderboard Client
