# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import discord
from datetime import datetime, timedelta
from pytz import timezone
import pytz

# BOT_TOKEN = "NTg0ODE4NjA4ODU3OTM5OTc5.XPQgbA.6aWNaAIlplXA_r1RC58NDN_LIOs"
BOT_TOKEN = "NTg0ODM3NTg4NjQ1MzE0NTYz.XPQugQ.4-TLXdoVN0Ca84xaLo4kGoG7Bhk"

# Start the BOT!


client = discord.Client()

# Read the INACTIVE data
# csv_path = "/Users/rmoctezuma/AppDev/ActivityBot/"
csv_path = "C:\\Users\\Lavender\\Documents\\GitHub\\ActivityBot\\"
d2_csv = pd.read_csv(csv_path + "processed.csv")
d2_inactive = d2_csv[d2_csv.Status.isna()]

@client.event
async def on_message(message):
    arg_pos = message.content.find(' ')
    if arg_pos > 0:
        arg = message.content[arg_pos + 1:]
        member = discord.utils.get(message.guild.members, name=arg)
    else:
        arg = ''
        member = None
        
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await message.channel.send(msg)
    if message.content.startswith('!inactive'):
        msg = ', '.join(d2_inactive.member.tolist())
        await message.channel.send(msg)
    if message.content.startswith('!jointime'):
        if arg == '':
            await message.channel.send("Please enter a member's name.")
        else:
            await message.channel.send(member.name + ' joined on ' + member.joined_at.strftime('%m/%d/%Y') + '.')
    if message.content.startswith('!game'):
        if arg == '':
            await message.channel.send("Please enter a member's name.")
        else:
            y = member.activities[0].name
            await message.channel.send(member.name + ' is currently playing '+ y + '.')
    if message.content.startswith('!emotes'):
        await message.channel.send(message.author.guild.emojis)
    if message.content.startswith('!memberactivity'):
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
    if message.content.startswith('!listchannels'):
        listOfChannels = message.guild.text_channels
        for val in listOfChannels:
            await message.channel.send(str(val) + ' ' + str(val.position))
    if message.content.startswith('!roleactivity'):
        # processes the message but looks for role instead of member
        # this should be made into a function that can be called per command to save space
        arg_pos = message.content.find(' ')
        if arg_pos > 0:
            arg = message.content[arg_pos + 1:]
            role = discord.utils.get(message.guild.roles, name=arg)
        else:
            arg = ''
            member = None
        listOfChannels = message.guild.text_channels
        for value in role.members:
            mostRecentMsg = None
            member = value
            for val in listOfChannels:
                async for m in val.history():
                    if m.author == member:
                        msgAware = pytz.utc.localize(m.created_at).astimezone(pytz.timezone('US/Central'))
                        if mostRecentMsg == None:
                            mostRecentMsg = msgAware
                        elif msgAware > mostRecentMsg:
                            mostRecentMsg = msgAware
                        break
            await message.channel.send(member.name + ' - ' + str(mostRecentMsg))
        await message.channel.send('Done!')

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(BOT_TOKEN)

