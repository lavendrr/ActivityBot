# -*- coding: utf-8 -*-
"""
Activity Bot created for the Shrouded Gaming Community
Author: Ricardo Moctezuma (Lavender) - Admin of Shrouded VII
Contributors: Roberto Moctezuma
"""

import discord
import asyncio
from datetime import datetime
import pytz
import bot_toolkit as bot

# Start the BOT!

client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    # MAIN FUNCTIONS
    #### !SHEET UPDATES
    if message.content.startswith('!updatesheets'):
        await bot.update_sheets(client, message)
    #### !DCotW UPDATES
    if message.content.startswith('!update_dcotw'):
        await bot.update_dcotw(client, message)
    if message.content.startswith('!channelactivity'):
        await bot.channel_activity(client, message)
#    if message.content.startswith('!leaderboard'):
#        await bot.update_leaderboard(client, message)

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
    
    #CREATE
    if message.content.startswith('!leaderboard create'):
        bot_member = discord.utils.get(message.guild.members, discriminator = client.user.discriminator)
        lb_dict = {}
        
        def check(m):
            return any(m.content) and m.author == message.author and m.channel == message.channel

        msg = await message.channel.send('Please enter the title for the leaderboard.')
        next_stage = False

        # Stage 1. Get the leaderboard title.
        try:
            data = await client.wait_for('message', timeout=120.0, check=check)
            lb_dict['Title'] = data.content
            text = 'The leaderboard will be titled {}.\n\nPlease #mention the channels you wish to generate the leaderboard from. Ensure the bot has permissions to view these channels.'.format(data.content)
            try:
                await data.delete(delay=0.5)
                await msg.edit(content = text)
            except discord.Forbidden:
                await message.channel.send(content = text)
            next_stage = True
        except asyncio.TimeoutError:
            await msg.edit(content = 'You did not respond in time. Please try again.')

        # Stage 2. Get the channel data
        repeat = True
        multiple_tries = False
        if next_stage == True:
            while repeat == True:
                try:
                    data = await client.wait_for('message', timeout=120.0, check=check)
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
                                await message.channel.send(content = text)
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
                    data = await client.wait_for('message', timeout=120.0, check=check)
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
                                await message.channel.send(content = text)
                            repeat = False
                            next_stage = True
                    else:
                        await message.channel.send(content = 'Error getting channel mention. Please try again.')
                        multiple_tries = True
                except asyncio.TimeoutError:
                    await msg.edit(content = 'You did not respond in time. Please try again.')
                    repeat = False
        
        '''else:
            await msg.edit(content = 'Please # mention the channel where you want the leaderboard. Please ensure the bot has permissions to send messages in this channel.')
            async for r in message.channel.history(limit = 1, oldest_first = False):
                if r.author == message.author:
                    if r.channel_mentions != None or r.channel_mentions != []:
                        response = r.channel_mentions[0]
                    else:
                        await message.channel.send('Please enter a valid channel mention.')
                else:
                    response = 'Response not found.'
            lb_dict.append(response)'''
        '''try:
            await client.wait_for('message', timeout=120.0, check=check)
        except asyncio.TimeoutError:
            await msg.edit(content = 'Leaderboard created!')'''

    
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