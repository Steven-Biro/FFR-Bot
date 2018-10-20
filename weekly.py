from datetime import datetime, timedelta
import json

class Weekly:
    def __init__(self, role = None, adminrole = None, seedchannel = None, leaderboardchannel = None, spoilerchannel = None):
        self.__role = role
        self.__adminrole = adminrole
        self.__seedchannel = seedchannel
        self.__leaderboardchannel = leaderboardchannel
        self.__spoilerchannel = spoilerchannel

    def load(self, seedchannel):
        try:
            with open('config.json', 'r') as f:
                data = json.load(f)
                self.__role = data[seedchannel]["role"]
                self.__adminrole = data[seedchannel]["adminrole"]
                self.__seedchannel = seedchannel
                self.__leaderboardchannel = data[seedchannel]["leaderboardchannel"]
                self.__spoilerchannel = data[seedchannel]["spoilerchannel"]
        except KeyError:
            print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "KeyError when trying to load " + seedchannel)


    def save(self):
        with open('config.json', 'r+') as f:
            data = json.load(f)
            f.seek(0)
            data[self.__seedchannel] = {"role": self.__role, "adminrole": self.__adminrole, "seedchannel": self.__seedchannel,
                                     "spoilerchannel": self.__spoilerchannel, "leaderboardchannel": self.__leaderboardchannel}
            json.dump(data, f)
            f.truncate()


    def set(self, variable, value):
        if variable == "seedchannel":
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
            return "trying to set invalid variable."

    def get(self, variable):
        if variable == "seedchannel":
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
            return "trying to get invalid variable."

    def getleaderboard(self):
        with open('leaderboards/'+self.__leaderboardchannel, 'r+') as f:
            self.__board = json.load(f)


    def saveboard(self):
        with open('leaderboards/' + self.__leaderboardchannel, 'r+') as f:
            f.seek(0)
            json.dump(self.__board, f)
            f.truncate()

    def loadboard(self):
        with open('leaderboards/' + self.__leaderboardchannel, 'r+') as f:
            self.__board = json.load(f)

    def initializeleaderboard(self, title, challengeplus = False):
        self.__board = dict()
        self.__board["title"] = title
        self.__board["times"] = []
        self.__board["forfeits"] = 0
        if challengeplus:
            self.__board["challenge+"] = []
            self.__board["forfeits+"] = 0
        self.saveboard()


    def addtoleaderboard(self, name, time, challengeplus = False):
        key = "times" if not challengeplus else "challenge+"
        self.__board[key][0] = name
        self.__board[key][1] = time
        self.__board[key].sort(
            key=lambda x: datetime.strptime(x[1].strip(), "%H:%M:%S"))
        self.saveboard()

    def removefromleaderboard(self, name, challengeplus = False):
        # TODO: change to use id instead of name, write the correct display name not the id
        key = "times" if not challengeplus else "challenge+"
        for i in range(len(self.__board["times"])):
            if self.__board[key][0] == name:
                del self.__board[key][i]
                break


    def writeleaderboard(self):
        boardstr = self.__board["title"] + "\n\n"
        for i in range(len(self.__board["times"])):
            boardstr += str(i + 1) + ") " + self.__board["times"][i][0] + " - " + self.__board["times"][i][1] + "\n"
        boardstr += "\nForfeits - " + self.__board["forfeits"]

        if "challenge+" in self.__board:
            boardstr += "\n\n**Challenge+**\n\n"
            for i in range(len(self.__board["challenge+"])):
                boardstr += str(i + 1) + ") " + self.__board["challenge+"][i][0] + " - " + self.__board["challenge+"][i][
                    1] + "\n"
            boardstr += "\nForfeits - " + self.__board["forfeits+"]

        return boardstr

