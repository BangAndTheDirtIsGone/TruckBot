# -*- coding: utf8 -*-
import discord
import asyncio
import json
import urllib.request
import random
import logging
import shlex
import threading
import hashlib
import os
import shutil
import math

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

client = discord.Client()
prefix = "truck!"
cmd = []
jsonret = ""
cachetime = 600 #Time in seconds before clearing main cache. Higher is better but delayed stats may show. Default: 600 seconds
cachetimesec = 60 #Time in seconds before clearing secondary cache. Higher is better but delayed stats may show. Default 60 seconds. Should be lower than main cache as shows more changing information

print("Using " + discord.__version__ + " version of discordpy")

async def addemoji(server,name,path):
    with open(path,"rb") as f:
        await client.create_custom_emoji(server=server,name=name,image=f.read())

def possibleint(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False
    
async def setplaying(str):
    print("Set playing to " + str)
    await client.change_presence(game=discord.Game(name=str))

def typing(message):
    client.send_typing(message.channel)

def urljson(url):
    urlresp = urllib.request.urlopen(urllib.request.Request(url,headers={"Accept":"*/*","User-Agent":"urllib2/1.0","Content-Type":"application/json","Cache=Control":"max-age=0"})).read()
    urldict = json.loads(urlresp)
    print("HTTP send to " + url)
    return urldict

def linked(m):
    return m.author == client.user or str(m.content).startswith(prefix)

def true(m):
    return True

def get_avatar_url(identifyer):
    if identifyer in cacheavatar:
        avatarurl = cacheavatar[identifyer]
        username = cachename[identifyer]
        print("[RCache] Read cachename." + identifyer)
        print("[RCache] Read cacheavatar." + identifyer)
        return avatarurl,username
    else:
        avatarurl = urljson("https://api.truckersmp.com/v2/player/" + identifyer)
        cacheavatar[identifyer] = avatarurl['response']['avatar']
        cachename[identifyer] = avatarurl['response']['name']
        print("[RCache] Set cacheavatar." + identifyer)
        print("[RCache] Set cachename." + identifyer)
        return get_avatar_url(identifyer)

def set_avatar_url(identifyer,url,name):
    if not (identifyer in cacheavatar):
        cacheavatar[identifyer] = url
        cachename[identifyer] = name
        print("[RCache] Set cacheavatar." + identifyer)
        print("[RCache] Set cachename." + identifyer)

# cacheing stuff

def clearcache():
    global cache
    cache = dict()
    cache['wotprofiles'] = dict() #1-wotprofiles
    cache['jobstats'] = dict() #2-jobstats
    cache['jobdetails'] = dict() #3-jobdetails
    cache['tmpprofile'] = dict() #4-tmpprofile
    cache['tmpbans'] = dict() #5-tmpbans
    cache['tmpversion'] = dict() #6-tmpversion
    cache['tmpavatar'] = dict() #7-ava
    print("[RCache] Cache Cleared")
    threading.Timer(cachetime,clearcache).start()

def clearcachesec():
    global cache2
    cache2 = dict()
    cache2['tmpservers'] = dict() #1-tmpservers
    cache2['tmptraffic'] = dict() #2-tmptraffic
    print("[RCache] Secondary Cache Cleared")
    threading.Timer(cachetimesec,clearcachesec).start()

def clearcacheava():
    global cacheavatar
    cacheavatar = dict()
    global cachename
    cachename = dict()
    print("[RCache] Avatar Cache Cleared")
    threading.Timer(18000,clearcacheava).start()

clearcache()
clearcachesec()
clearcacheava()

async def fiveminchecks():
    await setplaying("on " + str(len(client.servers)) + " servers! | " + prefix + "help")
    threading.Timer(300,fiveminchecks).start()

@client.event
async def on_ready():
    print("Restarted " + client.user.name + " [" + client.user.id + "]")
    await fiveminchecks()
    
    
@client.event
async def on_message(message):
    cmd = shlex.split(str(message.content))
    if message.author.bot == False:
        if cmd[0] == (prefix + "wotprofile"):
            'wotprofile <userid>'
            if len(cmd) >= 2:
                if cmd[1] in cache['wotprofiles']:
                    jsonret = cache['wotprofiles'][cmd[1]]
                    print("[RCache] Read cache.wotprofiles." + cmd[1])
                else:
                    jsonret = urljson("https://wotapi.thor.re/api/wot/player/" + cmd[1])
                    cache['wotprofiles'][cmd[1]] = jsonret
                    print("[RCache] Set cache.wotprofiles." + cmd[1])
            if (len(cmd) < 2) or ("error" in jsonret):
                await client.add_reaction(message,"\N{WARNING SIGN}")
                if (len(cmd) < 2):
                    await client.send_message(message.author,"```Shows basic information about a users WoT profile\nUsage: " + prefix + "wotprofile <userid>\n  UserID: The WorldOfTanks id for the user\n\nExample: " + prefix + "wotprofile 1847684```")
            else:
                typing(message)
                embed = discord.Embed(title=jsonret['username'] +"'s WoT account", colour=discord.Colour(random.randint(0,16777216)), url="https://worldoftrucks.com/en/online_profile.php?id=" + cmd[1], description="**\N{CHEQUERED FLAG} JOBS ACCOMPLISHED:** " + jsonret['details']['global']['jobsAccomplished'] + "\n**\N{WEIGHT LIFTER} MASS TRANSPORTED:** " + jsonret['details']['global']['totalMassTransported'] + "\n**\N{STRAIGHT RULER} TOTAL DISTANCE:** " + jsonret['details']['global']['totalDistance'] + "\n**\N{TIMER CLOCK} TIME ON DUTY:** " + jsonret['stats']['timeOnDuty'])
                await client.send_message(message.channel,embed=embed)
                
        if cmd[0] == (prefix + "jobstats"):
            'jobstats <userid>'
            if len(cmd) >= 2:
                if cmd[1] in cache['jobstats']:
                    jsonret = cache['jobstats'][cmd[1]]
                    print("[RCache] Read cache.jobstats." + cmd[1])
                else:
                    jsonret = urljson("https://wotapi.thor.re/api/wot/player/" + cmd[1])
                    cache['jobstats'][cmd[1]] = jsonret
                    print("[RCache] Set cache.jobstats." + cmd[1])
            if (len(cmd) < 2) or ("error" in jsonret):
                await client.add_reaction(message,"\N{WARNING SIGN}")
                if (len(cmd) < 2):
                    await client.send_message(message.author,"```Shows information about a users completed jobs\nUsage: " + prefix + "jobstats <userid>\n  UserID: The WorldOfTanks id for the user\n\nExample: " + prefix + "jobstats 1847684```")
            else:
                typing(message)
                if ("difficultSpotParking" in jsonret['details']['global']) :
                    difpark = jsonret['details']['global']['difficultSpotParking']
                else:
                    difpark = "0"
                if ("mediumSpotParking" in jsonret['details']['global']) :
                    medpark = jsonret['details']['global']['mediumSpotParking']
                else:
                    medpark = "0"
                if ("easySpotParking" in jsonret['details']['global']) :
                    easpark = jsonret['details']['global']['easySpotParking']
                else:
                    easpark = "0"
                embed = discord.Embed(title=jsonret['username'] + "'s Job Summary", colour=discord.Colour(random.randint(0,16777216)), description="**\N{CHEQUERED FLAG} JOBS ACCOMPLISHED:** " + jsonret['details']['global']['jobsAccomplished'] + "\n**\N{WEIGHT LIFTER} TOTAL MASS TRANSPORTED:** " + jsonret['details']['global']['totalMassTransported'] + "\n**\N{STRAIGHT RULER} AVG DELIVERY DISTANCE:** " + jsonret['details']['global']['averageDeliveryDistance'] + "\n**\N{MOTORWAY} LONGEST JOB DISTANCE:** " + jsonret['details']['global']['longestJobCompleted'] + "\n**\N{NEGATIVE SQUARED LATIN CAPITAL LETTER P} PARKING (HARD/MEDIUM/EASY)**: " + difpark + "-" + medpark + "-" + easpark)
                await client.send_message(message.channel,embed=embed)
                
        if cmd[0] == (prefix + "jobdetails"):
            'jobdetails <user> <ats/ets2>'
            if len(cmd) >= 2:
                if cmd[1] in cache['jobdetails']:
                    jsonret = cache['jobdetails'][cmd[1]]
                    print("[RCache] Read cache.jobdetails." + cmd[1])
                else:
                    jsonret = urljson("https://wotapi.thor.re/api/wot/player/" + cmd[1])
                    cache['jobdetails'][cmd[1]] = jsonret
                    print("[RCache] Set cache.jobdetails." + cmd[1])
            try:
                myVar
            except NameError:
                gameType = " "
            if len(cmd) >= 3:
                gameType = cmd[2].lower()
            else:
                gameType = " "
            if (len(cmd) < 3) or ("error" in jsonret) or ((gameType != "ats") and (gameType != "ets2")):
                await client.add_reaction(message,"\N{WARNING SIGN}")
                if (len(cmd) < 3):
                    await client.send_message(message.author,"```Shows information about a users jobs per game\nUsage: " + prefix + "jobdetails <userid> <gameType>\n  UserID: The WorldOfTanks id for the user\n  GameType: Game they are on (ATS/ETS2)\n\nExample: " + prefix + "jobdetails 1847684 ets2```")
            else:
                typing(message)
                embed = discord.Embed(title=jsonret['username'] + "'s " + gameType.upper() + " Job Summary", colour=discord.Colour(random.randint(0,16777216)), description="**\N{CHEQUERED FLAG} JOBS ACCOMPLISHED:** " + jsonret['details'][gameType]['jobsAccomplished'] +"\n**\N{WEIGHT LIFTER} MASS TRANSPORTED:** " + jsonret['details'][gameType]['totalMassTransported'] +"\n**\N{STRAIGHT RULER} TOTAL DISTANCE:** " + jsonret['details'][gameType]['totalDistance'] + "\n**\N{TIMER CLOCK} TIME ON DUTY:** " + jsonret['details'][gameType]['timeOnDuty'] + "\n**\N{SUNRISE} MOST JOBS IN A DAY:** " + jsonret['details'][gameType]['mostJobsInSingleWOTRDay'] + "\n**\N{CITYSCAPE} MOST USED CITY:** " + jsonret['details'][gameType]['mostJobsTakenFrom'] + "\n**\N{CARD INDEX DIVIDERS} MOST TAKEN CARGO** " + jsonret['details'][gameType]['mostTakenCargo'] + "\n**MOST SUPPLIED COMPANY:** " + jsonret['details'][gameType]['mostSuppliedCompany'] + "\n**MOST SOURCED COMPANY:** " + jsonret['details'][gameType]['mostSourcedCompany'])
                await client.send_message(message.channel,embed=embed)
                
        if cmd[0] == (prefix + "tmpprofile"):
            'tmpprofile <id>'
            if len(cmd) >= 2:
                if cmd[1] in cache['tmpprofile']:
                    jsonret = cache['tmpprofile'][cmd[1]]
                    print("[RCache] Read cache.tmpprofile." + cmd[1])
                else:
                    jsonret = urljson("https://api.truckersmp.com/v2/player/" + cmd[1])
                    cache['tmpprofile'][cmd[1]] = jsonret
                    print("[RCache] Set cache.tmpprofile." + cmd[1])
                    set_avatar_url(cmd[1],jsonret['response']['avatar'],jsonret['response']['name'])
            if (len(cmd) < 2) or jsonret['error'] == True:
                await client.add_reaction(message,"\N{WARNING SIGN}")
                if (len(cmd) < 2):
                    await client.send_message(message.author,"```Shows basic information about a users TruckersMP page\nUsage: " + prefix + "tmpprofile <userid>\n  UserID: The TruckersMP id for the user\n\nExample: " + prefix + "tmpprofile 1315569```")
            else: 
                typing(message)
                if jsonret['response']['permissions']['isGameAdmin'] == True:
                    memtype = "Admin"
                else:
                    memtype = "Member"
                '''embed = discord.Embed(title=jsonret['response']['name'] + "'s TruckersMP Profile", colour=discord.Colour(random.randint(0,16777216)), url="https://truckersmp.com/user/" + str(jsonret['response']['id']), description="**\N{PASSPORT CONTROL} ID:**: " + str(jsonret['response']['id']) + "\n**\N{CALENDAR} JOIN DATE:** " + jsonret['response']['joinDate'] + "\n**\N{TWO MEN HOLDING HANDS} GROUP NAME:** " + jsonret['response']['groupName'] + " (" + str(jsonret['response']['groupID']) + ")\n**\N{PAGE WITH CURL} TYPE:** " + memtype + "\n**\N{STEAM LOCOMOTIVE} STEAM ID:** " + str(jsonret['response']['steamID64']))
                embed.set_thumbnail(url=get_avatar_url(cmd[1]))
                await client.send_message(message.channel,embed=embed)'''
                embed = discord.Embed(title=jsonret['response']['name'] + "'s TruckersMP Profile", colour=discord.Colour(random.randint(0,16777216)), url="https://truckersmp.com/user/" + str(jsonret['response']['id']), description="**ID:** " + str(jsonret['response']['id']) + "\n**TYPE:** " + memtype + "\n**GROUP NAME:** " + jsonret['response']['groupName'] + " (" + str(jsonret['response']['groupID']) + ")\n**JOIN DATE:** " + jsonret['response']['joinDate'] + "\n**STEAMID:** " + str(jsonret['response']['steamID64']))
                avatarurl,username = get_avatar_url(str(jsonret['response']['id']))
                embed.set_thumbnail(url=avatarurl)
                await client.send_message(message.channel,embed=embed)
            
        if cmd[0] == (prefix + "tmpbans"):
            'tmpbans <id> [number]'
            if len(cmd) >= 2:
                if cmd[1] in cache['tmpbans']:
                    jsonret = cache['tmpbans'][cmd[1]]
                    print("[RCache] Read cache.tmpbans." + cmd[1])
                else:
                    jsonret = urljson("https://api.truckersmp.com/v2/bans/" + cmd[1])
                    cache['tmpbans'][cmd[1]] = jsonret
                    print("[RCache] Set cache.tmpbans." + cmd[1])
            if len(cmd) < 2:
                await client.add_reaction(message,"\N{WARNING SIGN}")
                await client.send_message(message.author,"```Shows information about a TruckersMPs bans\nUsage: " + prefix + "tmpbans <userid> [bannumber]\n  UserID: The TruckersMP id for the user\n  BanNumber: Used to query a ban that a user has gotten\n\nExample: " + prefix + "tmpbans 1315569\n         " + prefix + "tmpbans 1315569 1```")
            try:
                jsonret
            except NameError:
                await client.add_reaction(message,"\N{WARNING SIGN}")
            else:
                print(jsonret['error'])
                if jsonret['error'] != True:
                    if len(cmd) >= 3:
                        if not possibleint(cmd[2]):
                            await client.add_reaction(message,"\N{WARNING SIGN}")
                        else:
                            banid = int(cmd[2])-1
                            if banid < 0 or banid >= len(jsonret['response']):
                                await client.add_reaction(message,"\N{WARNING SIGN}")
                            else:
                                avatarurl,username = get_avatar_url(cmd[1])
                                embed = discord.Embed(title=username + "'s Ban History", colour=discord.Colour(random.randint(0,16777216)), description="**EXPIRATION:** " + jsonret['response'][banid]['expiration'] + "\n**BAN ISSUED BY:** " + jsonret['response'][banid]['adminName'] + " (" + str(jsonret['response'][banid]['adminID']) + ")\n**REASON:** " + jsonret['response'][banid]['reason'])
                                embed.set_thumbnail(url=avatarurl)
                                embed.set_footer(text="Ban " + cmd[2] + " / " + str(len(jsonret['response'])))
                                await client.send_message(message.channel,embed=embed)
                    elif len(cmd) >= 2:
                        avatarurl,username = get_avatar_url(cmd[1])
                        embed = discord.Embed(title=username + "'s Ban History", colour=discord.Colour(random.randint(0,16777216)), description="**TOTAL BANS:** " + str(len(jsonret['response'])))
                        embed.set_footer(text="Do " + prefix + "tmpbans " + cmd[1] + " <id> to view specific ban information")
                        embed.set_thumbnail(url=avatarurl)
                        await client.send_message(message.channel,embed=embed)
                else:
                    await client.add_reaction(message,"\N{WARNING SIGN}")
            
        if cmd[0] == (prefix + "tmpservers"):
            'tmpservers'
            if len(cache2['tmpservers']) > 0:
                jsonret = cache2['tmpservers']
                print("[RCache] Read cache2.tmpservers")
            else:
                jsonret = urljson("https://api.truckersmp.com/v2/servers")
                cache2['tmpservers'] = jsonret
                print("[RCache] Set cache2.tmpservers")
            serverlist = jsonret['response']
            serverinf = ""
            jsonret['glo'] = dict()
            jsonret['glo']['totalplayers'] = 0
            jsonret['glo']['totalslots'] = 0
            jsonret['glo']['totalqueue'] = 0
            for server in serverlist:
                if server['online'] == False:
                    serverinf = serverinf + "\N{WARNING SIGN} "
                serverinf = serverinf + "[" + server['game'] + "] " + server['name'] + " (" + server['shortname'] + ")"
                if server['speedlimiter'] == 1:
                    serverinf = serverinf + " \N{OCTAGONAL SIGN}"
                serverinf = serverinf + "\n***" + str(server['players']) + " / " + str(server['maxplayers']) + " [" + str(math.ceil((server['players']/server['maxplayers'])*100)) + "%] Users playing*** *" + str(server['queue']) + " in queue*\n"
                jsonret['glo']['totalplayers'] = jsonret['glo']['totalplayers'] + server['players']
                jsonret['glo']['totalqueue'] = jsonret['glo']['totalqueue'] + server['queue']
                jsonret['glo']['totalslots'] = jsonret['glo']['totalslots'] + server['maxplayers']
            embed = discord.Embed(title="TruckersMP Server Status", colour=discord.Colour(random.randint(0,16777216)), description=serverinf)
            embed.set_footer(text="Total users online: " + str(jsonret['glo']['totalplayers']) + " | Total slots: " + str(jsonret['glo']['totalslots']) + " | " + str(math.ceil((jsonret['glo']['totalplayers']/jsonret['glo']['totalslots'])*100)) + "% full | Total users in queue: " + str(jsonret['glo']['totalqueue']))
            await client.send_message(message.channel,embed=embed)
                
        if cmd[0] == (prefix + "tmpversion"):
            'tmpservers'
            if len(cache['tmpversion']) > 0:
                jsonret = cache['tmpversion']
                print("[RCache] Read cache.tmpversion")
            else:
                jsonret = urljson("https://api.truckersmp.com/v2/version")
                cache['tmpversion'] = jsonret
                print("[RCache] Set cache.tmpversion")
            embed = discord.Embed(title="Version information", colour=discord.Colour(random.randint(0,16777216)), description="**CURRENT VERSION NAME:** " + jsonret['name'] + " (" + str(jsonret['numeric']) + ")\n**STATE:** " + jsonret['stage'] + "\n**SUPPORTED ETS2 VERSION:** " + jsonret['supported_game_version'] + "\n**SUPPORTED ATS VERSION:** " + jsonret['supported_ats_game_version'])
            await client.send_message(message.channel,embed=embed)

        if cmd[0] == (prefix + "tmpavatar"):
            if len(cmd) < 2:
                await client.send_message(message.author,"```Shows a TruckerMP user's avatar\nUsage: " + prefix + "tmpavatar <userid>\n  UserID: The TruckersMP id for the user\n\nExample: " + prefix + "tmpavatar 1315569```")
                await client.add_reaction(message,"\N{WARNING SIGN}")
            else:
                if possibleint(cmd[1]):
                    avatar,username = get_avatar_url(cmd[1])
                    embed = discord.Embed()
                    embed.set_image(url=avatar)
                    embed.set_author(name="Visit their TruckerMP profile", url="https://truckersmp.com/user/" + cmd[1])
                    await client.send_message(message.channel,embed=embed)
                else:
                    await client.add_reaction(message,"\N{WARNING SIGN}")
        
        if cmd[0] == (prefix + "help"):
            embed = discord.Embed(title="Help", description="```Shows basic information about a users WoT profile\nUsage: " + prefix + "wotprofile <userid>\n  UserID: The WorldOfTanks id for the user\n\nExample: " + prefix + "wotprofile 1847684\n\nShows information about a users completed jobs\nUsage: " + prefix + "jobstats <userid>\n  UserID: The WorldOfTanks id for the user\n\nExample: " + prefix + "jobstats 1847684\n\n" + "Shows information about a users jobs per game\nUsage: " + prefix + "jobdetails <userid> <gameType>\n  UserID: The WorldOfTanks id for the user\n  GameType: Game they are on (ATS/ETS2)\n\nExample: " + prefix + "jobdetails 1847684 ets2\n\nShows basic information about a users TruckersMP page\nUsage: " + prefix + "tmpprofile <userid>\n  UserID: The TruckersMP id for the user\n\nExample: " + prefix + "tmpprofile 1315569\n\nShows a TruckerMP user's avatar\nUsage: " + prefix + "tmpavatar <userid>\n  UserID: The TruckersMP id for the user\n\nExample: " + prefix + "tmpavatar 1315569\n\nShows information about a TruckersMPs bans\nUsage: " + prefix + "tmpbans <userid> [bannumber]\n  UserID: The TruckersMP id for the user\n  BanNumber: Used to query a ban that a user has gotten\n\nExample: " + prefix + "tmpbans 1315569\n         " + prefix + "tmpbans 1315569 2\n\nShows details such as users on servers and in queue on all TruckersMP servers\nUsage: " + prefix + "tmpservers\n\nShows information reguarding versions of game and server\nUsage: " + prefix + "tmpversion\n\nHey! Why not add the bot to your server or a friends? All you have to do is just invite the bot and give it the necessary permissions and you're good to go! I would appreciate you concidering to add it, it means you like it!\nhttps://discordapp.com/oauth2/authorize?client_id=312658464935510016&scope=bot&permissions=1074129985 ```")
            await client.send_message(message.author,embed=embed)
            await client.add_reaction(message,"\N{OK HAND SIGN}")
            
#        if cmd[0] == (prefix + "purge"):
#           deleted = await client.purge_from(message.channel,check=linked,limit=20000)
#           await client.send_message(message.channel,"***Deleted " + str(len(deleted)) + " messages!***")
# 
#        if cmd[0] == (prefix + "clear"):
#            deleted = await client.purge_from(message.channel,check=true,limit=20000)
#            await client.send_message(message.channel,"***Deleted " + str(len(deleted)) + " messages!***")
#
        if cmd[0] == (prefix + "invite"):
            await client.send_message(message.author,"```It would be wonderful to know you like this bot so much you would like to spread it to other servers! It would mean the world to me. So heres the link :)``` https://discordapp.com/oauth2/authorize?client_id=312658464935510016&scope=bot&permissions=1074129985")
            await client.add_reaction(message,"\N{HEAVY BLACK HEART}")
        #if cmd[0] == (prefix + "invite"):
         #   if len(cmd) < 2:
         #       await client.send_message(message.author,"```Adds me to your server!\nUsage: " + prefix + "invite <inviteid>\n  inviteid: The discord invite id linking to your server.\n\nExample: " + prefix + "invite https://discord.gg/UpDYeaq\n         " + prefix + "invite UpDYeaq```")
         #       await client.add_reaction(message,"\N{WARNING SIGN}")
         #   else:
                #try:
         #       print(cmd[1])
          #      await client.accept_invite(cmd[1])
                #except discord.Forbidden or discord.HTTPException:
                #    await client.add_reaction(message,"\N{OCTAGONAL SIGN}")
                #except:
                 #   await client.add_reaction(message,"\N{WARNING SIGN}")
                #else:
                 #   await client.add_reaction(message,"\N{HEAVY BLACK HEART}")
                 #   await setplaying("on " + str(len(client.servers)) + " servers! | " + prefix + "help")
                    

client.run(key)
