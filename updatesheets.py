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
import getopt
import us_toolkit

client = discord.Client()

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
        await us_toolkit.update_sheets(run_mode,client)
        print('------')
        print('Logging out.')
        print('Time: {}'.format(datetime.now(pytz.timezone('US/Central')).strftime('%H:%M:%S %Z on %b %d, %Y')))
        sys.exit()

def main(argv):
    global run_mode, run_server
    
    try:
        opts, args = getopt.getopt(argv,"r:",["run_mode="])
    except getopt.GetoptError:
        print('updatesheets.py -r <PC/CONSOLE>')
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-r','--run_mode'):
            run_mode = arg
    
    print('Attempting to log in with token: {}'.format(us_toolkit.bot_token))
    client.run(us_toolkit.bot_token)
    if client.user is None:
        sys.exit('Couldn\'t log in.')
        
if __name__ == "__main__":
    main(sys.argv[1:])

        
