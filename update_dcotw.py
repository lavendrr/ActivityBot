#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:15:25 2019

@author: rmoctezuma
"""

import discord
from datetime import datetime
import pytz
import sys
import getopt
import dcotw_toolkit as dcotw
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

handler = logging.FileHandler(filename='update_dcotw.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

logger.addHandler(handler)
logger.addHandler(consoleHandler)

# Start the bot

intents = discord.Intents.default()
intents.members = True

client = discord.Client(intents=intents)


# Default is to run the code in PC mode
run_mode = 'PC'
run_server = 100291727209807872

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
        await dcotw.update_dcotw(run_mode,client)
        print('------')
        print('Logging out.')
        print('Time: {}'.format(datetime.now(pytz.timezone('US/Central')).strftime('%H:%M:%S %Z on %b %d, %Y')))
        sys.exit()
        
def main(argv):
    global run_mode, run_server
    
    try:
        opts, args = getopt.getopt(argv,"r:",["run_mode="])
    except getopt.GetoptError:
        print('update_dcotw.py -r <PC/CONSOLE>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-r','--run_mode'):
            run_mode = arg
    
    print('Attempting to log in with token: {}'.format(dcotw.bot_token))
    client.run(dcotw.bot_token)
    if client.user is None:
        sys.exit('Couldn\'t log in.')
        
if __name__ == "__main__":
    main(sys.argv[1:])

        
