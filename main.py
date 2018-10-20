import asyncio
import logging
import re
import time
import sqlite3
from datetime import datetime, timedelta
import weekly

from discord.ext import commands
from discord.utils import get

# logging.basicConfig(
#     format='%(asctime)s %(levelname)-8s %(message)s',
#     level=logging.INFO,
#     datefmt='%Y-%m-%d %H:%M:%S')

description = 'FFR discord bot'

# bot = commands.Bot(command_prefix='?', description=description)


# constants
Sleep_Time = 5000

# challenge = weekly.Weekly(role="challengeseed", adminrole="challengeseedadmin", seedchannel="challengeseed", spoilerchannel="challengeseedspoilerchat", leaderboardchannel="challengeseedleaderboard")
challenge = weekly.Weekly()
challenge.load("challengeseed")


# asyncseed = weekly.Weekly(role="asyncseed", adminrole="asynseedasmin", seedchannel="async-seed_flags", spoilerchannel="async-spoilers", leaderboardchannel="async-leaderboard")
asyncseed = weekly.Weekly()
asyncseed.load("async-seed_flags")


# def run_client(client, *args, **kwargs):
#     loop = asyncio.get_event_loop()
#     while True:
#         try:
#             print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Starting connection")
#             loop.run_until_complete(client.start(*args, **kwargs))
#         except KeyboardInterrupt:
#             loop.run_until_complete(client.logout())
#             break
#         except Exception as e:
#             print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), " Error", e)
#         print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Waiting until restart")
#         time.sleep(Sleep_Time)
#
#
# with open('token.txt', 'r') as f:
#     token = f.read()
# token.strip()
#
# run_client(bot, token)
