import asyncio
import logging
import re
import time
import pickle
from datetime import datetime, timedelta
import weekly
import urllib.request
import json
from io import StringIO

from discord.ext import commands
from discord.utils import get

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

description = 'FFR discord bot'

admins = []
bot = commands.Bot(command_prefix='?', description=description)
Weeklies = dict()

def is_admin(ctx):
    user = ctx.author
    return (user.id in admins) or ctx.bot.is_owner(user)

@bot.command(pass_context=True)
@commands.check(is_admin)
async def load(ctx):
    _load()

@bot.command(pass_context=True)
@commands.check(is_admin)
async def save(ctx):
    _save()


def _load():
    global admins, Weeklies
    with open('data', 'rb') as f:
        data = pickle.load(f)
        Weeklies = data[0]
        admins = data[1]
def _save():
    with open('data', 'wb') as f:
        data = [Weeklies,admins]
        pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)

@bot.command(pass_context=True)
@commands.check(is_admin)
async def set(ctx, variable, value):

    if variable is "admin":
        mentions = ctx.message.mentions
        if len(mentions) != 1:
            return
        else:
            admins.append(mentions[0].id)
    else:
        Weeklies[ctx.message.category.name].set(variable, value)


@bot.command(pass_context=True)
@commands.check(is_admin)
async def createweekly(ctx, *args):
    values = list(args)
    for i in range(len(args)):
        if args[i][1:2] == '#':
            values[i] = get(ctx.guild.channels, id=int(re.sub('[^0-9]', '', args[i])))
        else:
            values[i] = get(ctx.guild.roles, id=int(re.sub('[^0-9]', '', args[i])))
    Weeklies[ctx.channel.category.name] =\
        weekly.Weekly(server = ctx.guild, category = ctx.channel.category.name, role=values[0], adminrole=values[1],
                      seedchannel=values[2], spoilerchannel=values[3],leaderboardchannel=values[4])

@bot.command(pass_context=True)
async def wipeleaderboard(ctx, name: str):
    leaderboardchannel = await Weeklies[str(ctx.channel.category.id)].get("leaderboard")
    message = await leaderboardchannel.send("initializing...")
    await Weeklies[str(ctx.channel.category.id)].wipeleaderboard(name, message, ctx.author.roles)
    await message.edit(Weeklies[str(ctx.channel.category.id)].writeleaderboard())
    await ctx.channel.purge(1)

@bot.command(pass_context=True)
async def createleaderboard(ctx, name: str,  num: int = 1, *args: str):
    leaderboardchannel = Weeklies[str(ctx.channel.category.name)].get("leaderboard")
    print(leaderboardchannel)
    print(type(leaderboardchannel))
    message = await leaderboardchannel.send("initializing...")
    await Weeklies[str(ctx.channel.category.id)].initializeleaderboard(name, message, ctx.author.roles, num, *args)
    await message.edit(Weeklies[str(ctx.channel.category.id)].writeleaderboard())
    await ctx.channel.purge(1)

@bot.command(pass_context=True)
async def submit(ctx, runnertime: str = None, board_num: int = 0):
    await ctx.channel.purge(1)
    if runnertime is None:
        await ctx.author.send("You must include a time when you submit a time.")
        return

    if (board_num > Weeklies[str(ctx.channel.category.id)].get("board_num")) or (board_num < 0):
        await ctx.author.send("You must select a valid board to submit a time for.")
        return
    try:
        # convert to seconds using this method to make sure the time is readable and valid
        # also allows for time input to be lazy, ie 1:2:3 == 01:02:03 yet still maintain a consistent
        # style on the leaderboard
        t = datetime.strptime(runnertime, "%H:%M:%S")
    except ValueError:
        await ctx.author.send("The time you provided '" + str(runnertime) +
                               "', this is not in the format HH:MM:SS (or you took a day or longer)")
        return


    role = await Weeklies[str(ctx.channel.category.id)].addtoleaderboard(ctx.author.id,ctx.author.display_name,t,ctx.author.roles,board_num=board_num)
    board = await Weeklies[str(ctx.channel.category.id)].writeleaderboard()
    message = await Weeklies[str(ctx.channel.category.id)].get("leaderboardmessage")
    message.edit(board)

    await ctx.author.add_roles(role, "Automatic, for a weekly seed")

@bot.command(pass_context=True)
async def remove(ctx, board_num, *args):
    players = ctx.message.mentions
    for player in players:
        role = await Weeklies[str(ctx.channel.category.id)].removefromleaderboard(player, ctx.author.id, board_num=board_num)
        await ctx.author.remove_roles(role, "Automatic, for a weekly seed, must be a weekly seed admin to use")

@bot.command(pass_context=True)
async def spectate(ctx):
    role = await ctx.author.add_roles(Weeklies[str(ctx.channel.category.id)].spectate(ctx.author.id,ctx.author.roles))
    await ctx.author.add_roles(role, "Automatic, for a weekly seed")

@bot.command(pass_context=True)
async def forfeit(ctx, board_num = 0):
    role = await ctx.author.add_roles(Weeklies[str(ctx.channel.category.id)].forfeit(ctx.author.id,ctx.author.roles))
    await ctx.author.add_roles(role, "Automatic, for a weekly seed")

@bot.command(pass_context=True)
async def multi(ctx, raceid: str = None, allow_notready = None):
    user = ctx.message.author

    if raceid == None:
        await bot.send_message(user, "You need to supply the race id to get the multistream link.")
        return
    link = multistream(raceid, False if allow_notready is None else True)
    if link == None:
        await bot.say('There is no race with that 5 character id, try remove "srl-" from the room id.')
    else:
        await bot.say(link)


def multistream(raceid, allow_notready: bool):

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
                    (srl_json['entrants'][k]['statetext'] == "Ready") or allow_notready]
    except KeyError:
        return None
    entrants_2 = r'/'.join(entrants)
    ret = ms_tmp.format(entrants_2)
    return ret




with open('token.txt', 'r') as f:
    token = f.read()
token.strip()

bot.run(token)
