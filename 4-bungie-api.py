# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import requests
import pandas as pd
from datetime import datetime
import pytz

# Get the data!

bungie_api = "https://www.bungie.net/Platform"
api_key = "92fffbf33c304661b4766556741d0800"

#call = "/GroupV2/{groupId}/Members/"
call = "/GroupV2/3007121/Members/"

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

