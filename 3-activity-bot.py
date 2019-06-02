# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import discord

BOT_TOKEN = "NTg0ODE4NjA4ODU3OTM5OTc5.XPQgbA.6aWNaAIlplXA_r1RC58NDN_LIOs"

# Start the BOT!


client = discord.Client()

# Read the INACTIVE data
csv_path = "/Users/rmoctezuma/AppDev/ActivityBot/"
d2_csv = pd.read_csv(csv_path + "processed.csv")
d2_inactive = d2_csv[d2_csv.Status.isna()]

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await message.channel.send(msg)
    if message.content.startswith('!inactive'):
        msg = ', '.join(d2_inactive.member.tolist())
        await message.channel.send(msg)
                
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(BOT_TOKEN)

