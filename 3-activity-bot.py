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
import requests




#BOT_TOKEN = "NTg0ODE4NjA4ODU3OTM5OTc5.XP8kHw.Beigr96LwAu69_hxbBdhW5RzIIE"
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

def get_bungie_data(clan_id): #3007121
    # Get the data!
    bungie_api = "https://www.bungie.net/Platform"
    api_key = "92fffbf33c304661b4766556741d0800"    
    call = "/GroupV2/" + clan_id + "/Members/"
    
    # Get the data from the API
    response = requests.get(bungie_api + call, headers =  { 'X-API-Key' : api_key })
    
    # Convert the JSON response to a Pandas dataframe and extract results
    df = pd.read_json(response.text)
    results = df.loc['results','Response']
    
    # Now extract the goodies!
    clan = pd.DataFrame(results,columns = ['memberType','isOnline','lastOnlineStatusChange','groupId','destinyUserInfo',
                                           'bungieNetUserInfo','joinDate'])
    clan['destinyDisplayName'] = clan.apply(lambda x: x.destinyUserInfo['displayName'],axis=1)
    clan['destinyMembershipType'] = clan.apply(lambda x: x.destinyUserInfo['membershipType'],axis=1)
    clan['destinyMembershipId'] = clan.apply(lambda x: x.destinyUserInfo['membershipId'],axis=1)
    clan['bungieSupplementalDisplayName'] = clan.apply(lambda x: x.bungieNetUserInfo['supplementalDisplayName'],axis=1)
    clan['bungieIconPath'] = clan.apply(lambda x: x.bungieNetUserInfo['iconPath'],axis=1)
    clan['bungieMembershipType'] = clan.apply(lambda x: x.bungieNetUserInfo['membershipType'],axis=1)
    clan['bungieMembershipId'] = clan.apply(lambda x: x.bungieNetUserInfo['membershipId'],axis=1)
    clan['bungieDisplayName'] = clan.apply(lambda x: x.bungieNetUserInfo['displayName'],axis=1)
    
    # Convert naive datetime to date-aware
    clan['lastOnline'] = pd.to_datetime(clan.lastOnlineStatusChange, unit = 's').dt.tz_localize('UTC')
    
    # Convert to US Central
    clan['lastOnline'] = clan.lastOnline.dt.tz_convert('US/Central')
    right_now = pytz.utc.localize(datetime.utcnow()).astimezone(pytz.timezone('US/Central'))
    clan['active'] = (right_now - clan.lastOnline).dt.days
    clan = clan[['destinyDisplayName','memberType','lastOnline','active']]
    return clan

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
    if message.content.startswith('!roleactivity'):
        # Get the activity
        role = get_role(message)
        if role != None:
            member_list = []
            listOfChannels = message.guild.text_channels
            i = 0
            for member in role.members:
                i = i + 1
                if (i> 10):
                    break
                mostRecentMsg = None
                for val in listOfChannels:
                    try:
                        async for m in val.history():
                            if m.author == member:
                                msgAware = pytz.utc.localize(m.created_at).astimezone(pytz.timezone('US/Central'))
                                if mostRecentMsg == None:
                                    mostRecentMsg = msgAware
                                elif msgAware > mostRecentMsg:
                                    mostRecentMsg = msgAware
                                break
                    except (Exception) as e:
                        pass
                        print("Skipping channel {}, user {} has no access to it.".format(str(val), member.name))
                isActive = False
                if mostRecentMsg != None:
                    if (pytz.utc.localize(datetime.now()).astimezone(pytz.timezone('US/Central')) - timedelta(days=14)) < mostRecentMsg:
                        isActive = True
                member_data = { "member" :  member.name, "mostRecentMsg" : mostRecentMsg, "active" : isActive }
                member_list.append(member_data)
                await message.channel.send(member.name + ' - ' + str(mostRecentMsg))
            member_df = pd.DataFrame(member_list, columns = ['member','mostRecentMsg','active'])
            # Now get Bungie info
            bungie_info = get_bungie_data("3007121")
            # Merge them
            all_data = bungie_info.merge(member_df, how = 'outer', left_on='destinyDisplayName', right_on='member')
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

