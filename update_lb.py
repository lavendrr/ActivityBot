#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Sep 11 11:01:09 2019

@author: rmoctezuma
"""

import discord
from datetime import datetime
import pytz
import sys
import bot_toolkit as bot
import lb_toolkit as lb
import pandas as pd
from ast import literal_eval
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename='update_lb.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handler)
logger.addHandler(consoleHandler)

# Start the bot

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)

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
        lb_csv = pd.read_csv('leaderboards.csv',converters={'Channel Data': literal_eval}).set_index('Unnamed: 0')
        for lb_id in lb_csv.index:
            print('Updating leaderboard with ID {}.'.format(lb_id))
            await lb.update_leaderboard(client,lb_id)
        print('------')
        print('Logging out.')
        print('Time: {}'.format(datetime.now(pytz.timezone('US/Central')).strftime('%H:%M:%S %Z on %b %d, %Y')))
        sys.exit()

client.run(bot.bot_token)