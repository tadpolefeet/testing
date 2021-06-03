import requests
import json
import datetime
from datetime import timezone
count = 100
my_headers = {'X-API-Key' : 'f244e1ebd3864a67b3d02b1dc79edce0'}
membershipType = 3
rootList = ['4611686018468885977']
dupeList = []
activityIdList = []
current_date = datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d")
current_time = datetime.datetime.now(timezone.utc).strftime("%H%M")
minutetime = 60*int(current_time[0:2]) + int(current_time[2:4])


def API(main):
    response = requests.get(main,headers=my_headers)
    json_data = json.loads(response.text)
    return(json_data)


def Check_Player(rootList):
    try:
        destinyMembershipId = rootList.pop(0)
        print('Tried:', destinyMembershipId, f'    Currently {len(rootList)} players in list')
        destinyMembershipId = str(destinyMembershipId)
        if destinyMembershipId not in dupeList:
            dupeList.append(destinyMembershipId)
        parameters = ("?components=200")
        json_data = API(f'https://www.bungie.net/platform/Destiny2/3/Profile/{destinyMembershipId}/{parameters}')
        characterData = json_data['Response']['characters']['data']
        for item in characterData:
            getactivityhashes(destinyMembershipId, item)
    except:
        pass


def getactivityhashes(destinyMembershipId, characterId):
    parameters = '?count=3&mode=0&page=0'
    activities = API(f'https://www.bungie.net/Platform/Destiny2/3/Account/{destinyMembershipId}/Character/{characterId}/Stats/Activities/{parameters}')
    for activity in activities['Response']['activities']:
        PGCR(activity['activityDetails']['instanceId'])


def PGCR(activityId):
    Data = API(f'https://www.bungie.net/Platform/Destiny2/Stats/PostGameCarnageReport/{activityId}')
    ANALYSIS(Data, activityId)
    players = Data['Response']['entries']
    TempList = []
    for player in players:
        if 3 in player['player']['destinyUserInfo']['applicableMembershipTypes']:
            memberIdtoAppend = str(player['player']['destinyUserInfo']['membershipId']).replace("'", "")
            if memberIdtoAppend in dupeList:
                pass
            else:
                TempList.append(memberIdtoAppend)
    for item in TempList:
        rootList.append(item)
        if item not in dupeList:
            dupeList.append(item)


def ANALYSIS(Data, activityId):

    if activityId in activityIdList:
        pass

    else:
        try:
            activityIdList.append(activityId)
            game = {
                "modes": Data['Response']['activityDetails']['modes'],
            }
            players = dict()
            for j in range(len(Data['Response']['entries'])):
                p = Data['Response']['entries'][j]

                player_class = p['player']['characterClass']
                player_K = p['values']['kills']['basic']['value']
                player_D = p['values']['deaths']['basic']['value']
                player_A = p['values']['assists']['basic']['value']
                player_S = p['values']['score']['basic']['value']
                player_result = p['values']['standing']['basic']['displayValue']
                raw_loadout = p['extended']['weapons']
                player_loadout = dict()
                for i in range(len(raw_loadout)):
                    option = raw_loadout[i]
                    temp1 = {
                        "Hash": option['referenceId'],
                        "Kills": option['values']['uniqueWeaponKills']['basic']["value"],
                        "HS%": option['values']['uniqueWeaponKillsPrecisionKills']['basic']["value"]
                    }
                    player_loadout[f"Weapon {i}"] = temp1
                newdict = {
                    "Class": player_class,
                    "Kills": player_K,
                    "Deaths": player_D,
                    "Assists": player_A,
                    "Score": player_S,
                    "result": player_result,
                    "Loadout": player_loadout
                }
                players[f"Player {j + 1}"] = newdict

            if len(players) > 0:
                game["Players"] = players
                with open(f'D:d2_PGCR/{activityId}.json', 'w') as f:
                    f.write(str(game).replace("'",'"'))

        except:
            pass


while len(rootList) > 0 and count > 0:
    Check_Player(rootList)
    count -= 1
