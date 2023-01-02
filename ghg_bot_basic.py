import asyncio
import bec_rcon
import configparser
from dateutil.relativedelta import *
from dateutil.easter import *
from dateutil.rrule import *
from dateutil.parser import *
from datetime import *
import discord
from discord import *
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.utils import get
import esix
from ghg_functions import *
#from ghg_automatedTasks import *
from github import Github
import json
import logging
import logging.handlers
import mysql.connector
import os
import pendulum
import random
import requests
import schedule
import steam
from steam import game_servers as gs
import subprocess
import threading
import time
import traceback
import ts3
from typing import Optional


#Read Config for connection info
config = configparser.ConfigParser()
config.read('connectionInfo.ini')

MY_GUILD = discord.Object(id=int(config['Discord']['ghgGuildID']))  # replace with your guild id

class MyClient(discord.ext.commands.Bot):
    def __init__(self, *,command_prefix: '', intents: discord.Intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        #self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.all()
bot = MyClient(command_prefix='$', intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('--------------------------------------------')
	
#    for filename in os.listdir('./cogs'):
#        if filename.endswith('.py'):
#            try:
#                await bot.load_extension(f'cogs.{filename[:-3]}')
#                print(f'Loaded {filename}')
#            except Exception as e:
#                print(f'Failed to load {filename}')
#                print(f'[ERROR] {e}')
#    print("----------------------------------------")


@bot.event
async def on_error(interaction, error):
    await interaction.response.send_message("An error occured: {}".format(error))
    print(error)
    logger.error("An error occured: {}".format(error))

@bot.event
async def on_member_join(member):
    mydb = mydbConnect()
    discordID = member.id
    discordName = member.name
    mycursor = mydb.cursor()
    registerGETSQL = "Select discordID FROM users WHERE discordID = '{}'".format(member.id)
    mycursor.execute(registerGETSQL)
    dbID = mycursor.fetchone()
    if dbID == None:
        sql = "INSERT INTO `ghg_a3`.`users`(`discordID`,`discordName`)VALUES('{}','{}');".format(discordID,discordName)
        mycursor.execute(sql)
        mydb.commit()
    mydb.close()
        
#@bot.tree.command()
#@app_commands.describe(
#    first_value='The first value you want to add something to',
#    second_value='The value you want to add to the first value',
#)
#async def add(interaction: discord.Interaction, first_value: int, second_value: int):
#    """Adds two numbers together."""
#    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')


# The rename decorator allows us to change the display of the parameter on Discord.
# In this example, even though we use `text_to_send` in the code, the client will use `text` instead.
# Note that other decorators will still refer to it as `text_to_send` in the code.
#@bot.tree.command()
#@app_commands.rename(text_to_send='text')
#@app_commands.describe(text_to_send='Text to send in the current channel')
#async def send(interaction: discord.Interaction, text_to_send: str):
#    """Sends the text into the current channel."""
#    await interaction.response.send_message(text_to_send)


# To make an argument optional, you can either give it a supported default argument
# or you can mark it as Optional from the typing standard library. This example does both.
@bot.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    # If no member is explicitly provided then we use the command user here
    member = member or interaction.user

    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


# A Context Menu command is an app command that can be run on a member or on a message by
# accessing a menu within the client, usually via right clicking.
# It always takes an interaction as its first parameter and a Member or Message as its second parameter.

# This context menu command only works on members
@bot.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')
    
# This context menu command only works on messages
#@bot.tree.context_menu(name='Report to Moderators')
#async def report_message(interaction: discord.Interaction, message: discord.Message):
#    # We're sending this response message with ephemeral=True, so only the command executor can see it
#    await interaction.response.send_message(
#        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
#    )
#
#    # Handle report by sending it into a log channel
#    log_channel = interaction.guild.get_channel(0)  # replace with your channel id
#
#    embed = discord.Embed(title='Reported Message')
#    if message.content:
#        embed.description = message.content
#
#    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
#    embed.timestamp = message.created_at
#
#    url_view = discord.ui.View()
#    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))
#
#    await log_channel.send(embed=embed, view=url_view)


#################################

#Start of GHG-Specific stuff.


#################################


#################################
#Database


#################################




#Update user info across services
@bot.tree.context_menu(name='UpdateDB')
async def update_db(interaction: discord.Interaction, member: discord.Member):
    await fnc_updateDatabaseRoles(interaction,member)    
    await interaction.response.send_message(f'{member} has been updated.')
    


#################################
#Ops Stuff


#################################

#New Op Posting without Database
@bot.tree.command()
@app_commands.checks.has_any_role( int(config['Discord']['ghgOfficerRoleID']), int(config['Discord']['ghgJuniorOfficerRoleID']))
@app_commands.describe(date="Date of Op in format 'Month DD, YYYY'",op1_name="Name of first Op",op1_desc="Description of first Op",op2_name="Name of second OP", op2_desc="Description of second Op", is_offweek="Any String other than nothing will make this an off-week")
async def new_op_no_db(interaction: discord.Interaction, date: str, op1_name: str, op1_desc: str, op2_name: Optional[str] = "", op2_desc: Optional[str] = "", is_offweek: Optional[str] = ""):
    """Posts for weekly Op Event"""
    
    isOffWeek = bool(is_offweek) or False 
    
    mydb = mydbConnect()
    dateSTR = date
    isOffWeekDB = 0
    if isOffWeek:
        dateSTR = date + " (Off-Week)"
        isOffWeekDB = 1
    announcementChannel = interaction.guild.get_channel(int(config['Discord']['ghgAnnouncementChannelID']))
    
    embed=discord.Embed(title="Op Day {} @ 9pm EST / 6pm PST".format(dateSTR), color=0xffffff)
    embed.set_thumbnail(url="https://ghg.suznetworks.com/icon.png")
    embed.add_field(name="IP: suznetworks.com Port: 2302", value="Please connect to the training server at least 10 minutes to start time to verify you can connect properly.", inline=False)
    
    mycursor = mydb.cursor()
            
    embed.add_field(name="OP 1: {}".format(op1_name), value="{}".format(op1_desc), inline=True)
    
    if op2_name != "":
        embed.add_field(name="OP 2: {}".format(op1_name), value="{}".format(op2_desc), inline=True)
    
    embed.add_field(name="Website", value="[https://ghg.suznetworks.com](https://ghg.suznetworks.com) for help connecting.", inline=False)
    embed.add_field(name="Reactions", value="As usual, please use :white_check_mark: if you are able to attend, and :x: if you are not!", inline=False)
    embed.set_footer(text="If there are issues with this bot or the server please contact @BSuzinator")
    
    
    await announcementChannel.send('@everyone It\'s that time again!')
    message = await announcementChannel.send(embed=embed)
    await message.add_reaction('✅')
    await message.add_reaction('❌')
    await message.publish()
    
    #Add entry to op table
    dateDBObj = parse(date)
    dateDB = dateDBObj.strftime("%Y-%m-%d")
    
    addOpSQL = "INSERT INTO `ghg_a3`.`ops`(`announcementMessageID`,`opDate`,`isOffWeek`,`mission1Title`, `mission1Description`,`mission2Title`, `mission2Description`)VALUES('{}','{}','{}','{}','{}','{}','{}');".format(message.id,dateDB,isOffWeekDB,op1_name,op1_desc,op2_name,op2_desc)
    mycursor.execute(addOpSQL)
    mydb.commit()
    await interaction.response.send_message("Op Posted for {}".format(dateSTR))


#New Op Posting
@bot.tree.command()
@app_commands.checks.has_any_role( int(config['Discord']['ghgOfficerRoleID']), int(config['Discord']['ghgJuniorOfficerRoleID']))
@app_commands.describe(date="Date of Op in format 'Month DD, YYYY'",op1_id="Database ID of first Op",op2_id="Database ID of second OP", is_offweek="Any String other than nothing will make this an off-week")
async def new_op(interaction: discord.Interaction, date: str, op1_id: int, op2_id: int, is_offweek: Optional[str] = ""):
    """Posts for weekly Op Event"""
    
    isOffWeek = bool(is_offweek) or False 
    
    mydb = mydbConnect()
    dateSTR = date
    isOffWeekDB = 0
    if isOffWeek:
        dateSTR = date + " (Off-Week)"
        isOffWeekDB = 1
    announcementChannel = interaction.guild.get_channel(int(config['Discord']['ghgAnnouncementChannelID']))
    
    embed=discord.Embed(title="Op Day {} @ 9pm EST / 6pm PST".format(dateSTR), color=0xffffff)
    embed.set_thumbnail(url="https://ghg.suznetworks.com/icon.png")
    embed.add_field(name="IP: suznetworks.com Port: 2302", value="Please connect to the training server at least 10 minutes to start time to verify you can connect properly.", inline=False)
    
    mycursor = mydb.cursor()
    op1_idNameSQL = "Select missionName FROM missions WHERE missionID = {}".format(op1_id)
    op1_idDescriptionSQL = "Select missionDescription FROM missions WHERE missionID = {}".format(op1_id)
    mycursor.execute(op1_idNameSQL)
    op1_idName = mycursor.fetchone()
    mycursor.execute(op1_idDescriptionSQL)
    op1_idDescription = mycursor.fetchone()

    op2_idNameSQL = "Select missionName FROM missions WHERE missionID = {}".format(op2_id)
    op2_idDescriptionSQL = "Select missionDescription FROM missions WHERE missionID = {}".format(op2_id)
    mycursor.execute(op2_idNameSQL)
    op2_idName = mycursor.fetchone()
    mycursor.execute(op2_idDescriptionSQL)
    op2_idDescription = mycursor.fetchone()
        
    embed.add_field(name="OP 1: {}".format(op1_idName[0]), value="{}".format(op1_idDescription[0]), inline=True)
    embed.add_field(name="OP 2: {}".format(op2_idName[0]), value="{}".format(op2_idDescription[0]), inline=True)
    embed.add_field(name="Website", value="[https://ghg.suznetworks.com](https://ghg.suznetworks.com) for help connecting.", inline=False)
    embed.add_field(name="Reactions", value="As usual, please use :white_check_mark: if you are able to attend, and :x: if you are not!", inline=False)
    embed.set_footer(text="If there are issues with this bot or the server please contact @BSuzinator")
    
    
    await announcementChannel.send('@everyone It\'s that time again!')
    message = await announcementChannel.send(embed=embed)
    await message.add_reaction('✅')
    await message.add_reaction('❌')
    await message.publish()
    
    op1_idUpdateDate = 'UPDATE missions SET missionLastRunDate = "{}" WHERE missionID = {}'.format(date,op1_id)
    op2_idUpdateDate = 'UPDATE missions SET missionLastRunDate = "{}" WHERE missionID = {}'.format(date,op2_id)
    mycursor.execute(op1_idUpdateDate)
    mydb.commit()
    mycursor.execute(op2_idUpdateDate)
    mydb.commit()

    op1_idTotalRunsSQL = 'Select missionTotalRuns FROM missions WHERE missionID = {}'.format(op1_id)
    mycursor.execute(op1_idTotalRunsSQL)
    op1_idTotalRuns = mycursor.fetchone()

    op2_idTotalRunsSQL = 'Select missionTotalRuns FROM missions WHERE missionID = {}'.format(op2_id)
    mycursor.execute(op2_idTotalRunsSQL)
    op2_idTotalRuns = mycursor.fetchone()

    op1_idTotalRuns = int(op1_idTotalRuns[0])
    op2_idTotalRuns = int(op2_idTotalRuns[0])
    
    op1_idTotalRuns = op1_idTotalRuns + 1
    op2_idTotalRuns = op2_idTotalRuns + 1
    
    op1_idTotalRunsSQL = "UPDATE missions SET missionTotalRuns = {} WHERE missionID = {}".format(op1_idTotalRuns,op1_id)
    op2_idTotalRunsSQL = "UPDATE missions SET missionTotalRuns = {} WHERE missionID = {}".format(op2_idTotalRuns,op2_id)
    
    mycursor.execute(op1_idTotalRunsSQL)
    mydb.commit()
    mycursor.execute(op2_idTotalRunsSQL)
    mydb.commit()
    
    #Add entry to op table
    dateDBObj = parse(date)
    dateDB = dateDBObj.strftime("%Y-%m-%d")
    
    addOpSQL = "INSERT INTO `ghg_a3`.`ops`(`announcementMessageID`,`opDate`,`isOffWeek`,`mission1Title`, `mission1Description`,`mission2Title`, `mission2Description`)VALUES('{}','{}','{}','{}','{}','{}','{}');".format(message.id,dateDB,isOffWeekDB,op1_idName[0],op1_idDescription[0],op2_idName[0],op2_idDescription[0])
    mycursor.execute(addOpSQL)
    mydb.commit()
    
    await interaction.response.send_message("Op Posted for {}".format(dateSTR))




#Upload Op
@bot.tree.command()
@app_commands.describe(mission_type='Preset to Upload Op to. Defaults to Main',op_file='.PBO File of the mission. Must be formatted: GHG_[COOP/PVP]_MissionName_Author.pbo')
async def upload_op(interaction: discord.Interaction, op_file: discord.Attachment, mission_type: Optional[str] = "main"):
    """Uploads Op to designated preset"""
    opType = mission_type
    if (opType.lower() not in ['training','main','escapes']):
        await ctx.send("Op type not recognized. Please use \'Training\', \'Main\', or \'Escapes\'")
        return
    filePath = 'S:\GHG_A3\A3Missions'
    match opType.lower():
        case 'training':
            filePath += '\Training\\'
        case 'escapes':
            filePath += '\Escapes\\'
        case 'main':
            filePath += '\MainOps\\'
    print(filePath)
    
    opAttachment = op_file
    filename = opAttachment.filename
    if ((filename[0:9] == 'GHG_COOP_' or filename[0:8] == 'GHG_PVP_')) and (filename[-4:] == '.pbo'):
        filePath += filename
        await opAttachment.save(filePath)
        await interaction.response.send_message('Op uploaded successfully. If you do not see it, please restart the server and retry.')
        print(filePath)
        return
    else:
        await interaction.response.send_message('Op not formatted correctly. Please check the name and retry.\nFormat: GHG_[COOP/PVP]_MissionName_Author.pbo')
        return

#################################
#Server Control Stuff


#################################

#Check Server Status
@bot.tree.command()
async def server_status(interaction: discord.Interaction):
    """Displays statuses of currently running servers."""
    
    embed=discord.Embed(title="GHG Server Status", type="rich", color=0xffffff)
    embed.set_thumbnail(url="https://ghg.suznetworks.com/icon.png")
    print('Checking Server Status...')
    for server_addr in gs.query_master(r'gameaddr\98.157.250.120'):
        try: 
            print('---------------------')
            print(gs.a2s_info(server_addr))
            print('Game: {}'.format(gs.a2s_info(server_addr)['folder']))
            print('Port: {}'.format(gs.a2s_info(server_addr)['port']))
            print('Ping: {}ms'.format(round(gs.a2s_info(server_addr)['_ping'],3)))
            print('Mission: {}'.format(gs.a2s_info(server_addr)['game']))
            print('Players: {}/{}'.format(gs.a2s_info(server_addr)['players'],gs.a2s_info(server_addr)['max_players']))
            print('---------------------')
            embed.add_field(name="{}".format(gs.a2s_info(server_addr)['name']), value="Game: {}\nPort: {}\nPing: {}ms\nMission: {}\nPlayers: {}/{}".format(gs.a2s_info(server_addr)['folder'],gs.a2s_info(server_addr)['port'],round(gs.a2s_info(server_addr)['_ping'],3),gs.a2s_info(server_addr)['game'],gs.a2s_info(server_addr)['players'],gs.a2s_info(server_addr)['max_players']), inline=False)
        except Exception as e:
            print('---------------------')
            print(e)
            embed.add_field(name="Server Error", value="Unknown Server online and not reporting correctly to steam\n{}".format(e), inline=False)
            print('---------------------')
    if embed.fields == []:
        embed.add_field(name="No servers found", value="Summoning <@!728552205283754065>!")
    embed.set_footer(text="If there are issues with this bot or the server please contact @BSuzinator")
    #await interaction.channel.send(embed=embed)
    # The format_dt function formats the date time into a human readable representation in the official client
    await interaction.response.send_message(embed=embed)




#Restart Server
@bot.tree.command()
@app_commands.checks.has_any_role( int(config['Discord']['ghgAdminRoleID']), int(config['Discord']['ghgOfficerRoleID']), int(config['Discord']['ghgJuniorOfficerRoleID']))
@app_commands.describe(restart_type='Preset the server will restart to. Escapes, Main, Training. Defaults to Training')
async def restart_server(interaction: discord.Interaction, restart_type: Optional[str] = "Training"):
    """Restarts Server to specified preset."""
    # If no member is explicitly provided then we use the command user here
    member = interaction.user
    restart_type = restart_type.lower()
    
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%d_%H-%M-%S")
    
    serverControlLogChannel = interaction.guild.get_channel(int(config['Discord']['ghgLogChannelID']))
    
    #await interaction.channel.send('Restarting server. Please allow 5 minutes for the process to complete. Errors will not be shown here. Contact <@144905725133586432>')
    
    subprocess.run("taskkill /f /im arma3server_x64.exe")
    
    if (restart_type == "escapes"):
        if (os.path.isdir("S:\GHG_A3\A3Master\mpmissions")):
            subprocess.run(["rmdir", "S:\GHG_A3\A3Master\mpmissions"], shell=True)
        subprocess.run("mklink /j S:\GHG_A3\A3Master\mpmissions S:\GHG_A3\A3Missions\Escapes", shell=True)
        os.startfile (r"E:\Desktop\GHG_Escapes.lnk")
        await interaction.response.send_message('Escapes server starting...')
        await serverControlLogChannel.send("Server restarted to Escapes Configuration by {} at {}".format(interaction.user,dt_string))
    elif (restart_type == "main") :
        if (os.path.isdir("S:\GHG_A3\A3Master\mpmissions")):
                subprocess.run(["rmdir", "S:\GHG_A3\A3Master\mpmissions"], shell=True)
        subprocess.run("mklink /j S:\GHG_A3\A3Master\mpmissions S:\GHG_A3\A3Missions\MainOps", shell=True)
        os.startfile (r"E:\Desktop\GHG_Main.lnk")
        await interaction.response.send_message('Main server starting...')
        await serverControlLogChannel.send("Server restarted to Main Configuration by {} at {}".format(interaction.user,dt_string))
    else:
        if (os.path.isdir("S:\GHG_A3\A3Master\mpmissions")):
                subprocess.run(["rmdir", "S:\GHG_A3\A3Master\mpmissions"], shell=True)
        subprocess.run("mklink /j S:\GHG_A3\A3Master\mpmissions S:\GHG_A3\A3Missions\Training", shell=True)
        os.startfile (r"E:\Desktop\GHG_Training.lnk")
        await interaction.response.send_message('Training server starting...')
        await serverControlLogChannel.send("Server restarted to Training Configuration by {} at {}".format(interaction.user,dt_string))


#Update Server
@bot.tree.command()
@app_commands.checks.has_any_role( int(config['Discord']['ghgAdminRoleID']), int(config['Discord']['ghgOfficerRoleID']), int(config['Discord']['ghgJuniorOfficerRoleID']))
async def update_server(interaction: discord.Interaction):
    """Updates Server and restarts to Training Preset."""
    
    serverControlLogChannel = interaction.guild.get_channel(int(config['Discord']['ghgLogChannelID']))
    await interaction.response.send_message('Updating Server. Please allow 10 minutes for the process to complete. Errors will not be shown here.')
    asyncio.ensure_future(update(interaction))
    
    
















bot.run(config['Discord']['botToken'])