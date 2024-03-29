#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 20 11:03:06 2019

@author: rmoctezuma
"""


import discord
import asyncio
import pytz
import bot_toolkit as bot
import pandas as pd
from datetime import datetime
from random import randrange
from ast import literal_eval

async def lb_create(client,message):
    bot_member = discord.utils.get(message.guild.members, id = client.user.id)
    lb_dict = {}
    time_out = 120.0
    
    def check(m):
        return any(m.content) and m.author == message.author and m.channel == message.channel

    msg = await message.channel.send('Please enter the title for the leaderboard.')
    next_stage = False

    # Stage 1. Get the leaderboard title.
    try:
        data = await client.wait_for('message', timeout=time_out, check=check)
        lb_dict['Title'] = data.content
        text = 'The leaderboard will be titled {}.\n\nPlease #mention the channels you wish to generate the leaderboard from. Ensure the bot has permissions to view these channels.'.format(data.content)
        try:
            await data.delete(delay=0.5)
            await msg.edit(content = text)
        except discord.Forbidden:
            msg = await message.channel.send(content = text)
        next_stage = True
    except asyncio.TimeoutError:
        await msg.edit(content = 'You did not respond in time. Please try again.')

    # Stage 2. Get the channel data
    repeat = True
    multiple_tries = False
    if next_stage == True:
        while repeat == True:
            try:
                data = await client.wait_for('message', timeout=time_out, check=check)
                has_perms = True
                channel_list = []
                mentions = ''
                if len(data.channel_mentions) >= 1:
                    for s in data.channel_mentions:
                        chl = discord.utils.get(message.guild.text_channels, mention = s.mention)
                        if chl.permissions_for(bot_member).read_messages == False:
                            await message.channel.send('The bot cannot read messages in {}. Please try again.'.format(s))
                            multiple_tries = True
                            has_perms = False
                        else:
                            channel_list.append(chl.id)
                            mentions += (' ' + chl.mention)
                    if has_perms == True:
                        lb_dict['Channel Data'] = channel_list
                        text = 'The leaderboard will pull messages from{}.\n\nPlease #mention the channel where you wish the leaderboard to be posted.'.format(mentions)
                        try:
                            if multiple_tries == True:
                                raise NameError
                            await data.delete(delay=0.5)
                            await msg.edit(content = text)
                        except(discord.Forbidden, NameError):
                            msg = await message.channel.send(content = text)
                        repeat = False
                        next_stage = True
                else:
                    await message.channel.send(content = 'Error getting channel mentions. Please try again.')
                    multiple_tries = True
            except asyncio.TimeoutError:
                await msg.edit(content = 'You did not respond in time. Please try again.')
                repeat = False
            
    # Stage 3. Get the leaderboard location
    repeat = True
    multiple_tries = False
    if next_stage == True:
        while repeat == True:
            next_stage = False
            try:
                data = await client.wait_for('message', timeout=time_out, check=check)
                if len(data.channel_mentions) > 1:
                    await message.channel.send('Please only mention one channel. Please try again.')
                    multiple_tries = True
                elif len(data.channel_mentions) == 1:
                    #await message.channel.send(str(data.channel_mentions[0].mention))
                    chl = discord.utils.get(message.guild.text_channels, mention = data.channel_mentions[0].mention)
                    if chl.permissions_for(bot_member).read_messages == False:
                        await message.channel.send('The bot cannot read messages in that channel. Please try again.')
                        multiple_tries = True
                    elif chl.permissions_for(bot_member).send_messages == False:
                        await message.channel.send('The bot cannot send messages in that channel. Please try again.')
                        multiple_tries = True
                    else:
                        lb_dict['Leaderboard Channel'] = chl.id
                        text = 'The leaderboard will be posted in {}.\n\n{}'.format(chl.mention,str(lb_dict))
                        try:
                            if multiple_tries == True:
                                raise NameError
                            await data.delete(delay=0.5)
                            await msg.edit(content = text)
                        except(discord.Forbidden, NameError):
                            msg = await message.channel.send(content = text)
                        repeat = False
                        next_stage = True
                else:
                    await message.channel.send(content = 'Error getting channel mention. Please try again.')
                    multiple_tries = True
            except asyncio.TimeoutError:
                await msg.edit(content = 'You did not respond in time. Please try again.')
                repeat = False
    
    if next_stage == True:
        lb_csv = pd.read_csv('leaderboards.csv',converters={'Channel Data': literal_eval}).set_index('Unnamed: 0')
        lb_dict['Message ID'] = 0
        lb_id = randrange(1000)
        while lb_id in lb_csv.index:
            lb_id = randrange(1000)
        lb_csv.loc[lb_id] = lb_dict
        lb_csv.to_csv('leaderboards.csv')
        print('Saved leaderboard {} to csv.'.format(lb_id))
        await update_leaderboard(client,lb_id)
    
async def update_leaderboard(client,lb_id):
    print('Starting lb process...')
    lb_csv = pd.read_csv('leaderboards.csv',converters={'Channel Data': literal_eval}).set_index('Unnamed: 0')
    # Retrieving Discord objects from CSV data
    channel_list = []
    for a in lb_csv.at[lb_id,'Channel Data']:
        channel_list.append(client.get_channel(int(a)))
    lb_channel = client.get_channel(int(lb_csv.at[lb_id,'Leaderboard Channel']))
    if lb_csv.at[lb_id,'Message ID'] != 0:
        print('Fetching message with ID {} in channel with ID {}...'.format(int(lb_csv.at[lb_id,'Message ID']),int(lb_csv.at[lb_id,'Leaderboard Channel'])))
        lb_message = await lb_channel.fetch_message(int(lb_csv.at[lb_id,'Message ID']))
    else:
        lb_message = None
        
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Eastern'))
    time_since_tues = bot.time_since_tuesday(right_now)
    
    # Start check
    if channel_list != []:
        try:
            activity_cutoff = datetime.now() - time_since_tues
            leaderboard = {}
            for a in channel_list:
                history = await a.history(limit = 25000, after = activity_cutoff, oldest_first = False).flatten()
                for m in history:
                    if m.author.display_name in leaderboard:
                        leaderboard[m.author.display_name] += 1
                    else:
                        leaderboard[m.author.display_name] = 1
                
            mention_list = ''
            for a in channel_list:
                mention_list += (a.mention + ' ')
                
            lb_sorted = {}

            count = 0
            for key, value in sorted(leaderboard.items(), key=lambda item: item[1], reverse = True):
                if count < 10:
                    lb_sorted[key] = value
                    count += 1
                else:
                    break
                
            lb_string = ''
            for item, amount in lb_sorted.items():
                lb_string += ('{} - {} messages\n'.format(item, amount))
            
            embed = discord.Embed(title='__**{}**__'.format(str(lb_csv.at[lb_id,'Title'])), colour=discord.Colour(0xf58027), description=(lb_string), timestamp=pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Eastern')))

            embed.set_thumbnail(url='https://www.freepnglogos.com/uploads/discord-logo-png/discord-orange-icon-23.png')
            embed.set_author(name='SGC Activity Bot', icon_url=client.user.avatar)
            embed.set_footer(text='Developed by Lavender', icon_url=client.get_user(329382120344518656).avatar)
            
            embed.add_field(name='ID', value=str(lb_id))
            embed.add_field(name='Channels', value=mention_list)
            
            if lb_message != None:
                await lb_message.edit(content = '', embed=embed)
            else:
                lb_message = await lb_channel.send(content = '', embed = embed)

                lb_csv.loc[lb_id,'Message ID'] = lb_message.id
                lb_csv.to_csv('leaderboards.csv')
                print('Leaderboard with ID {} created.'.format(lb_id))
            print('LB process complete.')
        except:
            pass
    else:
        print('Channel list not found.')

async def delete_leaderboard(client,lb_id):
    lb_csv = pd.read_csv('leaderboards.csv',converters={'Channel Data': literal_eval}).set_index('Unnamed: 0')
    lb_channel = client.get_channel(int(lb_csv.at[lb_id,'Leaderboard Channel']))
    lb_message = await lb_channel.fetch_message(int(lb_csv.at[lb_id,'Message ID']))
    await lb_message.delete()
    lb_csv.drop(index=lb_id,inplace=True)
    lb_csv.to_csv('leaderboards.csv')
    print('Deleted leaderboard {}.'.format(lb_id))
    
# REFERENCE
'''
df2 = pd.read_csv('leaderboards.csv').set_index('Unnamed: 0')
csv_dict = df2.to_dict(orient='index')
message.channel.send(str(csv_dict))

Dictionary to single-row DF
df = pd.DataFrame({k: [v] for k, v in test.items()})

Save to CSV
df.to_csv('leaderboards.csv')

Read DF back from CSV
df = pd.read_csv('leaderboards.csv',converters={'Channel Data': literal_eval}).set_index('Unnamed: 0')

Dict from DF
dictionary = df.to_dict(orient='index')

Access item from DF
df.at[index,column]
'''