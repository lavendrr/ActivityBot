# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import pandas as pd
import discord
from datetime import datetime, timedelta
import pytz
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import time

BOT_TOKEN = "NTg0ODM3NTg4NjQ1MzE0NTYz.XPQugQ.4-TLXdoVN0Ca84xaLo4kGoG7Bhk"

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
    
# Start the BOT!

client = discord.Client()

######################################################
# Google Sheet Access

def get_clan_list():
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('google_keys.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("SGC Clans List").worksheet('Key')
    clan_data = sheet.get_all_records()
    clan_df = pd.DataFrame(clan_data,columns = ['Name','Tag','ID','Platform','Key'])
    return clan_df

def upload_clan(sh_title, clan_df):
    df = clan_df.copy()
    df.sort_values(by=['memberType','member'],ascending=[False,True],inplace=True)
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('google_keys.json', scope)
    client = gspread.authorize(creds)
    sheet = client.open("SGC Clans List")
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
    api_key = "92fffbf33c304661b4766556741d0800"    
    call = "/GroupV2/" + str(clan_id) + "/Members/"
    
    # Get the data from the API
    response = requests.get(bungie_api + call, headers =  { 'X-API-Key' : api_key })
    
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
    clan['game_active'] = ((right_now - clan.lastOnline).dt.days <= 14)
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
    #### !ALLACTIVITY
    if message.content.startswith('!allactivity'):
        # Get the clan list
        clan_list = get_clan_list()
        # Get a dataframe with the discord names - it's just one Discord server, set them all as Inactive now
        member_list = []
        for index,clan in clan_list.iterrows():
            # The different clans are identified as roles
            print("Getting members of clan {}".format(clan.Tag))
            discord_clan = discord.utils.get(message.guild.roles, name=clan.Tag)
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
        # Lets now get the Bungie data
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
        all_data['clan'] = all_data.apply(lambda x: x.bungie_clan if not pd.isnull(x.bungie_clan) else x.discord_clan, axis=1)
        
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
            upload_clan(clan.Tag, clan_data)
            print("Uploaded clan {} to Google Sheets, sleeping for 30 secs...".format(clan.Tag))
            time.sleep(10)
            
        if len(all_data[all_data.clan == '[NONE]'])>0:
            clan_data = all_data[all_data.clan == '[NONE]']
            clan_data = clan_data[['member','destinyDisplayName','memberType','game_active','discord_active']]
            upload_clan('[NONE]',clan_data)
        await message.channel.send("Done!")
        
    if message.content.startswith('!roleactivity'):
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
            await message.channel.send('Done!')
        else:
            await message.channel.send("Please enter a valid role.")

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(BOT_TOKEN)

