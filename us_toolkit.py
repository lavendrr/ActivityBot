#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 23:18:57 2019

@author: rmoctezuma
"""
import pandas as pd
import discord
from datetime import datetime, timedelta
import pytz
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
import sys
from random import randrange

# Constants
MAX_MESSAGES = 25000
RUN_CHANNEL = 594568388869881856
STAFF_GUILD = 601229332026753044
STAFF_CHANNEL = 629511503296593930

# Load credentials and tokens
import bot_toolkit as bot
bot_token = bot.bot_token
bungie_api_token = bot.bungie_api_token
google_keys_file = bot.google_keys_file

# Google Sheets

def get_clan_list():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(google_keys_file, scope)
    client = gspread.authorize(creds)
    keyfile_sheet = client.open("SGC Clans Key File").worksheet('Key')
    clan_data = keyfile_sheet.get_all_records()
    clan_df = pd.DataFrame(clan_data,columns = ['Name','Tag','ID','Platform','Key'])
    return clan_df

def upload_clan(sh_title, clan_df, platform):
    df = clan_df.copy()
    df.sort_values(by=['memberType','discord_active','game_active','member'],ascending=[False,False,False,True],inplace=True)
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(google_keys_file, scope)
    client = gspread.authorize(creds)
    sheet = client.open('SGC Activity ' + platform)
    try:
        worksheet = sheet.worksheet(sh_title)
        sheet.del_worksheet(worksheet)
    except:
        pass
    worksheet = sheet.add_worksheet(title=sh_title, rows= str(len(df) + 10), cols="10")
    cell_list = worksheet.range('A1:E' + str(len(df)+1))
    cell_list[0].value = 'Discord name'
    cell_list[1].value = 'Steam name'
    cell_list[2].value = 'Discord active'
    cell_list[3].value = 'Game active'     
    cell_list[4].value = 'Member type'
    row_counter = 0
    for index,m in df.iterrows():
        cell_list[row_counter*5 + 5].value = m.member
        cell_list[row_counter*5 + 6].value = m.destinyDisplayName
        cell_list[row_counter*5 + 7].value = m.discord_active
        cell_list[row_counter*5 + 8].value = m.game_active        
        cell_list[row_counter*5 + 9].value = m.memberType
        row_counter = row_counter + 1
    result = worksheet.update_cells(cell_list)
    return result

# Bungie

def get_bungie_data(client, clan_id, run_mode):
    log_channel = client.get_guild(STAFF_GUILD).get_channel(STAFF_CHANNEL)
    # Get the data!
    bungie_api = "https://www.bungie.net/Platform"
    call = "/GroupV2/" + str(clan_id) + "/Members/"
    data_ok = False
    retries = 0
    while not data_ok:
        try:
            # Get the data from the API
            response = requests.get(bungie_api + call, headers =  { 'X-API-Key' : bungie_api_token })
            # Convert the JSON response to a Pandas dataframe and extract results
            df = pd.read_json(response.text)
        except:
            retries += 1
            if retries < 10:
                sleep_for = 2 + randrange(0, min(300, 2**retries))
                time.sleep(sleep_for)
                print('Error reading Bungie API data. Retrying... #{}'.format(retries))
            else:
                print('Terminal error reading Bungie API data. {} sheets update failed.'.format(run_mode))
                log_channel.send('Terminal error reading Bungie API data. {} sheets update failed.'.format(run_mode))
                sys.exit()
        else:
            data_ok = True
            results = df.loc['results','Response']
    
    # Now extract the goodies!
    clan = pd.DataFrame(results,columns = ['memberType','isOnline','lastOnlineStatusChange','groupId','destinyUserInfo',
                                           'bungieNetUserInfo','joinDate'])
    clan['destinyDisplayName'] = clan.apply(lambda x: x.destinyUserInfo['displayName'],axis=1)
    
    # Convert naive datetime to date-aware
    clan['lastOnline'] = pd.to_datetime(clan.lastOnlineStatusChange, unit = 's').dt.tz_localize('UTC')
    
    # Convert to US Central
    clan['lastOnline'] = clan.lastOnline.dt.tz_convert('US/Central')
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Central'))
    clan['game_active'] = ((right_now - clan.lastOnline).dt.days <= 10)
    clan = clan[['destinyDisplayName','memberType','game_active']]
    return clan

def get_destiny_name(member_df, bungie_name, bungie_clan):
    # Get the members with an exact match first
    m = member_df[member_df.member == bungie_name]
    if len(m)==0:
        # No exact match, so try case insensitive
        m = member_df[member_df.member.str.lower() == bungie_name.lower()]
        if len(m) == 0:
            # Still no match, try contains [but in same clan]
            member_names = member_df.member.str.lower()
            m = member_df[((member_names.str.contains(bungie_name.lower(),regex=False)==True)
                            & (member_df.discord_clan.str.lower() == bungie_clan.lower()))]
    if len(m) > 0:
        return m.member.iloc[0]
    return None

# Update sheets
async def update_sheets(run_mode, client):
    # Set the mode
    print('Running in mode {}.'.format(run_mode))
    run_server = 100291727209807872 if run_mode == 'PC' else 614125874958303242
    # Get the channel for the staff log 
    log_channel = client.get_guild(STAFF_GUILD).get_channel(STAFF_CHANNEL)
    # Now get the guild to process
    server = client.get_guild(run_server)
    print('Server: ' + server.name)
    print('Commencing sheet updates.')
    await log_channel.send('Starting {} sheet updates at {}...'.format(run_mode, datetime.now(pytz.timezone('US/Central')).strftime('%H:%M:%S %Z on %b %d, %Y')))
    # Get the clan list
    clan_list = get_clan_list()
    # Select the subset of clans to process (PC or CONSOLE)
    if run_mode == 'PC':
        clan_list = clan_list[clan_list['Platform']=='PC']
    else:
        clan_list = clan_list[clan_list['Platform']!='PC']
    # Get a dataframe with the discord names - it's just one Discord server, set them all as Inactive now
    member_list = []
    for index,clan in clan_list.iterrows():
        # The different clans are identified as roles
        print("Getting members of clan {}".format(clan.Tag))
        # Check to see if the tag is ok
        listOfRoles = server.roles
        current_clan_tag = clan.Tag
        for val in listOfRoles:
            if clan.Tag == str(val)[0:len(clan.Tag)]:
                current_clan_tag = str(val)
        if len(current_clan_tag) != len(clan.Tag):
            print("Replaced {} with tag {}".format(clan.Tag,current_clan_tag))
        discord_clan = discord.utils.get(server.roles, name=current_clan_tag)
        if (not discord_clan is None):
            for member in discord_clan.members:
                 member_data = { "discord_clan" : clan.Tag , "member" :  member.display_name, "discord_active" : False }
                 member_list.append(member_data)
    member_df = pd.DataFrame(member_list, columns = ['discord_clan', 'member', 'discord_active'])
    # Now loop through the messages, marking people who have messaged as Active
    activity_cutoff = datetime.now() - timedelta(days=14)
    listOfChannels = server.text_channels
    max_messages_found = 0
    for channel in listOfChannels:
        try:
            history = await channel.history(limit = MAX_MESSAGES, after = activity_cutoff, oldest_first = False).flatten()
            print("Processing channel {} with {} messages in the past 14 days.".format(str(channel), len(history)))
            if max_messages_found < len(history):
                max_messages_found = len(history)
            for m in history:
                member_df.loc[member_df.member == m.author.display_name,'discord_active'] = True
        except:
            pass
    # Let's now get the Bungie data
    print("Completed. Max messages per channel at {}/{}".format(max_messages_found, MAX_MESSAGES))
    print("Beginning Bungie data process")
    all_bungie_data = pd.DataFrame()
    for index,clan in clan_list.iterrows():
        print("Getting members of clan {} with Bungie ID # {}".format(clan.Tag,clan.ID))
        # Get Bungie info
        bungie_info = get_bungie_data(client, clan.ID, run_mode)
        bungie_info['bungie_clan'] = clan.Tag
        bungie_info['discordName'] = bungie_info.apply(lambda x: get_destiny_name(member_df,x.destinyDisplayName, clan.Tag),axis=1)
        # Merge them
        all_bungie_data = pd.concat([all_bungie_data,bungie_info],axis = 0, ignore_index = True, sort = False)        
    
    # Save to a CSV for debugging
    all_bungie_data.to_csv('bungie.csv')
    member_df.to_csv('discord.csv')
    
    # Merge them
    all_data = all_bungie_data.merge(member_df, how = 'outer', left_on='discordName', right_on='member',indicator=True)
    
    all_data['clan'] = all_data.apply(lambda x: x.discord_clan if not pd.isnull(x.discord_clan) else x.bungie_clan, axis=1)
    
    all_data.clan.fillna(value='[NONE]',axis=0,inplace=True)
    all_data.member.fillna('',inplace=True)
    all_data.destinyDisplayName.fillna('',inplace=True)
    all_data.memberType.fillna(0,inplace=True)
    all_data.discord_active.fillna(False,inplace=True)
    all_data.game_active.fillna(False,inplace=True)
    
    # Save the CSV
    all_data.reset_index(drop=True,inplace=True)
    all_data.to_csv('activity.csv')
    
    for index,clan in clan_list.iterrows():
        clan_data = all_data[all_data.clan == clan.Tag]
        clan_data = clan_data[['member','destinyDisplayName','memberType','game_active','discord_active']]
        upload_clan(clan.Tag, clan_data, clan.Platform)
        print("Uploaded clan {} to Google Sheets, sleeping for 10 secs...".format(clan.Tag))
        time.sleep(10)
        
    if len(all_data[all_data.clan == '[NONE]'])>0:
        clan_data = all_data[all_data.clan == '[NONE]']
        clan_data = clan_data[['member','destinyDisplayName','memberType','game_active','discord_active']]
        upload_clan('[NONE]',clan_data, 'PC')
    print('Sheet updates completed.')
    await log_channel.send("{} sheet updates completed at {}!".format(run_mode, datetime.now(pytz.timezone('US/Central')).strftime('%H:%M:%S %Z on %b %d, %Y')))
