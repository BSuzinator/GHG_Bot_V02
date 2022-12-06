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
from discord import *
from discord.ext import commands
from discord.ext.commands import CommandNotFound
from discord.utils import get
import esix
#from ghg_functions import *
#from ghg_automatedTasks import *
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

#Read Config for connection info
config = configparser.ConfigParser()
config.read('connectionInfo.ini')

intents = discord.Intents.all()

client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        await message.channel.send('Hello!')

client.run(config['Discord']['botToken'])