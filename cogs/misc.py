from typing import Optional
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
import subprocess
import threading
import time
import traceback
import ts3

class misc(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @bot.tree.command()
    async def hello(interaction: discord.Interaction):
        """Says hello!"""
        await interaction.response.send_message(f'Hi, {interaction.user.mention}')

    async def setup(bot):
        await bot.add_cog(misc(bot))