import asyncio
import logging
import re
import time
from datetime import datetime, timedelta
import random

import urllib
import urllib.request
import json
from io import StringIO


from discord.ext import commands
from discord.utils import get

# format logging
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M:%S')

description = 'FFR discord bot'

bot = commands.Bot(command_prefix='?', description=description)

# constants
Sleep_Time = 5000
challengeseedadmin = "challengeseedadmin"
asyncseedadmin = "asyncseedadmin"
adminroles = [challengeseedadmin, asyncseedadmin]
challengeseedrole = "challengeseed"
asyncseedrole = "asyncseed"
nonadminroles = [challengeseedrole, asyncseedrole]
challengeseedchannel = "challengeseed"
challengeseedleaderboard = "challengeseedleaderboard"
challengeseedspoiler = "challengeseedspoilerchat"
asyncchannel = "async-seed_flags"
asyncleaderboard = "async-leaderboard"
asyncspoiler = "async-spoilers"


@bot.event
async def on_ready():
    print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ' Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command(pass_context=True)
async def ff1flags(ctx, flags: str = None, site: str = None):
    user = ctx.message.author
    if ctx.message.channel.name != "call_for_races":
        await bot.purge_from(ctx.message.channel, limit=1)
        await bot.send_message(user, "please only use that command in 'call_for_races'")
        return
    if flags == None:
        await bot.send_message(user, "You need to supply the flags to role a seed.")
        return
    await bot.say(flagseedgen(flags, site))

@bot.command(pass_context=True)
async def ff1beta(ctx, flags: str = None):
    user = ctx.message.author
    if ctx.message.channel.name != "call_for_races":
        await bot.purge_from(ctx.message.channel, limit=1)
        await bot.send_message(user, "please only use that command in 'call_for_races'")
        return
    site = "beta"
    if flags == None:
        await bot.send_message(user, "You need to supply the flags to role a seed.")
        return
    await bot.say(flagseedgen(flags, site))

@bot.command(pass_context=True)
async def ff1alpha(ctx, flags: str = None):
    user = ctx.message.author
    if ctx.message.channel.name != "call_for_races":
        await bot.purge_from(ctx.message.channel, limit=1)
        await bot.send_message(user, "please only use that command in 'call_for_races'")
        return
    site = "alpha"
    if ctx.message.channel.name != "call_for_races":
        return
    if flags == None:
        await bot.send_message(user, "You need to supply the flags to role a seed.")
        return
    await bot.say(flagseedgen(flags, site))

def flagseedgen(flags,site):
    seed = random.randint(0, 4294967295)
    url = "http://"
    if site:
        url += site +"."

    url += "finalfantasyrandomizer.com/Home/Randomize?s=" + ("{0:-0{1}x}".format(seed,8)) + "&f=" + flags
    return url

@bot.command(pass_context=True)
async def ff1seed(ctx):
    user = ctx.message.author
    if ctx.message.channel.name != "call_for_races":
        await bot.purge_from(ctx.message.channel, limit=1)
        await bot.send_message(user, "please only use that command in 'call_for_races'")
        return
    await bot.say("{0:-0{1}x}".format(random.randint(0, 4294967295),8))


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

@bot.command(pass_context=True)
async def multiall(ctx, raceid: str = None):
    user = ctx.message.author

    if raceid == None:
        await bot.send_message(user, "You need to supply the race id to get the multistream link.")
        return
    link = multistream(raceid, True)
    if link == None:
        await bot.say('There is no race with that 5 character id')
    else:
        await bot.say(link)


def multistream(raceid, all: bool = False):
    srl_tmp = r"http://api.speedrunslive.com/races/{}"
    ms_tmp = r"http://multistre.am/{}/"
    if raceid[0:4] == 'srl-':
        raceid = raceid[4:]
    srlurl = srl_tmp.format(raceid)
    data = ""
    with urllib.request.urlopen(srlurl) as response:
        data = response.read()

    data = data.decode()
    srlio = StringIO(data)
    srl_json = json.load(srlio)
    try:
        entrants = [srl_json['entrants'][k]['twitch'] for k in srl_json['entrants'].keys() if
                    (srl_json['entrants'][k]['statetext'] == "Ready") or all]
    except KeyError:
        return None
    entrants_2 = r'/'.join(entrants)
    ret = ms_tmp.format(entrants_2)
    return ret

@bot.command(pass_context=True)
async def purgemembers(ctx):
    """
    Removes members from the role associated with the channel,
    works for asyncseedrole and challengeseedrole
    :param ctx: context of the command
    :return: None
    """
    user = ctx.message.author
    role = await getrole(ctx)

    if role in user.roles and role.name in adminroles:
        if role.name == challengeseedadmin:
            role = get(ctx.message.server.roles, name=challengeseedrole)
        else:
            role = get(ctx.message.server.roles, name=asyncseedrole)
        members = ctx.message.server.members
        role_members = [x for x in members if role in x.roles]

        for x in role_members:
            await bot.remove_roles(x, role)
    else:
        await bot.send_message(user, ("... Wait a second.. YOU AREN'T AN ADMIN! (note, you need the correct admin role"
                                      " and need to use this in the spoilerchat for the role you want to purge members"
                                      " from)"))

    await bot.purge_from(ctx.message.channel, limit=1)


@bot.command(pass_context=True)
async def submit(ctx, runnertime: str = None):
    """
    Submits a runners time to the leaderboard and gives the appropriate role
    :param runnertime: time of the runner, in the format H:M:S, e.g. 2:32:12
    :param ctx: context of the command
    :return: None
    """
    user = ctx.message.author
    role = await getrole(ctx)

    if runnertime is None:
        await bot.send_message(user, "You must include a time when you submit a time.")
        await bot.purge_from(ctx.message.channel, limit=1)
        return

    if role is not None and role not in user.roles and role.name in nonadminroles:
        try:
            # convert to seconds using this method to make sure the time is readable and valid
            # also allows for time input to be lazy, ie 1:2:3 == 01:02:03 yet still maintain a consistent
            # style on the leaderboard
            t = datetime.strptime(runnertime, "%H:%M:%S")
        except ValueError:
            await bot.send_message(user, "The time you provided '" + str(runnertime) +
                                   "', this is not in the format HH:MM:SS (or you took a day or longer)")
            await bot.purge_from(ctx.message.channel, limit=1)
            return

        await bot.add_roles(user, role)

        delta = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second)
        username = re.sub('[()-]', '', user.display_name)
        leaderboard = await getleaderboard(ctx)
        leaderboard_list = leaderboard.content.split("\n")

        # the title is at the start and the forfeit # is after the hyphen at the end of the last line
        title = leaderboard_list[0]
        forfeits = int(leaderboard_list[-1].split('-')[-1])

        # trim the leaderboard to remove the title and forfeit message
        leaderboard_list = leaderboard_list[2:len(leaderboard_list)-2]

        for i in range(len(leaderboard_list)):
            leaderboard_list[i] = re.split('[)-]', leaderboard_list[i])[1:]

        # convert the time back to hours minutes and seconds for the leaderboard
        totsec = delta.total_seconds()
        h = totsec // 3600
        m = (totsec % 3600) // 60
        s = (totsec % 3600) % 60

        leaderboard_list.append(
            [" "+username+" ", " %d:%02d:%02d" % (h, m, s)])

        # sort the times
        leaderboard_list.sort(
            key=lambda x: datetime.strptime(x[1].strip(), "%H:%M:%S"))

        # build the string for the leaderboard
        new_leaderboard = title+"\n\n"
        for i in range(len(leaderboard_list)):
            new_leaderboard += str(i+1) + ")" + \
                leaderboard_list[i][0]+"-" + leaderboard_list[i][1] + "\n"
        new_leaderboard += "\nForfeits - " + str(forfeits)

        await bot.edit_message(leaderboard, new_leaderboard)
        await bot.send_message(await getspoilerchat(ctx), 'GG %s' % user.mention)
        await bot.purge_from(ctx.message.channel, limit=1)
        await changeparticipants(ctx)
    else:
        await bot.send_message(user, "You already have the relevent role.")
        await bot.purge_from(ctx.message.channel, limit=1)

@bot.command(pass_context=True)
async def remove(ctx, *, players: str = None):
    """
    Removes people from the leaderboard and allows them to reenter a time
    This entire function is gross, it works but is messy
    :param ctx: context of the command
    :param players: @mentions of the players that will be removed from the leaderboard
    :return: None
    """
    user = ctx.message.author
    if players is None:
        await bot.send_message(user, "You did not mention a player.")
        await bot.purge_from(ctx.message.channel, limit=1)
        print("players==none")
        return

    channel = ctx.message.channel
    roles = ctx.message.server.roles
    role = None
    channels = ctx.message.server.channels
    challengeseed = get(channels, name=challengeseedleaderboard)
    asyncseed = get(channels, name=asyncleaderboard)
    if channel == challengeseed:
        role = get(roles, name=challengeseedadmin)
        remove_role = get(roles, name= challengeseedrole)
        participantnumchannel = get(channels, name= challengeseedchannel)
    if channel == asyncseed:
        role = get(roles, name=asyncseedadmin)
        remove_role = get(roles, name=asyncseedrole)
        participantnumchannel = get(channels, name=asyncchannel)
    if role in user.roles:
        leaderboard = bot.logs_from(channel, 100, reverse=True)
        async for x in leaderboard:
            if bot.user == x.author:
                leaderboard = x

        leaderboard_list = leaderboard.content.split("\n")

        # the title is at the start and the forfeit # is after the hyphen at the end of the last line
        title = leaderboard_list[0]
        forfeits = int(leaderboard_list[-1].split('-')[-1])

        # trim the leaderboard to remove the title and forfeit message
        leaderboard_list = leaderboard_list[2:len(leaderboard_list) - 2]

        for i in range(len(leaderboard_list)):
            leaderboard_list[i] = re.split('[)-]', leaderboard_list[i])[1:]

        players = ctx.message.mentions
        if not players:
            await bot.send_message(user, "You did not mention a player.")
            await bot.purge_from(ctx.message.channel, limit=1)
            return

        for player in players:
            i = 0
            for i in range(len(leaderboard_list)):
                if leaderboard_list[i][0] == re.sub('[()-]', '', player.display_name):
                    del leaderboard_list[i]
                    await bot.remove_roles(player, remove_role)
                    await changeparticipants(ctx, increment=False, channel=participantnumchannel)
                    break
            

        # should already be sorted
        #leaderboard_list.sort(
         #   key=lambda x: datetime.strptime(x[1].strip(), "%H:%M:%S"))

        # build the string for the leaderboard
        new_leaderboard = title + "\n\n"
        for i in range(len(leaderboard_list)):
            new_leaderboard += str(i + 1) + ")" + \
                               leaderboard_list[i][0] + "-" + leaderboard_list[i][1] + "\n"
        new_leaderboard += "\nForfeits - " + str(forfeits)

        await bot.edit_message(leaderboard, new_leaderboard)
        await bot.purge_from(ctx.message.channel, limit=1)




@bot.command(pass_context=True)
async def createleaderboard(ctx, name: str = None):
    """
    Creates a leaderboard post with a title and the number of forfeits
    :param ctx: context of the command
    :param name: title of the leaderboard
    :return: None
    """
    
    user = ctx.message.author
    if name is None:
        bot.send_message(user, "You did not submit a name.")
        await bot.purge_from(ctx.message.channel, limit=1)
        return
    role = await getrole(ctx)

    # gross way of doing this, works for now
    if role in user.roles and role.name == challengeseedadmin:
        await bot.send_message(get(ctx.message.server.channels, name=challengeseedleaderboard),
                               name+"\n\nForfeits - 0")
        await bot.send_message(get(ctx.message.server.channels, name=challengeseedchannel), "Number of participants: 0")

    elif role in user.roles and role.name == asyncseedadmin:
        await bot.send_message(get(ctx.message.server.channels, name=asyncleaderboard),
                               name + "\n\nForfeits - 0")
        await bot.send_message(get(ctx.message.server.channels, name=asyncchannel), "Number of participants: 0")

    else:
        await bot.send_message(user, ("... Wait a second.. YOU AREN'T AN ADMIN! (note, you need the admin role"
                                      "for this channel)"))

    await bot.purge_from(ctx.message.channel, limit=1)


@bot.command(pass_context=True)
async def forfeit(ctx):
    """
    Increments the number of forfeits and gives the appropriate role to the user
    :param ctx: context of the command
    :return: None
    """

    user = ctx.message.author
    role = await getrole(ctx)

    if role is not None and role not in user.roles and role.name in nonadminroles:
        await bot.add_roles(user, role)
        leaderboard = await getleaderboard(ctx)
        new_leaderboard = leaderboard.content.split("\n")
        forfeits = int(new_leaderboard[-1].split("-")[-1]) + 1
        new_leaderboard[-1] = "Forfeits - " + str(forfeits)
        seperator = "\n"
        new_leaderboard = seperator.join(new_leaderboard)

        await bot.edit_message(leaderboard, new_leaderboard)
        await bot.purge_from(ctx.message.channel, limit=1)
        await changeparticipants(ctx)
    else:
        await bot.purge_from(ctx.message.channel, limit=1)

# @bot.command()
# async def testexit():
#     await bot.say("exiting, should restart right away")
#     SystemExit()


@bot.command(pass_context=True)
async def spectate(ctx):
    """
    Gives the user the appropriate role
    :param ctx: context of the command
    :return: None
    """
    user = ctx.message.author
    role = await getrole(ctx)
    if role is not None and role.name in nonadminroles:
        await bot.add_roles(user, role)
    await bot.purge_from(ctx.message.channel, limit=1)


async def getrole(ctx):
    """
    Returns the Role object depending on the channel the command is used in
    Acts as a check for making sure commands are executed in the correct spot as well
    :param ctx: context of the command
    :return: Role or None
    """

    user = ctx.message.author
    roles = ctx.message.server.roles
    channel = ctx.message.channel
    channels = ctx.message.server.channels
    challengeseed = get(channels, name=challengeseedchannel)
    asyncseed = get(channels, name=asyncchannel)
    chalseedspoilerobj = get(channels, name=challengeseedspoiler)
    asyseedspoilerobj = get(channels, name=asyncspoiler)

    if channel == challengeseed:
        role = get(roles, name=challengeseedrole)
    elif channel == asyncseed:
        role = get(roles, name=asyncseedrole)
    elif channel == chalseedspoilerobj:
        role = get(roles, name=challengeseedadmin)
    elif channel == asyseedspoilerobj:
        role = get(roles, name=asyncseedadmin)
    else:
        await bot.send_message(user, "That command isn't allowed here.")
        return None

    return role


async def getleaderboard(ctx):
    """
    Returns the leaderboard Message object depending on the channel the command is used in
    :param ctx: context of the command
    :return: Message or None
    """
    user = ctx.message.author
    channel = ctx.message.channel
    channels = ctx.message.server.channels
    challengeseed = get(channels, name=challengeseedchannel)
    asyncseed = get(channels, name=asyncchannel)

    if channel == challengeseed:
        leaderboard = bot.logs_from(
            get(channels, name=challengeseedleaderboard), 100, reverse=True)
    elif channel == asyncseed:
        leaderboard = bot.logs_from(
            get(channels, name=asyncleaderboard), 100, reverse=True)
    else:
        await bot.send_message(user, "That command isn't allowed here.")
        return None

    async for x in leaderboard:
        if bot.user == x.author:
            leaderboard = x

    return leaderboard


async def getspoilerchat(ctx):
    """
    Returns the spoiler Channel object depending on the channel the command is used in
    :param ctx: context of the command
    :return: Channel or None
    """

    user = ctx.message.author
    channel = ctx.message.channel
    channels = ctx.message.server.channels
    challengeseed = get(channels, name=challengeseedchannel)
    asyncseed = get(channels, name=asyncchannel)

    if channel == challengeseed:
        spoilerchat = get(channels, name='challengeseedspoilerchat')
    elif channel == asyncseed:
        spoilerchat = get(channels, name='async-spoilers')
    else:
        await bot.send_message(user, "That command isn't allowed here.")
        return None

    return spoilerchat


async def changeparticipants(ctx,increment = True, channel = None):
    """
    changes the participant number
    :param ctx: context of the command
    :param increment: sets if it is incremented or decremented
    :return: None
    """

    participants = bot.logs_from(ctx.message.channel if channel is None else channel, 100, reverse=True)
    async for x in participants:
        if x.author == bot.user:
            participants = x
    num_partcipents = int(participants.content.split(":")[1])
    if increment:
        num_partcipents += 1
    else:
        num_partcipents -= 1
    new_participants = "Number of participants: " + str(num_partcipents)
    await bot.edit_message(participants, new_participants)


# used to clear channels for testing purposes

# @bot.command(pass_context = True)
# async def purge(ctx):
#     channel = ctx.message.channel
#     await bot.purge_from(channel, limit=100000)


def handle_exit(client,loop):
    # taken from https://stackoverflow.com/a/50981577
    loop.run_until_complete(client.logout())
    for t in asyncio.Task.all_tasks(loop=loop):
        if t.done():
            t.exception()
            continue
        t.cancel()
        try:
            loop.run_until_complete(asyncio.wait_for(t, 5, loop=loop))
            t.exception()
        except asyncio.InvalidStateError:
            pass
        except asyncio.TimeoutError:
            pass
        except asyncio.CancelledError:
            pass


def run_client(client, *args, **kwargs):
    loop = asyncio.get_event_loop()
    while True:
        try:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Starting connection")
            loop.run_until_complete(client.start(*args, **kwargs))
        except KeyboardInterrupt:
            handle_exit(client, loop)
            client.loop.close()
            print("Program ended")
            break
        except Exception as e:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), " Error", e)
            handle_exit(client, loop)
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "Waiting until restart")
        time.sleep(Sleep_Time)


with open('token.txt', 'r') as f:
    token = f.read()
token = token.strip()


run_client(bot, token)
