#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:09:42 2019

@author: rmoctezuma
"""

import pandas as pd
import discord
from datetime import datetime, timedelta
import pytz
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
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


### Upload dictionary to DCotW spreadsheet as new sheet
def dict_update(dictionary,sheet,sh_title,sort):
    df = pd.DataFrame.from_dict(dictionary,orient='index',columns=['value'])
    df = df.sort_values(by='value',ascending=False) if sort == True else df
    try:
        sheet.del_worksheet(sheet.worksheet(sh_title))
    except:
        pass
    worksheet = sheet.add_worksheet(title=str(sh_title),rows=str(len(df)),cols='2')
    cell_list = worksheet.range('A1:B' + str(len(df)))
    row_counter = 0
    for index,row in df.iterrows():
        cell_list[row_counter].value = str(index)
        cell_list[row_counter + 1].value = str(row['value'])
        row_counter += 2
    worksheet.update_cells(cell_list)
    
async def update_dcotw(run_mode,client):
    
    # Set the mode
    print('Running in mode {}.'.format(run_mode))
    run_server = 100291727209807872 if run_mode == 'PC' else 742246399697092618
    # Get the channel for the staff log 
    log_channel = client.get_guild(STAFF_GUILD).get_channel(STAFF_CHANNEL)
    # Now get the guild to process
    server = client.get_guild(run_server)
    print('Server: ' + server.name)
    print('Commencing DCotW updates.')
    await log_channel.send('Starting {} DCotW updates at {}...'.format(run_mode, datetime.now(pytz.timezone('US/Central')).strftime('%H:%M:%S %Z on %b %d, %Y')))
    
    results = []
    ctg_totals = {}
    activity_cutoff = datetime.now() - timedelta(days=7)
    #Single category mode --> category = get_category(message)
    for category in server.categories:
        print("Category: {}".format(category.name))
        ctg_dict = {}
        chl_dict = {}
        for channel in category.channels:
            if channel.type == discord.ChannelType.text:
                try:
                    history = await channel.history(limit = 25000, after = activity_cutoff, oldest_first = False).flatten()
                    if len(history) > 24999:
                        chl_dict[channel.name] = 25000
                    else:
                        chl_dict[channel.name] = len(history)
                except:
                    chl_dict[channel.name] = 'Inaccessible.'
        total = 0
        for val in chl_dict.values():
            if type(val) is int:
                total += val
        chl_dict['Total Messages'] = total
        ctg_dict[category.name] = chl_dict
        ctg_totals[category.name] = total
        results.append(ctg_dict)
    
    ### Google Sheets
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(google_keys_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open('SGC DCotW ' + run_mode)
    
    dict_update(ctg_totals,sheet,'Category Totals',True)
    print("Uploaded category totals to Google Sheets, sleeping 5 seconds...")
    time.sleep(5)
    
    for category in results:
        for cat_name in category.keys():
            dict_update(category[cat_name],sheet,str(cat_name),False)
            print("Uploaded category {} to Google Sheets, sleeping 5 seconds...".format(cat_name))
            time.sleep(5)
    
    print('DCotW updates completed.')
    await log_channel.send("{} DCotW updates completed at {}!".format(run_mode, datetime.now(pytz.timezone('US/Central')).strftime('%H:%M:%S %Z on %b %d, %Y')))
    
    return results

