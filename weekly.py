from datetime import datetime, timedelta
import json

from discord.ext import commands
from discord.utils import get

class Weekly:
    """
    A class that represents a group of channels that is usually used for weekly races (a better name would be helpful)
    """
    def __init__(self, server = None, category = None, role = None, adminrole = None, seedchannel = None, leaderboardchannel = None,
                 spoilerchannel = None):
        self.__category = category
        self.__role = role
        self.__adminrole = adminrole
        self.__seedchannel = seedchannel
        self.__leaderboardchannel = leaderboardchannel
        self.__spoilerchannel = spoilerchannel
        self.__server = server
        self.__board = dict()


    def set(self, variable, value):
        """
        set variables for this Weekly
        :param variable: str of the variable to set
        :param value: value for that variable
        :return: None
        """
        if variable == "category":
            self.__category = value
        elif variable == "seedchannel":
            self.__seedchannel = value
        elif variable == "leaderboard":
            self.__spoilerchannel = value
        elif variable == "spoilerchannel":
            self.__leaderboardchannel = value
        elif variable == "adminrole":
            self.__adminrole = value
        elif variable == "board_num":
            self.__board["num"] = value
        elif variable == "leaderboardmessage":
            self.__board["leaderboardmessage"] = value
        elif variable == "role":
            self.__role = value
        else:
            raise Exception("Cannot set variable.")

    def get(self, variable):
        """
        returns the value of self.__variable
        :param variable: str of te variable you want
        :return: value of the variable you want
        """
        if variable == "category":
            return self.__category
        elif variable == "seedchannel":
            return self.__seedchannel
        elif variable == "spoilerchannel":
            return self.__spoilerchannel
        elif variable == "leaderboard":
            return self.__leaderboardchannel
        elif variable == "adminrole":
            return self.__adminrole
        elif variable == "board_num":
            return self.__board["num"]
        elif variable == "leaderboardmessage":
            return self.__board["leaderboardmessage"]
        elif variable == "role":
            return self.__role
        else:
            raise Exception("Cannot get variable.")

    def load(self, category):
        """
        loads the stored data for this Weekly from the config file
        :param category: unique id for the category associated with this Weekly
        :return: None
        """
        try:
            with open('config.json', 'r') as f:
                data = json.load(f)
                self.__category = category
                self.__role = data[str(category)]["role"]
                self.__adminrole = data[str(category)]["adminrole"]
                self.__seedchannel = data[str(category)]["seedchannel"]
                self.__leaderboardchannel = data[str(category)]["leaderboardchannel"]
                self.__spoilerchannel = data[str(category)]["spoilerchannel"]
        except KeyError:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "KeyError when trying to load " + str(category))

    def save(self):
        """
        saves the stored data for this Weekly to the config file
        :return:
        """
        with open('config.json', 'r+') as f:
            data = json.load(f)
            f.seek(0)
            data[self.__category] = {"role": self.__role, "adminrole": self.__adminrole, "category": self.__category,
                                     "seedchannel": self.__seedchannel, "spoilerchannel": self.__spoilerchannel,
                                     "leaderboardchannel": self.__leaderboardchannel}
            json.dump(data, f)
            f.truncate()


    def saveboard(self):
        """
        saves the current board to a text file in the leaderboards folder
        :return: None
        """
        with open('leaderboards/' + self.__leaderboardchannel+"/"+self.__board["name"], 'r+') as f:
            f.seek(0)
            json.dump(self.__board, f)
            f.truncate()

    def loadboard(self, name = None):
        """
        loads a leaderboard from the leaderboards folder, if no name is provided, it uses the current board's name
        :param name: name of the leaderboard to load
        :return: None
        """
        with open('leaderboards/' + self.__leaderboardchannel+"/"+
                          name if name != None else self.__board["name"], 'r+') as f:
            self.__board = json.load(f)

    def initializeleaderboard(self, name, leaderboardmessage, roles, leaderboardnum = 1, *args):
        """
        initializes the leaderboard and creates as many sub categories as needed, a name and role is needed for each
        :param name: name of the leaderboard
        :param leaderboardnum: amount of leaderboards, ie challenge and challenge+ is 2, with
            challenge++ its 3
        :param args: name and role associated with allowing a player to enter this leaderboard, use ! in front
            to make the condition if a player doesnt have that role instead of if they have it
        :return: None
        """
        if self.__adminrole not in roles:
            return #TODO make this return something so a message can be sent to the user of the command
        self.__board = dict()
        self.__board["name"] = name
        self.__board["num"] = leaderboardnum
        self.__board["leaderboardmessage"] = leaderboardmessage
        for i in range(leaderboardnum):
            self.__board[str(i)] = dict()
            self.__board[str(i)]["title"] = args[3*i]
            self.__board[str(i)]["role"] = args[3*i+1]
            self.__board[str(i)]["updatable"] = args[3*i+2]
            self.__board[str(i)]["times"] = []
            self.__board[str(i)]["forfeits"] = 0
            self.__board[str(i)]["participants"] = 0
            self.__board[str(i)]["requiredrole"] = None
            self.__board[str(i)]["spectators"] = []
            self.__board[str(i)]["forfeiters"] = []

        self.saveboard()

    def wipeleaderboard(self, name, leaderboardmessage, roles, *args):
        """
        wipes the leaderboard of times and renames the whole thing, the amount of leaderboards and each name
            for the specific ones stays the same
        :param name: Name for the new leaderboard
        :return: None
        """
        if self.__adminrole not in roles:
            return #TODO make this return something so a message can be sent to the user of the command
        self.__board["name"] = name
        self.__board["leaderboardmessage"] = leaderboardmessage
        for i in range(self.__board["num"]):
            self.__board[str(i)]["times"] = []
            self.__board[str(i)]["forfeits"] = 0
            self.__board[str(i)]["participants"] = 0
            if bool(args[i]):
                self.__board[str(i)]["updateable"] = True
            else:
                self.__board[str(i)]["updateable"] = False
        self.saveboard()

    def addtoleaderboard(self, id, name, time, roles, board_num = 0):
        """
        adds (or updates) a player time to the leaderboard based on the board number given
        :param id: player unique id
        :param name: player display name
        :param time: player time
        :param roles: roles that the player has
        :param board_num: the board number, + boards etc will be below in the same message (this might need to be changed
            to a separate message in the future
        :return: None
        """
        key = None
        if (self.__board[board_num]["role"] not in roles) or (self.__board[board_num]["updatable"]):
            if (self.__board[board_num]["requiredrole"] == None) or (self.__board[board_num]["requiredrole"] in roles):
                key = board_num
        if key == None:
            raise Exception("Cannot add to leaderboard.")
        updated = False
        for i in range(len(self.__board[str(board_num)]["times"])):
            if self.__board[str(board_num)]["times"][i] == id:
                self.__board[str(board_num)]["times"][i][2] = time
                updated = True
        if not updated:
            self.__board[key]["times"].append([id,name,time])
        self.__board[key]["times"].sort(
            key=lambda x: datetime.strptime(x[2].strip(), "%H:%M:%S"))
        self.__board["participants"] += 1
        self.saveboard()
        return self.__board[board_num]["role"]



    def removefromleaderboard(self, id, roles, board_num = 0):
        """
        removes a player from the leaderboard specified by number board_num
        :param id: player id to remove
        :param board_num: board_num number to remove the player from
        :return: None
        """
        if self.__adminrole not in roles:
            return #TODO make this return something so a message can be sent to the user of the command

        for i in range(len(self.__board[str(board_num)]["times"])):
            if self.__board[str(board_num)]["times"][i][0] == id:
                del self.__board[str(board_num)]["times"][i]
                self.__board["participants"] -= 1
                self.saveboard()
                return self.__board[board_num]["role"]

    def forfeit(self, id, roles, board_num = 0):
        if self.__board[board_num]["role"] not in roles:
            self.__board[str(board_num)]["forfeiters"].append(id)
            self.__board["forfeits"] += 1
            self.__board["participants"] += 1
            return self.__board[str(board_num)]["role"]

    def spectate(self, id, roles, board_num=0):
        if self.__board[board_num]["role"] not in roles:
            self.__board[str(board_num)]["spectators"].append(id)
            return self.__board[str(board_num)]["role"]


    def writeleaderboard(self):
        """
        returns a string with the entire leaderboard
        :return: boardstr, essentially a formated self.__board
        """
        boardstr = self.__board["name"]
        for i in range(len(self.__board["num"])):
            boardstr += "\n\n" + self.__board[str(i)]["title"]+"\n"
            for j in range(len(self.__board[str(i)]["times"])):
                boardstr += str(j + 1) + ") " + self.__board[str(i)]["times"][j][1] + " - " +\
                            self.__board[str(i)]["times"][j][2] + "\n"
            boardstr += "\nForfeits - " + self.__board[str(i)]["forfeits"]


        return boardstr

