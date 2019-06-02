# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""


import discord
import requests

discord_api_url = "https://discordapp.com/api/guilds/"
discord_server_id = "371340115932479499"

# 1. Register a client application and retrieve client_id and secret
CLIENT_ID = "584818608857939979"
CLIENT_SECRET = "9ki7LXsNZevTcryUQXk0t86_2ZdRQpcv"

# 2. Add a bot to the app, and get its token
BOT_NAME = "ActivityBot#7190"
BOT_TOKEN = "NTg0ODE4NjA4ODU3OTM5OTc5.XPQgbA.6aWNaAIlplXA_r1RC58NDN_LIOs"
# Permissions: View Channels, Read Message History, Send Messages, Manage Messages
BOT_PERMISSIONS = "76800"

# 3. To add the bot to the Discord server, go to:
BOT_URL = "https://discordapp.com/oauth2/authorize?client_id=" + CLIENT_ID + "&scope=bot" #&permissions=" + BOT_PERMISSIONS

# 4. Call the API endpoint

API_ENDPOINT = 'https://discordapp.com/api/v6'
GUILD_ID = "371340115932479499"

def get_api(endpoint):
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded',
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET
  }
  r = requests.get('%s/%s' % (API_ENDPOINT, endpoint), headers)
  r.raise_for_status()
  return r.json()


# Start the BOT!
  
client = discord.Client()

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.author == client.user:
        return
    if message.content.startswith('!hello'):
        msg = 'Hello {0.author.mention}'.format(message)
        await message.channel.send(msg)
                
@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

client.run(BOT_TOKEN)


## 2. Get Oauth2 authentication
#
#REDIRECT_URI = 'https://nicememe.website'
#

#@bot.command(pass_context=True)  
#async def getuser(ctx, role: discord.Role):
#    role = discord.utils.get(ctx.message.server.roles, name="mod")
#    if role is None:
#        await bot.say('There is no "mod" role on this server!')
#        return
#    empty = True
#    for member in ctx.message.server.members:
#        if role in member.roles:
#            await bot.say("{0.name}: {0.id}".format(member))
#            empty = False
#    if empty:
#        await bot.say("Nobody has the role {}".format(role.mention))