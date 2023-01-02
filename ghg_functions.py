from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import bec_rcon
import configparser
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import discord
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.utils import get
import esix
from github import Github
import json
import logging
import mysql.connector
import os
import pendulum
import random
import requests
import schedule
import subprocess
import threading
import time
import traceback
import ts3

#Read Config for secrets
config = configparser.ConfigParser()
config.read('connectionInfo.ini')

def checkForOP(dateDB=None):
    print("DateDB: {}".format(dateDB))
    if dateDB == None:
        dateDB = pendulum.now().next(pendulum.SATURDAY).strftime('%Y-%m-%d')
    print("DateDB After check: {}".format(dateDB))
    mydb = mydbConnect()
    mycursor = mydb.cursor()
    checkOPOnDateSQL = "Select opDate FROM ghg_a3.ops WHERE opDate = '{}'".format(dateDB)
    mycursor.execute(checkOPOnDateSQL)
    checkOpOnDateR = mycursor.fetchone()
    print("sql result: {}".format(checkOpOnDateR))
    mydb.close()
    isOp = False
    if checkOpOnDateR:
        isOp = True
        print("There is an op this saturday")
    else:
        isOp = False
        print("There is NOT an op this saturday")
    return isOp

def getPost():
    postList = []
    for p in esix.post.search("rating:s order:random score:>=50 -type:webm -type:swf -type:mp4 -type:zip", limit=5):
        postList.append(p)
    selectedPost = random.choice(postList)
    return selectedPost

def getPostNSFW():
    postListNSFW = []
    for p in esix.post.search("-rating:s order:random score:>=50 -type:webm -type:swf -type:mp4 -type:zip", limit=5):
        postListNSFW.append(p)
    selectedPostNSFW = random.choice(postListNSFW)
    return selectedPostNSFW

def gitRepo():
    g = Github(config['Github']['githubToken'])
    repo = g.get_repo("BSuzinator/GHG_Framework")
    return repo
    
def mydbConnect():
    mydb = mysql.connector.connect(
    host=config['Database']['host'],
    user=config['Database']['user'],
    password=config['Database']['pass'],
    database=config['Database']['database']
    )
    return mydb

def rconConnect():
    rcon = bec_rcon.ARC("127.0.0.1", config['Arma']['serverCommandPass'], 2300)
    rcon.authorize()
    return rcon

async def update(interaction):
    subprocess.run("taskkill /f /im arma3server_x64.exe")
    keyPath = "S:\GHG_A3\A3Files\A3Keys.bat"
    modPath = "S:\GHG_A3\A3Files\A3ModsUpdate.bat"
    mainPath = "S:\GHG_A3\A3Files\A3Update.bat"
    modSuccess = subprocess.call(modPath, shell=True)
    mainSuccess = subprocess.call(mainPath, shell=True)
    subprocess.run("taskkill /f /im arma3server_x64.exe")
    if (os.path.isdir("S:\GHG_A3\A3Master\mpmissions")):
        subprocess.run(["rmdir", "S:\GHG_A3\A3Master\mpmissions"], shell=True)
    subprocess.run("mklink /j S:\GHG_A3\A3Master\mpmissions S:\GHG_A3\A3Missions\Training", shell=True)
    waitUntil(modSuccess + mainSuccess == 0, subprocess.call(keyPath, shell=True),os.startfile (r"E:\Desktop\GHG_Training.lnk"))
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    serverControlLogChannel = interaction.guild.get_channel(int(config['Discord']['ghgLogChannelID']))
    await serverControlLogChannel.send("Server Updated and restarted to Training Configuration by {} at {}".format(interaction.user,dt_string))
    #a3UpdateIP = False

def waitUntil(condition, output, output2):
    wU = True
    while wU == True:
        if condition:
            output
            output2
            wU = False
        time.sleep(5)

async def fnc_updateDatabaseRoles(interaction,member=None,isAll="no"):
    guild = interaction.guild
    loaChannelID = 891141241113301002
    loaChannel = guild.get_channel(loaChannelID)
    activityCheckChannelID = 891141579895607336
    activityCheckChannel = guild.get_channel(activityCheckChannelID)
    role_id = 891142215848570891
    loaRole = get(guild.roles, id=role_id)
    degenerateRole_ID = 925569335328657479
    degenerateRole = get(guild.roles, id=degenerateRole_ID)
    activeRole_ID = 446959255262855168
    activeRole = get(guild.roles, id=activeRole_ID)
    zeusRole_ID = 711351892969783346
    zeusRole = get(guild.roles, id=zeusRole_ID)
    juniorOfficerRole_ID = 888633649656897576
    juniorOfficerRole = get(guild.roles, id=juniorOfficerRole_ID)
    officerRole_ID = 728552205283754065
    officerRole = get(guild.roles, id=officerRole_ID)
    headAdminRole_ID = 176412413736779777
    headAdminRole = get(guild.roles, id=headAdminRole_ID)
    unregisteredList = "Unregistered Users: \n"
    noTeamspeakIDList = "No Teamspeak ID Users: \n"
    allMembers = []
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    if isAll == "yes":
        allMembers = guild.members
       # unregisteredList = "{} Unregistered Members:".format(dt_string)
    else:
        allMembers.append(member)
    mydb = mydbConnect()
    mycursor = mydb.cursor()
    for member in allMembers:
        checkUserSQL = "Select discordID FROM users WHERE discordID = {}".format(member.id)
        mycursor.execute(checkUserSQL)
        dbID = mycursor.fetchone()
        if dbID == None:
            
            print('{} is unregistered'.format(member.name))
            if isAll == "yes":
                unregisteredList = unregisteredList + "{}\n".format(member.name)
            #if activeRole in member.roles:
                #emb=discord.Embed(title="GHG Registration", description="Hi, {}! We noticed you have not yet registered into our database. We use this to keep thing fluid and simple for everyone between the Arma Server, Discord, and Teampseak. Please take a moment to do so at your earliest convenience by first joining the Teamspeak server, then in the #bot-commands channel using `$register [steam64ID] [teamspeakUID]`".format(member.name))
                #try:
                    #await member.send(embed=emb)
                    #print("{} | Register Notify Success".format(member.name))
                #except Exception as e:
                    #print("{} | Register Notify Fail: {}".format(member.name, e))
        else:
            checkNameSQL = "Select discordName FROM users WHERE discordID = {}".format(member.id)
            mycursor.execute(checkNameSQL)
            dbname = mycursor.fetchone()
            if dbname != member.display_name:
                nameUpdate = "UPDATE users SET discordName = '{}' WHERE discordID = {}".format(member.display_name,member.id)
                mycursor.execute(nameUpdate)
                mydb.commit()
            if headAdminRole in member.roles:
                headAdminUpdate = 'UPDATE users SET isAdmin = "1" WHERE discordID = {}'.format(member.id)
                mycursor.execute(headAdminUpdate)
                mydb.commit()
            else:
                headAdminUpdate = 'UPDATE users SET isAdmin = "0" WHERE discordID = {}'.format(member.id)
                mycursor.execute(headAdminUpdate)
                mydb.commit()
            if officerRole in member.roles:
                officerUpdate = 'UPDATE users SET isOfficer = "1" WHERE discordID = {}'.format(member.id)
                mycursor.execute(officerUpdate)
                mydb.commit()
            else:
                officerUpdate = 'UPDATE users SET isOfficer = "0" WHERE discordID = {}'.format(member.id)
                mycursor.execute(officerUpdate)
                mydb.commit()
            if juniorOfficerRole in member.roles:
                juniorOfficerUpdate = 'UPDATE users SET isJuniorOfficer = "1" WHERE discordID = {}'.format(member.id)
                mycursor.execute(juniorOfficerUpdate)
                mydb.commit()
            else:
                juniorOfficerUpdate = 'UPDATE users SET isJuniorOfficer = "0" WHERE discordID = {}'.format(member.id)
                mycursor.execute(juniorOfficerUpdate)
                mydb.commit()
            if zeusRole in member.roles:
                zeusUpdate = 'UPDATE users SET isZeus = "1" WHERE discordID = {}'.format(member.id)
                mycursor.execute(zeusUpdate)
                mydb.commit()
            else:
                zeusUpdate = 'UPDATE users SET isZeus = "0" WHERE discordID = {}'.format(member.id)
                mycursor.execute(zeusUpdate)
                mydb.commit()
            if activeRole in member.roles:
                activeUpdate = 'UPDATE users SET isActive = "1" WHERE discordID = {}'.format(member.id)
                mycursor.execute(activeUpdate)
                mydb.commit()
            else:
                activeUpdate = 'UPDATE users SET isActive = "0" WHERE discordID = {}'.format(member.id)
                mycursor.execute(activeUpdate)
                mydb.commit()
            if degenerateRole in member.roles:
                degenerateUpdate = 'UPDATE users SET isDegenerate = "1" WHERE discordID = {}'.format(member.id)
                mycursor.execute(degenerateUpdate)
                mydb.commit()
            else:
                degenerateUpdate = 'UPDATE users SET isDegenerate = "0" WHERE discordID = {}'.format(member.id)
                mycursor.execute(degenerateUpdate)
                mydb.commit()
            tsInfoMsg = fnc_updateTSDB(interaction,member,mydb)
            if isAll == "yes":
                noTeamspeakIDList = noTeamspeakIDList + tsInfoMsg            
            
            loaDataSQL = "SELECT loaStartDate,loaExpectedReturn,loaMessageID FROM ghg_a3.loas WHERE discordID = '{}';".format(member.id)
            mycursor.execute(loaDataSQL)
            loaData = mycursor.fetchone()
            
            if loaData:
                expectedReturnDBObj = loaData[1]
                loaStartDBObj = loaData[0]
                loaMessageID = loaData[2]
                if (expectedReturnDBObj <= now.date()):
                    loaMessage = await loaChannel.fetch_message(loaMessageID)
                    expectedReturnDB = expectedReturnDBObj.strftime("%Y-%m-%d")
                    expectedReturnSTR = expectedReturnDBObj.strftime("%B %d, %Y")
                    loaStartDB = loaStartDBObj.strftime("%Y-%m-%d")
                    loaStartSTR = loaStartDBObj.strftime("%B %d, %Y")
                    embed=discord.Embed(title="LOA for {}".format(member.name), color=0xffffff)
                    embed.add_field(name="Start Date", value="{}".format(loaStartSTR), inline=False)
                    embed.add_field(name="Expected Return Date", value="{}".format(expectedReturnSTR), inline=False)
                    embed.add_field(name="LOA EXPIRED", value="{} should be back now.".format(member.name), inline=False)
                    await loaMessage.edit(embed=embed)
                    await member.remove_roles(loaRole, reason="LOA Expired")
                    loaDeleteSQL = "DELETE FROM ghg_a3.loas WHERE discordID = '{}';".format(member.id)
                    mydb.commit()
            
    mydb.close()
    if isAll == "yes":
        await activityCheckChannel.send("Database Update for: {}\n\n{}\n\n{}".format(dt_string,unregisteredList,noTeamspeakIDList))

def fnc_updateTSDB(interaction,member,mydb):
    mycursor = mydb.cursor()
    getRolesSQL = "Select teamspeakUID,isAdmin,isOfficer,isJuniorOfficer,isZeus,isActive,isDegenerate,discordName FROM users WHERE discordID = {}".format(member.id)
    mycursor.execute(getRolesSQL)
    userRoles = mycursor.fetchone()
    teamspeakUID = userRoles[0]
    isAdmin = userRoles[1]
    isOfficer = userRoles[2]
    isJuniorOfficer = userRoles[3]
    isZeus = userRoles[4]
    isActive = userRoles[5]
    isDegenerate = userRoles[6]
    discordName = userRoles[7]
    message = "Unable to connect to teamspeak server."
    tsErrorMsg = ""
    with ts3.query.TS3Connection("localhost") as ts3conn:
        try:
            ts3conn.login(client_login_name=config['Teamspeak']['sqLogin'], client_login_password=config['Teamspeak']['sqPass'])
            ts3conn.use(sid="1")
            cldibfromuidResponse = ts3conn.clientgetdbidfromuid(cluid=teamspeakUID)
            tsClientID = int(cldibfromuidResponse.parsed[0].get('cldbid'))
            if isAdmin:
                try:
                    ts3conn.servergroupaddclient(sgid=6, cldbid=tsClientID)
                    print("{} added to Server Admin in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} already a(n) Server Admin in Teamspeak".format(member.name))
            else:
                try:
                    ts3conn.servergroupdelclient(sgid=6, cldbid=tsClientID)
                    print("{} removed from Server Admin in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} reamains not a(n) Server Admin in Teamspeak".format(member.name))
            if isOfficer:
                try:
                    ts3conn.servergroupaddclient(sgid=24, cldbid=tsClientID)
                    print("{} added to Officer in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} already a(n) Officer in Teamspeak".format(member.name))
            else:
                try:
                    ts3conn.servergroupdelclient(sgid=24, cldbid=tsClientID)
                    print("{} removed from Officer in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} reamains not a(n) Officer in Teamspeak".format(member.name))
            if isJuniorOfficer:
                try:
                    ts3conn.servergroupaddclient(sgid=29, cldbid=tsClientID)
                    print("{} added to Junior Officer in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} already a(n) Junior Officer in Teamspeak".format(member.name))
            else:
                try:
                    ts3conn.servergroupdelclient(sgid=29, cldbid=tsClientID)
                    print("{} removed from Junior Officer in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} reamains not a(n) Junior Officer in Teamspeak".format(member.name))
            if isZeus:
                try:
                    ts3conn.servergroupaddclient(sgid=25, cldbid=tsClientID)
                    print("{} added to Zeus in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} already a(n) Zeus in Teamspeak".format(member.name))
            else:
                try:
                    ts3conn.servergroupdelclient(sgid=25, cldbid=tsClientID)
                    print("{} removed from Zeus in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} reamains not a(n) Zeus in Teamspeak".format(member.name))
            if isActive:
                try:
                    ts3conn.servergroupaddclient(sgid=28, cldbid=tsClientID)
                    print("{} added to Arma/Active in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} already a(n) Arma/Active in Teamspeak".format(member.name))
            else:
                try:
                    ts3conn.servergroupdelclient(sgid=28, cldbid=tsClientID)
                    print("{} removed from Arma/Active in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} reamains not a(n) Arma/Active in Teamspeak".format(member.name))
            if isDegenerate:
                try:
                    ts3conn.servergroupaddclient(sgid=26, cldbid=tsClientID)
                    print("{} added to Degenerate in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} already a(n) Degenerate in Teamspeak".format(member.name))
            else:
                try:
                    ts3conn.servergroupdelclient(sgid=26, cldbid=tsClientID)
                    print("{} removed from Degenerate in Teamspeak".format(member.name))
                except Exception as e:
                    print("{} reamains not a(n) Degenerate in Teamspeak".format(member.name))
            #clientGroups = ts3conn.servergroupsbyclientid(cldbid=tsClientID)
            #groupList = "Teamspeak Server Groups for {}:".format(ctx.author.name)
            #for groupDict in clientGroups:
                #groupName = groupDict['name']
                #if groupName != 'Traitor' or groupName != 'Degenerate':
                    #groupList += "\n{}".format(groupName)
        except Exception as e:
            print("{} for {}".format(e,discordName))
            tsErrorMsg = "{} for {}\n".format(e,discordName)
    ts3conn.quit()
    return tsErrorMsg