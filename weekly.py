from datetime import datetime, timedelta
import json

class Error(Exception):
   """Base class for other exceptions"""
   pass

class AddToLeaderboardError(Error):
    """raised when a player cannot be added to a leaderboard"""
    pass

class DeleteFromLeaderboardError(Error):
    """raised when deleting a player from a leaderboard has failed"""
    pass

class CannotSetVariable(Error):
    """raised when variable cannot be set"""
    pass

class CannotGetVariable(Error):
    """raised when trying to get a variable fails"""
    pass


class Weekly:
    """
    A class that represents a group of channels that is usually used for weekly races (a better name would be helpful)
    """
    def __init__(self, category = None, role = None, adminrole = None, seedchannel = None, leaderboardchannel = None,
                 spoilerchannel = None):
        self.__category = category
        self.__role = role
        self.__adminrole = adminrole
        self.__seedchannel = seedchannel
        self.__leaderboardchannel = leaderboardchannel
        self.__spoilerchannel = spoilerchannel
        self.__board = dict()

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
        elif variable == "role":
            self.__role = value
        elif variable == "adminrole":
            self.__adminrole = value
        else:
            raise CannotSetVariable

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
        elif variable == "leaderboard":
            return self.__spoilerchannel
        elif variable == "spoilerchannel":
            return self.__leaderboardchannel
        elif variable == "role":
            return self.__role
        elif variable == "adminrole":
            return self.__adminrole
        else:
            return CannotGetVariable


    def saveboard(self):
        """
        saves the current board to a text file in the leaderboards folder
        :return: None
        """
        #TODO fix saveboard and loadboard to take a board name to load
        with open('leaderboards/' + self.__leaderboardchannel, 'r+') as f:
            f.seek(0)
            json.dump(self.__board, f)
            f.truncate()

    def loadboard(self):
        """
        loads a leaderboard from the leaderboards folder
        :return: None
        """
        with open('leaderboards/' + self.__leaderboardchannel, 'r+') as f:
            self.__board = json.load(f)

    def initializeleaderboard(self, name, leaderboardnum = 1, *args):
        """
        initializes the leaderboard and creates as many sub categories as needed, a name and role is needed for each
        :param name: name of the leaderboard
        :param leaderboardnum: amount of leaderboards, ie challenge and challenge+ is 2, with
            challenge++ its 3
        :param args: name and role associated with allowing a player to enter this leaderboard, use ! in front
            to make the condition if a player doesnt have that role instead of if they have it
        :return: None
        """
        self.__board = dict()
        self.__board["name"] = name
        self.__board["num"] = leaderboardnum
        for i in range(leaderboardnum):
            self.__board[str(i)] = dict()
            self.__board[str(i)]["title"] = args[2*i]
            self.__board[str(i)]["role"] = args[2*i+1]
            self.__board[str(i)]["times"] = []
            self.__board[str(i)]["forfeits"] = 0
        self.saveboard()

    def wipeleaderboard(self, name):
        """
        wipes the leaderboard of times and renames the whole thing, the amount of leaderboards and each name
            for the specific ones stays the same
        :param name: Name for the new leaderboard
        :return: None
        """
        self.__board["name"] = name
        for i in range(self.__board["num"]):
            self.__board[str(i)]["times"] = []
            self.__board[str(i)]["forfeits"] = 0

    def addtoleaderboard(self, id, name, time, roles, matchrole = True):
        """
        adds a player time to the leaderboard based on the role matching or not
        ":param id: player unique id
        :param name: player display name
        :param time: player time
        :param roles: roles that the player has
        :param matchrole: true if the role must match, false if not
        :return: None
        """
        key = None
        for i in range(self.__board["num"]):
            if (self.__board[str(i)]["role"] in roles) ^ (not matchrole):
                key = str(i)
                break
        if key == None:
            raise AddToLeaderboardError
        self.__board[key]["times"].append([id,name,time])
        self.__board[key]["times"].sort(
            key=lambda x: datetime.strptime(x[2].strip(), "%H:%M:%S"))
        self.saveboard()

    def removefromleaderboard(self, id, leaderboardnum = 0):
        """
        removes a player from the leaderboard specified by number leaderboardnum
        :param id: player id to remove
        :param leaderboardnum: leaderboard number to remove the player from
        :return: None
        """
        for i in range(len(self.__board[str(leaderboardnum)]["times"])):
            if self.__board[str(leaderboardnum)]["times"][i] == id:
                del self.__board[str(leaderboardnum)]["times"][i]
                return
        raise DeleteFromLeaderboardError



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

