# -*- coding: utf-8 -*-
"""
Activity Bot created for the Shrouded Gaming Community
Author: Ricardo Moctezuma (Lavender) - Officer of Shrouded VII
Contributors: Roberto Moctezuma
"""

import pandas as pd
import asyncio
import discord
from datetime import datetime, timedelta
import pytz
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time
from enum import Enum

# Load credentials and tokens
creds = pd.read_csv('credentials/credentials.csv').set_index('key').transpose()
google_keys_file = 'credentials/google_keys.json'

def get_member(msg):
    arg_pos = msg.content.find(' ')
    if arg_pos > 0:
        arg = msg.content[arg_pos + 1:]
        member = discord.utils.get(msg.guild.members, name=arg)
    else:
        member = None
    return member

def get_role(msg):
    arg_pos = msg.content.find(' ')
    if arg_pos > 0:
        arg = msg.content[arg_pos + 1:]
        role = discord.utils.get(msg.guild.roles, name=arg)
    else:
        role = None
    return role

def get_channel(msg):
    arg_pos = msg.content.find(' ')
    if arg_pos > 0:
        arg = msg.content[arg_pos + 1:]
        channel = discord.utils.get(msg.guild.text_channels, mention=arg)
    else:
        channel = None
    return channel

# MULTIPLE CHANNEL GET
def get_multiple_channels(msg):
    a = msg.content.split(' | ')
    b = a[0].split(' ')
    c = a[1]
    del b[0]
    channel_list = []
    for d in b:
        channel_list.append(discord.utils.get(msg.guild.text_channels, mention = d))
    channel_list.append(discord.utils.get(msg.guild.text_channels, mention = c))
    return channel_list

# ACTIVITY LEADERBOARD
# SYNTAX = !leaderboard [# mention of channel to be checked], [#CHANNEL], [#CHANNEL] | [#CHANNEL TO POST LEADERBOARD MESSAGE IN]
async def update_leaderboard(message, lb_msg):
    channel_list = get_multiple_channels(message)
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Central'))
    # Time since Tuesday (Noon CST - Destiny 2 Reset)  
    # Tuesday Conditions      
    if right_now.weekday() == 1:
        if right_now.hour >= 12:
            time_since_tues = timedelta(hours = right_now.hour - 12, minutes = right_now.minute, days = 0)
        else:
            time_since_tues = timedelta(hours = right_now.hour + 12, minutes = right_now.minute, days = 6)
    # Non-Tuesday conditions
    else:
        if right_now.hour >= 12:
            time_since_tues = timedelta(hours = right_now.hour - 12, minutes = right_now.minute, days = right_now.weekday() - 1)
        else:
            time_since_tues = timedelta(hours = right_now.hour + 12, minutes = right_now.minute, days = right_now.weekday() - 2)
    # Start check
    if channel_list != []:
        try:
            activity_cutoff = datetime.now() - time_since_tues
            leaderboard = {}
            for a in channel_list[:len(channel_list) - 1]:
                history = await a.history(limit = 10000, after = activity_cutoff, oldest_first = False).flatten()
                for m in history:
                    if m.author.display_name in leaderboard:
                        leaderboard[m.author.display_name] += 1
                    else:
                        leaderboard[m.author.display_name] = 1
            lb_sorted = {}
            lb_string = '__**Shrouded Gaming Activity Leaderboard**__\n\n'
            count = 0
            for key, value in sorted(leaderboard.items(), key=lambda item: item[1], reverse = True):
                if count < 10:
                    lb_sorted[key] = value
                    count += 1
                else:
                    break
            for item, amount in lb_sorted.items():
                lb_string += ("{} - {} messages\n".format(item, amount))
            lb_string += ('\nUpdated ' + right_now.strftime('%H:%M %p %Z on %A, %B %d.'))
            # Auto-update
            await lb_msg.edit(content = lb_string)
        except:
            await message.channel.send('The bot does not have access to that channel.')
    else:
        await message.channel.send('That channel does not exist.')
# Start the BOT!

client = discord.Client()

######################################################
# Google Sheet Access

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
    cell_list[1].value = 'Destiny display name'
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

def get_bungie_data(clan_id):
    # Get the data!
    bungie_api = "https://www.bungie.net/Platform"
    call = "/GroupV2/" + str(clan_id) + "/Members/"
    
    # Get the data from the API
    response = requests.get(bungie_api + call, headers =  { 'X-API-Key' : creds.bungie_api[0] })
    
    # Convert the JSON response to a Pandas dataframe and extract results
    df = pd.read_json(response.text)
    results = df.loc['results','Response']
    
    # Now extract the goodies!
    clan = pd.DataFrame(results,columns = ['memberType','isOnline','lastOnlineStatusChange','groupId','destinyUserInfo',
                                           'bungieNetUserInfo','joinDate'])
    clan['destinyDisplayName'] = clan.apply(lambda x: x.destinyUserInfo['displayName'],axis=1)
 #   clan['destinyMembershipType'] = clan.apply(lambda x: x.destinyUserInfo['membershipType'],axis=1)
 #   clan['destinyMembershipId'] = clan.apply(lambda x: x.destinyUserInfo['membershipId'],axis=1)
 #   clan['bungieSupplementalDisplayName'] = clan.apply(lambda x: x.bungieNetUserInfo['supplementalDisplayName'],axis=1)
 #   clan['bungieIconPath'] = clan.apply(lambda x: x.bungieNetUserInfo['iconPath'],axis=1)
 #   clan['bungieMembershipType'] = clan.apply(lambda x: x.bungieNetUserInfo['membershipType'],axis=1)
 #   clan['bungieMembershipId'] = clan.apply(lambda x: x.bungieNetUserInfo['membershipId'],axis=1)
 #   clan['bungieDisplayName'] = clan.apply(lambda x: x.bungieNetUserInfo['displayName'],axis=1)
    
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
            m = member_df[((member_df.member.str.lower().str.contains(bungie_name.lower())==True)
                            & (member_df.discord_clan.str.lower() == bungie_clan.lower()))]
    if len(m) > 0:
        return m.member.iloc[0]
    return None

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await message.channel.send(msg)
#    if message.content.startswith('!inactive'):
#        msg = ', '.join(d2_inactive.member.tolist())
#        await message.channel.send(msg)
    if message.content.startswith('!jointime'):
        member = get_member(message)
        if member != None:
            await message.channel.send(member.name + ' joined on ' + member.joined_at.strftime('%m/%d/%Y') + '.')
        else:
            await message.channel.send("Please enter a member's name.")
    if message.content.startswith('!game'):
        member = get_member(message)
        if member != None:
            game_name = member.activities[0].name
            await message.channel.send(member.name + ' is currently playing '+ game_name + '.')
        else:
            await message.channel.send("Please enter a member's name.")
    if message.content.startswith('!emotes'):
        await message.channel.send(message.author.guild.emojis)
    if message.content.startswith('!memberactivity'):
        member = get_member(message)
        if member != None:
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
        else:
            await message.channel.send("Please enter a member's name.")
    if message.content.startswith('!listchannels'):
        listOfChannels = message.guild.text_channels
        for val in listOfChannels:
            await message.channel.send(str(val) + ' ' + str(val.position))
    ##############################
    # !messagemembers
    if message.content.startswith('!dmactivity'):
        role = get_role(message)
        right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Central'))
        if role != None:
            dm_activity = []
            for member in role.members: 
                if member.dm_channel == None:
                    await member.create_dm()
                dm = member.dm_channel
                msg = await dm.send(content = 'This is an automated message from Shrouded VII. Please respond to this with a message to avoid the monthly inactivity purge. You have until ' + str((right_now + timedelta(days=2)).strftime('%H:%M %p %Z, %A, %B %d, %Y')) + ' (48 hours) to respond. Thank you!')
                def check(m):
                    return any(m.content) and m.author != client.user and m.channel == dm
                try:
                    await client.wait_for('message', timeout=60.0, check=check)
                except asyncio.TimeoutError:
                    await msg.edit(content = 'You did not respond in time and have been marked for inactivity. In the event you are kicked, you can rejoin the clan at any time by reapplying on Bungie.net and in the Discord by @-ing Persepolis or Lavender.')
                    dm_activity.append([message.author.name,False,'N/A'])
                else:
                    await msg.edit(content = 'You\'ve been marked for activity. Thanks for staying active in the community!')
                    async for r in dm.history(limit = 1, oldest_first = False):
                        if r.author == member:
                            response = r
                        else:
                            response = 'Response not found.'
                    dm_activity.append([message.author.name,True,response.content])
                dm_activity_df = pd.DataFrame(data = dm_activity, columns = ['Name','Active','Response'])
                print(dm_activity_df)
                print(dm_activity)
            await message.channel.send('Done!')
        else:
            await message.channel.send('Please enter a valid role.')
    if message.content.startswith('!testmessage'):
        dm_activity = []
        right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Central'))
        #dm_check = pd.DataFrame(columns = ['discord_name','active','response'])
        if message.author.dm_channel == None:
            await message.author.create_dm()
        dm = message.author.dm_channel
        msg = await dm.send(content = 'This is an automated message from Shrouded VII. Please respond to this with a message to avoid the monthly inactivity purge. You have until ' + str((right_now + timedelta(days=2)).strftime('%H:%M %p %Z, %A, %B %d, %Y')) + ' (48 hours) to respond. Thank you!')
        def check(m):
            return any(m.content) and m.author != client.user and m.channel == dm
        try:
            await client.wait_for('message', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await msg.edit(content = 'You did not respond in time and have been marked for inactivity. In the event you are kicked, you can rejoin the clan at any time by reapplying on Bungie.net and in the Discord by @-ing Persepolis or Lavender.')
            dm_activity.append([message.author.name,False,'N/A'])
        else:
            await msg.edit(content = 'You\'ve been marked for activity. Thanks for staying active in the community!',delete_after = 10.0)
            async for r in dm.history(limit = 1, oldest_first = False):
                response = r
            dm_activity.append([message.author.name,True,response.content])
        dm_activity_df = pd.DataFrame(data = dm_activity, columns = ['Name','Active','Response'])
        print(dm_activity_df)
        print(dm_activity)
        #msg = message(content = 'This is a test DM.')
        #await msg.edit ('15 seconds has elapsed.')
    ##############################
    #### !ALLACTIVITY
    if message.content.startswith('!updatesheets'):
        # Get the clan list
        clan_list = get_clan_list()
        # Get a dataframe with the discord names - it's just one Discord server, set them all as Inactive now
        member_list = []
        for index,clan in clan_list.iterrows():
            # The different clans are identified as roles
            print("Getting members of clan {}".format(clan.Tag))
            # Check to see if the tag is ok
            listOfRoles = message.guild.roles
            current_clan_tag = clan.Tag
            for val in listOfRoles:
                if clan.Tag == str(val)[0:len(clan.Tag)]:
                    current_clan_tag = str(val)
            if len(current_clan_tag) != len(clan.Tag):
                print("Replaced {} with tag {}".format(clan.Tag,current_clan_tag))
            discord_clan = discord.utils.get(message.guild.roles, name=current_clan_tag)
            if (not discord_clan is None):
                for member in discord_clan.members:
                     member_data = { "discord_clan" : clan.Tag , "member" :  member.display_name, "discord_active" : False }
                     member_list.append(member_data)
        member_df = pd.DataFrame(member_list, columns = ['discord_clan', 'member', 'discord_active'])
        # Now loop through the messages, marking people who have messaged as Active
        activity_cutoff = datetime.now() - timedelta(days=14)
        listOfChannels = message.guild.text_channels
        max_messages_found = 0
        for channel in listOfChannels:
            try:
                history = await channel.history(limit = 10000, after = activity_cutoff, oldest_first = False).flatten()
                print("Processing channel {} with {} messages in the past 14 days.".format(str(channel), len(history)))
                if max_messages_found < len(history):
                    max_messages_found = len(history)
                for m in history:
                    member_df.loc[member_df.member == m.author.display_name,'discord_active'] = True
            except:
                pass
        # Let's now get the Bungie data
        print("Completed. Max messages per channel at {}/10000".format(max_messages_found))
        print("Beginning Bungie data process")
        all_bungie_data = pd.DataFrame()
        for index,clan in clan_list.iterrows():
            print("Getting members of clan {} with Bungie ID # {}".format(clan.Tag,clan.ID))
            # Get Bungie info
            bungie_info = get_bungie_data(clan.ID)
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
        print('Clan weekly activity sheet complete.')
        await message.channel.send("SGC weekly activity sheets completed!")
        
    '''if message.content.startswith('!roleactivity'):
        # Get the activity
        activity_cutoff = datetime.now() - timedelta(days=14)
        role = get_role(message)
        if role != None:
            member_list = []
            listOfChannels = message.guild.text_channels
            for member in role.members:
                member_data = { "member" :  member.display_name, "discord_active" : False }
                member_list.append(member_data)
            member_df = pd.DataFrame(member_list, columns = ['member', 'discord_active'])
            for channel in listOfChannels:
                try:
                    history = await channel.history(limit = 10000, after = activity_cutoff, oldest_first = False).flatten()
                    print("Processing channel {} with {} messages in the past 14 days.".format(str(channel), len(history)))
                    for m in history:
                        member_df.loc[member_df.member == m.author.display_name,'discord_active'] = True
                except:
                    pass
            # Now get Bungie info
            bungie_info = get_bungie_data("3007121")
            # Merge them
            bungie_info.destinyDisplayName = bungie_info.destinyDisplayName.str.lower()
            member_df.member = member_df.member.str.lower()
            bungie_info['discordName'] = bungie_info.apply(lambda x: 
                get_destiny_name(member_df,x.destinyDisplayName),axis=1)
            all_data = bungie_info.merge(member_df, how = 'outer', left_on='discordName', right_on='member')
            # Save the CSV
            all_data.to_csv('activity-list.csv')
            await message.channel.send('Done checking activity for ' + role.name + '.')
        else:
            await message.channel.send("Please enter a valid role.")'''
    if message.content.startswith('!channelactivity'):
        channel = get_channel(message)
        if channel != None:
            activity_cutoff = datetime.now() - timedelta(days=7)
            try:
                history = await channel.history(limit = 10000, after = activity_cutoff, oldest_first = False).flatten()
                if len(history) > 9999:
                    await message.channel.send('Channel {} has over 10,000 messages in the past 7 days.'.format(str(channel)))
                else:
                    await message.channel.send('Channel {} has {} messages in the past 7 days.'.format(str(channel), len(history)))
            except:
                await message.channel.send('The bot does not have access to that channel.')
        else:
            await message.channel.send('That role does not exist.')
    if message.content.startswith('!leaderboard'):
        channel_list = get_multiple_channels(message)
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Central'))
    # Time since Tuesday (Noon CST - Destiny 2 Reset)  
    # Tuesday Conditions      
    if right_now.weekday() == 1:
        if right_now.hour >= 12:
            time_since_tues = timedelta(hours = right_now.hour - 12, minutes = right_now.minute, days = 0)
        else:
            time_since_tues = timedelta(hours = right_now.hour + 12, minutes = right_now.minute, days = 6)
    # Non-Tuesday conditions
    else:
        if right_now.hour >= 12:
            time_since_tues = timedelta(hours = right_now.hour - 12, minutes = right_now.minute, days = right_now.weekday() - 1)
        else:
            time_since_tues = timedelta(hours = right_now.hour + 12, minutes = right_now.minute, days = right_now.weekday() - 2)
    # Start check
    if channel_list != []:
        try:
            activity_cutoff = datetime.now() - time_since_tues
            leaderboard = {}
            lb_channel = channel_list[len(channel_list) - 1]
            for a in channel_list[:len(channel_list) - 1]:
                history = await a.history(limit = 10000, after = activity_cutoff, oldest_first = False).flatten()
                for m in history:
                    if m.author.display_name in leaderboard:
                        leaderboard[m.author.display_name] += 1
                    else:
                        leaderboard[m.author.display_name] = 1
            msg = None
            lb_sorted = {}
            lb_string = '__**Shrouded Gaming Activity Leaderboard**__\n\n'
            count = 0
            for key, value in sorted(leaderboard.items(), key=lambda item: item[1], reverse = True):
                if count < 10:
                    lb_sorted[key] = value
                    count += 1
                else:
                    break
            for item, amount in lb_sorted.items():
                lb_string += ("{} - {} messages\n".format(item, amount))
            lb_string += ('\nUpdated ' + right_now.strftime('%H:%M %p %Z on %A, %B %d.'))
            async for m in lb_channel.history(limit = 2):
                if m.author == client.user:
                    msg = m
                    break
            if msg == None:
                await lb_channel.send(lb_string)
                time.sleep(1)
                await lb_channel.last_message.pin()
                time.sleep(1)
                await lb_channel.last_message.delete()
            else:
                await msg.edit(content = lb_string)
        except:
            await message.channel.send('The bot does not have access to that channel.')
    else:
        await message.channel.send('That channel does not exist.')
        
        
        
        
        '''channel_list = get_multiple_channels(message)
        right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Central'))
        # Time since Tuesday (Noon CST - Destiny 2 Reset)
        # Monday conditions
        if right_now.weekday() == 0 and right_now.hour >= 12:
            time_since_tues = timedelta(hours = right_now.hour - 12, minutes = right_now.minute, days = 6)
        elif right_now.weekday() == 0 and right_now.hour < 12:
            time_since_tues = timedelta(hours = right_now.hour + 12, minutes = right_now.minute, days = 5)
        # Other weekday conditions
        elif right_now.hour >= 12:
            time_since_tues = timedelta(hours = right_now.hour - 12, minutes = right_now.minute, days = (right_now.weekday() - 1))
        elif right_now.hour < 12:
            time_since_tues = timedelta(hours = right_now.hour + 12, minutes = right_now.minute, days = (right_now.weekday() - 2))
        # Start check
        if channel_list != []:
            activity_cutoff = datetime.now() - time_since_tues
            leaderboard = {}
            lb_channel = channel_list[len(channel_list) - 1]
            for a in channel_list[:len(channel_list) - 1]:
                history = await a.history(limit = 10000, after = activity_cutoff, oldest_first = False).flatten()
                for m in history:
                    if m.author.display_name in leaderboard:
                        leaderboard[m.author.display_name] += 1
                    else:
                        leaderboard[m.author.display_name] = 1
            lb_sorted = {}
            lb_string = '__**Shrouded Gaming Activity Leaderboard**__\n\n'
            count = 0
            for key, value in sorted(leaderboard.items(), key=lambda item: item[1], reverse = True):
                if count < 10:
                    lb_sorted[key] = value
                    count += 1
                else:
                    break
            for item, amount in lb_sorted.items():
                lb_string += ("{} - {} messages\n".format(item, amount))
            lb_string += ('\nUpdated ' + right_now.strftime('%H:%M %p %Z on %A, %B %d.'))
            # Auto-updating WIP
            await lb_channel.send(lb_string)
            time.sleep(1)
            lb_msg = lb_channel.last_message
            await lb_msg.pin()
            time.sleep(1)
            for a in await lb_channel.history(limit = 3).flatten():  
                if a.type == discord.MessageType.pins_add:
                    await a.delete()
            while lb_msg != None:
                time.wait(60)
                await update_leaderboard(message, lb_msg)
        else:
            await message.channel.send('That channel does not exist.')
        '''
    ### MEME COMMANDS
    """
    if message.content.startswith('!hoesmad'):
        x = 0
        while x < 3:
            await message.channel.send('hoes mad x' + str(x + 1))
            x += 1
    if message.content.startswith('!f'):
        await message.channel.send('F')
    if message.content.startswith('!bruh'):
        await message.channel.send('bruh moment')
    if message.content.startswith('!vii'):
        await message.channel.send('VII best clan')
    """
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(creds.bot_token[0])

