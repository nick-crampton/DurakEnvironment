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
    "rankList" : 'd'
}

##Pass array of players with their respective types:
## Human    - 0
## Bot      - 1
## Agent    - 2

trainingIterations = 1000
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
        'survivalCount': 0,
        'durakCount' : 0,
        'totalReward': 0
    }

    for i in range(trainingIterations):
        print(f"\nGame {i+1}")

        game = Game(playerList, lrParams, gameProperties)
        game.newGame()

        gameStats['survivalCount'] += game.survivalCount
        gameStats['durakCount'] += game.durakCount
        gameStats['totalReward'] += game.totalReward

    agent = game.agent

    return gameStats, agent

def saveExperimentResults(experimentNo, gameStats, agent, directory):
    filepath = os.path.join(directory, f"experiment_{experimentNo}.txt")
    os.makedirs(directory, exist_ok=True)

    with open(filepath, "w") as file:
        file.write(f"Experiment: {experimentNo}\n")
        file.write(f"Survival Count = {gameStats['survivalCount']}\n")
        file.write(f"Durak Count = {gameStats['durakCount']}\n")
        file.write(f"Total Reward = {gameStats['totalReward']}\n\n")
        file.write("State-Action Pairs and Q-Values:\n")

        for key, value in agent.qTable.items():
            file.write(f"{key}: {value}\n")

    print(f"Experiment results saved as {filepath}")

experimentNo = 1
playerList = createPlayers(playerTypes)
gameStats, agent = runExperiment(trainingIterations, playerList, lrParams, gameProperties)

targetDirectory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))

saveExperimentResults(experimentNo, gameStats, agent, targetDirectory)
