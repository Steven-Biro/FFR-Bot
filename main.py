import asyncio
import logging
import re
import time
import sqlite3
from datetime import datetime, timedelta
import weekly
import urllib.request
import json
from io import StringIO

from discord.ext import commands
from discord.utils import get

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

description = 'FFR discord bot'

bot = commands.Bot(command_prefix='?', description=description)


# constants
Sleep_Time = 5000

# challenge = weekly.Weekly(category = "Challenge Seed", role="challengeseed", adminrole="challengeseedadmin", seedchannel="challengeseed", spoilerchannel="challengeseedspoilerchat", leaderboardchannel="challengeseedleaderboard")
challenge = weekly.Weekly()
challenge.load("Challenge Seed")


# asyncseed = weekly.Weekly(category = "Weekly-Async", role="asyncseed", adminrole="asynseedasmin", seedchannel="async-seed_flags", spoilerchannel="async-spoilers", leaderboardchannel="async-leaderboard")
asyncseed = weekly.Weekly()
asyncseed.load("Weekly-Async")

Weeklies = dict()
Weeklies[challenge.get("category")] = challenge
Weeklies[asyncseed.get("category")] = asyncseed

@bot.command()
async def wipeleaderboard(ctx, name: str):
    await Weeklies[str(ctx.channel.category())].wipeleaderboard(name)
    await ctx.channel.purge(1)

@bot.command()
async def createleaderboard(ctx, name: str,  num: int, *args: str):
    await Weeklies[str(ctx.channel.category())].initializeleaderboard(name, num, *args)
    await ctx.channel.purge(1)


@bot.command(pass_context=True)
async def multi(ctx, raceid: str = None):
    user = ctx.message.author

    if raceid == None:
        await bot.send_message(user, "You need to supply the race id to get the multistream link.")
        return
    link = multistream(raceid)
    if link == None:
        await bot.say('There is no race with that 5 character id, try remove "srl-" from the room id.')
    else:
        await bot.say(link)



def multistream(raceid):

    srl_tmp = r"http://api.speedrunslive.com/races/{}"
    ms_tmp = r"http://multistre.am/{}/"
    srlurl = srl_tmp.format(raceid)
    data = ""
    with urllib.request.urlopen(srlurl) as response:
        data = response.read()

    data = data.decode()
    srlio = StringIO(data)
    srl_json = json.load(srlio)
    try:
        entrants = [srl_json['entrants'][k]['twitch'] for k in srl_json['entrants'].keys() if
                    srl_json['entrants'][k]['statetext'] == "Ready"]
    except KeyError:
        return None
    entrants_2 = r'/'.join(entrants)
    ret = ms_tmp.format(entrants_2)
    return ret

@bot.command()
async def submit(ctx, runnertime: str = None):
    if runnertime is None:
        await ctx.author.send("You must include a time when you submit a time.")
        await ctx.channel.purge(1)
        return

    try:
        # convert to seconds using this method to make sure the time is readable and valid
        # also allows for time input to be lazy, ie 1:2:3 == 01:02:03 yet still maintain a consistent
        # style on the leaderboard
        t = datetime.strptime(runnertime, "%H:%M:%S")
    except ValueError:
        await ctx.author.send("The time you provided '" + str(runnertime) +
                               "', this is not in the format HH:MM:SS (or you took a day or longer)")
        await ctx.channel.purge(1)
        return



    challenge.addtoleaderboard(ctx.author.id,ctx.author.display_name,t,ctx.author.roles)
    Weeklies[str(ctx.channel.category())].addtoleaderboard(ctx.author.id,ctx.author.display_name,)


def run_client(client, *args, **kwargs):
    loop = asyncio.get_event_loop()
    while True:
        try:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Starting connection")
            loop.run_until_complete(client.start(*args, **kwargs))
        except KeyboardInterrupt:
            loop.run_until_complete(client.logout())
            break
        except Exception as e:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), " Error", e)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Waiting until restart")
        time.sleep(Sleep_Time)


with open('token.txt', 'r') as f:
    token = f.read()
token.strip()

run_client(bot, token)
