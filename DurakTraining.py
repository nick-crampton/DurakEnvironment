from durakNew.game import Game
from durakNew.playerTypes.agentPlayer import AgentPlayer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.humanPlayer import HumanPlayer
import json
import os

##RL Agent parameters
lrParams = {
    "learningRate": 0.1,
    "discount": 0.99,
    "epsilon": 0.1,
    "deckCount" : 36
}

gameProperties = {
    "handCount" : 3,
    "talonCount" : 12,
    "rankList" : rankListS
}

##Pass array of players with their respective types:
## Human    - 0
## Bot      - 1
## Agent    - 2

trainingIterations = 100
playerTypes = [2, 1]

def createPlayers(playerTypes):
    playerList = []
        
    for i, playerType in enumerate(playerTypes):
        if playerType == 0:
            ##Create HumanPlayer
            newPlayer = HumanPlayer([], i, None)
            pass
        elif playerType == 1:
            ##Create BotPlayer
            newPlayer = RandomBot([], i,  None)
            pass
        elif playerType == 2:
            ##Create AgentPlayer
            newPlayer = AgentPlayer([], i, None, learningRate = lrParams["learningRate"], discount = lrParams["discount"], epsilon = lrParams["epsilon"], deckCount=lrParams["deckCount"])
            pass

        playerList.append(newPlayer)

    return playerList

def runExperiment(trainingIterations, playerList, lrParams, gameProperties):
    
    gameStats = {
        'winCount': 0,
        'survivalCount': 0,
        'totalReward': 0,
    }

    for i in range(trainingIterations):
        game = Game(playerList, lrParams, gameProperties)
        game.newGame()

        gameStats['winCount'] += game.winCount
        gameStats['survivalCount'] += game.survivalCount
        gameStats['totalReward'] += game.totalReward

    agent = getAgent(playerList)

    return gameStats, agent

def getAgent(playerList):

    for player in playerList:

        if isinstance(player, AgentPlayer):
            return player
        
        else:
            print("no agent found.")
            return None

def saveQ_Table(qTable, filename, directory):
    filepath = os.path.join(directory, filename)
    os.makedirs(directory, exist_ok=True)

    qTable_to_json = json.dumps(qTable)
    with open(filename, "w") as file:
        file.write(qTable_to_json)

    print(f"Q-table saved as {filename}")

def loadQ_Table(qTable, filename, directory):
    
    with open(filename, "r") as file:
        qTable_from_json = file.read()

    qTable = json.loads(qTable_from_json)
    return qTable


playerList = createPlayers(playerTypes)
experimentX, agentX = runExperiment(trainingIterations, playerList, lrParams, gameProperties)

fname = "experimentX.json"
targetDirectory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))
saveQ_Table(agentX.qTable, fname, targetDirectory)

