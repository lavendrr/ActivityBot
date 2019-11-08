#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct  8 10:53:45 2019

@author: rmoctezuma
"""

import pandas as pd
import asyncio
import discord
from datetime import datetime, timedelta
import pytz

# Load credentials and tokens
creds = pd.read_csv('credentials/credentials.csv').set_index('key').transpose()
bot_token = creds['bot_token'].loc['value']
bungie_api_token = creds['bungie_api'].loc['value']
google_keys_file = 'credentials/google_keys.json'

import us_toolkit as us
import dcotw_toolkit as dc

##############################
#       BOT UTILITIES        #
##############################        

def get_member(msg):
    arg_pos = msg.content.find(' ')
    if arg_pos > 0:
        arg = msg.content[arg_pos + 1:]
        member = discord.utils.get(msg.guild.members, name=arg)
    else:
        member = None
    return member

def get_role(msg):
    arg_pos = msg.content.find(' ')
    if arg_pos > 0:
        arg = msg.content[arg_pos + 1:]
        role = discord.utils.get(msg.guild.roles, name=arg)
    else:
        role = None
    return role

def get_channel(msg):
    arg_pos = msg.content.find(' ')
    if arg_pos > 0:
        arg = msg.content[arg_pos + 1:]
        channel = discord.utils.get(msg.guild.text_channels, mention=arg)
    else:
        channel = None
    return channel

def get_category(msg):
    arg_pos = msg.content.find(' ')
    if arg_pos > 0:
        arg = msg.content[arg_pos + 1:]
        channel = discord.utils.get(msg.guild.categories, name=arg)
    else:
        channel = None
    return channel

def get_multiple_channels(msg):
    a = msg.content.split(' | ')
    b = a[0].split(' ')
    c = a[1]
    del b[0]
    channel_list = []
    for d in b:
        channel_list.append(discord.utils.get(msg.guild.text_channels, mention = d))
    channel_list.append(discord.utils.get(msg.guild.text_channels, mention = c))
    return channel_list

def time_since_tuesday(right_now):
    # Time since Tuesday (Noon CDT/EST - Destiny 2 Reset)  
    # Tuesday Conditions      
    if right_now.weekday() == 1:
        if right_now.hour >= 12:
            time_since_tues = timedelta(hours = right_now.hour - 12, minutes = right_now.minute, days = 0)
        else:
            time_since_tues = timedelta(hours = right_now.hour + 12, minutes = right_now.minute, days = 6)
    # Monday conditions
    elif right_now.weekday() == 0:
        if right_now.hour >= 12:
            time_since_tues = timedelta(hours = right_now.hour - 12, minutes = right_now.minute, days = 6)
        else:
            time_since_tues = timedelta(hours = right_now.hour + 12, minutes = right_now.minute, days = 5)
    # Other weekday conditions
    else:
        if right_now.hour >= 12:
            time_since_tues = timedelta(hours = right_now.hour - 12, minutes = right_now.minute, days = right_now.weekday() - 1)
        else:
            time_since_tues = timedelta(hours = right_now.hour + 12, minutes = right_now.minute, days = right_now.weekday() - 2)
    return time_since_tues

async def data_display(data,client,channel):
    ### Discord data display
    msg = ''
    for category in data:
        for name in category.keys():
            msg += '**' + name + '**\n\t'
        for key, value in list(category.values())[0].items():
            if key != 'Total Messages':
                msg += (key + ' - ' + str(value) + '\n\t')
            else:
                msg += ('__' + key + ' - ' + str(value) + '__\n\t')
        msg += '\n'
        
    # Print with segments
    s_start = 0
    s_end = min(1900, len(msg))
    if s_end < len(msg):
        while msg[s_end-1] != '\n':
            s_end -= 1 
    while(s_start < s_end):
        await channel.send(msg[s_start:s_end])
        s_start = s_end
        s_end = min(s_start + 1900, len(msg))
        if s_end < len(msg):
            while msg[s_end-1] != '\n':
                s_end -= 1


##############################        
#          RELEASED          #
##############################        

##############################
# MAIN FUNCTIONS

## ACTIVITY SHEETS

async def update_sheets(client, message):
    if message.content.split(' ')[1] == 'PC' or message.content.split(' ')[1] == 'CONSOLE':
        run_mode = message.content.split(' ')[1]
        await us.update_sheets(run_mode, client)
    else:
        await message.channel.send('Please enter a valid run mode: PC/CONSOLE')

## DISCORD CLAN OF THE WEEK
        
# Print categories and their respective text channels
async def get_categories(client, message):
    msg = ''
    for a in message.guild.categories:
        msg += '**' + a.name + '**\n\t'
        for b in a.channels:
            if b.type == discord.ChannelType.text:
                msg += ' ' + b.mention
        msg += '\n'
    await message.channel.send(msg)

# DCotW manual update
async def update_dcotw(client, message):
    if message.content.split(' ')[1] == 'PC' or message.content.split(' ')[1] == 'CONSOLE':
        run_mode = message.content.split(' ')[1]
        data = await dc.update_dcotw(run_mode,client)
        await data_display(data,client,client.get_guild(us.STAFF_GUILD).get_channel(us.STAFF_CHANNEL))
    else:
        await message.channel.send('Please enter a valid run mode: PC/CONSOLE')

## DISCORD LEADERBOARDS/ACTIVITY

# Activity Leaderboard
# SYNTAX = !leaderboard [# mention of channel to be checked] [#CHANNEL] [#CHANNEL] | [#CHANNEL TO POST LEADERBOARD MESSAGE IN]
async def update_leaderboard(client, message):
    channel_list = get_multiple_channels(message)
    lb_channel = channel_list[-1]
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Eastern'))
    time_since_tues = time_since_tuesday(right_now)
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
        
# Single-channel message count
async def channel_activity(client, message):
    channel = get_channel(message)
    if channel != None:
        activity_cutoff = datetime.now() - timedelta(days=7)
        try:
            history = await channel.history(limit = 25000, after = activity_cutoff, oldest_first = False).flatten()
            if len(history) > 24999:
                await message.channel.send('Channel {} has over 25,000 messages in the past 7 days.'.format(str(channel)))
            else:
                await message.channel.send('Channel {} has {} messages in the past 7 days.'.format(str(channel), len(history)))
        except:
            await message.channel.send('The bot does not have access to that channel.')
    else:
        await message.channel.send('That role does not exist.')

##############################
# SOCIAL

# HELLO
async def hello(client, message):
    msg = 'Hello {0.author.mention}'.format(message)
    await message.channel.send(msg)

# GOOD NIGHT
async def gn(client, message):
    msg = None
    for a in message.author.guild.emojis:
        if a.name == 'PeepoBlanket':
            msg = message.author.mention + ' says goodnight! {}'.format(a)
    if msg != None:
        await message.channel.send(msg)
    else:
        await message.channel.send(message.author.mention + ' says goodnight! {}'.format(':PeepoBlanket:'))

##############################
# MISCELLANEOUS

async def join_time(client, message):
    member = get_member(message)
    if member != None:
        await message.channel.send(member.name + ' joined on ' + member.joined_at.strftime('%m/%d/%Y') + '.')
    else:
        await message.channel.send("Please enter a member's name.")
        
async def game_activity(client, message):
    member = get_member(message)
    if member != None:
        game_name = member.activities[0].name
        await message.channel.send(member.name + ' is currently playing '+ game_name + '.')
    else:
        await message.channel.send("Please enter a member's name.")

async def member_activity(client, message):
    member = get_member(message)
    if member != None:
        listOfChannels = message.guild.text_channels
        mostRecentMsg = None
        for val in listOfChannels:
            async for m in val.history():
                if m.author == member:
                    msgAware = pytz.utc.localize(m.created_at).astimezone(pytz.timezone('US/Central'))
                    if mostRecentMsg == None:
                        mostRecentMsg = msgAware
                    elif msgAware > mostRecentMsg:
                        mostRecentMsg = msgAware
                    break
        await message.channel.send(mostRecentMsg)
    else:
        await message.channel.send("Please enter a member's name.")

async def list_channels(client, message):
    listOfChannels = message.guild.text_channels
    for val in listOfChannels:
        await message.channel.send(str(val) + ' ' + str(val.position))
    
##############################
#       IN DEVELOPMENT       #
##############################

##############################

# !messagemembers
async def dm_activity(client, message):
    role = get_role(message)
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Central'))
    if role != None:
        dm_activity = []
        for member in role.members: 
            if member.dm_channel == None:
                await member.create_dm()
            dm = member.dm_channel
            msg = await dm.send(content = 'This is an automated message from Shrouded VII. Please respond to this with a message to avoid the monthly inactivity purge. You have until ' + str((right_now + timedelta(days=2)).strftime('%H:%M %p %Z, %A, %B %d, %Y')) + ' (48 hours) to respond. Thank you!')
            def check(m):
                return any(m.content) and m.author != client.user and m.channel == dm
            try:
                await client.wait_for('message', timeout=60.0, check=check)
            except asyncio.TimeoutError:
                await msg.edit(content = 'You did not respond in time and have been marked for inactivity. In the event you are kicked, you can rejoin the clan at any time by reapplying on Bungie.net and in the Discord by @-ing Persepolis or Lavender.')
                dm_activity.append([message.author.name,False,'N/A'])
            else:
                await msg.edit(content = 'You\'ve been marked for activity. Thanks for staying active in the community!')
                async for r in dm.history(limit = 1, oldest_first = False):
                    if r.author == member:
                        response = r
                    else:
                        response = 'Response not found.'
                dm_activity.append([message.author.name,True,response.content])
            dm_activity_df = pd.DataFrame(data = dm_activity, columns = ['Name','Active','Response'])
            print(dm_activity_df)
            print(dm_activity)
        await message.channel.send('Done!')
    else:
        await message.channel.send('Please enter a valid role.')
            
async def test_message(client, message):
    dm_activity = []
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Central'))
    #dm_check = pd.DataFrame(columns = ['discord_name','active','response'])
    if message.author.dm_channel == None:
        await message.author.create_dm()
    dm = message.author.dm_channel
    msg = await dm.send(content = 'This is an automated message from Shrouded VII. Please respond to this with a message to avoid the monthly inactivity purge. You have until ' + str((right_now + timedelta(days=2)).strftime('%H:%M %p %Z, %A, %B %d, %Y')) + ' (48 hours) to respond. Thank you!')
    def check(m):
        return any(m.content) and m.author != client.user and m.channel == dm
    try:
        await client.wait_for('message', timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await msg.edit(content = 'You did not respond in time and have been marked for inactivity. In the event you are kicked, you can rejoin the clan at any time by reapplying on Bungie.net and in the Discord by @-ing Persepolis or Lavender.')
        dm_activity.append([message.author.name,False,'N/A'])
    else:
        await msg.edit(content = 'You\'ve been marked for activity. Thanks for staying active in the community!',delete_after = 10.0)
        async for r in dm.history(limit = 1, oldest_first = False):
            response = r
        dm_activity.append([message.author.name,True,response.content])
    dm_activity_df = pd.DataFrame(data = dm_activity, columns = ['Name','Active','Response'])
    print(dm_activity_df)
    print(dm_activity)
    #msg = message(content = 'This is a test DM.')
    #await msg.edit ('15 seconds have elapsed.')