from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import asyncpg
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
import subprocess
import threading
import time
import traceback
import ts3
from typing import List, Optional

#Read Config for connection info
config = configparser.ConfigParser()
config.read('connectionInfo.ini')

#MY_GUILD = discord.Object(id=int(config['Discord']['ghgGuildID']))  # replace with your guild id

class CustomBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        db_pool: asyncpg.Pool,
        web_client: ClientSession,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.db_pool = db_pool
        self.web_client = web_client
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:

        # here, we are loading extensions prior to sync to ensure we are syncing interactions defined in those extensions.

        for extension in self.initial_extensions:
            await self.load_extension(extension)

        # In overriding setup hook,
        # we can do things that require a bot prior to starting to process events from the websocket.
        # In this case, we are using this to ensure that once we are connected, we sync for the testing guild.
        # You should not do this for every guild or for global sync, those should only be synced when changes happen.
        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)

        # This would also be a good place to connect to our database and
        # load anything that should be in memory prior to handling events.


async def main():

    # When taking over how the bot process is run, you become responsible for a few additional things.

    # 1. logging

    # for this example, we're going to set up a rotating file logger.
    # for more info on setting up logging,
    # see https://discordpy.readthedocs.io/en/latest/logging.html and https://docs.python.org/3/howto/logging.html

    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)

    handler = logging.handlers.RotatingFileHandler(
        filename='discord.log',
        encoding='utf-8',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=10,  # Rotate through 5 files
    )
    dt_fmt = '%Y-%m-%d %H:%M:%S'
    formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Alternatively, you could use:
    # discord.utils.setup_logging(handler=handler, root=False)

    # One of the reasons to take over more of the process though
    # is to ensure use with other libraries or tools which also require their own cleanup.

    # Here we have a web client and a database pool, both of which do cleanup at exit.
    # We also have our bot, which depends on both of these.

    async with ClientSession() as our_client, asyncpg.create_pool(user='postgres', command_timeout=30) as pool:
        # 2. We become responsible for starting the bot.

        exts = ['','']
        async with CustomBot(commands.when_mentioned, db_pool=pool, web_client=our_client, testing_guild_id=417512514771746817, initial_extensions=exts) as bot:

            await bot.start(os.getenv(config['Discord']['botToken'], ''))


# For most use cases, after defining what needs to run, we can just tell asyncio to run it:
asyncio.run(main())