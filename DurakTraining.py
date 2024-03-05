from durakNew.game import Game
from durakNew.playerTypes.agentPlayer import AgentPlayer
from durakNew.playerTypes.randomBot import RandomBot
from durakNew.playerTypes.humanPlayer import HumanPlayer
from durakNew.playerTypes.lowestValueBot import LowestValueBot
import json
import os
import matplotlib.pyplot as plt

##Pass array of players with their respective types:
## Human    - 0
## RandomBot      - 1
## Agent    - 2
## LowestValueBot - 3

def createPlayers(playerTypes, qTable = None, training = True):
    playerList = []
        
    for i, playerType in enumerate(playerTypes):
        if playerType == 0:
            ##Create HumanPlayer
            newPlayer = HumanPlayer([], i, None)
            pass
        elif playerType == 1:
            ##Create RandomBot
            newPlayer = RandomBot([], i,  None)
            pass
        elif playerType == 2:
            ##Create AgentPlayer
            newPlayer = AgentPlayer([], i, None, learningRate = lrParams["learningRate"], discount = lrParams["discount"], epsilon = lrParams["epsilon"], qTable = None, isTraining = training)
            pass

        elif playerType == 3:
            ##Create LowestValueBot
            newPlayer = LowestValueBot([], i, None)

        playerList.append(newPlayer)

    return playerList

def playAgent(playerTypes, gameProperties, directory, experimentNo):
    qTable = loadJSON(directory, experimentNo)
    
    playerList = createPlayers(playerTypes, qTable, False)

    game = Game(playerList, gameProperties = gameProperties)
    game.newGame()

def runExperiment(trainingIterations, playerList, lrParams, gameProperties, plotIntervals, metadata = None):
    
    if metadata is None:
        gameStats = {
        'trainingCount' : 0,
        'survivalCount': 0,
        'durakCount' : 0,
        'totalReward': 0,
        'survivalRates': [] 
        }

    else:
        gameStats = metadata

    for i in range(trainingIterations):
        print(f"\nGame {i+1}")

        game = Game(playerList, lrParams, gameProperties)
        game.newGame()

        gameStats['trainingCount'] += 1
        gameStats['survivalCount'] += game.survivalCount
        gameStats['durakCount'] += game.durakCount
        
        
        tempAgent = game.agent
        
        gameStats['totalReward'] += tempAgent.totalReward
        game.agent.totalReward = 0

        print(f"\nreward accumulated in game is {tempAgent.totalReward}")

        if i % plotIntervals == 0 and i > 0:
            survivalRate = (gameStats['survivalCount'] / gameStats['trainingCount']) * 100
            gameStats['survivalRates'].append(survivalRate)

    agent = game.agent

    return gameStats, agent

def saveMetadata(metadata, directory, experimentNo):
    metadataDirectory = os.path.join(directory, 'Metadata')
    filepath = os.path.join(metadataDirectory, f'metadata_{experimentNo}.json')

    with open(filepath, 'w') as file:
        json.dump(metadata, file)

def loadMetadata(directory, experimentNo):
    metadataDirectory = os.path.join(directory, 'Metadata')
    filepath = os.path.join(metadataDirectory, f'metadata_{experimentNo}.json')

    if not os.path.exists(filepath):
        print(f"No metadata found at {filepath}")
        return None
    
    with open(filepath, 'r') as file:
        metadata = json.load(file)

    return metadata

def saveJSON(qTable, directory, experimentNo):
    
    tableDirectory = os.path.join(directory, 'Q-Tables')
    filepath = os.path.join(tableDirectory, f'experiment_{experimentNo}.json')

    qTableSave = {str(key): value for key, value in qTable.items()}

    with open(filepath, 'w') as file:
        json.dump(qTableSave, file)

def loadJSON(directory, experimentNo):
    tableDirectory = os.path.join(directory, 'Q-Tables')
    filepath = os.path.join(tableDirectory, f'experiment_{experimentNo}.json')

    if not os.path.exists(filepath):
        print(f"No Q-table found at {filepath}")
        return None
    
    with open(filepath, 'r') as file:
        qTableStrKeys = json.load(file)

    qTable = {eval(key): value for key, value in qTableStrKeys.items()}
    return qTable

def plotSurvivalRate(gameStats, interval, experimentNo, directory):
    x = list(range(interval, len(gameStats['survivalRates']) * interval + 1, interval))
    y = gameStats['survivalRates']

    plt.plot(x, y, marker='o')
    plt.xlabel('Number of Games')
    plt.ylabel('Survival Rate (%)')
    plt.title('Survival Rate Over Time')
    plt.ylim(0, 100)  # Set y-axis to range from 0 to 100
    plt.axhline(y=50, color='r', linestyle='--')  # Add a horizontal line at 50%
    plt.grid(True)
    
    graphDirectory = os.path.join(directory, 'survival graphs')
    plt.savefig(os.path.join(graphDirectory, f"experiment {experimentNo}.png"))
    plt.show()
    print("Experiment graph saved.")

def saveExperimentResults(experimentNo, gameStats, lrParams, gameProperties, agent, directory):
    filepath = os.path.join(directory, f"experiment_{experimentNo}.txt")
    os.makedirs(directory, exist_ok=True)

    with open(filepath, "w") as file:
        file.write(f"Experiment: {experimentNo}\n")
        file.write(f"Survival Count = {gameStats['survivalCount']}\n")
        file.write(f"Durak Count = {gameStats['durakCount']}\n")
        file.write(f"Total Reward = {gameStats['totalReward']}\n")

        file.write(f"\nReinforcement Learning Parameters\n")
        for key, value in lrParams.items():
            file.write(f"{key}: {value}\n")
            
        file.write('\nGame Properties\n')

        for key, value in gameProperties.items():
            file.write(f"{key}: {value}\n")
            

        file.write("\nState-Action Pairs, their Q-Values, and the visitation tally:\n")

        sortedQTable = sorted(agent.qTable.keys(), key=lambda k: agent.stateActionCounter.get(k, 0), reverse=True)
        for key in sortedQTable:
            value = agent.qTable[key]
            count = agent.stateActionCounter.get(key, 0)
            
            file.write(f"{key}: {value}, Tally {count}\n")

    print(f"Experiment results saved as {filepath}")

def agentTraining(directory, playerTypes, experimentNo, lrParams, gameProperties, intervals, trainingIterations, qTable = False):
    
    if qTable:
        qTable = loadJSON(targetDirectory, experimentNo)
        metadata = loadMetadata(targetDirectory, experimentNo)
        playerList = createPlayers(playerTypes, qTable)
        gameStats, agent = runExperiment(trainingIterations, playerList, lrParams, gameProperties, intervals, metadata)

    else:
        playerList = createPlayers(playerTypes)
        gameStats, agent = runExperiment(trainingIterations, playerList, lrParams, gameProperties, intervals)

    saveExperimentResults(experimentNo, gameStats, lrParams, gameProperties, agent, directory)
    plotSurvivalRate(gameStats, intervals, experimentNo, directory)
    saveJSON(agent.qTable, targetDirectory, experimentNo)
    saveMetadata(gameStats, directory, experimentNo)

trainingIterations = 10000
playerTypes = [2, 3]
experimentNo = '4'
intervals = 100
targetDirectory = os.path.abspath(os.path.join(os.getcwd(), 'experiments'))

##RL Agent parameters
lrParams = {
    "learningRate": 0.1,
    "discount": 0.99,
    "epsilon": 0.1,
}

gameProperties = {
    "handCount" : 3,
    "talonCount" : 12,
    "rankList" : 'd'
}

agentTraining(targetDirectory, playerTypes, experimentNo, lrParams, gameProperties, intervals, trainingIterations, True)

##playAgent(playerTypes, gameProperties, targetDirectory, experimentNo)