# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import discord

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
    x = message.content.split()
    if len(x) == 2:
        u = x[1]
        member = discord.utils.get(message.guild.members, name=u)
        
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
        if len(x) != 2:
            await message.channel.send('Wrong # of arguments.')
        else:
            await message.channel.send(member.name + ' joined on ' + member.joined_at.strftime('%m/%d/%Y') + '.')
    if message.content.startswith('!activities'):
        if len(x) != 2:
            await message.channel.send('Wrong # of arguments.')
        else:
            y = member.activities[0].name
            await message.channel.send(member.name + ' is currently playing '+ y + '.')
    if message.content.startswith('!emotes'):
        await message.channel.send(message.author.guild.emojis)
    if message.content.startswith('!lastmsg'):
        async for message in message.channel.history():
            if message.author == member:
                await message.channel.send(message.created_at)
                break
#        async for message in member.history(limit=1):
#            z = message.created_at
#        await message.channel.send(z)
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(BOT_TOKEN)

